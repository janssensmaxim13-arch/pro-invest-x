# ============================================================================
# ACADEMY SYSTEM MODULE (DOSSIER 1)
# ============================================================================

import streamlit as st
from datetime import datetime, date
from typing import Dict

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import Options, Messages
from database.connection import get_data, run_query
from utils.helpers import generate_uuid
from auth.security import log_audit
from ui.components import metric_row, page_header


def get_academies_dropdown() -> Dict[str, str]:
    df = get_data("academies")
    if df.empty:
        return {}
    return {row['academy_id']: f"{row['name']} ({row['city']})" for _, row in df.iterrows()}


def get_talents_dropdown() -> Dict[str, str]:
    df = get_data("ntsp_talent_profiles")
    if df.empty:
        return {}
    return {row['talent_id']: f"{row['first_name']} {row['last_name']}" for _, row in df.iterrows()}


def render(username: str):
    """Render Academy System module."""
    
    page_header(" Academy System", "Dossier 1 | 250 Academies | Certificering")
    
    tabs = st.tabs([t("overview"), " Nieuwe Academy", " Teams", " Inschrijvingen", " Staff"])
    
    with tabs[0]:
        render_overview()
    with tabs[1]:
        render_new_academy(username)
    with tabs[2]:
        render_teams(username)
    with tabs[3]:
        render_enrollments(username)
    with tabs[4]:
        render_staff(username)


def render_overview():
    df = get_data("academies")
    
    if not df.empty:
        metric_row([
            (" Academies", len(df)),
            (" Capaciteit", f"{df['total_capacity'].sum():,}" if 'total_capacity' in df.columns else 0),
            (" Ingeschreven", f"{df['current_enrollment'].sum():,}" if 'current_enrollment' in df.columns else 0),
        ])
        
        display_cols = ['name', 'city', 'region', 'academy_type', 'certification_level', 'status']
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
    else:
        st.info(" Nog geen academies.")


def render_new_academy(username: str):
    with st.form("academy_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Naam *", placeholder="Raja Academy")
            region = st.selectbox("Regio *", Options.REGIONS_MOROCCO)
        with col2:
            city = st.text_input("Stad *", placeholder="Casablanca")
            academy_type = st.selectbox("Type *", Options.ACADEMY_TYPES)
        with col3:
            certification = st.selectbox("Certificering", Options.CERTIFICATION_LEVELS)
            parent_club = st.text_input("Moederclub", placeholder="Raja Casablanca")
        
        col4, col5 = st.columns(2)
        with col4:
            total_capacity = st.number_input("Capaciteit", 10, 500, 100)
            director = st.text_input("Directeur")
        with col5:
            num_pitches = st.number_input("Velden", 0, 20, 2)
            email = st.text_input("E-mail")
        
        if st.form_submit_button(" REGISTREREN", use_container_width=True):
            if not name or not city:
                st.error(t("error_fill_required"))
            else:
                success = run_query("""
                    INSERT INTO academies (academy_id, name, region, city, country, academy_type, 
                    certification_level, parent_club, total_capacity, num_pitches, director_name, email, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (generate_uuid("ACA"), name, region, city, "Morocco", academy_type, 
                      certification, parent_club or None, total_capacity, num_pitches, 
                      director or None, email or None, "ACTIVE", datetime.now().isoformat()))
                
                if success:
                    st.success(t("success_registered"))
                    log_audit(username, "ACADEMY_CREATED", "Academy")
                    st.balloons()


def render_teams(username: str):
    academies = get_academies_dropdown()
    
    if not academies:
        st.warning(t("warning_no_academies"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("team_form"):
            academy_id = st.selectbox("Academy", list(academies.keys()), format_func=lambda x: academies.get(x, x))
            team_name = st.text_input("Team Naam *")
            age_group = st.selectbox("Leeftijdsgroep", Options.AGE_GROUPS)
            head_coach = st.text_input("Coach")
            
            if st.form_submit_button(" TOEVOEGEN"):
                if team_name:
                    run_query("""
                        INSERT INTO academy_teams (team_id, academy_id, team_name, age_group, head_coach, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (generate_uuid("TM"), academy_id, team_name, age_group, head_coach or None, "ACTIVE", datetime.now().isoformat()))
                    st.success(t("success_added"))
    
    with col2:
        df = get_data("academy_teams")
        if not df.empty:
            st.dataframe(df[['team_name', 'age_group', 'head_coach', 'status']], use_container_width=True, hide_index=True)


def render_enrollments(username: str):
    academies = get_academies_dropdown()
    talents = get_talents_dropdown()
    
    if not academies or not talents:
        st.warning(t("warning_no_data"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("enroll_form"):
            academy_id = st.selectbox("Academy", list(academies.keys()), format_func=lambda x: academies.get(x, x))
            talent_id = st.selectbox("Talent", list(talents.keys()), format_func=lambda x: talents.get(x, x))
            enrollment_type = st.selectbox("Type", Options.ENROLLMENT_TYPES)
            is_residential = st.checkbox("Internaat")
            
            if st.form_submit_button(" INSCHRIJVEN"):
                run_query("""
                    INSERT INTO academy_enrollments (enrollment_id, academy_id, talent_id, enrollment_date, enrollment_type, is_residential, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (generate_uuid("ENR"), academy_id, talent_id, str(date.today()), enrollment_type, 1 if is_residential else 0, "ACTIVE", datetime.now().isoformat()))
                run_query("UPDATE academies SET current_enrollment = current_enrollment + 1 WHERE academy_id = ?", (academy_id,))
                st.success(t("success_registered"))
    
    with col2:
        df = get_data("academy_enrollments")
        if not df.empty:
            st.dataframe(df[['talent_id', 'academy_id', 'enrollment_type', 'status']], use_container_width=True, hide_index=True)


def render_staff(username: str):
    academies = get_academies_dropdown()
    
    if not academies:
        st.warning(t("warning_no_academies"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("staff_form"):
            academy_id = st.selectbox("Academy", list(academies.keys()), format_func=lambda x: academies.get(x, x))
            first_name = st.text_input("Voornaam *")
            last_name = st.text_input("Achternaam *")
            role = st.selectbox("Rol", Options.ACADEMY_STAFF_ROLES)
            license_level = st.selectbox("Licentie", Options.COACHING_LICENSES)
            
            if st.form_submit_button(" TOEVOEGEN"):
                if first_name and last_name:
                    run_query("""
                        INSERT INTO academy_staff (staff_id, academy_id, first_name, last_name, role, coaching_license, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (generate_uuid("STF"), academy_id, first_name, last_name, role, license_level if license_level != "None" else None, "ACTIVE", datetime.now().isoformat()))
                    st.success(f" {first_name} toegevoegd!")
    
    with col2:
        df = get_data("academy_staff")
        if not df.empty:
            st.dataframe(df[['first_name', 'last_name', 'role', 'coaching_license']], use_container_width=True, hide_index=True)
