# ============================================================================
# ADAPTERS MODULE
# Sport, Mobility en Health adapters
# ============================================================================

import streamlit as st
from datetime import datetime

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import Options
from database.connection import get_data, run_query
from utils.helpers import get_identity_names_map, generate_uuid
from auth.security import log_audit
from ui.components import metric_row, page_header


# =============================================================================
# SPORT ADAPTER
# =============================================================================

def render_sport(username: str):
    """Render de Sport Adapter module."""
    
    page_header(
        " Sport Adapter",
        "National AMS | Athlete Management System - FRMF Integration Ready"
    )
    
    id_map = get_identity_names_map()
    
    with st.expander(" Register Athlete Record", expanded=False):
        with st.form("sport_reg"):
            col1, col2 = st.columns(2)
            
            with col1:
                if id_map:
                    athlete_id = st.selectbox(
                        "Select Verified Identity", 
                        list(id_map.keys()), 
                        format_func=lambda x: id_map.get(x, x)
                    )
                else:
                    st.warning(t("warning_no_identities"))
                    athlete_id = None
                
                discipline = st.text_input("Discipline/Position", placeholder="e.g., Forward")
            
            with col2:
                club = st.text_input("Current Club", placeholder="e.g., Raja Casablanca")
                status = st.selectbox(t("status"), Options.ATHLETE_STATUSES)
            
            contract_end = st.date_input("Contract End Date")
            
            if st.form_submit_button(" UPDATE RECORD", width='stretch'):
                if not athlete_id:
                    st.error(" Please select an identity.")
                elif not discipline:
                    st.error(" Discipline is required.")
                else:
                    sport_id = generate_uuid("ATH")
                    
                    success = run_query(
                        "INSERT INTO sport_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (sport_id, athlete_id, discipline, club, status, 
                         str(contract_end), datetime.now().isoformat())
                    )
                    
                    if success:
                        st.success(" Athlete record updated in National AMS")
                        log_audit(username, "ATHLETE_REGISTERED", "Sport Adapter")
                        st.rerun()
    
    st.divider()
    
    # Athletes list
    st.write("###  Registered Athletes")
    df_sport = get_data("sport_records")
    
    if not df_sport.empty:
        total_athletes = len(df_sport)
        active_athletes = len(df_sport[df_sport['status'] == 'Active'])
        clubs = df_sport['club'].nunique()
        
        metric_row([
            ("Total Athletes", total_athletes),
            ("Active", active_athletes),
            ("Clubs", clubs),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.dataframe(df_sport, width='stretch', hide_index=True)
        
        st.write("###  Athletes by Status")
        status_dist = df_sport['status'].value_counts()
        st.bar_chart(status_dist)
    else:
        st.info("No athletes registered yet.")


# =============================================================================
# MOBILITY ADAPTER
# =============================================================================

def render_mobility(username: str):
    """Render de Mobility Adapter module."""
    
    page_header(
        " Mobility Adapter",
        "National Logistics | Infrastructure & Fleet Asset Management"
    )
    
    tab1, tab2 = st.tabs([" Fleet Management", " Event Mobility Bookings"])
    
    with tab1:
        render_fleet_management(username)
    
    with tab2:
        render_mobility_bookings()


def render_fleet_management(username: str):
    """Render fleet management."""
    
    with st.expander(" Deploy New Asset", expanded=False):
        with st.form("mob"):
            col1, col2 = st.columns(2)
            
            with col1:
                asset = st.text_input("Asset Name", placeholder="e.g., Hub Alpha")
                asset_type = st.selectbox("Type", Options.ASSET_TYPES)
            
            with col2:
                region = st.text_input("Region", placeholder="e.g., Casablanca")
                status = st.selectbox(t("status"), Options.ASSET_STATUSES)
            
            if st.form_submit_button(" DEPLOY", width='stretch'):
                if not asset or not region:
                    st.error(" Asset Name and Region required.")
                else:
                    mob_id = generate_uuid("MOB")
                    
                    success = run_query(
                        "INSERT INTO mobility_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (mob_id, asset, asset_type, region, status, 
                         datetime.now().strftime("%Y-%m-%d"), datetime.now().isoformat())
                    )
                    
                    if success:
                        st.success(f" Asset '{asset}' deployed")
                        log_audit(username, "ASSET_DEPLOYED", "Mobility Adapter")
                        st.rerun()
    
    st.divider()
    
    # Fleet list
    st.write("###  Operational Fleet")
    df_mobility = get_data("mobility_records")
    
    if not df_mobility.empty:
        total_assets = len(df_mobility)
        operational = len(df_mobility[df_mobility['status'] == 'Operational'])
        regions = df_mobility['region'].nunique()
        
        metric_row([
            ("Total Assets", total_assets),
            ("Operational", operational),
            ("Regions", regions),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.dataframe(df_mobility, width='stretch', hide_index=True)
        
        st.write("###  Assets by Type")
        type_dist = df_mobility['type'].value_counts()
        st.bar_chart(type_dist)
    else:
        st.info("No assets deployed yet.")


def render_mobility_bookings():
    """Render mobility bookings."""
    
    st.subheader(" Transport Bookings for Events")
    
    df_bookings = get_data("mobility_bookings")
    
    if not df_bookings.empty:
        st.write(f"###  Total Bookings: {len(df_bookings)}")
        
        total_bookings = len(df_bookings)
        confirmed = len(df_bookings[df_bookings['booking_status'] == 'CONFIRMED'])
        
        metric_row([
            ("Total Bookings", total_bookings),
            ("Confirmed", confirmed),
            ("Transport Types", df_bookings['transport_type'].nunique()),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.dataframe(df_bookings, width='stretch', hide_index=True)
        
        st.write("###  Bookings by Transport Type")
        transport_dist = df_bookings['transport_type'].value_counts()
        st.bar_chart(transport_dist)
    else:
        st.info("No mobility bookings yet. Bookings are created automatically when tickets are minted for mobility-enabled events.")


# =============================================================================
# HEALTH ADAPTER
# =============================================================================

def render_health(username: str):
    """Render de Health Adapter module."""
    
    page_header(
        " Health Adapter",
        "Medical Records Management | Secure Health Information System with GDPR Compliance"
    )
    
    id_map = get_identity_names_map()
    
    with st.expander(" Register Health Record", expanded=False):
        with st.form("health"):
            col1, col2 = st.columns(2)
            
            with col1:
                if id_map:
                    patient_id = st.selectbox(
                        "Identity", 
                        list(id_map.keys()), 
                        format_func=lambda x: id_map.get(x, x)
                    )
                else:
                    st.warning(t("warning_no_identities"))
                    patient_id = None
                
                checkup_type = st.selectbox("Checkup Type", Options.CHECKUP_TYPES)
            
            with col2:
                medical_status = st.selectbox("Medical Clearance", Options.MEDICAL_STATUSES)
                expiry_date = st.date_input("Expiry Date")
            
            if st.form_submit_button(" COMMIT RECORD", width='stretch'):
                if not patient_id:
                    st.error(" Identity required.")
                else:
                    health_id = generate_uuid("HLT")
                    
                    success = run_query(
                        "INSERT INTO health_records VALUES (?, ?, ?, ?, ?, ?)",
                        (health_id, patient_id, checkup_type, medical_status, 
                         str(expiry_date), datetime.now().isoformat())
                    )
                    
                    if success:
                        st.success(" Health record secured")
                        log_audit(username, "HEALTH_RECORD_CREATED", "Health Adapter")
                        st.rerun()
    
    st.divider()
    
    # Health records list
    st.write("###  Medical Records Registry")
    df_health = get_data("health_records")
    
    if not df_health.empty:
        total_records = len(df_health)
        cleared = len(df_health[df_health['medical_status'] == 'CLEARED'])
        urgent = len(df_health[df_health['medical_status'] == 'URGENT'])
        
        metric_row([
            ("Total Records", total_records),
            ("Cleared", cleared),
            (" Urgent", urgent),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.dataframe(df_health, width='stretch', hide_index=True)
        
        st.write("###  Records by Status")
        status_dist = df_health['medical_status'].value_counts()
        st.bar_chart(status_dist)
    else:
        st.info("No health records yet.")
