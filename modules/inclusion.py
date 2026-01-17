# ============================================================================
# INCLUSION MODULE - WOMEN FOOTBALL & PARALYMPICS (DOSSIER 6)
# 
# Implementeert:
# - 12 Women Football Hubs (regionale centra)
# - Paralympic High Performance Center (HPC)
# - Talent tracking voor vrouwen en para-atleten
# - Specifieke beurzen en programma's
# - Evenementen en competities
# ============================================================================

import streamlit as st
from datetime import datetime, date
from typing import Dict, Optional

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import DB_FILE, Options, Messages, FOUNDATION_RATE
from database.connection import get_data, run_query, get_connection, count_records, aggregate_sum
from utils.helpers import generate_uuid
from auth.security import log_audit, check_permission
from ui.components import metric_row, page_header, paginated_dataframe


# ============================================================================
# CONSTANTEN
# ============================================================================

# 12 Women Football Hubs (verdeeld over Marokko)
WOMEN_HUBS = [
    {"id": "HUB-CAS", "name": "Casablanca Women Hub", "region": "Casablanca-Settat", "city": "Casablanca"},
    {"id": "HUB-RAB", "name": "Rabat Women Hub", "region": "Rabat-Salé-Kénitra", "city": "Rabat"},
    {"id": "HUB-MAR", "name": "Marrakech Women Hub", "region": "Marrakech-Safi", "city": "Marrakech"},
    {"id": "HUB-FES", "name": "Fès Women Hub", "region": "Fès-Meknès", "city": "Fès"},
    {"id": "HUB-TNG", "name": "Tanger Women Hub", "region": "Tanger-Tétouan-Al Hoceïma", "city": "Tanger"},
    {"id": "HUB-AGA", "name": "Agadir Women Hub", "region": "Souss-Massa", "city": "Agadir"},
    {"id": "HUB-OUJ", "name": "Oujda Women Hub", "region": "Oriental", "city": "Oujda"},
    {"id": "HUB-BEN", "name": "Béni Mellal Women Hub", "region": "Béni Mellal-Khénifra", "city": "Béni Mellal"},
    {"id": "HUB-LAA", "name": "Laâyoune Women Hub", "region": "Laâyoune-Sakia El Hamra", "city": "Laâyoune"},
    {"id": "HUB-DAK", "name": "Dakhla Women Hub", "region": "Dakhla-Oued Ed-Dahab", "city": "Dakhla"},
    {"id": "HUB-KEN", "name": "Kénitra Women Hub", "region": "Rabat-Salé-Kénitra", "city": "Kénitra"},
    {"id": "HUB-MEK", "name": "Meknès Women Hub", "region": "Fès-Meknès", "city": "Meknès"},
]

# Paralympic disciplines
PARALYMPIC_DISCIPLINES = [
    "Para Athletics",
    "Para Swimming",
    "Wheelchair Basketball",
    "Sitting Volleyball",
    "Para Powerlifting",
    "Para Taekwondo",
    "Blind Football",
    "Goalball",
    "Boccia",
    "Para Cycling",
    "Para Table Tennis",
    "Wheelchair Tennis"
]

# Disability classifications
DISABILITY_CLASSES = [
    "Visual Impairment (VI)",
    "Physical Impairment (PI)",
    "Intellectual Impairment (II)",
    "Hearing Impairment (HI)",
    "Limb Deficiency",
    "Spinal Cord Injury",
    "Cerebral Palsy",
    "Multiple Disabilities"
]


# ============================================================================
# DATABASE TABELLEN
# ============================================================================

def init_inclusion_tables():
    """Initialiseer Inclusion-specifieke tabellen."""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Women Football Hubs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS women_hubs (
            hub_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT NOT NULL,
            city TEXT NOT NULL,
            
            -- Faciliteiten
            capacity INTEGER DEFAULT 0,
            has_accommodation INTEGER DEFAULT 0,
            has_medical INTEGER DEFAULT 0,
            has_education INTEGER DEFAULT 0,
            
            -- Contact
            director_name TEXT,
            email TEXT,
            phone TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            opened_date TEXT,
            
            -- Stats
            total_players INTEGER DEFAULT 0,
            teams_count INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # Women Players Registry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS women_players (
            player_id TEXT PRIMARY KEY,
            
            -- Persoonlijk
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT DEFAULT 'Moroccan',
            
            -- Diaspora
            is_diaspora INTEGER DEFAULT 0,
            diaspora_country TEXT,
            
            -- Voetbal
            position TEXT,
            preferred_foot TEXT,
            hub_id TEXT,
            current_club TEXT,
            
            -- Niveau
            level TEXT DEFAULT 'AMATEUR',
            national_team INTEGER DEFAULT 0,
            national_team_caps INTEGER DEFAULT 0,
            
            -- Scores
            overall_score INTEGER DEFAULT 0,
            potential_score INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            scholarship INTEGER DEFAULT 0,
            scholarship_type TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (hub_id) REFERENCES women_hubs(hub_id)
        )
    ''')
    
    # Paralympic Athletes Registry
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paralympic_athletes (
            athlete_id TEXT PRIMARY KEY,
            
            -- Persoonlijk
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT DEFAULT 'Moroccan',
            
            -- Diaspora
            is_diaspora INTEGER DEFAULT 0,
            diaspora_country TEXT,
            
            -- Paralympic info
            discipline TEXT NOT NULL,
            disability_class TEXT NOT NULL,
            classification_code TEXT,
            
            -- Club/Team
            current_club TEXT,
            training_center TEXT,
            
            -- Performance
            national_team INTEGER DEFAULT 0,
            international_ranking INTEGER,
            personal_best TEXT,
            
            -- Support
            coach_name TEXT,
            support_staff TEXT,
            equipment_sponsor TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            scholarship INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # Inclusion Programs (beurzen, trainingen)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_programs (
            program_id TEXT PRIMARY KEY,
            
            -- Info
            name TEXT NOT NULL,
            program_type TEXT NOT NULL,
            target_group TEXT NOT NULL,
            
            -- Details
            description TEXT,
            duration_months INTEGER,
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            
            -- Financieel
            budget REAL DEFAULT 0,
            scholarship_amount REAL DEFAULT 0,
            
            -- Periode
            start_date TEXT,
            end_date TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # Program Enrollments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_enrollments (
            enrollment_id TEXT PRIMARY KEY,
            program_id TEXT NOT NULL,
            
            -- Deelnemer (kan women_player of paralympic_athlete zijn)
            participant_type TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            
            -- Beurs
            scholarship_awarded REAL DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ENROLLED',
            enrollment_date TEXT,
            completion_date TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (program_id) REFERENCES inclusion_programs(program_id)
        )
    ''')
    
    # Inclusion Events (wedstrijden, toernooien)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_events (
            event_id TEXT PRIMARY KEY,
            
            -- Info
            name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            target_group TEXT NOT NULL,
            
            -- Locatie
            location TEXT,
            hub_id TEXT,
            
            -- Datum
            event_date TEXT,
            end_date TEXT,
            
            -- Details
            description TEXT,
            max_participants INTEGER,
            registered_participants INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'UPCOMING',
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_women_hub ON women_players(hub_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_women_diaspora ON women_players(is_diaspora)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_para_discipline ON paralympic_athletes(discipline)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_program_type ON inclusion_programs(program_type)")
    
    conn.commit()
    conn.close()
    
    # Seed default hubs als ze nog niet bestaan
    seed_women_hubs()


def seed_women_hubs():
    """Voeg de 12 Women Hubs toe als ze nog niet bestaan."""
    for hub in WOMEN_HUBS:
        existing = count_records("women_hubs", "hub_id = ?", (hub['id'],))
        if existing == 0:
            run_query("""
                INSERT INTO women_hubs (hub_id, name, region, city, status, created_at)
                VALUES (?, ?, ?, ?, 'ACTIVE', ?)
            """, (hub['id'], hub['name'], hub['region'], hub['city'], datetime.now().isoformat()))


def register_inclusion_tables():
    """Registreer tabellen in whitelist."""
    from config import ALLOWED_TABLES
    tables = [
        'women_hubs',
        'women_players',
        'paralympic_athletes',
        'inclusion_programs',
        'inclusion_enrollments',
        'inclusion_events'
    ]
    for table in tables:
        if table not in ALLOWED_TABLES:
            ALLOWED_TABLES.append(table)


# ============================================================================
# MAIN RENDER
# ============================================================================

def render(username: str):
    """Render de Inclusion module."""
    
    # Init
    init_inclusion_tables()
    register_inclusion_tables()
    
    page_header(
        " Women Football & Paralympics",
        "Dossier 6 | 12 Women Hubs | Paralympic HPC | Inclusiviteit & Gelijkheid"
    )
    
    # Info
    st.info("""
    **ProInvestiX** zet zich in voor **gelijke kansen** in de sport. Deze module ondersteunt:
    - **12 Women Football Hubs** verspreid over heel Marokko
    - **Paralympic High Performance Center** voor para-atleten
    - **Beurzen en programma's** voor vrouwen en para-atleten
    """)
    
    tabs = st.tabs([
        " Women Hubs",
        " Women Players",
        " Paralympics",
        " Programma's",
        " Events",
        " Analytics"
    ])
    
    with tabs[0]:
        render_women_hubs(username)
    
    with tabs[1]:
        render_women_players(username)
    
    with tabs[2]:
        render_paralympics(username)
    
    with tabs[3]:
        render_programs(username)
    
    with tabs[4]:
        render_events(username)
    
    with tabs[5]:
        render_inclusion_analytics()


# ============================================================================
# TAB 1: WOMEN HUBS
# ============================================================================

def render_women_hubs(username: str):
    """Render Women Football Hubs overzicht."""
    
    st.subheader(" 12 Women Football Hubs")
    
    df_hubs = get_data("women_hubs")
    
    if not df_hubs.empty:
        # Metrics
        total_hubs = len(df_hubs)
        active_hubs = len(df_hubs[df_hubs['status'] == 'ACTIVE'])
        total_players = df_hubs['total_players'].sum()
        total_teams = df_hubs['teams_count'].sum()
        
        metric_row([
            (" Totaal Hubs", total_hubs),
            (" Actief", active_hubs),
            (" Speelsters", int(total_players)),
            (" Teams", int(total_teams)),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Hub kaart (simpele weergave)
        st.write("###  Hub Overzicht")
        
        col1, col2 = st.columns(2)
        
        for i, (_, hub) in enumerate(df_hubs.iterrows()):
            col = col1 if i % 2 == 0 else col2
            
            with col:
                status_emoji = "" if hub['status'] == 'ACTIVE' else ""
                
                with st.expander(f"{status_emoji} {hub['name']}"):
                    st.write(f"**Regio:** {hub['region']}")
                    st.write(f"**Stad:** {hub['city']}")
                    st.write(f"**Speelsters:** {hub['total_players']}")
                    st.write(f"**Teams:** {hub['teams_count']}")
                    
                    # Faciliteiten
                    facilities = []
                    if hub.get('has_accommodation'): facilities.append(" Accommodatie")
                    if hub.get('has_medical'): facilities.append(" Medisch")
                    if hub.get('has_education'): facilities.append(" Onderwijs")
                    
                    if facilities:
                        st.write(f"**Faciliteiten:** {', '.join(facilities)}")
                    
                    # Update knop
                    if check_permission(["SuperAdmin", "Academy Admin"], silent=True):
                        if st.button(f" Bewerk", key=f"edit_hub_{hub['hub_id']}"):
                            st.session_state['edit_hub'] = hub['hub_id']
        
        # Edit hub form
        if 'edit_hub' in st.session_state:
            st.markdown("---")
            st.write("###  Hub Bewerken")
            
            hub_id = st.session_state['edit_hub']
            hub_data = df_hubs[df_hubs['hub_id'] == hub_id].iloc[0]
            
            with st.form("edit_hub_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    capacity = st.number_input("Capaciteit", value=int(hub_data['capacity'] or 0))
                    has_accommodation = st.checkbox("Heeft accommodatie", value=bool(hub_data['has_accommodation']))
                    has_medical = st.checkbox("Heeft medische faciliteit", value=bool(hub_data['has_medical']))
                    has_education = st.checkbox("Heeft onderwijs", value=bool(hub_data['has_education']))
                
                with col2:
                    director = st.text_input("Directeur", value=hub_data['director_name'] or "")
                    email = st.text_input("Email", value=hub_data['email'] or "")
                    phone = st.text_input("Telefoon", value=hub_data['phone'] or "")
                
                if st.form_submit_button(" Opslaan"):
                    run_query("""
                        UPDATE women_hubs SET
                            capacity = ?, has_accommodation = ?, has_medical = ?, has_education = ?,
                            director_name = ?, email = ?, phone = ?
                        WHERE hub_id = ?
                    """, (capacity, int(has_accommodation), int(has_medical), int(has_education),
                          director, email, phone, hub_id))
                    
                    st.success(" Hub bijgewerkt!")
                    del st.session_state['edit_hub']
                    st.rerun()
    else:
        st.warning("Geen hubs gevonden. Database wordt geïnitialiseerd...")


# ============================================================================
# TAB 2: WOMEN PLAYERS
# ============================================================================

def render_women_players(username: str):
    """Render Women Players registry."""
    
    st.subheader(" Women Players Registry")
    
    df_hubs = get_data("women_hubs")
    hubs_map = {row['hub_id']: row['name'] for _, row in df_hubs.iterrows()} if not df_hubs.empty else {}
    
    tab1, tab2 = st.tabs([t("overview"), " Nieuwe Speelster"])
    
    with tab1:
        df = get_data("women_players")
        
        if not df.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                hub_filter = st.selectbox("Filter Hub", ["All"] + list(hubs_map.keys()),
                                         format_func=lambda x: "Alle Hubs" if x == "All" else hubs_map.get(x, x))
            with col2:
                level_filter = st.selectbox("Filter Level", ["All", "AMATEUR", "SEMI_PRO", "PROFESSIONAL"])
            with col3:
                diaspora_filter = st.selectbox("Diaspora", ["All", "Ja", "Nee"])
            
            filtered = df.copy()
            if hub_filter != "All":
                filtered = filtered[filtered['hub_id'] == hub_filter]
            if level_filter != "All":
                filtered = filtered[filtered['level'] == level_filter]
            if diaspora_filter == "Ja":
                filtered = filtered[filtered['is_diaspora'] == 1]
            elif diaspora_filter == "Nee":
                filtered = filtered[filtered['is_diaspora'] == 0]
            
            # Metrics
            metric_row([
                (" Totaal", len(filtered)),
                (" Diaspora", len(filtered[filtered['is_diaspora'] == 1])),
                (" Nationaal Team", len(filtered[filtered['national_team'] == 1])),
                (" Met Beurs", len(filtered[filtered['scholarship'] == 1])),
            ])
            
            # Tabel
            display_cols = ['first_name', 'last_name', 'position', 'level', 'hub_id', 'overall_score']
            paginated_dataframe(filtered[display_cols], per_page=20, key_prefix="women_players")
        else:
            st.info("Nog geen speelsters geregistreerd.")
    
    with tab2:
        with st.form("new_women_player"):
            st.markdown("### Persoonlijke Gegevens")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                first_name = st.text_input("Voornaam *")
                last_name = st.text_input("Achternaam *")
                dob = st.date_input("Geboortedatum", min_value=date(1980, 1, 1))
            
            with col2:
                nationality = st.selectbox("Nationaliteit", Options.NATIONALITIES)
                is_diaspora = st.checkbox("Diaspora speelster")
                if is_diaspora:
                    diaspora_country = st.selectbox("Diaspora land", Options.DIASPORA_COUNTRIES)
                else:
                    diaspora_country = None
            
            with col3:
                position = st.selectbox("Positie", Options.POSITIONS)
                preferred_foot = st.selectbox("Voorkeurvoet", Options.PREFERRED_FOOT)
                hub_id = st.selectbox("Hub", list(hubs_map.keys()), 
                                     format_func=lambda x: hubs_map.get(x, x)) if hubs_map else None
            
            st.markdown("### Club & Niveau")
            
            col1, col2 = st.columns(2)
            
            with col1:
                current_club = st.text_input("Huidige Club")
                level = st.selectbox("Niveau", ["AMATEUR", "SEMI_PRO", "PROFESSIONAL", "YOUTH"])
            
            with col2:
                national_team = st.checkbox("Nationaal Team")
                if national_team:
                    caps = st.number_input("Interlands", 0, 200, 0)
                else:
                    caps = 0
                scholarship = st.checkbox("Heeft beurs")
            
            if st.form_submit_button(" REGISTREER SPEELSTER", width="stretch"):
                if not first_name or not last_name:
                    st.error("Vul naam in.")
                else:
                    player_id = generate_uuid("WPL")
                    
                    success = run_query("""
                        INSERT INTO women_players (
                            player_id, first_name, last_name, date_of_birth, nationality,
                            is_diaspora, diaspora_country, position, preferred_foot, hub_id,
                            current_club, level, national_team, national_team_caps, scholarship,
                            status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (
                        player_id, first_name, last_name, str(dob), nationality,
                        1 if is_diaspora else 0, diaspora_country, position, preferred_foot,
                        hub_id, current_club, level, 1 if national_team else 0, caps,
                        1 if scholarship else 0, datetime.now().isoformat()
                    ))
                    
                    if success:
                        # Update hub player count
                        if hub_id:
                            run_query("UPDATE women_hubs SET total_players = total_players + 1 WHERE hub_id = ?", (hub_id,))
                        
                        st.success(f" Speelster {first_name} {last_name} geregistreerd!")
                        log_audit(username, "WOMEN_PLAYER_REGISTERED", "Inclusion")
                        st.rerun()


# ============================================================================
# TAB 3: PARALYMPICS
# ============================================================================

def render_paralympics(username: str):
    """Render Paralympic Athletes registry."""
    
    st.subheader(" Paralympic Athletes Registry")
    
    st.info("""
    **Paralympic High Performance Center (HPC)** ondersteunt atleten met een beperking
    om hun volledige potentieel te bereiken op het hoogste niveau.
    """)
    
    tab1, tab2 = st.tabs([" Atleten", " Nieuwe Atleet"])
    
    with tab1:
        df = get_data("paralympic_athletes")
        
        if not df.empty:
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                discipline_filter = st.selectbox("Discipline", ["All"] + PARALYMPIC_DISCIPLINES)
            with col2:
                class_filter = st.selectbox("Beperking", ["All"] + DISABILITY_CLASSES)
            
            filtered = df.copy()
            if discipline_filter != "All":
                filtered = filtered[filtered['discipline'] == discipline_filter]
            if class_filter != "All":
                filtered = filtered[filtered['disability_class'] == class_filter]
            
            # Metrics
            metric_row([
                (" Totaal Atleten", len(filtered)),
                (" Nationaal Team", len(filtered[filtered['national_team'] == 1])),
                (" Diaspora", len(filtered[filtered['is_diaspora'] == 1])),
                (" Met Beurs", len(filtered[filtered['scholarship'] == 1])),
            ])
            
            # Tabel
            if not filtered.empty:
                display_cols = ['first_name', 'last_name', 'discipline', 'disability_class', 'national_team']
                paginated_dataframe(filtered[display_cols], per_page=20, key_prefix="para_athletes")
        else:
            st.info("Nog geen para-atleten geregistreerd.")
    
    with tab2:
        with st.form("new_para_athlete"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Persoonlijk")
                first_name = st.text_input("Voornaam *")
                last_name = st.text_input("Achternaam *")
                dob = st.date_input("Geboortedatum", min_value=date(1960, 1, 1))
                nationality = st.selectbox("Nationaliteit", Options.NATIONALITIES)
                
                is_diaspora = st.checkbox("Diaspora atleet")
                diaspora_country = st.selectbox("Diaspora land", Options.DIASPORA_COUNTRIES) if is_diaspora else None
            
            with col2:
                st.markdown("### Paralympic Info")
                discipline = st.selectbox("Discipline *", PARALYMPIC_DISCIPLINES)
                disability_class = st.selectbox("Type Beperking *", DISABILITY_CLASSES)
                classification_code = st.text_input("Classificatie Code", placeholder="Bijv: T11, S6, F40")
                
                current_club = st.text_input("Club/Team")
                training_center = st.text_input("Trainingscentrum")
                
                national_team = st.checkbox("Nationaal Team")
                scholarship = st.checkbox("Heeft beurs")
            
            coach_name = st.text_input("Coach")
            
            if st.form_submit_button(" REGISTREER ATLEET", width="stretch"):
                if not first_name or not last_name or not discipline:
                    st.error("Vul verplichte velden in.")
                else:
                    athlete_id = generate_uuid("PAR")
                    
                    success = run_query("""
                        INSERT INTO paralympic_athletes (
                            athlete_id, first_name, last_name, date_of_birth, nationality,
                            is_diaspora, diaspora_country, discipline, disability_class,
                            classification_code, current_club, training_center, national_team,
                            coach_name, scholarship, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (
                        athlete_id, first_name, last_name, str(dob), nationality,
                        1 if is_diaspora else 0, diaspora_country, discipline, disability_class,
                        classification_code, current_club, training_center, 1 if national_team else 0,
                        coach_name, 1 if scholarship else 0, datetime.now().isoformat()
                    ))
                    
                    if success:
                        st.success(f" Para-atleet {first_name} {last_name} geregistreerd!")
                        log_audit(username, "PARA_ATHLETE_REGISTERED", "Inclusion")
                        st.rerun()


# ============================================================================
# TAB 4: PROGRAMMA'S
# ============================================================================

def render_programs(username: str):
    """Render inclusion programs."""
    
    st.subheader(" Inclusion Programma's & Beurzen")
    
    program_types = [
        "SCHOLARSHIP",      # Studiebeurs
        "TRAINING_CAMP",    # Trainingskamp
        "MENTORSHIP",       # Mentorprogramma
        "EQUIPMENT_GRANT",  # Materiaal subsidie
        "TRAVEL_GRANT",     # Reis subsidie
        "EDUCATION"         # Opleiding
    ]
    
    target_groups = ["WOMEN", "PARALYMPIC", "BOTH"]
    
    tab1, tab2 = st.tabs([t("overview"), " Nieuw Programma"])
    
    with tab1:
        df = get_data("inclusion_programs")
        
        if not df.empty:
            active = df[df['status'] == 'ACTIVE']
            
            metric_row([
                (" Totaal Programma's", len(df)),
                (" Actief", len(active)),
                (" Totaal Budget", f"€ {df['budget'].sum():,.0f}"),
                (" Deelnemers", int(df['current_participants'].sum())),
            ])
            
            st.dataframe(df[['name', 'program_type', 'target_group', 'current_participants', 'status']], 
                        width="stretch", hide_index=True)
        else:
            st.info("Nog geen programma's.")
    
    with tab2:
        if not check_permission(["SuperAdmin", "Academy Admin"], silent=True):
            st.warning(" Alleen administrators kunnen programma's aanmaken.")
            return
        
        with st.form("new_program"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Programma Naam *")
                program_type = st.selectbox("Type *", program_types)
                target_group = st.selectbox("Doelgroep *", target_groups,
                                           format_func=lambda x: {"WOMEN": "Vrouwen", "PARALYMPIC": "Para-atleten", "BOTH": "Beide"}.get(x, x))
                description = st.text_area("Beschrijving")
            
            with col2:
                duration = st.number_input("Duur (maanden)", 1, 48, 12)
                max_participants = st.number_input("Max Deelnemers", 1, 1000, 50)
                budget = st.number_input("Budget (€)", 0, 10000000, 50000)
                scholarship_amount = st.number_input("Beurs per persoon (€)", 0, 100000, 5000)
                
                start_date = st.date_input("Start Datum")
            
            if st.form_submit_button(" PROGRAMMA AANMAKEN", width="stretch"):
                if not name:
                    st.error("Vul programma naam in.")
                else:
                    program_id = generate_uuid("PRG")
                    
                    success = run_query("""
                        INSERT INTO inclusion_programs (
                            program_id, name, program_type, target_group, description,
                            duration_months, max_participants, budget, scholarship_amount,
                            start_date, status, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (
                        program_id, name, program_type, target_group, description,
                        duration, max_participants, budget, scholarship_amount,
                        str(start_date), datetime.now().isoformat()
                    ))
                    
                    if success:
                        st.success(f" Programma '{name}' aangemaakt!")
                        log_audit(username, "INCLUSION_PROGRAM_CREATED", "Inclusion")
                        st.rerun()


# ============================================================================
# TAB 5: EVENTS
# ============================================================================

def render_events(username: str):
    """Render inclusion events."""
    
    st.subheader(" Inclusion Events")
    
    event_types = [
        "TOURNAMENT",       # Toernooi
        "TRAINING_CAMP",    # Trainingskamp
        "WORKSHOP",         # Workshop
        "EXHIBITION",       # Demonstratie wedstrijd
        "CHAMPIONSHIP",     # Kampioenschap
        "TRIAL_DAY"         # Selectiedag
    ]
    
    tab1, tab2 = st.tabs([" Kalender", " Nieuw Event"])
    
    with tab1:
        df = get_data("inclusion_events")
        
        if not df.empty:
            upcoming = df[df['status'] == 'UPCOMING']
            
            metric_row([
                (" Totaal Events", len(df)),
                (" Upcoming", len(upcoming)),
            ])
            
            st.dataframe(df[['name', 'event_type', 'target_group', 'event_date', 'status']], 
                        width="stretch", hide_index=True)
        else:
            st.info("Nog geen events.")
    
    with tab2:
        with st.form("new_event"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Event Naam *")
                event_type = st.selectbox("Type *", event_types)
                target_group = st.selectbox("Doelgroep *", ["WOMEN", "PARALYMPIC", "BOTH"])
                location = st.text_input("Locatie")
            
            with col2:
                event_date = st.date_input("Datum")
                max_participants = st.number_input("Max Deelnemers", 1, 10000, 100)
                description = st.text_area("Beschrijving")
            
            if st.form_submit_button(" EVENT AANMAKEN", width="stretch"):
                event_id = generate_uuid("EVT")
                
                run_query("""
                    INSERT INTO inclusion_events (
                        event_id, name, event_type, target_group, location,
                        event_date, max_participants, description, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'UPCOMING', ?)
                """, (
                    event_id, name, event_type, target_group, location,
                    str(event_date), max_participants, description, datetime.now().isoformat()
                ))
                
                st.success(f" Event '{name}' aangemaakt!")
                log_audit(username, "INCLUSION_EVENT_CREATED", "Inclusion")
                st.rerun()


# ============================================================================
# TAB 6: ANALYTICS
# ============================================================================

def render_inclusion_analytics():
    """Render inclusion analytics."""
    
    st.subheader(" Inclusion Analytics")
    
    df_women = get_data("women_players")
    df_para = get_data("paralympic_athletes")
    df_programs = get_data("inclusion_programs")
    
    # Overview metrics
    total_women = len(df_women) if not df_women.empty else 0
    total_para = len(df_para) if not df_para.empty else 0
    diaspora_women = len(df_women[df_women['is_diaspora'] == 1]) if not df_women.empty else 0
    diaspora_para = len(df_para[df_para['is_diaspora'] == 1]) if not df_para.empty else 0
    
    metric_row([
        (" Women Players", total_women),
        (" Para-atleten", total_para),
        (" Diaspora (W)", diaspora_women),
        (" Diaspora (P)", diaspora_para),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("####  Women per Level")
        if not df_women.empty:
            st.bar_chart(df_women['level'].value_counts())
        else:
            st.info("Geen data.")
    
    with col2:
        st.write("####  Para per Discipline")
        if not df_para.empty:
            st.bar_chart(df_para['discipline'].value_counts())
        else:
            st.info("Geen data.")
    
    # Programs budget
    if not df_programs.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("####  Programma Budget per Type")
        budget_by_type = df_programs.groupby('program_type')['budget'].sum()
        st.bar_chart(budget_by_type)
