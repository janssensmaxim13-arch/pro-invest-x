# ============================================================================
# TRANSFER MANAGEMENT MODULE (DOSSIER 1)
# Complete module voor:
# - Transfer registratie en tracking
# - Smart Contract simulatie (blockchain hash)
# - Opleidingsvergoedingen berekening
# - Solidariteitsbijdragen
# - Foundation bijdrage (0.5% MASTERPLAN)
# - Agent fee tracking
# ============================================================================

import streamlit as st
import sqlite3
import hashlib
import hmac
from datetime import datetime, date
from typing import Optional, Dict, List

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import (
    DB_FILE, Options, Messages, TransferRules,
    BLOCKCHAIN_SECRET, FOUNDATION_RATE
)
from database.connection import get_data, run_query, get_connection
from utils.helpers import generate_uuid
from auth.security import log_audit
from ui.components import metric_row, page_header, data_table_with_empty_state


# ============================================================================
# HELPER FUNCTIES
# ============================================================================

def get_talents_for_transfer() -> Dict[str, str]:
    """Haal talenten op die transfereerbaar zijn."""
    df = get_data("ntsp_talent_profiles")
    if df.empty:
        return {}
    
    return {
        row['talent_id']: f"{row['first_name']} {row['last_name']} ({row['current_club'] or 'Free Agent'})"
        for _, row in df.iterrows()
    }


def generate_smart_contract_hash(transfer_data: dict) -> str:
    """Genereer blockchain-grade hash voor transfer contract."""
    message = f"{transfer_data['talent_id']}|{transfer_data['from_club']}|{transfer_data['to_club']}|{transfer_data['fee']}|{transfer_data['date']}"
    return hmac.new(
        BLOCKCHAIN_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()


def calculate_training_compensation(talent_age: int, years_at_club: int, club_category: int = 3) -> float:
    """Bereken opleidingsvergoeding volgens FIFA regels."""
    if talent_age < 12 or talent_age > 23:
        return 0
    
    rates = {
        1: TransferRules.TRAINING_COMPENSATION_CAT_1,
        2: TransferRules.TRAINING_COMPENSATION_CAT_2,
        3: TransferRules.TRAINING_COMPENSATION_CAT_3,
        4: TransferRules.TRAINING_COMPENSATION_CAT_4
    }
    
    rate = rates.get(club_category, TransferRules.TRAINING_COMPENSATION_CAT_3)
    return rate * years_at_club


def calculate_solidarity_contribution(transfer_fee: float, training_years: dict) -> dict:
    """Bereken solidariteitsbijdrage volgens FIFA regels."""
    contributions = {}
    
    for club, years in training_years.items():
        years_12_15 = years.get('years_12_15', 0)
        years_16_23 = years.get('years_16_23', 0)
        
        percentage = (
            years_12_15 * TransferRules.SOLIDARITY_PER_YEAR_12_15 +
            years_16_23 * TransferRules.SOLIDARITY_PER_YEAR_16_23
        )
        
        contribution = transfer_fee * (percentage / 100)
        contributions[club] = {
            'percentage': percentage,
            'amount': contribution,
            'years_12_15': years_12_15,
            'years_16_23': years_16_23
        }
    
    return contributions


def calculate_foundation_contribution(transfer_fee: float) -> float:
    """Bereken Foundation bijdrage (0.5% MASTERPLAN)."""
    return transfer_fee * FOUNDATION_RATE


# ============================================================================
# MAIN RENDER FUNCTIE
# ============================================================================

def render(username: str):
    """Render de Transfer Management module."""
    
    page_header(
        " Transfer Management",
        "Dossier 1 | Smart Contracts | Opleidingsvergoedingen | Foundation 0.5%"
    )
    
    tabs = st.tabs([
        t("overview"),
        " Nieuwe Transfer",
        " Calculator",
        " Templates",
        " Analytics"
    ])
    
    with tabs[0]:
        render_transfer_overview(username)
    
    with tabs[1]:
        render_new_transfer(username)
    
    with tabs[2]:
        render_compensation_calculator()
    
    with tabs[3]:
        render_contract_templates(username)
    
    with tabs[4]:
        render_transfer_analytics()


def render_transfer_overview(username: str):
    """Render transfer overzicht."""
    
    st.subheader(" Transfer Overzicht")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox(t("status"), ["All"] + Options.TRANSFER_STATUSES, key="tf_status")
    with col2:
        filter_type = st.selectbox("Type", ["All"] + Options.TRANSFER_TYPES, key="tf_type")
    with col3:
        filter_year = st.selectbox("Jaar", ["All", "2025", "2024", "2023"], key="tf_year")
    
    df = get_data("transfers")
    
    if not df.empty:
        filtered = df.copy()
        
        if filter_status != "All":
            filtered = filtered[filtered['transfer_status'] == filter_status]
        if filter_type != "All":
            filtered = filtered[filtered['transfer_type'] == filter_type]
        if filter_year != "All":
            filtered = filtered[filtered['transfer_date'].str.startswith(filter_year)]
        
        total_volume = df['transfer_fee'].sum()
        total_foundation = df['foundation_contribution'].sum()
        
        metric_row([
            (" Transfers", len(df)),
            (" Volume", f"€ {total_volume:,.0f}"),
            (" Foundation", f"€ {total_foundation:,.0f}"),
            (" Afgerond", len(df[df['transfer_status'] == 'COMPLETED'])),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if not filtered.empty:
            display_cols = ['transfer_id', 'talent_id', 'from_club', 'to_club', 'transfer_fee', 'transfer_status']
            display_cols = [c for c in display_cols if c in filtered.columns]
            display_df = filtered[display_cols].copy()
            
            if 'transfer_fee' in display_df.columns:
                display_df['transfer_fee'] = display_df['transfer_fee'].apply(lambda x: f"€ {x:,.0f}" if x else "Free")
            
            st.dataframe(display_df, width='stretch', hide_index=True)
    else:
        st.info(" Nog geen transfers.")


def render_new_transfer(username: str):
    """Render form voor nieuwe transfer."""
    
    st.subheader(" Nieuwe Transfer")
    
    talents = get_talents_for_transfer()
    
    if not talents:
        st.warning(" Geen talenten. Registreer eerst in NTSP™.")
        return
    
    with st.form("transfer_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            talent_id = st.selectbox("Talent *", list(talents.keys()), format_func=lambda x: talents.get(x, x))
        with col2:
            from_club = st.text_input("Van Club *", placeholder="AFC Ajax")
            from_country = st.selectbox("Land (van)", ["Netherlands"] + Options.DIASPORA_COUNTRIES)
        with col3:
            to_club = st.text_input("Naar Club *", placeholder="Raja Casablanca")
            to_country = st.selectbox("Land (naar)", ["Morocco"] + Options.DIASPORA_COUNTRIES)
        
        st.markdown("---")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            transfer_type = st.selectbox("Type", Options.TRANSFER_TYPES)
            transfer_date = st.date_input("Datum", value=date.today())
        with col5:
            transfer_fee = st.number_input("Fee (€)", min_value=0.0, step=100000.0)
            training_comp = st.number_input("Opleidingsvergoeding (€)", min_value=0.0, step=10000.0)
        with col6:
            solidarity = st.number_input("Solidariteit (€)", min_value=0.0, step=5000.0)
            sell_on = st.number_input("Doorverkoop %", 0.0, 50.0, 15.0)
        
        foundation = calculate_foundation_contribution(transfer_fee)
        st.info(f" **Foundation (0.5%):** € {foundation:,.2f}")
        
        col7, col8 = st.columns(2)
        with col7:
            agent_name = st.text_input("Agent")
            agent_fee = st.number_input("Agent Fee (€)", min_value=0.0, step=10000.0)
        with col8:
            contract_years = st.number_input("Contract jaren", 1, 10, 3)
            submit_status = st.selectbox(t("status"), Options.TRANSFER_STATUSES)
        
        notes = st.text_area("Notities")
        generate_contract = st.checkbox(" Smart Contract Hash", value=True)
        
        if st.form_submit_button(" REGISTREREN", width='stretch'):
            if not from_club or not to_club:
                st.error("Club info verplicht.")
            else:
                transfer_id = generate_uuid("TRF")
                
                smart_hash = None
                if generate_contract:
                    smart_hash = generate_smart_contract_hash({
                        'talent_id': talent_id, 'from_club': from_club,
                        'to_club': to_club, 'fee': transfer_fee, 'date': str(transfer_date)
                    })
                
                success = run_query("""
                    INSERT INTO transfers (
                        transfer_id, talent_id, from_club, from_club_country, to_club, to_club_country,
                        transfer_type, transfer_date, contract_years, transfer_fee,
                        training_compensation, solidarity_contribution, sell_on_percentage,
                        agent_name, agent_fee, foundation_contribution, foundation_percentage,
                        smart_contract_hash, smart_contract_status, transfer_status, notes,
                        created_at, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    transfer_id, talent_id, from_club, from_country, to_club, to_country,
                    transfer_type, str(transfer_date), contract_years, transfer_fee,
                    training_comp, solidarity, sell_on,
                    agent_name or None, agent_fee, foundation, FOUNDATION_RATE * 100,
                    smart_hash, "DEPLOYED" if smart_hash else "PENDING", submit_status, notes or None,
                    datetime.now().isoformat(), username
                ))
                
                if success:
                    if foundation > 0:
                        run_query("""
                            INSERT INTO foundation_contributions (contribution_id, source_id, source_type, amount, auto_generated, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (generate_uuid("FND"), transfer_id, "TRANSFER", foundation, 1, datetime.now().isoformat()))
                    
                    run_query("""
                        UPDATE ntsp_talent_profiles SET current_club = ?, current_club_country = ?, updated_at = ? WHERE talent_id = ?
                    """, (to_club, to_country, datetime.now().isoformat(), talent_id))
                    
                    st.success(Messages.TRANSFER_CREATED.format(transfer_id))
                    if smart_hash:
                        st.code(smart_hash, language="text")
                    log_audit(username, "TRANSFER_CREATED", "Transfers", details=f"Fee: €{transfer_fee:,.0f}")
                    st.balloons()


def render_compensation_calculator():
    """Render vergoedingen calculator."""
    
    st.subheader(" Vergoedingen Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Opleidingsvergoeding")
        calc_age = st.number_input("Leeftijd", 12, 35, 18, key="c_age")
        calc_years = st.number_input("Jaren bij club", 1, 15, 4, key="c_years")
        calc_cat = st.selectbox("Club Categorie", [1, 2, 3, 4], index=2)
        
        training = calculate_training_compensation(calc_age, calc_years, calc_cat)
        st.metric("Opleidingsvergoeding", f"€ {training:,.0f}")
    
    with col2:
        st.markdown("### Solidariteit & Foundation")
        calc_fee = st.number_input("Transfer Fee (€)", 0.0, 200000000.0, 1000000.0, step=100000.0)
        
        solidarity = calc_fee * 0.05
        foundation = calculate_foundation_contribution(calc_fee)
        
        st.metric("Solidariteit (5%)", f"€ {solidarity:,.0f}")
        st.metric("Foundation (0.5%)", f"€ {foundation:,.0f}")


def render_contract_templates(username: str):
    """Render contract templates."""
    
    st.subheader(" Contract Templates")
    
    df = get_data("contract_templates")
    
    if not df.empty:
        for _, t in df.iterrows():
            st.write(f" **{t['name']}** - {t['contract_type']} (Foundation: {t.get('default_foundation_percentage', 0.5)}%)")
    else:
        st.info("Geen templates.")
        
        if st.button(" Maak Standaard Templates"):
            templates = [
                ("Professional Contract", "PERMANENT", 0.5, 5.0),
                ("Loan Agreement", "LOAN", 0.5, 5.0),
                ("Youth Contract", "YOUTH_TRANSFER", 0.5, 5.0),
            ]
            
            for name, ctype, foundation, solidarity in templates:
                run_query("""
                    INSERT INTO contract_templates (template_id, name, contract_type, default_foundation_percentage, default_solidarity_percentage, is_active, version, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (generate_uuid("TPL"), name, ctype, foundation, solidarity, 1, "1.0", datetime.now().isoformat()))
            
            st.success(" Templates aangemaakt!")
            st.rerun()


def render_transfer_analytics():
    """Render transfer analytics."""
    
    st.subheader(" Transfer Analytics")
    
    df = get_data("transfers")
    
    if df.empty:
        st.info("Geen data.")
        return
    
    metric_row([
        (" Transfers", len(df)),
        (" Volume", f"€ {df['transfer_fee'].sum():,.0f}"),
        (" Foundation", f"€ {df['foundation_contribution'].sum():,.0f}"),
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Per Type")
        st.bar_chart(df['transfer_type'].value_counts())
    
    with col2:
        st.write("#### Per Status")
        st.bar_chart(df['transfer_status'].value_counts())
