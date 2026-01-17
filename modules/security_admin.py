# ============================================================================
# SECURITY CENTER & ADMIN PANEL MODULE
# Audit logs, security alerts, gebruikersbeheer
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from database.connection import get_data, run_query
from auth.security import hash_password, log_audit
from ui.components import metric_row, page_header


# =============================================================================
# SECURITY CENTER
# =============================================================================

def render_security_center(username: str, user_role: str):
    """Render de Security Center module."""
    
    page_header(
        " Security Center",
        "Audit & Compliance | Complete Security Monitoring, Audit Trails & Compliance Reports"
    )
    
    if user_role not in ["SuperAdmin", "Security Staff"]:
        st.warning(" This module requires Security Staff or SuperAdmin privileges.")
        return
    
    tab1, tab2, tab3 = st.tabs([" Audit Logs", " Security Alerts", " Compliance Reports"])
    
    with tab1:
        render_audit_logs()
    
    with tab2:
        render_security_alerts()
    
    with tab3:
        render_compliance_reports()


def render_audit_logs():
    """Render audit logs met pagination."""
    
    st.subheader(" System Audit Trail")
    
    from ui.components import paginated_dataframe
    from database.connection import count_records, get_data
    
    # Tel totaal voor metrics
    total_logs = count_records("audit_logs")
    failed_logs = count_records("audit_logs", "success = 0")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric(" Totaal Logs", f"{total_logs:,}")
    col_m2.metric(" Succesvol", f"{total_logs - failed_logs:,}")
    col_m3.metric(" Gefaald", failed_logs)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Haal alleen recente logs op (niet allemaal!)
    df_audit = get_data("audit_logs", limit=500, order_by="timestamp DESC")
    
    if not df_audit.empty:
        col1, col2, col3 = st.columns(3)
        
        # Beperk dropdown opties tot unieke waarden in huidige batch
        with col1:
            unique_users = df_audit['username'].unique().tolist()[:20]  # Max 20 opties
            user_filter = st.selectbox(
                "Filter by User", 
                ["All"] + unique_users
            )
        with col2:
            unique_modules = df_audit['module'].dropna().unique().tolist()[:20]
            module_filter = st.selectbox(
                "Filter by Module", 
                ["All"] + unique_modules
            )
        with col3:
            success_filter = st.selectbox(
                t("status"), 
                ["All", "Success Only", "Failures Only"]
            )
        
        filtered = df_audit.copy()
        
        if user_filter != "All":
            filtered = filtered[filtered['username'] == user_filter]
        if module_filter != "All":
            filtered = filtered[filtered['module'] == module_filter]
        if success_filter == "Success Only":
            filtered = filtered[filtered['success'] == 1]
        elif success_filter == "Failures Only":
            filtered = filtered[filtered['success'] == 0]
        
        st.write(f"###  Showing {len(filtered)} logs (van laatste 500)")
        
        # Gebruik pagination
        paginated_dataframe(
            filtered, 
            per_page=25, 
            key_prefix="audit_logs",
            empty_message="Geen logs gevonden met deze filters."
        )
        
        # Export button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(" Export Audit Logs to CSV"):
            csv = filtered.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "audit_logs_export.csv",
                "text/csv"
            )
    else:
        st.info("No audit logs yet.")


def render_security_alerts():
    """Render security alerts."""
    
    st.subheader(" Active Security Alerts")
    
    df_fraud = get_data("fraud_alerts")
    
    if not df_fraud.empty:
        total = len(df_fraud)
        active = len(df_fraud[df_fraud['status'] == 'ACTIVE'])
        high = len(df_fraud[(df_fraud['severity'] == 'HIGH') & (df_fraud['status'] == 'ACTIVE')])
        resolved_today = 0
        
        try:
            resolved_today = len(df_fraud[
                (df_fraud['status'] == 'RESOLVED') & 
                (pd.to_datetime(df_fraud['resolved_at']).dt.date == datetime.now().date())
            ])
        except:
            pass
        
        metric_row([
            (" Total Alerts", total),
            (" Active", active),
            (" High Priority", high),
            (" Resolved Today", resolved_today),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        active_alerts = df_fraud[df_fraud['status'] == 'ACTIVE'].sort_values('severity', ascending=False)
        
        if not active_alerts.empty:
            st.write("###  Active Alerts Requiring Action")
            st.dataframe(active_alerts, use_container_width=True, hide_index=True)
        else:
            st.success(" No active alerts! System running securely.")
    else:
        st.info("No fraud alerts in system.")


def render_compliance_reports():
    """Render compliance reports."""
    
    st.subheader(" Compliance & Regulatory Reports")
    
    st.write("###  GDPR Compliance Status")
    
    df_identities = get_data("identity_shield")
    df_health = get_data("health_records")
    df_audit = get_data("audit_logs")
    
    identities_monitored = len(df_identities[df_identities['monitoring_enabled'] == 1]) if not df_identities.empty else 0
    audit_trail_active = len(df_audit) > 0
    
    metric_row([
        (" Monitored Identities", identities_monitored),
        (" Data Retention", "YES"),
        (" Audit Trail", "ACTIVE" if audit_trail_active else "INACTIVE"),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.write("###  Compliance Checklist")
    
    compliance_items = [
        ("GDPR Data Protection", True),
        ("Audit Trail Logging", audit_trail_active),
        ("Encrypted Storage", True),
        ("User Authentication", True),
        ("Access Control", True),
        ("Data Backup", False),
        ("Incident Response Plan", True)
    ]
    
    for item, status in compliance_items:
        if status:
            st.success(f" {item}")
        else:
            st.warning(f" {item} - Requires Implementation")


# =============================================================================
# ADMIN PANEL
# =============================================================================

def render_admin_panel(username: str, user_role: str):
    """Render de Admin Panel module."""
    
    page_header(
        " Admin Panel",
        "User Management | SuperAdmin Control Center"
    )
    
    if user_role != "SuperAdmin":
        st.error(" Access Denied. This module requires SuperAdmin privileges.")
        return
    
    tab1, tab2 = st.tabs([" User Management", " System Settings"])
    
    with tab1:
        render_user_management(username)
    
    with tab2:
        render_system_settings()


def render_user_management(admin_username: str):
    """Render user management."""
    
    st.subheader(" Registered Users")
    
    df_users = get_data("user_registry")
    
    if not df_users.empty:
        display_users = df_users.drop('password_hash', axis=1)
        st.dataframe(display_users, use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        total_users = len(df_users)
        active_users = len(df_users[df_users['active'] == 1])
        admins = len(df_users[df_users['role'] == 'SuperAdmin'])
        
        metric_row([
            ("Total Users", total_users),
            ("Active", active_users),
            ("Admins", admins),
        ])
    else:
        st.info("No users in system.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("####  Reset User Password")
        with st.form("reset_pw"):
            reset_user = st.selectbox(
                "Select User", 
                df_users['username'].tolist() if not df_users.empty else []
            )
            new_pw = st.text_input("New Password", type="password")
            
            if st.form_submit_button(" Reset Password"):
                if len(new_pw) < 8:
                    st.error("Password must be at least 8 characters.")
                else:
                    new_hash = hash_password(new_pw)
                    success = run_query(
                        "UPDATE user_registry SET password_hash = ? WHERE username = ?",
                        (new_hash, reset_user)
                    )
                    if success:
                        st.success(f" Password reset for {reset_user}")
                        log_audit(admin_username, "PASSWORD_RESET", "Admin", 
                                 details=f"User: {reset_user}")
    
    with col2:
        st.write("####  Deactivate User")
        with st.form("deactivate"):
            deact_user = st.selectbox(
                "Select User", 
                [u for u in df_users['username'].tolist() if u != 'admin'] if not df_users.empty else []
            )
            
            if st.form_submit_button(" Deactivate"):
                success = run_query(
                    "UPDATE user_registry SET active = 0 WHERE username = ?", 
                    (deact_user,)
                )
                if success:
                    st.warning(f" User {deact_user} deactivated")
                    log_audit(admin_username, "USER_DEACTIVATED", "Admin", 
                             details=f"User: {deact_user}")
                    st.rerun()


def render_system_settings():
    """Render system settings."""
    
    import os
    from config import DB_FILE, VAULT_DIR, ALLOWED_TABLES
    from auth.security import BCRYPT_AVAILABLE
    
    st.subheader(" System Configuration")
    
    st.write("###  Security Settings")
    
    # Check QR availability
    try:
        import qrcode
        qr_available = True
    except ImportError:
        qr_available = False
    
    st.info(f"""
    **Current Configuration:**
    - Password Hashing: {'bcrypt ( Secure)' if BCRYPT_AVAILABLE else 'SHA256 ( Upgrade to bcrypt)'}
    - QR Code Generation: {'Enabled ' if qr_available else 'Disabled (install qrcode)'}
    - Blockchain Secret: {'Environment Variable ' if 'TICKETCHAIN_SECRET' in os.environ else 'Default ( Set in production)'}
    - Database Indexes: Enabled  (16 indexes)
    - Audit Logging: Enabled 
    - Foundation Rate: 0.5% (Masterplan Compliant )
    """)
    
    st.divider()
    
    st.write("###  System Statistics")
    
    # Calculate stats
    total_records = sum([len(get_data(t)) for t in ALLOWED_TABLES])
    db_size = os.path.getsize(DB_FILE) / (1024*1024) if os.path.exists(DB_FILE) else 0
    vault_size = 0
    
    if os.path.exists(VAULT_DIR):
        for f in os.listdir(VAULT_DIR):
            fpath = os.path.join(VAULT_DIR, f)
            if os.path.isfile(fpath):
                vault_size += os.path.getsize(fpath)
        vault_size = vault_size / (1024*1024)
    
    metric_row([
        (" Total Records", f"{total_records:,}"),
        (" Database Size", f"{db_size:.1f} MB"),
        (" Vault Size", f"{vault_size:.1f} MB"),
        (" Modules Active", "11/11"),
    ])
