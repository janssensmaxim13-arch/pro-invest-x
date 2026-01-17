# ============================================================================
# NTSP™ - NATIONAAL TALENT SCOUTING PLATFORM (DOSSIER 1)
# Complete module voor:
# - Talent registratie en tracking (80.000 jongeren)
# - Diaspora scouting (3.200+ talenten)
# - Scout management
# - Evaluaties (technisch, fysiek, mentaal)
# - Medische gegevens
# - Carrière tracking
# - Watchlist management
# ============================================================================

import streamlit as st
import sqlite3
from datetime import datetime, date
from typing import Optional, Dict, List
import json

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import (
    DB_FILE, Options, Messages, ScoreWeights,
    FOUNDATION_RATE
)
from database.connection import get_data, run_query, get_connection
from utils.helpers import generate_uuid, get_identity_names_map
from auth.security import log_audit
from ui.components import metric_row, page_header, data_table_with_empty_state


# ============================================================================
# HELPER FUNCTIES
# ============================================================================

def calculate_age(birth_date_str: str) -> int:
    """Bereken leeftijd op basis van geboortedatum."""
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - birth_date.year
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        return age
    except:
        return 0


def calculate_overall_score(technical: float, physical: float, mental: float) -> float:
    """Bereken overall score met gewichten."""
    weights = ScoreWeights.OVERALL
    return (
        technical * weights["technical"] +
        physical * weights["physical"] +
        mental * weights["mental"]
    )


def calculate_potential_score(overall_score: float, age: int) -> float:
    """Bereken potential score gebaseerd op leeftijd."""
    modifier = 1.0
    for age_range, mod in ScoreWeights.AGE_POTENTIAL_MODIFIER.items():
        if age in age_range:
            modifier = mod
            break
    
    return min(100, overall_score * modifier)


def get_talent_by_id(talent_id: str) -> Optional[Dict]:
    """Haal talent op met ID."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ntsp_talent_profiles WHERE talent_id = ?", (talent_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_talents_dropdown() -> Dict[str, str]:
    """Haal talent dropdown map op."""
    df = get_data("ntsp_talent_profiles")
    if df.empty:
        return {}
    
    return {
        row['talent_id']: f"{row['first_name']} {row['last_name']} ({row['current_club'] or 'No club'})"
        for _, row in df.iterrows()
    }


def get_scouts_dropdown() -> Dict[str, str]:
    """Haal scouts dropdown map op."""
    df = get_data("ntsp_scouts")
    if df.empty:
        return {}
    
    return {
        row['scout_id']: f"{row['first_name']} {row['last_name']} ({row['region'] or 'Global'})"
        for _, row in df.iterrows()
    }


# ============================================================================
# MAIN RENDER FUNCTIE
# ============================================================================

def render(username: str):
    """Render de NTSP™ module."""
    
    page_header(
        " NTSP™ - Nationaal Talent Scouting Platform",
        "Dossier 1 | 80.000 jongeren tracking | Diaspora scouting | Complete evaluatie systeem"
    )
    
    # Tabs voor verschillende functionaliteiten
    tabs = st.tabs([
        " Talent Database",
        " Nieuw Talent",
        " Evaluaties",
        " Medisch",
        " Mentaal",
        " Watchlist",
        " Scouts",
        " Analytics"
    ])
    
    with tabs[0]:
        render_talent_database(username)
    
    with tabs[1]:
        render_new_talent(username)
    
    with tabs[2]:
        render_evaluations(username)
    
    with tabs[3]:
        render_medical(username)
    
    with tabs[4]:
        render_mental(username)
    
    with tabs[5]:
        render_watchlist(username)
    
    with tabs[6]:
        render_scouts(username)
    
    with tabs[7]:
        render_analytics()


# ============================================================================
# TAB 1: TALENT DATABASE
# ============================================================================

def render_talent_database(username: str):
    """Render talent database overview."""
    
    st.subheader(" Talent Database")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        filter_status = st.selectbox(
            t("status"), 
            ["All"] + Options.TALENT_STATUSES,
            key="db_filter_status"
        )
    
    with col2:
        filter_position = st.selectbox(
            "Positie", 
            ["All"] + Options.POSITIONS,
            key="db_filter_position"
        )
    
    with col3:
        filter_diaspora = st.selectbox(
            "Diaspora",
            ["All", "Yes", "No"],
            key="db_filter_diaspora"
        )
    
    with col4:
        filter_priority = st.selectbox(
            "Prioriteit",
            ["All"] + Options.PRIORITY_LEVELS,
            key="db_filter_priority"
        )
    
    # Search
    search = st.text_input(" Zoek op naam, club of land", key="db_search")
    
    # Data ophalen
    df = get_data("ntsp_talent_profiles")
    
    if not df.empty:
        # Filters toepassen
        filtered = df.copy()
        
        if filter_status != "All":
            filtered = filtered[filtered['talent_status'] == filter_status]
        
        if filter_position != "All":
            filtered = filtered[filtered['primary_position'] == filter_position]
        
        if filter_diaspora == "Yes":
            filtered = filtered[filtered['is_diaspora'] == 1]
        elif filter_diaspora == "No":
            filtered = filtered[filtered['is_diaspora'] == 0]
        
        if filter_priority != "All":
            filtered = filtered[filtered['priority_level'] == filter_priority]
        
        if search:
            search_lower = search.lower()
            filtered = filtered[
                filtered['first_name'].str.lower().str.contains(search_lower, na=False) |
                filtered['last_name'].str.lower().str.contains(search_lower, na=False) |
                filtered['current_club'].str.lower().str.contains(search_lower, na=False) |
                filtered['nationality'].str.lower().str.contains(search_lower, na=False)
            ]
        
        # Metrics
        total = len(df)
        diaspora = len(df[df['is_diaspora'] == 1])
        high_priority = len(df[df['priority_level'].isin(['CRITICAL', 'HIGH'])])
        avg_score = df['overall_score'].mean() if 'overall_score' in df.columns else 0
        
        metric_row([
            (" Totaal Talenten", total),
            (" Diaspora", diaspora),
            ("⭐ Hoge Prioriteit", high_priority),
            (" Gem. Score", f"{avg_score:.1f}"),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display data
        if not filtered.empty:
            # Selecteer kolommen voor weergave
            display_cols = [
                'talent_id', 'first_name', 'last_name', 'nationality',
                'primary_position', 'current_club', 'talent_status',
                'overall_score', 'potential_score', 'is_diaspora', 'priority_level'
            ]
            
            # Alleen bestaande kolommen
            display_cols = [c for c in display_cols if c in filtered.columns]
            
            display_df = filtered[display_cols].copy()
            
            # Format kolommen
            if 'is_diaspora' in display_df.columns:
                display_df['is_diaspora'] = display_df['is_diaspora'].apply(
                    lambda x: " Yes" if x == 1 else "No"
                )
            
            if 'overall_score' in display_df.columns:
                display_df['overall_score'] = display_df['overall_score'].apply(
                    lambda x: f"{x:.1f}" if x else "-"
                )
            
            if 'potential_score' in display_df.columns:
                display_df['potential_score'] = display_df['potential_score'].apply(
                    lambda x: f"{x:.1f}" if x else "-"
                )
            
            st.write(f"### Resultaten ({len(filtered)} talenten)")
            st.dataframe(display_df, width="stretch", hide_index=True)
            
            # Talent detail viewer
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("###  Talent Details")
            
            talents = get_talents_dropdown()
            if talents:
                selected_talent = st.selectbox(
                    "Selecteer talent voor details",
                    list(talents.keys()),
                    format_func=lambda x: talents.get(x, x),
                    key="detail_select"
                )
                
                if selected_talent:
                    render_talent_detail(selected_talent)
        else:
            st.info("Geen talenten gevonden met deze filters.")
    else:
        st.info(" Nog geen talenten geregistreerd. Gebruik 'Nieuw Talent' om te beginnen.")


def render_talent_detail(talent_id: str):
    """Render detail view voor een talent."""
    
    talent = get_talent_by_id(talent_id)
    
    if not talent:
        st.error("Talent niet gevonden.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Persoonlijke Info")
        st.write(f"**Naam:** {talent['first_name']} {talent['last_name']}")
        st.write(f"**Geboortedatum:** {talent['date_of_birth']}")
        st.write(f"**Nationaliteit:** {talent['nationality']}")
        if talent['dual_nationality']:
            st.write(f"**Tweede nationaliteit:** {talent['dual_nationality']}")
        st.write(f"**Positie:** {talent['primary_position']}")
        if talent['secondary_position']:
            st.write(f"**Tweede positie:** {talent['secondary_position']}")
        st.write(f"**Voorkeurvoet:** {talent['preferred_foot']}")
    
    with col2:
        st.markdown("####  Club Info")
        st.write(f"**Club:** {talent['current_club'] or 'Geen'}")
        st.write(f"**Land:** {talent['current_club_country'] or '-'}")
        st.write(f"**Competitie:** {talent['current_league'] or '-'}")
        st.write(f"**Contract tot:** {talent['contract_end'] or '-'}")
        st.write(f"**Rugnummer:** {talent['jersey_number'] or '-'}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("####  Scores")
        st.metric("Overall Score", f"{talent['overall_score']:.1f}" if talent['overall_score'] else "-")
        st.metric("Potential Score", f"{talent['potential_score']:.1f}" if talent['potential_score'] else "-")
        st.metric("Geschatte Marktwaarde", f"€ {talent['market_value_estimate']:,.0f}" if talent['market_value_estimate'] else "-")
    
    with col4:
        st.markdown("#### ️ Status")
        st.write(f"**Status:** {talent['talent_status']}")
        st.write(f"**Prioriteit:** {talent['priority_level']}")
        st.write(f"**Diaspora:** {'Ja' if talent['is_diaspora'] else 'Nee'}")
        if talent['is_diaspora']:
            st.write(f"**Diaspora land:** {talent['diaspora_country']}")
        st.write(f"**Nat. team eligible:** {'Ja' if talent['national_team_eligible'] else 'Nee'}")
    
    # Notities
    if talent['notes']:
        st.markdown("####  Notities")
        st.write(talent['notes'])


# ============================================================================
# TAB 2: NIEUW TALENT REGISTREREN
# ============================================================================

def render_new_talent(username: str):
    """Render form voor nieuw talent."""
    
    st.subheader(" Nieuw Talent Registreren")
    
    with st.form("new_talent_form"):
        st.markdown("### Persoonlijke Gegevens")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            first_name = st.text_input("Voornaam *", placeholder="Mohammed")
            date_of_birth = st.date_input(
                "Geboortedatum *",
                min_value=date(1980, 1, 1),
                max_value=date.today(),
                value=date(2005, 1, 1)
            )
            nationality = st.selectbox("Nationaliteit *", Options.NATIONALITIES)
        
        with col2:
            last_name = st.text_input("Achternaam *", placeholder="El Amrani")
            place_of_birth = st.text_input("Geboorteplaats", placeholder="Casablanca")
            dual_nationality = st.selectbox(
                "Tweede Nationaliteit", 
                ["None"] + Options.NATIONALITIES
            )
        
        with col3:
            passport_number = st.text_input("Paspoortnummer", placeholder="XX1234567")
            email = st.text_input("E-mail", placeholder="talent@email.com")
            phone = st.text_input("Telefoon", placeholder="+212 6XX XXX XXX")
        
        st.markdown("---")
        st.markdown("###  Diaspora Informatie")
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            is_diaspora = st.checkbox("Is Diaspora Talent")
        
        with col5:
            diaspora_country = st.selectbox(
                "Diaspora Land",
                ["N/A"] + Options.DIASPORA_COUNTRIES,
                disabled=not is_diaspora
            )
        
        with col6:
            diaspora_city = st.text_input(
                "Stad",
                placeholder="Amsterdam",
                disabled=not is_diaspora
            )
        
        col7, col8, col9 = st.columns(3)
        
        with col7:
            years_abroad = st.number_input(
                "Jaren in buitenland",
                min_value=0,
                max_value=30,
                value=0,
                disabled=not is_diaspora
            )
        
        with col8:
            speaks_arabic = st.checkbox("Spreekt Arabisch", disabled=not is_diaspora)
        
        with col9:
            speaks_french = st.checkbox("Spreekt Frans", disabled=not is_diaspora)
        
        st.markdown("---")
        st.markdown("###  Voetbal Gegevens")
        
        col10, col11, col12 = st.columns(3)
        
        with col10:
            primary_position = st.selectbox("Primaire Positie *", Options.POSITIONS)
            current_club = st.text_input("Huidige Club", placeholder="AFC Ajax")
            contract_start = st.date_input("Contract Start", value=None)
        
        with col11:
            secondary_position = st.selectbox(
                "Secundaire Positie", 
                ["None"] + Options.POSITIONS
            )
            current_club_country = st.selectbox(
                "Club Land",
                ["Morocco"] + Options.DIASPORA_COUNTRIES
            )
            contract_end = st.date_input("Contract Einde", value=None)
        
        with col12:
            preferred_foot = st.selectbox("Voorkeurvoet", Options.PREFERRED_FOOT)
            current_league = st.text_input("Competitie", placeholder="Eredivisie U19")
            jersey_number = st.number_input("Rugnummer", min_value=0, max_value=99, value=0)
        
        col13, col14 = st.columns(2)
        
        with col13:
            height_cm = st.number_input("Lengte (cm)", min_value=100, max_value=220, value=175)
        
        with col14:
            weight_kg = st.number_input("Gewicht (kg)", min_value=30, max_value=120, value=70)
        
        st.markdown("---")
        st.markdown("### ‍‍ Familie Contact (voor jeugd)")
        
        col15, col16, col17 = st.columns(3)
        
        with col15:
            parent_name = st.text_input("Naam Ouder/Voogd", placeholder="Ahmed El Amrani")
        
        with col16:
            parent_phone = st.text_input("Telefoon Ouder", placeholder="+212 6XX XXX XXX")
        
        with col17:
            parent_email = st.text_input("E-mail Ouder", placeholder="parent@email.com")
        
        st.markdown("---")
        st.markdown("### ️ Status & Prioriteit")
        
        col18, col19, col20 = st.columns(3)
        
        with col18:
            talent_status = st.selectbox(t("status"), Options.TALENT_STATUSES, index=0)
        
        with col19:
            priority_level = st.selectbox("Prioriteit", Options.PRIORITY_LEVELS, index=2)
        
        with col20:
            national_team_eligible = st.checkbox("Eligible voor Nat. Team", value=True)
        
        interest_in_morocco = st.checkbox("Heeft interesse getoond in Marokko")
        
        notes = st.text_area("Notities", placeholder="Eventuele opmerkingen...")
        
        st.markdown("---")
        
        submitted = st.form_submit_button(" TALENT REGISTREREN", width="stretch")
        
        if submitted:
            # Validatie
            if not first_name or not last_name:
                st.error("Naam is verplicht.")
            elif not primary_position:
                st.error("Positie is verplicht.")
            else:
                talent_id = generate_uuid("TLT")
                
                success = run_query("""
                    INSERT INTO ntsp_talent_profiles (
                        talent_id, first_name, last_name, date_of_birth, place_of_birth,
                        nationality, dual_nationality, passport_number,
                        is_diaspora, diaspora_country, diaspora_city, years_abroad,
                        speaks_arabic, speaks_french,
                        email, phone,
                        parent_name, parent_phone, parent_email,
                        primary_position, secondary_position, preferred_foot,
                        height_cm, weight_kg,
                        current_club, current_club_country, current_league,
                        contract_start, contract_end, jersey_number,
                        talent_status, priority_level, national_team_eligible,
                        interest_in_morocco, notes,
                        created_at, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    talent_id, first_name, last_name, str(date_of_birth), place_of_birth,
                    nationality,
                    dual_nationality if dual_nationality != "None" else None,
                    passport_number or None,
                    1 if is_diaspora else 0,
                    diaspora_country if is_diaspora and diaspora_country != "N/A" else None,
                    diaspora_city if is_diaspora else None,
                    years_abroad if is_diaspora else 0,
                    1 if speaks_arabic else 0,
                    1 if speaks_french else 0,
                    email or None, phone or None,
                    parent_name or None, parent_phone or None, parent_email or None,
                    primary_position,
                    secondary_position if secondary_position != "None" else None,
                    preferred_foot,
                    height_cm, weight_kg,
                    current_club or None, current_club_country, current_league or None,
                    str(contract_start) if contract_start else None,
                    str(contract_end) if contract_end else None,
                    jersey_number if jersey_number > 0 else None,
                    talent_status, priority_level,
                    1 if national_team_eligible else 0,
                    1 if interest_in_morocco else 0,
                    notes or None,
                    datetime.now().isoformat(), username
                ))
                
                if success:
                    st.success(Messages.TALENT_REGISTERED.format(f"{first_name} {last_name}"))
                    log_audit(username, "TALENT_REGISTERED", "NTSP", 
                             details=f"Talent: {talent_id}, Name: {first_name} {last_name}")
                    st.balloons()


# ============================================================================
# TAB 3: EVALUATIES
# ============================================================================

def render_evaluations(username: str):
    """Render evaluaties tab."""
    
    st.subheader(" Talent Evaluaties")
    
    talents = get_talents_dropdown()
    scouts = get_scouts_dropdown()
    
    if not talents:
        st.warning("Geen talenten beschikbaar. Registreer eerst een talent.")
        return
    
    if not scouts:
        st.warning("Geen scouts beschikbaar. Registreer eerst een scout in de Scouts tab.")
        return
    
    tab1, tab2 = st.tabs([" Nieuwe Evaluatie", " Evaluatie Overzicht"])
    
    with tab1:
        render_new_evaluation(username, talents, scouts)
    
    with tab2:
        render_evaluation_overview(talents)


def render_new_evaluation(username: str, talents: Dict, scouts: Dict):
    """Render form voor nieuwe evaluatie."""
    
    with st.form("new_evaluation_form"):
        st.markdown("### Evaluatie Details")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            talent_id = st.selectbox(
                "Talent *",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
        
        with col2:
            scout_id = st.selectbox(
                "Scout *",
                list(scouts.keys()),
                format_func=lambda x: scouts.get(x, x)
            )
        
        with col3:
            evaluation_date = st.date_input("Datum *", value=date.today())
        
        col4, col5 = st.columns(2)
        
        with col4:
            match_observed = st.text_input("Wedstrijd", placeholder="Ajax U19 vs PSV U19")
        
        with col5:
            match_date = st.date_input("Wedstrijd Datum", value=None)
        
        st.markdown("---")
        st.markdown("###  Technische Scores (1-100)")
        
        tech_col1, tech_col2, tech_col3 = st.columns(3)
        
        with tech_col1:
            score_ball_control = st.slider("Balcontrole", 1, 100, 50, key="tech_bc")
            score_passing = st.slider("Passen", 1, 100, 50, key="tech_pass")
        
        with tech_col2:
            score_dribbling = st.slider("Dribbelen", 1, 100, 50, key="tech_drib")
            score_shooting = st.slider("Schieten", 1, 100, 50, key="tech_shoot")
        
        with tech_col3:
            score_heading = st.slider("Koppen", 1, 100, 50, key="tech_head")
            score_first_touch = st.slider("Eerste Touch", 1, 100, 50, key="tech_ft")
        
        st.markdown("---")
        st.markdown("###  Fysieke Scores (1-100)")
        
        phys_col1, phys_col2, phys_col3 = st.columns(3)
        
        with phys_col1:
            score_speed = st.slider("Snelheid", 1, 100, 50, key="phys_speed")
            score_acceleration = st.slider("Acceleratie", 1, 100, 50, key="phys_acc")
        
        with phys_col2:
            score_stamina = st.slider("Uithoudingsvermogen", 1, 100, 50, key="phys_stam")
            score_strength = st.slider("Kracht", 1, 100, 50, key="phys_str")
        
        with phys_col3:
            score_jumping = st.slider("Sprongkracht", 1, 100, 50, key="phys_jump")
            score_agility = st.slider("Behendigheid", 1, 100, 50, key="phys_agil")
        
        st.markdown("---")
        st.markdown("###  Mentale Scores (1-100)")
        
        ment_col1, ment_col2, ment_col3 = st.columns(3)
        
        with ment_col1:
            score_positioning = st.slider("Positiespel", 1, 100, 50, key="ment_pos")
            score_vision = st.slider(t("overview"), 1, 100, 50, key="ment_vis")
        
        with ment_col2:
            score_composure = st.slider("Rust aan de bal", 1, 100, 50, key="ment_comp")
            score_leadership = st.slider("Leiderschap", 1, 100, 50, key="ment_lead")
        
        with ment_col3:
            score_work_rate = st.slider("Werkethiek", 1, 100, 50, key="ment_work")
            score_decision_making = st.slider("Besluitvorming", 1, 100, 50, key="ment_dec")
        
        st.markdown("---")
        st.markdown("###  Aanbeveling & Notities")
        
        col6, col7 = st.columns(2)
        
        with col6:
            recommendation = st.selectbox("Aanbeveling", Options.EVALUATION_RECOMMENDATIONS)
            follow_up_required = st.checkbox("Follow-up nodig")
        
        with col7:
            recommended_for_academy = st.checkbox("Aanbevolen voor Academy")
            recommended_for_national_team = st.checkbox("Aanbevolen voor Nat. Team")
        
        strengths = st.text_area("Sterke Punten", placeholder="Beschrijf de sterke punten...")
        weaknesses = st.text_area("Zwakke Punten", placeholder="Beschrijf de verbeterpunten...")
        development_areas = st.text_area("Ontwikkelgebieden", placeholder="Waar moet aan gewerkt worden...")
        general_notes = st.text_area("Algemene Notities", placeholder="Overige observaties...")
        
        submitted = st.form_submit_button(" EVALUATIE OPSLAAN", width="stretch")
        
        if submitted:
            # Bereken totaalscores
            overall_technical = (
                score_ball_control * 0.20 +
                score_passing * 0.20 +
                score_dribbling * 0.15 +
                score_shooting * 0.15 +
                score_heading * 0.10 +
                score_first_touch * 0.20
            )
            
            overall_physical = (
                score_speed * 0.20 +
                score_acceleration * 0.15 +
                score_stamina * 0.20 +
                score_strength * 0.15 +
                score_jumping * 0.15 +
                score_agility * 0.15
            )
            
            overall_mental = (
                score_positioning * 0.20 +
                score_vision * 0.15 +
                score_composure * 0.15 +
                score_leadership * 0.15 +
                score_work_rate * 0.20 +
                score_decision_making * 0.15
            )
            
            overall_score = calculate_overall_score(overall_technical, overall_physical, overall_mental)
            
            # Haal talent op voor leeftijd
            talent = get_talent_by_id(talent_id)
            age = calculate_age(talent['date_of_birth']) if talent else 20
            potential_score = calculate_potential_score(overall_score, age)
            
            evaluation_id = generate_uuid("EVAL")
            scout_name = scouts.get(scout_id, "Unknown")
            
            success = run_query("""
                INSERT INTO ntsp_evaluations (
                    evaluation_id, talent_id, scout_id, scout_name,
                    evaluation_date, match_observed, match_date,
                    score_ball_control, score_passing, score_dribbling,
                    score_shooting, score_heading, score_first_touch,
                    score_speed, score_acceleration, score_stamina,
                    score_strength, score_jumping, score_agility,
                    score_positioning, score_vision, score_composure,
                    score_leadership, score_work_rate, score_decision_making,
                    overall_technical, overall_physical, overall_mental,
                    overall_score, potential_score,
                    recommendation, follow_up_required,
                    recommended_for_academy, recommended_for_national_team,
                    strengths, weaknesses, development_areas, general_notes,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evaluation_id, talent_id, scout_id, scout_name,
                str(evaluation_date), match_observed or None,
                str(match_date) if match_date else None,
                score_ball_control, score_passing, score_dribbling,
                score_shooting, score_heading, score_first_touch,
                score_speed, score_acceleration, score_stamina,
                score_strength, score_jumping, score_agility,
                score_positioning, score_vision, score_composure,
                score_leadership, score_work_rate, score_decision_making,
                overall_technical, overall_physical, overall_mental,
                overall_score, potential_score,
                recommendation, 1 if follow_up_required else 0,
                1 if recommended_for_academy else 0,
                1 if recommended_for_national_team else 0,
                strengths or None, weaknesses or None,
                development_areas or None, general_notes or None,
                datetime.now().isoformat()
            ))
            
            if success:
                # Update talent profiel met nieuwe score
                run_query("""
                    UPDATE ntsp_talent_profiles 
                    SET overall_score = ?, potential_score = ?, 
                        last_evaluation_date = ?,
                        evaluation_count = evaluation_count + 1,
                        updated_at = ?
                    WHERE talent_id = ?
                """, (overall_score, potential_score, str(evaluation_date),
                      datetime.now().isoformat(), talent_id))
                
                st.success(Messages.EVALUATION_SAVED.format(talents.get(talent_id, talent_id)))
                log_audit(username, "EVALUATION_CREATED", "NTSP",
                         details=f"Talent: {talent_id}, Score: {overall_score:.1f}")


def render_evaluation_overview(talents: Dict):
    """Render overzicht van evaluaties."""
    
    df = get_data("ntsp_evaluations")
    
    if df.empty:
        st.info("Nog geen evaluaties opgeslagen.")
        return
    
    # Filter op talent
    selected_talent = st.selectbox(
        "Filter op talent",
        ["All"] + list(talents.keys()),
        format_func=lambda x: "Alle talenten" if x == "All" else talents.get(x, x)
    )
    
    if selected_talent != "All":
        df = df[df['talent_id'] == selected_talent]
    
    if df.empty:
        st.info("Geen evaluaties gevonden voor dit talent.")
        return
    
    # Display
    display_cols = [
        'evaluation_id', 'talent_id', 'scout_name', 'evaluation_date',
        'overall_score', 'potential_score', 'recommendation'
    ]
    display_cols = [c for c in display_cols if c in df.columns]
    
    st.dataframe(df[display_cols], width="stretch", hide_index=True)


# ============================================================================
# TAB 4: MEDISCH
# ============================================================================

def render_medical(username: str):
    """Render medische records tab. Alleen voor medisch personeel!"""
    
    from auth.security import check_permission
    
    st.subheader(" Medische Gegevens")
    
    # PRIVACY: Medische data alleen voor bevoegd personeel
    allowed_roles = ["SuperAdmin", "Medical Staff", "Psychologist", "Academy Admin"]
    
    if not check_permission(allowed_roles, silent=True):
        st.warning(" **Medische gegevens zijn vertrouwelijk.**")
        st.info(f"Toegang vereist één van deze rollen: {', '.join(allowed_roles)}")
        st.info("Neem contact op met je supervisor als je toegang nodig hebt.")
        return
    
    talents = get_talents_dropdown()
    
    if not talents:
        st.warning("Geen talenten beschikbaar.")
        return
    
    tab1, tab2 = st.tabs([" Nieuwe Medical", t("overview")])
    
    with tab1:
        with st.form("medical_form"):
            st.markdown("### Talent & Basis Info")
            
            col1, col2 = st.columns(2)
            
            with col1:
                talent_id = st.selectbox(
                    "Talent *",
                    list(talents.keys()),
                    format_func=lambda x: talents.get(x, x)
                )
                blood_type = st.selectbox(
                    "Bloedgroep",
                    ["Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
                )
            
            with col2:
                allergies = st.text_input("Allergieën", placeholder="Geen / Penicilline, etc.")
                chronic_conditions = st.text_input("Chronische aandoeningen", placeholder="Geen / Astma, etc.")
            
            st.markdown("---")
            st.markdown("###  Fysieke Metingen")
            
            col3, col4, col5 = st.columns(3)
            
            with col3:
                height_cm = st.number_input("Lengte (cm)", 100, 220, 175)
                body_fat = st.number_input("Vetpercentage (%)", 0.0, 40.0, 12.0)
            
            with col4:
                weight_kg = st.number_input("Gewicht (kg)", 30, 120, 70)
                muscle_mass = st.number_input("Spiermassa (kg)", 0.0, 80.0, 35.0)
            
            with col5:
                bmi = weight_kg / ((height_cm / 100) ** 2)
                st.metric("BMI", f"{bmi:.1f}")
            
            st.markdown("---")
            st.markdown("###  Fitness Tests")
            
            col6, col7, col8 = st.columns(3)
            
            with col6:
                vo2_max = st.number_input("VO2 Max", 0.0, 80.0, 50.0)
                sprint_10m = st.number_input("10m Sprint (sec)", 0.0, 5.0, 1.8)
            
            with col7:
                sprint_30m = st.number_input("30m Sprint (sec)", 0.0, 10.0, 4.2)
                vertical_jump = st.number_input("Verticale sprong (cm)", 0, 100, 45)
            
            with col8:
                agility_test = st.number_input("Agility test (sec)", 0.0, 30.0, 15.0)
                beep_test = st.number_input("Beep test niveau", 0.0, 20.0, 12.0)
            
            st.markdown("---")
            st.markdown("### 🩺 Medische Keuring")
            
            col9, col10 = st.columns(2)
            
            with col9:
                medical_clearance = st.selectbox("Medische Goedkeuring", Options.MEDICAL_STATUSES)
                last_checkup = st.date_input("Laatste keuring", value=date.today())
            
            with col10:
                clearance_expiry = st.date_input("Geldig tot", value=None)
                doctor_name = st.text_input("Arts", placeholder="Dr. Ahmed Benali")
            
            injury_history = st.text_area("Blessure Geschiedenis", placeholder="Eerdere blessures...")
            doctor_notes = st.text_area("Notities Arts", placeholder="Medische notities...")
            
            submitted = st.form_submit_button(" OPSLAAN", width="stretch")
            
            if submitted:
                medical_id = generate_uuid("MED")
                
                success = run_query("""
                    INSERT INTO ntsp_medical_records (
                        medical_id, talent_id, blood_type, allergies, chronic_conditions,
                        height_cm, weight_kg, body_fat_percentage, muscle_mass_kg, bmi,
                        vo2_max, sprint_10m_seconds, sprint_30m_seconds,
                        vertical_jump_cm, agility_test_seconds, beep_test_level,
                        injury_history, last_medical_checkup, medical_clearance_status,
                        medical_clearance_expiry, doctor_name, doctor_notes,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    medical_id, talent_id,
                    blood_type if blood_type != "Unknown" else None,
                    allergies or None, chronic_conditions or None,
                    height_cm, weight_kg, body_fat, muscle_mass, bmi,
                    vo2_max, sprint_10m, sprint_30m, vertical_jump, agility_test, beep_test,
                    injury_history or None,
                    str(last_checkup), medical_clearance,
                    str(clearance_expiry) if clearance_expiry else None,
                    doctor_name or None, doctor_notes or None,
                    datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" Medische gegevens opgeslagen!")
                    log_audit(username, "MEDICAL_CREATED", "NTSP", details=f"Talent: {talent_id}")
    
    with tab2:
        df = get_data("ntsp_medical_records")
        data_table_with_empty_state(df, "Geen medische gegevens beschikbaar.")


# ============================================================================
# TAB 5: MENTAAL
# ============================================================================

def render_mental(username: str):
    """Render mentale evaluaties tab. Alleen voor psychologen!"""
    
    from auth.security import check_permission
    
    st.subheader(" Mentale Evaluaties")
    
    # PRIVACY: Mentale gezondheid data is zeer vertrouwelijk
    allowed_roles = ["SuperAdmin", "Psychologist", "Medical Staff"]
    
    if not check_permission(allowed_roles, silent=True):
        st.warning(" **Mentale gezondheidsgegevens zijn strikt vertrouwelijk.**")
        st.info(f"Toegang vereist één van deze rollen: {', '.join(allowed_roles)}")
        st.info("Alleen psychologen en medisch personeel mogen deze data inzien.")
        return
    
    st.info("Dit onderdeel is cruciaal voor het **Hayat Initiative** (Dossier 5) - mentale gezondheid van atleten.")
    
    talents = get_talents_dropdown()
    
    if not talents:
        st.warning("Geen talenten beschikbaar.")
        return
    
    with st.form("mental_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            talent_id = st.selectbox(
                "Talent *",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
            psychologist_name = st.text_input("Psycholoog", placeholder="Dr. Fatima Alaoui")
        
        with col2:
            evaluation_date = st.date_input("Datum", value=date.today())
            evaluation_type = st.selectbox(
                "Type Evaluatie",
                ["Initial Assessment", "Follow-up", "Crisis Intervention", "Routine Check"]
            )
        
        with col3:
            personality_type = st.text_input("Persoonlijkheidstype", placeholder="ENFJ / Introvert")
            learning_style = st.selectbox(
                "Leerstijl",
                ["Visual", "Auditory", "Kinesthetic", "Reading/Writing", "Mixed"]
            )
        
        st.markdown("---")
        st.markdown("###  Mentale Scores (1-10)")
        
        col4, col5, col6, col7 = st.columns(4)
        
        with col4:
            stress_mgmt = st.slider("Stressmanagement", 1, 10, 5)
            pressure = st.slider("Omgaan met druk", 1, 10, 5)
        
        with col5:
            confidence = st.slider("Zelfvertrouwen", 1, 10, 5)
            motivation = st.slider("Motivatie", 1, 10, 5)
        
        with col6:
            focus = st.slider("Concentratie", 1, 10, 5)
            resilience = st.slider("Veerkracht", 1, 10, 5)
        
        with col7:
            team_dynamics = st.slider("Teamdynamiek", 1, 10, 5)
            communication = st.slider("Communicatie", 1, 10, 5)
        
        st.markdown("---")
        st.markdown("### ️ Risico Factoren")
        
        col8, col9, col10 = st.columns(3)
        
        with col8:
            burnout_risk = st.selectbox("Burnout Risico", Options.RISK_LEVELS)
        
        with col9:
            homesickness_risk = st.selectbox("Heimwee Risico", Options.RISK_LEVELS)
        
        with col10:
            integration_support = st.checkbox("Integratie ondersteuning nodig")
        
        st.markdown("---")
        st.markdown("###  Diaspora Specifiek")
        
        col11, col12 = st.columns(2)
        
        with col11:
            cultural_identity = st.slider("Culturele Identiteit Score", 1, 10, 5)
            connection_morocco = st.selectbox(
                "Verbinding met Marokko",
                ["Strong", "Moderate", "Weak", "None/Unclear"]
            )
        
        with col12:
            language_barrier = st.selectbox(
                "Taalbarrière Assessment",
                ["None", "Minor", "Moderate", "Significant"]
            )
        
        st.markdown("---")
        
        recommendations = st.text_area("Aanbevelingen", placeholder="Aanbevelingen voor begeleiding...")
        session_notes = st.text_area("Sessie Notities", placeholder="Notities van de sessie...")
        
        follow_up_needed = st.checkbox("Follow-up sessies nodig")
        referral_needed = st.checkbox("Doorverwijzing nodig")
        
        submitted = st.form_submit_button(" OPSLAAN", width="stretch")
        
        if submitted:
            mental_id = generate_uuid("MENT")
            
            success = run_query("""
                INSERT INTO ntsp_mental_evaluations (
                    mental_eval_id, talent_id, psychologist_name, evaluation_date,
                    evaluation_type, personality_type, learning_style,
                    score_stress_management, score_pressure_handling, score_confidence,
                    score_motivation, score_focus, score_resilience,
                    score_team_dynamics, score_communication,
                    burnout_risk, homesickness_risk, integration_support_needed,
                    cultural_identity_score, connection_to_morocco, language_barrier_assessment,
                    recommendations, session_notes,
                    follow_up_sessions_needed, referral_needed,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                mental_id, talent_id, psychologist_name or None, str(evaluation_date),
                evaluation_type, personality_type or None, learning_style,
                stress_mgmt, pressure, confidence, motivation, focus, resilience,
                team_dynamics, communication,
                burnout_risk, homesickness_risk, 1 if integration_support else 0,
                cultural_identity, connection_morocco, language_barrier,
                recommendations or None, session_notes or None,
                1 if follow_up_needed else 0, 1 if referral_needed else 0,
                datetime.now().isoformat()
            ))
            
            if success:
                st.success(" Mentale evaluatie opgeslagen!")
                log_audit(username, "MENTAL_EVAL_CREATED", "NTSP", details=f"Talent: {talent_id}")


# ============================================================================
# TAB 6: WATCHLIST
# ============================================================================

def render_watchlist(username: str):
    """Render watchlist tab."""
    
    st.subheader(" Scout Watchlist")
    
    talents = get_talents_dropdown()
    scouts = get_scouts_dropdown()
    
    if not talents or not scouts:
        st.warning("Talenten en scouts moeten eerst worden geregistreerd.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("###  Toevoegen aan Watchlist")
        
        with st.form("watchlist_form"):
            scout_id = st.selectbox(
                "Scout",
                list(scouts.keys()),
                format_func=lambda x: scouts.get(x, x)
            )
            
            talent_id = st.selectbox(
                "Talent",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
            
            priority = st.selectbox("Prioriteit", Options.PRIORITY_LEVELS)
            reason = st.text_input("Reden", placeholder="Waarom volgen?")
            target_action = st.text_input("Gewenste actie", placeholder="Bijv: Academy test")
            follow_up_date = st.date_input("Follow-up datum", value=None)
            notes = st.text_area("Notities")
            
            if st.form_submit_button(" TOEVOEGEN"):
                watchlist_id = generate_uuid("WL")
                
                success = run_query("""
                    INSERT OR REPLACE INTO ntsp_watchlist (
                        watchlist_id, scout_id, talent_id, priority,
                        reason, target_action, follow_up_date, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    watchlist_id, scout_id, talent_id, priority,
                    reason or None, target_action or None,
                    str(follow_up_date) if follow_up_date else None,
                    notes or None, datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" Toegevoegd aan watchlist!")
                    log_audit(username, "WATCHLIST_ADD", "NTSP")
    
    with col2:
        st.markdown("###  Huidige Watchlist")
        
        df = get_data("ntsp_watchlist")
        
        if not df.empty:
            # Voeg talent namen toe
            talent_names = {k: v.split(" (")[0] for k, v in talents.items()}
            df['talent_name'] = df['talent_id'].map(talent_names)
            
            display_cols = ['talent_name', 'priority', 'reason', 'target_action', 'follow_up_date']
            display_cols = [c for c in display_cols if c in df.columns]
            
            st.dataframe(df[display_cols], width="stretch", hide_index=True)
        else:
            st.info("Watchlist is leeg.")


# ============================================================================
# TAB 7: SCOUTS
# ============================================================================

def render_scouts(username: str):
    """Render scouts management tab."""
    
    st.subheader(" Scout Management")
    
    tab1, tab2 = st.tabs([" Nieuwe Scout", " Scout Overzicht"])
    
    with tab1:
        with st.form("scout_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                first_name = st.text_input("Voornaam *", placeholder="Youssef")
                email = st.text_input("E-mail", placeholder="scout@proinvestix.ma")
                region = st.selectbox("Regio", ["Global"] + Options.REGIONS_MOROCCO + Options.DIASPORA_COUNTRIES)
            
            with col2:
                last_name = st.text_input("Achternaam *", placeholder="Bennani")
                phone = st.text_input("Telefoon", placeholder="+212 6XX XXX XXX")
                country = st.selectbox("Land", ["Morocco"] + Options.DIASPORA_COUNTRIES)
            
            with col3:
                specialization = st.selectbox("Specialisatie", Options.SCOUT_SPECIALIZATIONS)
                license_level = st.selectbox("Licentie", Options.COACHING_LICENSES)
                license_expiry = st.date_input("Licentie geldig tot", value=None)
            
            frmf_certified = st.checkbox("FRMF Gecertificeerd")
            
            if st.form_submit_button(" SCOUT REGISTREREN", width="stretch"):
                if not first_name or not last_name:
                    st.error("Naam is verplicht.")
                else:
                    scout_id = generate_uuid("SCT")
                    
                    success = run_query("""
                        INSERT INTO ntsp_scouts (
                            scout_id, first_name, last_name, email, phone,
                            region, country, specialization,
                            license_level, license_expiry, frmf_certified,
                            status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        scout_id, first_name, last_name, email or None, phone or None,
                        region, country, specialization,
                        license_level if license_level != "None" else None,
                        str(license_expiry) if license_expiry else None,
                        1 if frmf_certified else 0,
                        "ACTIVE", datetime.now().isoformat()
                    ))
                    
                    if success:
                        st.success(f" Scout {first_name} {last_name} geregistreerd!")
                        log_audit(username, "SCOUT_REGISTERED", "NTSP")
    
    with tab2:
        df = get_data("ntsp_scouts")
        
        if not df.empty:
            # Metrics
            total = len(df)
            active = len(df[df['status'] == 'ACTIVE'])
            frmf = len(df[df['frmf_certified'] == 1])
            
            metric_row([
                (" Totaal Scouts", total),
                (" Actief", active),
                ("️ FRMF Gecertificeerd", frmf),
            ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            display_cols = ['scout_id', 'first_name', 'last_name', 'region', 'specialization', 
                          'license_level', 'frmf_certified', 'status']
            display_cols = [c for c in display_cols if c in df.columns]
            
            st.dataframe(df[display_cols], width="stretch", hide_index=True)
        else:
            st.info("Nog geen scouts geregistreerd.")


# ============================================================================
# TAB 8: ANALYTICS
# ============================================================================

def render_analytics():
    """Render NTSP analytics."""
    
    st.subheader(" NTSP™ Analytics")
    
    df_talents = get_data("ntsp_talent_profiles")
    df_evals = get_data("ntsp_evaluations")
    df_scouts = get_data("ntsp_scouts")
    
    if df_talents.empty:
        st.info("Geen data beschikbaar voor analytics.")
        return
    
    # Totaal metrics
    total_talents = len(df_talents)
    diaspora_talents = len(df_talents[df_talents['is_diaspora'] == 1])
    total_evals = len(df_evals) if not df_evals.empty else 0
    total_scouts = len(df_scouts) if not df_scouts.empty else 0
    
    metric_row([
        (" Totaal Talenten", total_talents),
        (" Diaspora Talenten", diaspora_talents),
        (" Evaluaties", total_evals),
        (" Scouts", total_scouts),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("####  Talenten per Positie")
        if 'primary_position' in df_talents.columns:
            pos_dist = df_talents['primary_position'].value_counts()
            st.bar_chart(pos_dist)
    
    with col2:
        st.write("#### ️ Talenten per Status")
        if 'talent_status' in df_talents.columns:
            status_dist = df_talents['talent_status'].value_counts()
            st.bar_chart(status_dist)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.write("####  Diaspora per Land")
        diaspora_df = df_talents[df_talents['is_diaspora'] == 1]
        if not diaspora_df.empty and 'diaspora_country' in diaspora_df.columns:
            country_dist = diaspora_df['diaspora_country'].value_counts()
            st.bar_chart(country_dist)
        else:
            st.info("Geen diaspora data.")
    
    with col4:
        st.write("#### ⭐ Score Verdeling")
        if 'overall_score' in df_talents.columns:
            scores = df_talents[df_talents['overall_score'] > 0]['overall_score']
            if not scores.empty:
                st.line_chart(scores.sort_values())
            else:
                st.info("Geen scores beschikbaar.")
    
    # Top talenten
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("####  Top 10 Talenten (op score)")
    
    if 'overall_score' in df_talents.columns:
        top_talents = df_talents.nlargest(10, 'overall_score')[
            ['first_name', 'last_name', 'primary_position', 'current_club', 'overall_score', 'potential_score']
        ]
        if not top_talents.empty:
            st.dataframe(top_talents, width="stretch", hide_index=True)
        else:
            st.info("Geen talenten met scores.")
