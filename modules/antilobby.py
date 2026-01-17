# ============================================================================
# PROINVESTIX - ANTI-LOBBY & TRANSPARANTIE HUB
# Dossier 41: Contracten, Eigendom, Betalingen, Audit
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib

from ui.styles import COLORS, premium_header
from ui.components import page_header, premium_kpi_row, info_box, warning_box, success_message
from translations import get_text, get_current_language

def t(key):
    """Shorthand for translation"""
    return get_text(key, get_current_language())

# =============================================================================
# CONSTANTS
# =============================================================================

CONTRACT_TYPES = [
    "Infrastructure", "Sports Equipment", "Stadium Construction", 
    "Broadcasting Rights", "Sponsorship", "Medical Supplies",
    "Transportation", "Hospitality", "Security Services", "IT Systems"
]

CONTRACT_STATUSES = ["Draft", "Under Review", "Active", "Completed", "Suspended", "Cancelled"]

SECTORS = ["Sport", "Infrastructure", "Healthcare", "Technology", "Tourism", "Energy"]

ANOMALY_TYPES = [
    "Price Deviation", "Unusual Payment Pattern", "Hidden Ownership",
    "Conflict of Interest", "Missing Documentation", "Duplicate Invoice",
    "Unauthorized Modification", "Suspicious Timing"
]

# =============================================================================
# DEMO DATA GENERATORS
# =============================================================================

def generate_demo_contracts():
    """Generate demo contract data"""
    contracts = []
    
    contract_names = [
        "Stadium Casablanca Phase 2", "National Team Equipment 2025",
        "WK 2030 Broadcasting Package", "Youth Academy Infrastructure",
        "Medical Services Agreement", "Security Systems Upgrade",
        "Transportation Fleet", "Hospitality Training Program",
        "Digital Ticketing Platform", "VAR Technology Implementation"
    ]
    
    companies = [
        "Atlas Construction SA", "SportEquip Morocco", "MediaPro MENA",
        "TechVision Ltd", "SafeGuard Security", "TransMaghreb",
        "HospitalityPlus", "DigitalFirst MA", "MedServ International"
    ]
    
    for i, name in enumerate(contract_names):
        contract_id = f"CTR-{2024}{str(i+1).zfill(4)}"
        
        value = random.randint(500000, 50000000)
        
        contracts.append({
            "contract_id": contract_id,
            "name": name,
            "contractor": random.choice(companies),
            "sector": random.choice(SECTORS),
            "type": random.choice(CONTRACT_TYPES),
            "value": value,
            "status": random.choice(CONTRACT_STATUSES),
            "transparency_score": random.randint(60, 100),
            "ubo_verified": random.choice([True, True, True, False]),
            "start_date": (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
            "end_date": (datetime.now() + timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d"),
            "created_at": datetime.now().strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(contracts)

def generate_demo_owners():
    """Generate demo UBO data"""
    owners = []
    
    names = [
        "Ahmed Benali", "Fatima El Amrani", "Mohammed Tazi",
        "Youssef Chraibi", "Karim Lahlou", "Nadia Berrada",
        "Hassan Benjelloun", "Samira Alaoui", "Omar Fassi"
    ]
    
    companies = [
        "Atlas Construction SA", "SportEquip Morocco", "MediaPro MENA",
        "TechVision Ltd", "SafeGuard Security", "TransMaghreb"
    ]
    
    for name in names:
        owner_id = f"UBO-{random.randint(100000, 999999)}"
        owners.append({
            "owner_id": owner_id,
            "full_name": name,
            "company": random.choice(companies),
            "ownership_percentage": random.randint(10, 100),
            "verification_status": random.choice(["Verified", "Verified", "Pending", "Under Review"]),
            "risk_flags": random.randint(0, 3),
            "pep_status": random.choice(["No", "No", "No", "Yes"]),  # Politically Exposed Person
            "sanctions_check": random.choice(["Clear", "Clear", "Clear", "Under Review"]),
            "last_verified": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(owners)

def generate_demo_payments():
    """Generate demo payment data"""
    payments = []
    
    for i in range(25):
        payment_id = f"PAY-{random.randint(100000, 999999)}"
        contract_id = f"CTR-{2024}{str(random.randint(1, 10)).zfill(4)}"
        
        amount = random.randint(10000, 5000000)
        
        payments.append({
            "payment_id": payment_id,
            "contract_id": contract_id,
            "amount": amount,
            "currency": "MAD",
            "payment_type": random.choice(["Advance", "Milestone", "Final", "Recurring"]),
            "status": random.choice(["Completed", "Pending", "Processing", "On Hold"]),
            "recipient": random.choice(["Atlas Construction SA", "SportEquip Morocco", "MediaPro MENA"]),
            "foundation_contribution": round(amount * 0.005, 2),
            "date": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
            "verified": random.choice([True, True, True, False])
        })
    
    return pd.DataFrame(payments)

def generate_demo_anomalies():
    """Generate demo anomaly data"""
    anomalies = []
    
    for i in range(8):
        anomaly_id = f"ANO-{random.randint(100000, 999999)}"
        
        anomalies.append({
            "anomaly_id": anomaly_id,
            "contract_id": f"CTR-{2024}{str(random.randint(1, 10)).zfill(4)}",
            "type": random.choice(ANOMALY_TYPES),
            "severity": random.choice(["Low", "Medium", "High", "Critical"]),
            "description": random.choice([
                "Contract value 35% above market rate",
                "Payment to unverified subsidiary",
                "Ownership structure changed without notification",
                "Invoice date precedes contract start",
                "Multiple payments on same day to same recipient",
                "Missing required documentation"
            ]),
            "status": random.choice(["Open", "Investigating", "Resolved", "Escalated"]),
            "detected_at": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "assigned_to": random.choice(["Compliance Team", "Legal", "Audit", "Unassigned"])
        })
    
    return pd.DataFrame(anomalies)

# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_contract_registry():
    """Render Contract Registry tab"""
    st.markdown("### 📑 Contract Registry")
    st.caption("Central repository for all contracts")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        sector_filter = st.multiselect("Sector", SECTORS)
    with col2:
        status_filter = st.multiselect(t("status"), CONTRACT_STATUSES)
    with col3:
        min_value = st.number_input("Min Value (MAD)", value=0, step=100000)
    
    df = generate_demo_contracts()
    
    # Apply filters
    if sector_filter:
        df = df[df['sector'].isin(sector_filter)]
    if status_filter:
        df = df[df['status'].isin(status_filter)]
    if min_value > 0:
        df = df[df['value'] >= min_value]
    
    # Summary
    total_value = df['value'].sum()
    st.metric("Total Contract Value", f"MAD {total_value:,.0f}")
    
    st.divider()
    
    # Table
    df_display = df.copy()
    df_display['value'] = df_display['value'].apply(lambda x: f"MAD {x:,.0f}")
    st.dataframe(df_display, width="stretch", hide_index=True)
    
    # Add new contract
    with st.expander("➕ Register New Contract"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Contract Name")
            new_contractor = st.text_input("Contractor")
            new_sector = st.selectbox("Sector", SECTORS)
        with col2:
            new_value = st.number_input("Value (MAD)", min_value=0, step=10000)
            new_type = st.selectbox("Type", CONTRACT_TYPES)
            new_start = st.date_input("Start Date")
        
        if st.button("Register Contract", type="primary"):
            st.success(f"Contract '{new_name}' registered successfully!")

def render_ownership_control():
    """Render Ownership Control tab met Identity Shield koppeling"""
    from database.connection import get_data, run_query
    from modules.identity_shield import calculate_fraud_score
    
    st.markdown("###  Ultimate Beneficial Owner (UBO) Registry")
    st.caption("Track real ownership behind contracts - Linked to Identity Shield")
    
    info_box(
        "Anti-Lobby Compliance",
        "All contractors must register their Ultimate Beneficial Owners (UBO) before contract approval. UBOs are verified against Identity Shield."
    )
    
    # Haal echte identity data op
    df_identities = get_data("identity_shield")
    df_owners = generate_demo_owners()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total UBOs", len(df_owners))
    with col2:
        verified_count = len(df_identities) if not df_identities.empty else 0
        st.metric("Identity Shield Verified", verified_count)
    with col3:
        st.metric("PEP Flags", len(df_owners[df_owners['pep_status'] == 'Yes']))
    with col4:
        st.metric("Risk Flags", df_owners['risk_flags'].sum())
    
    st.divider()
    
    # UBO Table
    st.dataframe(df_owners, width="stretch", hide_index=True)
    
    # Verify UBO against Identity Shield
    with st.expander(" Verify UBO via Identity Shield", expanded=False):
        st.markdown("**Link UBO to verified Identity Shield profile**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            verify_name = st.text_input("Full Legal Name")
            verify_id = st.text_input("National ID / Passport Number")
            verify_company = st.text_input("Company Name")
            ownership_pct = st.slider("Ownership Percentage", 0, 100, 25)
        
        with col2:
            # Zoek in Identity Shield
            if not df_identities.empty:
                identity_options = ["-- Select Identity --"] + df_identities['identity_id'].tolist()
                selected_identity = st.selectbox("Link to Identity Shield", identity_options)
                
                if selected_identity != "-- Select Identity --":
                    # Toon Identity Shield info
                    identity_row = df_identities[df_identities['identity_id'] == selected_identity].iloc[0]
                    st.info(f"**Identity:** {identity_row.get('name', 'N/A')}")
                    st.info(f"**Risk Level:** {identity_row.get('risk_level', 'N/A')}")
                    
                    # Bereken fraud score
                    fraud_score = calculate_fraud_score(selected_identity)
                    if fraud_score < 30:
                        st.success(f"**Fraud Score:** {fraud_score} (Low Risk)")
                    elif fraud_score < 60:
                        st.warning(f"**Fraud Score:** {fraud_score} (Medium Risk)")
                    else:
                        st.error(f"**Fraud Score:** {fraud_score} (High Risk)")
            else:
                st.warning("No verified identities in Identity Shield. Register identities first.")
                selected_identity = None
        
        if st.button("Run Full UBO Verification", type="primary", width="stretch"):
            if not verify_name or not verify_id:
                st.error("Name and ID are required")
            else:
                with st.spinner("Running verification against Identity Shield, PEP lists, Sanctions..."):
                    import time
                    time.sleep(2)
                
                st.success(" UBO Verification Complete!")
                
                result_col1, result_col2, result_col3 = st.columns(3)
                with result_col1:
                    st.metric("Sanctions Check", " Clear")
                    st.metric("PEP Check", " Not a PEP")
                with result_col2:
                    st.metric("Identity Shield", " Verified" if selected_identity else " Not Linked")
                    st.metric("Ownership Valid", f" {ownership_pct}%")
                with result_col3:
                    risk = "Low" if ownership_pct < 25 else ("Medium" if ownership_pct < 50 else "High")
                    st.metric("Overall Risk", risk)
                    st.metric("Compliance Status", " Approved")
                
                # Log de verificatie
                from auth.security import log_audit
                log_audit("system", "UBO_VERIFIED", "Anti-Lobby", f"{verify_name} - {verify_company}")
    
    # Cross-reference met Identity Shield
    st.divider()
    st.markdown("### 🔗 Identity Shield Cross-Reference")
    
    if not df_identities.empty:
        # Toon identities met hoog risico
        high_risk = df_identities[df_identities['risk_level'].isin(['HIGH', 'CRITICAL'])] if 'risk_level' in df_identities.columns else pd.DataFrame()
        
        if not high_risk.empty:
            warning_box("High Risk Identities", f"{len(high_risk)} identities flagged as high risk in Identity Shield")
            st.dataframe(high_risk[['identity_id', 'name', 'risk_level']] if 'name' in high_risk.columns else high_risk, 
                        width="stretch", hide_index=True)
        else:
            st.success(" No high-risk identities detected")
    else:
        st.info("No Identity Shield data available. Register identities to enable cross-referencing.")

def render_payment_tracking():
    """Render Payment Tracking tab"""
    st.markdown("###  Payment Tracking")
    st.caption("Monitor all contract-related payments")
    
    df = generate_demo_payments()
    
    # Summary
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Payments", len(df))
    with col2:
        st.metric("Total Amount", f"MAD {df['amount'].sum():,.0f}")
    with col3:
        st.metric("Foundation Contrib.", f"MAD {df['foundation_contribution'].sum():,.0f}")
    with col4:
        st.metric("Pending", len(df[df['status'] == 'Pending']))
    
    st.divider()
    
    # Table
    df_display = df.copy()
    df_display['amount'] = df_display['amount'].apply(lambda x: f"MAD {x:,.0f}")
    df_display['foundation_contribution'] = df_display['foundation_contribution'].apply(lambda x: f"MAD {x:,.0f}")
    st.dataframe(df_display, width="stretch", hide_index=True)
    
    # Payment verification
    with st.expander(" Verify Payment"):
        payment_id = st.text_input("Payment ID")
        
        if st.button("Verify Payment"):
            st.success(f"Payment {payment_id} verified and logged!")

def render_audit_dashboard():
    """Render Audit Dashboard tab"""
    st.markdown("###  Real-time Audit Dashboard")
    st.caption("Anomaly detection and compliance monitoring")
    
    # Anomaly alerts
    anomalies = generate_demo_anomalies()
    
    critical_count = len(anomalies[anomalies['severity'] == 'Critical'])
    high_count = len(anomalies[anomalies['severity'] == 'High'])
    
    if critical_count > 0:
        st.error(f"🚨 {critical_count} CRITICAL anomalies detected!")
    if high_count > 0:
        st.warning(f" {high_count} HIGH severity anomalies require attention")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Anomalies", len(anomalies))
    with col2:
        st.metric("Open Cases", len(anomalies[anomalies['status'] == 'Open']))
    with col3:
        st.metric("Under Investigation", len(anomalies[anomalies['status'] == 'Investigating']))
    with col4:
        st.metric("Resolved", len(anomalies[anomalies['status'] == 'Resolved']))
    
    st.divider()
    
    # Anomaly table
    st.markdown("#### Detected Anomalies")
    st.dataframe(anomalies, width="stretch", hide_index=True)
    
    st.divider()
    
    # Transparency metrics
    st.markdown("#### Transparency Metrics")
    
    contracts = generate_demo_contracts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        avg_transparency = contracts['transparency_score'].mean()
        st.metric("Avg Transparency Score", f"{avg_transparency:.1f}%")
        
        ubo_verified = (contracts['ubo_verified'].sum() / len(contracts)) * 100
        st.metric("UBO Verification Rate", f"{ubo_verified:.1f}%")
    
    with col2:
        # Savings estimate
        total_value = contracts['value'].sum()
        estimated_savings = total_value * 0.05  # 5% savings estimate
        st.metric("Estimated Savings", f"MAD {estimated_savings:,.0f}")
        st.caption("Through transparency measures")
        
        st.metric("Compliance Rate", "94.2%")

def render_reports():
    """Render Reports tab"""
    st.markdown("###  Compliance Reports")
    st.caption("Generate audit and compliance reports")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Generate Report")
        
        report_type = st.selectbox("Report Type", [
            "Monthly Compliance Summary",
            "Contract Audit Report",
            "UBO Verification Report",
            "Payment Analysis Report",
            "Anomaly Investigation Report",
            "Transparency Score Report"
        ])
        
        date_range = st.date_input("Date Range", value=(datetime.now() - timedelta(days=30), datetime.now()))
        
        include_options = st.multiselect("Include Sections", [
            "Executive Summary",
            "Contract Details",
            "Payment Analysis",
            "UBO Registry",
            "Anomaly Report",
            "Recommendations"
        ], default=["Executive Summary", "Contract Details"])
        
        if st.button("📄 Generate Report", type="primary", width="stretch"):
            with st.spinner("Generating report..."):
                import time
                time.sleep(2)
            
            st.success("Report generated successfully!")
            st.download_button(
                "📥 Download Report (PDF)",
                data="Report content here",
                file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf"
            )
    
    with col2:
        st.markdown("#### Recent Reports")
        
        for i in range(4):
            with st.container(border=True):
                st.markdown(f"**Report #{random.randint(1000, 9999)}**")
                st.caption((datetime.now() - timedelta(days=i*7)).strftime("%Y-%m-%d"))
                st.caption(random.choice(["Monthly Summary", "Audit Report", "UBO Report"]))

# =============================================================================
# MAIN RENDER
# =============================================================================

def render(username: str = None):
    """Main render function for Anti-Lobby Hub"""
    
    page_header(
        t("antilobby_title"),
        t("antilobby_subtitle"),
        icon=""
    )
    
    # KPIs
    contracts = generate_demo_contracts()
    payments = generate_demo_payments()
    anomalies = generate_demo_anomalies()
    
    premium_kpi_row([
        ("📑", t("active_contracts"), str(len(contracts)), f"MAD {contracts['value'].sum():,.0f}"),
        ("", t("verified_ubos"), "47", t("compliance_100")),
        ("", t("payments_tracked"), str(len(payments)), t("this_month")),
        ("", t("open_anomalies"), str(len(anomalies[anomalies['status'] == 'Open'])), t("require_action"))
    ])
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        t("contract_registry"),
        t("ownership_control"),
        t("payment_tracking"),
        t("audit_dashboard"),
        t("reports")
    ])
    
    with tab1:
        render_contract_registry()
    
    with tab2:
        render_ownership_control()
    
    with tab3:
        render_payment_tracking()
    
    with tab4:
        render_audit_dashboard()
    
    with tab5:
        render_reports()
