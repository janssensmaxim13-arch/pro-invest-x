# ============================================================================
# IDENTITY SHIELD™ MODULE
# Digitale identiteit bescherming en fraud detectie
# ============================================================================

import streamlit as st
import uuid
from datetime import datetime, timedelta

from config import Options, Messages, DB_FILE
from database.connection import get_data, run_query, check_duplicate_id
from utils.helpers import sanitize_id, generate_uuid
from auth.security import log_audit
from ui.components import metric_row, data_table_with_empty_state, page_header


def calculate_fraud_score(identity_id: str) -> int:
    """
    Bereken fraud score voor een identiteit.
    
    Factoren:
    - Actieve fraud alerts
    - Recent ticket volume (mogelijke bot)
    - Gefaalde login pogingen
    """
    import sqlite3
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    score = 0
    
    try:
        # Factor 1: Actieve fraud alerts
        cursor.execute(
            "SELECT COUNT(*) FROM fraud_alerts WHERE identity_id=? AND status='ACTIVE'", 
            (identity_id,)
        )
        active_alerts = cursor.fetchone()[0]
        score += active_alerts * 20
        
        # Factor 2: Recent tickets (mogelijke bot)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute(
            "SELECT COUNT(*) FROM ticketchain_tickets WHERE owner_id=? AND minted_at > ?", 
            (identity_id, week_ago)
        )
        recent_tickets = cursor.fetchone()[0]
        if recent_tickets > 50:
            score += 30
        elif recent_tickets > 20:
            score += 15
        
        # Factor 3: Gefaalde logins
        cursor.execute(
            "SELECT COUNT(*) FROM audit_logs WHERE username=? AND action='LOGIN_FAILED' AND timestamp > ?", 
            (identity_id, week_ago)
        )
        failed_logins = cursor.fetchone()[0]
        score += min(failed_logins * 5, 25)
        
        # Update score in database
        cursor.execute(
            "UPDATE identity_shield SET fraud_score=? WHERE id=?", 
            (min(score, 100), identity_id)
        )
        conn.commit()
        
        return score
        
    except:
        return 0
    finally:
        conn.close()


def render(username: str):
    """Render de Identity Shield module."""
    
    page_header(
        "️ Identity Shield™",
        "Digital Protection Layer | 24/7 AI-Powered Identity Verification & Fraud Detection"
    )
    
    tab1, tab2, tab3 = st.tabs([" Identity Registry", " Fraud Monitoring", " Analytics"])
    
    # =========================================================================
    # TAB 1: Identity Registry
    # =========================================================================
    with tab1:
        render_identity_registry(username)
    
    # =========================================================================
    # TAB 2: Fraud Monitoring
    # =========================================================================
    with tab2:
        render_fraud_monitoring(username)
    
    # =========================================================================
    # TAB 3: Analytics
    # =========================================================================
    with tab3:
        render_analytics()


def render_identity_registry(username: str):
    """Render identity registration form and list."""
    
    with st.expander(" Register New Identity", expanded=False):
        with st.form("id_reg"):
            col1, col2 = st.columns(2)
            
            with col1:
                raw_id = st.text_input("ID/Passport Number", help="Unique identifier")
                name = st.text_input("Full Legal Name")
                country = st.text_input("Country of Origin")
            
            with col2:
                role = st.selectbox("Role", Options.ROLES)
                monitoring = st.checkbox("Enable 24/7 Monitoring", value=True)
            
            if st.form_submit_button(" VERIFY & STORE", width="stretch"):
                sid = sanitize_id(raw_id)
                
                if not sid:
                    st.error(Messages.INVALID_ID)
                elif not name or not name.strip():
                    st.error(Messages.NAME_REQUIRED)
                elif check_duplicate_id(sid, 'identity_shield'):
                    st.error(Messages.DUPLICATE_ID.format(sid))
                else:
                    risk = "MEDIUM" if role in ["Investor", "Partner"] else "LOW"
                    
                    success = run_query(
                        "INSERT INTO identity_shield VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (sid, name, role, country, risk, 0, 1 if monitoring else 0, 
                         datetime.now().isoformat())
                    )
                    
                    if success:
                        st.success(Messages.IDENTITY_SECURED.format(name, risk))
                        log_audit(username, "IDENTITY_CREATED", "Identity Shield", 
                                 details=f"ID: {sid}, Role: {role}")
                        st.rerun()
    
    st.divider()
    
    # Identity list
    st.write("### ️ Verified Identity Registry")
    df = get_data("identity_shield")
    
    if not df.empty:
        display_df = df.copy()
        display_df['risk_indicator'] = display_df.apply(
            lambda x: f" HIGH ({x['fraud_score']})" if x['fraud_score'] >= 70 
            else f" MEDIUM ({x['fraud_score']})" if x['fraud_score'] >= 30 
            else f" LOW ({x['fraud_score']})",
            axis=1
        )
        
        cols_to_show = ['id', 'name', 'role', 'country', 'risk_indicator', 'timestamp']
        st.dataframe(display_df[cols_to_show], width="stretch", hide_index=True)
    else:
        st.info(" No verified identities yet. Register the first identity above.")


def render_fraud_monitoring(username: str):
    """Render fraud monitoring section."""
    
    st.subheader(" Active Fraud Detection System")
    
    df_fraud = get_data("fraud_alerts")
    
    if not df_fraud.empty:
        # Metrics
        active = len(df_fraud[df_fraud['status'] == 'ACTIVE'])
        resolved = len(df_fraud[df_fraud['status'] == 'RESOLVED'])
        total = len(df_fraud)
        
        metric_row([
            (" Active Alerts", active),
            (" Resolved", resolved),
            (" Total Detected", total),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Active alerts
        st.write("####  Active Fraud Alerts")
        active_alerts = df_fraud[df_fraud['status'] == 'ACTIVE']
        
        if not active_alerts.empty:
            for idx, alert in active_alerts.iterrows():
                severity_color = "" if alert['severity'] == "HIGH" else "" if alert['severity'] == "MEDIUM" else ""
                
                with st.expander(f"{severity_color} {alert['alert_type']} - {alert['identity_id']} ({alert['created_at'][:10]})"):
                    st.write(f"**Description:** {alert['description']}")
                    st.write(f"**Auto-detected:** {'Yes' if alert['auto_detected'] else 'Manual'}")
                    st.write(f"**Created:** {alert['created_at']}")
                    
                    if st.button(f" Mark as Resolved", key=f"resolve_{alert['alert_id']}"):
                        run_query(
                            "UPDATE fraud_alerts SET status='RESOLVED', resolved_at=? WHERE alert_id=?",
                            (datetime.now().isoformat(), alert['alert_id'])
                        )
                        log_audit(username, "FRAUD_RESOLVED", "Identity Shield",
                                 details=f"Alert: {alert['alert_id']}")
                        st.success(Messages.ALERT_RESOLVED)
                        st.rerun()
        else:
            st.success(" No active alerts! System running clean.")
    else:
        st.info("No fraud alerts in system.")
    
    st.divider()
    
    # Manual alert creation
    render_manual_alert_form(username)


def render_manual_alert_form(username: str):
    """Render form for creating manual fraud alerts."""
    
    st.write("####  Create Manual Fraud Alert")
    
    from database.connection import get_data
    
    with st.form("manual_alert"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Zoekfunctie in plaats van dropdown (schaalbaarheid voor 80k+ users)
            search_query = st.text_input(
                " Zoek Identity (ID of naam)",
                placeholder="Type om te zoeken..."
            )
            
            # Zoek in database met limit
            df_identities = get_data("identity_shield", limit=50)
            
            identity_options = {}
            if not df_identities.empty:
                if search_query:
                    # Filter op zoekterm
                    mask = (
                        df_identities['id'].str.contains(search_query, case=False, na=False) |
                        df_identities['name'].str.contains(search_query, case=False, na=False)
                    )
                    filtered = df_identities[mask].head(20)
                else:
                    filtered = df_identities.head(20)
                
                identity_options = {
                    row['id']: f"{row['name']} ({row['id']})"
                    for _, row in filtered.iterrows()
                }
            
            if not identity_options:
                st.warning("Geen identiteiten gevonden. Registreer eerst in Identity Shield.")
                alert_identity = None
            else:
                alert_identity = st.selectbox(
                    "Selecteer Identity",
                    list(identity_options.keys()),
                    format_func=lambda x: identity_options.get(x, x)
                )
            
            alert_type = st.selectbox("Alert Type", Options.FRAUD_ALERT_TYPES)
        
        with col2:
            severity = st.selectbox("Severity", Options.URGENCY_LEVELS)
            description = st.text_area("Description", placeholder="Describe the fraud incident...")
        
        submitted = st.form_submit_button(" CREATE ALERT", width="stretch")
        
        if submitted:
            if not alert_identity:
                st.error("Selecteer een identity.")
            else:
                alert_id = generate_uuid("FRD")
                
                success = run_query(
                    "INSERT INTO fraud_alerts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (alert_id, alert_identity, alert_type, severity, description, 
                     0, "ACTIVE", datetime.now().isoformat(), None)
                )
                
                if success:
                    calculate_fraud_score(alert_identity)
                    st.success("Alert created and fraud score updated!")
                    log_audit(username, "FRAUD_ALERT_CREATED", "Identity Shield")
                    st.rerun()


def render_analytics():
    """Render identity analytics."""
    
    st.subheader(" Identity & Fraud Analytics")
    
    df = get_data("identity_shield")
    
    if not df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("#### Risk Distribution")
            risk_dist = df['risk_level'].value_counts()
            st.bar_chart(risk_dist)
        
        with col2:
            st.write("#### Role Distribution")
            role_dist = df['role'].value_counts()
            st.bar_chart(role_dist)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # High risk identities
        high_risk = df[df['fraud_score'] >= 50].sort_values('fraud_score', ascending=False)
        
        if not high_risk.empty:
            st.warning("️ **High-Risk Identities Requiring Attention:**")
            st.dataframe(
                high_risk[['id', 'name', 'fraud_score', 'risk_level']], 
                width="stretch", 
                hide_index=True
            )
        else:
            st.success(" No high-risk identities detected.")
    else:
        st.info("No identity data available for analytics.")
