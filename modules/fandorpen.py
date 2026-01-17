# ============================================================================
# FANDORPEN MODULE - WK2030 SUPPORTER GOVERNANCE
# 
# Implementeert:
# - FanDorp Management (per land)
# - Vrijwilliger Registry (dubbele nationaliteit)
# - Taalvaardigheden & Bevoegdheden
# - Diensten/Shift Planning
# - Incident Management
# - Digital Consulate Hub Integratie
# - Identity Shield Verificatie
# - Supporter Services Tracking
# ============================================================================

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import random

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import DB_FILE, Options, FOUNDATION_RATE
from database.connection import get_data, run_query, run_transaction, count_records, aggregate_sum
from utils.helpers import generate_uuid
from auth.security import log_audit, check_permission
from ui.styles import COLORS, premium_header, render_kpi_row


# ============================================================================
# CONSTANTEN
# ============================================================================

# Deelnemende landen WK2030
WK2030_COUNTRIES = [
    ("België", "BE", "", ["Nederlands", "Frans", "Duits"]),
    ("Nederland", "NL", "", ["Nederlands"]),
    ("Frankrijk", "FR", "", ["Frans"]),
    ("Duitsland", "DE", "", ["Duits"]),
    ("Spanje", "ES", "", ["Spaans"]),
    ("Portugal", "PT", "", ["Portugees"]),
    ("Italië", "IT", "", ["Italiaans"]),
    ("Engeland", "UK", "", ["Engels"]),
    ("Verenigde Staten", "US", "", ["Engels", "Spaans"]),
    ("Brazilië", "BR", "", ["Portugees"]),
    ("Argentinië", "AR", "", ["Spaans"]),
    ("Japan", "JP", "", ["Japans"]),
    ("Zuid-Korea", "KR", "", ["Koreaans"]),
    ("Saoedi-Arabië", "SA", "", ["Arabisch"]),
    ("Qatar", "QA", "", ["Arabisch"]),
    ("Canada", "CA", "", ["Engels", "Frans"]),
]

# FanDorp locaties in Marokko
FANDORP_LOCATIONS = [
    "Casablanca", "Rabat", "Marrakech", "Tangier", "Fes", 
    "Agadir", "Oujda", "Kenitra", "El Jadida", "Nador"
]

# Vrijwilliger rollen
VOLUNTEER_ROLES = [
    "Welkomst Coördinator",
    "Taalassistent",
    "Culturele Gids",
    "Transport Helper",
    "Informatiebalie",
    "Medische Liaison",
    "Veiligheidssteward",
    "Consulaat Liaison",
    "VIP Begeleider",
    "Sociale Media",
]

# Talen
LANGUAGES = [
    "Arabisch", "Darija", "Frans", "Nederlands", "Engels", "Duits", 
    "Spaans", "Portugees", "Italiaans", "Japans", "Koreaans", "Turks"
]

# Incident types
INCIDENT_TYPES = [
    "Verloren voorwerp",
    "Medische hulp",
    "Taalprobleem",
    "Vervoerprobleem",
    "Accommodatie issue",
    "Ticket probleem",
    "Oplichting poging",
    "Cultureel misverstand",
    "Noodgeval",
    "Andere",
]

# Shift types
SHIFT_TYPES = [
    ("OCHTEND", "06:00 - 14:00"),
    ("MIDDAG", "14:00 - 22:00"),
    ("AVOND", "22:00 - 06:00"),
    ("WEDSTRIJD", "Match Day"),
    ("SPECIAAL", "Special Event"),
]

# Bevoegdheidsniveaus
CLEARANCE_LEVELS = [
    ("BASIC", "Basis vrijwilliger"),
    ("VERIFIED", "Geverifieerde vrijwilliger"),
    ("SENIOR", "Senior vrijwilliger"),
    ("COORDINATOR", "FanDorp coördinator"),
    ("LIAISON", "Consulaat liaison"),
]

# Training Modules
TRAINING_MODULES = [
    ("welkom", "Welkom & Gastvrijheid", "Basis ontvangst en communicatie", 30),
    ("cultuur", "Culturele Sensitiviteit", "Marokkaanse cultuur en tradities", 45),
    ("nood", "Noodprocedures", "EHBO en evacuatie procedures", 60),
    ("taal", "Taalvaardigheden", "Communicatie in meerdere talen", 30),
    ("conflict", "Conflict Resolutie", "De-escalatie technieken", 45),
    ("medisch", "Medische Basis", "Eerste hulp en doorverwijzing", 60),
    ("vip", "VIP Protocol", "Omgang met VIP gasten", 30),
    ("digitaal", "Digitale Tools", "Gebruik van ProInvestiX platform", 20),
]

# Badges
BADGES = {
    "welkom_expert": ("", "Welkomst Expert", "5+ positieve beoordelingen"),
    "cultureel": ("", "Cultureel Ambassadeur", "Cultuur training afgerond"),
    "ehbo": ("", "EHBO Certified", "Medische training afgerond"),
    "meertalig": ("", "Meertalig", "3+ talen vloeiend"),
    "top_performer": ("", "Top Performer", "95%+ tevredenheid"),
    "veiligheid": ("", "Veiligheid Pro", "Nood & Conflict training"),
    "vip": ("", "VIP Service", "VIP Protocol certified"),
    "veteraan": ("", "Veteraan", "50+ shifts voltooid"),
    "mentor": ("‍", "Mentor", "5+ nieuwe vrijwilligers begeleid"),
    "innovator": ("", "Innovator", "Verbetervoorstel geïmplementeerd"),
}

# Service types
SERVICE_TYPES = [
    "Informatie",
    "Vertaling", 
    "Begeleiding",
    "Medische hulp",
    "Transport assistentie",
    "VIP Service",
    "Ticket hulp",
    "Accommodatie hulp",
]


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def ensure_fandorpen_tables():
    """Maak FanDorpen tabellen aan als ze niet bestaan."""
    queries = [
        # FanDorpen tabel
        """
        CREATE TABLE IF NOT EXISTS fandorpen (
            fandorp_id TEXT PRIMARY KEY,
            country_name TEXT NOT NULL,
            country_code TEXT NOT NULL,
            country_flag TEXT,
            location TEXT NOT NULL,
            languages TEXT,
            capacity INTEGER DEFAULT 500,
            coordinator_id TEXT,
            consulate_id TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT,
            updated_at TEXT
        )
        """,
        # Vrijwilligers tabel
        """
        CREATE TABLE IF NOT EXISTS fandorp_volunteers (
            volunteer_id TEXT PRIMARY KEY,
            identity_id TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            nationality_1 TEXT DEFAULT 'Moroccan',
            nationality_2 TEXT,
            languages TEXT,
            role TEXT,
            fandorp_id TEXT,
            clearance_level TEXT DEFAULT 'BASIC',
            verified INTEGER DEFAULT 0,
            background_check INTEGER DEFAULT 0,
            training_completed INTEGER DEFAULT 0,
            training_score INTEGER DEFAULT 0,
            badges TEXT,
            qr_code TEXT,
            status TEXT DEFAULT 'PENDING',
            registered_at TEXT,
            updated_at TEXT
        )
        """,
        # Diensten/Shifts tabel
        """
        CREATE TABLE IF NOT EXISTS fandorp_shifts (
            shift_id TEXT PRIMARY KEY,
            volunteer_id TEXT NOT NULL,
            fandorp_id TEXT NOT NULL,
            shift_date TEXT NOT NULL,
            shift_type TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            status TEXT DEFAULT 'SCHEDULED',
            check_in TEXT,
            check_out TEXT,
            notes TEXT,
            created_at TEXT
        )
        """,
        # Incidenten tabel
        """
        CREATE TABLE IF NOT EXISTS fandorp_incidents (
            incident_id TEXT PRIMARY KEY,
            fandorp_id TEXT NOT NULL,
            volunteer_id TEXT,
            incident_type TEXT NOT NULL,
            description TEXT,
            supporter_nationality TEXT,
            severity TEXT DEFAULT 'LOW',
            status TEXT DEFAULT 'OPEN',
            resolution TEXT,
            escalated_to TEXT,
            reported_at TEXT,
            resolved_at TEXT
        )
        """,
        # Supporter services log
        """
        CREATE TABLE IF NOT EXISTS fandorp_services (
            service_id TEXT PRIMARY KEY,
            fandorp_id TEXT NOT NULL,
            volunteer_id TEXT,
            service_type TEXT NOT NULL,
            supporter_nationality TEXT,
            language_used TEXT,
            description TEXT,
            satisfaction_score INTEGER,
            served_at TEXT
        )
        """,
        # Training tabel
        """
        CREATE TABLE IF NOT EXISTS fandorp_training (
            training_id TEXT PRIMARY KEY,
            volunteer_id TEXT NOT NULL,
            module_name TEXT NOT NULL,
            module_type TEXT,
            score INTEGER,
            passed INTEGER DEFAULT 0,
            completed_at TEXT
        )
        """,
        # Chat/Messages tabel
        """
        CREATE TABLE IF NOT EXISTS fandorp_messages (
            message_id TEXT PRIMARY KEY,
            fandorp_id TEXT NOT NULL,
            sender_id TEXT NOT NULL,
            sender_name TEXT,
            message_type TEXT DEFAULT 'CHAT',
            content TEXT,
            priority TEXT DEFAULT 'NORMAL',
            read_by TEXT,
            created_at TEXT
        )
        """
    ]
    
    for query in queries:
        try:
            run_query(query)
        except:
            pass


def get_fandorp_stats() -> Dict:
    """Haal FanDorpen statistieken op."""
    try:
        fandorpen = count_records('fandorpen')
        volunteers = count_records('fandorp_volunteers')
        active_volunteers = len(get_data("fandorp_volunteers", "status = 'ACTIVE'"))
        shifts = count_records('fandorp_shifts')
        incidents = count_records('fandorp_incidents')
        services = count_records('fandorp_services')
        
        return {
            'fandorpen': fandorpen,
            'volunteers': volunteers,
            'active_volunteers': active_volunteers,
            'shifts': shifts,
            'incidents': incidents,
            'services': services
        }
    except:
        return {
            'fandorpen': 0,
            'volunteers': 0,
            'active_volunteers': 0,
            'shifts': 0,
            'incidents': 0,
            'services': 0
        }


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render(username: str):
    """Render FanDorpen module."""
    
    # Ensure tables exist
    ensure_fandorpen_tables()
    
    # Header
    premium_header(
        " FANDORPEN",
        "WK2030 Internationale Supporter Governance"
    )
    
    # Get stats
    stats = get_fandorp_stats()
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric(" FanDorpen", stats['fandorpen'])
    col2.metric(" Vrijwilligers", stats['volunteers'])
    col3.metric(" Actief", stats['active_volunteers'])
    col4.metric(" Diensten", stats['shifts'])
    col5.metric(" Services", stats['services'])
    
    # Tabs
    tabs = st.tabs([
        " FanDorpen",
        " Vrijwilligers", 
        " Training & Badges",
        " QR Check-in",
        " Diensten",
        " Communicatie",
        " Incidenten",
        " Dashboard"
    ])
    
    with tabs[0]:
        render_fandorpen_management(username)
    
    with tabs[1]:
        render_volunteers(username)
    
    with tabs[2]:
        render_training_badges(username)
    
    with tabs[3]:
        render_qr_checkin(username)
    
    with tabs[4]:
        render_shifts(username)
    
    with tabs[5]:
        render_chat(username)
    
    with tabs[6]:
        render_incidents(username)
    
    with tabs[7]:
        render_dashboard(username)


# ============================================================================
# FANDORPEN MANAGEMENT
# ============================================================================

def render_fandorpen_management(username: str):
    """Beheer FanDorpen per land."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(212, 175, 55, 0.3);'>
            <h3 style='color: {COLORS["gold"]}; margin: 0;'> FanDorpen Management</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Officieel georganiseerde supporterzones voor WK2030 bezoekers
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Bestaande FanDorpen
        df = get_data("fandorpen")
        
        if not df.empty:
            st.markdown("###  Actieve FanDorpen")
            
            for _, row in df.iterrows():
                with st.expander(f"{row.get('country_flag', '')} FanDorp {row['country_name']} - {row['location']}"):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"**Land:** {row['country_name']} ({row['country_code']})")
                        st.write(f"**Locatie:** {row['location']}")
                        st.write(f"**Capaciteit:** {row.get('capacity', 500)} supporters")
                    with col_b:
                        st.write(f"**Talen:** {row.get('languages', 'N/A')}")
                        st.write(f"**Status:** {row.get('status', 'ACTIVE')}")
                        
                        # Aantal vrijwilligers
                        vol_df = get_data("fandorp_volunteers", f"fandorp_id = '{row['fandorp_id']}'")
                        st.write(f"**Vrijwilligers:** {len(vol_df)}")
        else:
            st.info("Nog geen FanDorpen aangemaakt. Gebruik het formulier rechts om te starten.")
    
    with col2:
        st.markdown("###  Nieuw FanDorp")
        
        with st.form("new_fandorp"):
            # Land selectie
            country_options = [f"{c[2]} {c[0]}" for c in WK2030_COUNTRIES]
            selected_country = st.selectbox("Land", country_options)
            
            # Location
            location = st.selectbox("Locatie in Marokko", FANDORP_LOCATIONS)
            
            # Capaciteit
            capacity = st.number_input("Capaciteit", min_value=100, max_value=5000, value=500, step=100)
            
            if st.form_submit_button(" Aanmaken", width="stretch"):
                # Find country details
                idx = country_options.index(selected_country)
                country = WK2030_COUNTRIES[idx]
                
                fandorp_id = generate_uuid("FDP")
                languages = ", ".join(country[3] + ["Arabisch", "Darija"])
                
                success = run_query("""
                    INSERT INTO fandorpen 
                    (fandorp_id, country_name, country_code, country_flag, location, 
                     languages, capacity, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                """, (fandorp_id, country[0], country[1], country[2], location,
                      languages, capacity, datetime.now().isoformat(), datetime.now().isoformat()))
                
                if success:
                    log_audit(username, "FANDORP_CREATED", f"FanDorp {country[0]} in {location}")
                    st.success(f" FanDorp {country[0]} aangemaakt!")
                    st.rerun()
                else:
                    st.error(" Kon FanDorp niet aanmaken")


# ============================================================================
# VRIJWILLIGERS MANAGEMENT
# ============================================================================

def render_volunteers(username: str):
    """Beheer vrijwilligers met dubbele nationaliteit."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(72, 187, 120, 0.3);'>
            <h3 style='color: {COLORS["success"]}; margin: 0;'> Vrijwilligers Registry</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Diaspora vrijwilligers met dubbele nationaliteit - de menselijke laag van WK2030
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t("overview"), " Registratie"])
    
    with tab1:
        df = get_data("fandorp_volunteers")
        
        if not df.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                status_filter = st.selectbox(t("status"), ["Alle", "PENDING", "ACTIVE", "INACTIVE"])
            with col2:
                role_filter = st.selectbox("Rol", ["Alle"] + VOLUNTEER_ROLES)
            with col3:
                clearance_filter = st.selectbox("Bevoegdheid", ["Alle"] + [c[0] for c in CLEARANCE_LEVELS])
            
            # Apply filters
            filtered_df = df.copy()
            if status_filter != "Alle":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            if role_filter != "Alle":
                filtered_df = filtered_df[filtered_df['role'] == role_filter]
            if clearance_filter != "Alle":
                filtered_df = filtered_df[filtered_df['clearance_level'] == clearance_filter]
            
            st.markdown(f"**{len(filtered_df)} vrijwilligers gevonden**")
            
            # Display
            for _, vol in filtered_df.iterrows():
                status_color = {
                    'ACTIVE': COLORS['success'],
                    'PENDING': COLORS['warning'],
                    'INACTIVE': COLORS['error']
                }.get(vol.get('status', 'PENDING'), COLORS['text_muted'])
                
                verified_badge = "" if vol.get('verified', 0) else "⏳"
                training_badge = "" if vol.get('training_completed', 0) else ""
                
                with st.expander(f"{verified_badge} {vol['first_name']} {vol['last_name']} - {vol.get('role', 'N/A')} {training_badge}"):
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.write(f"**Naam:** {vol['first_name']} {vol['last_name']}")
                        st.write(f"**Email:** {vol.get('email', 'N/A')}")
                        st.write(f"**Telefoon:** {vol.get('phone', 'N/A')}")
                    
                    with col_b:
                        st.write(f"**Nationaliteit 1:**  {vol.get('nationality_1', 'Moroccan')}")
                        st.write(f"**Nationaliteit 2:** {vol.get('nationality_2', 'N/A')}")
                        st.write(f"**Talen:** {vol.get('languages', 'N/A')}")
                    
                    with col_c:
                        st.write(f"**Rol:** {vol.get('role', 'N/A')}")
                        st.write(f"**Bevoegdheid:** {vol.get('clearance_level', 'BASIC')}")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{vol.get('status', 'PENDING')}</span>", unsafe_allow_html=True)
                    
                    # Verificatie badges
                    st.markdown("---")
                    badge_col1, badge_col2, badge_col3 = st.columns(3)
                    with badge_col1:
                        if vol.get('verified', 0):
                            st.success(" Identity Verified")
                        else:
                            st.warning("⏳ Awaiting Verification")
                    with badge_col2:
                        if vol.get('background_check', 0):
                            st.success(" Background Check OK")
                        else:
                            st.warning(" Background Check Pending")
                    with badge_col3:
                        if vol.get('training_completed', 0):
                            st.success(" Training Completed")
                        else:
                            st.info(" Training Required")
                    
                    # Admin actions
                    if check_permission(["SuperAdmin", "Official"], silent=True):
                        st.markdown("---")
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if not vol.get('verified', 0):
                                if st.button(" Verify", key=f"verify_{vol['volunteer_id']}"):
                                    run_query("UPDATE fandorp_volunteers SET verified = 1, updated_at = ? WHERE volunteer_id = ?",
                                              (datetime.now().isoformat(), vol['volunteer_id']))
                                    log_audit(username, "VOLUNTEER_VERIFIED", vol['volunteer_id'])
                                    st.rerun()
                        
                        with action_col2:
                            if vol.get('status') == 'PENDING':
                                if st.button(" Activate", key=f"activate_{vol['volunteer_id']}"):
                                    run_query("UPDATE fandorp_volunteers SET status = 'ACTIVE', updated_at = ? WHERE volunteer_id = ?",
                                              (datetime.now().isoformat(), vol['volunteer_id']))
                                    log_audit(username, "VOLUNTEER_ACTIVATED", vol['volunteer_id'])
                                    st.rerun()
                        
                        with action_col3:
                            new_clearance = st.selectbox(
                                "Upgrade clearance",
                                [c[0] for c in CLEARANCE_LEVELS],
                                index=[c[0] for c in CLEARANCE_LEVELS].index(vol.get('clearance_level', 'BASIC')),
                                key=f"clearance_{vol['volunteer_id']}"
                            )
                            if new_clearance != vol.get('clearance_level', 'BASIC'):
                                if st.button("Update", key=f"update_cl_{vol['volunteer_id']}"):
                                    run_query("UPDATE fandorp_volunteers SET clearance_level = ?, updated_at = ? WHERE volunteer_id = ?",
                                              (new_clearance, datetime.now().isoformat(), vol['volunteer_id']))
                                    log_audit(username, "VOLUNTEER_CLEARANCE_UPDATED", f"{vol['volunteer_id']} -> {new_clearance}")
                                    st.rerun()
        else:
            st.info("Nog geen vrijwilligers geregistreerd.")
    
    with tab2:
        render_volunteer_registration(username)


def render_volunteer_registration(username: str):
    """Vrijwilliger registratie formulier."""
    
    st.markdown("###  Vrijwilliger Registratie")
    st.markdown("""
        > **Vereisten:**
        > - Marokkaanse nationaliteit (geboorte of naturalisatie)
        > - Tweede nationaliteit van WK2030 deelnemend land
        > - Vloeiend in minstens 2 talen
    """)
    
    # Get FanDorpen for dropdown
    fandorpen_df = get_data("fandorpen")
    fandorp_options = {f"{row['country_flag']} FanDorp {row['country_name']}": row['fandorp_id'] 
                       for _, row in fandorpen_df.iterrows()} if not fandorpen_df.empty else {}
    
    with st.form("volunteer_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("Voornaam *")
            last_name = st.text_input("Achternaam *")
            email = st.text_input("Email *")
            phone = st.text_input("Telefoon")
        
        with col2:
            nationality_2 = st.selectbox("Tweede Nationaliteit *", 
                                          [c[0] for c in WK2030_COUNTRIES])
            languages = st.multiselect("Talen *", LANGUAGES, default=["Arabisch"])
            role = st.selectbox("Gewenste Rol", VOLUNTEER_ROLES)
            
            if fandorp_options:
                fandorp_selection = st.selectbox("FanDorp Voorkeur", list(fandorp_options.keys()))
            else:
                fandorp_selection = None
                st.warning("Nog geen FanDorpen beschikbaar")
        
        st.markdown("---")
        
        agree = st.checkbox("Ik bevestig dat ik de Marokkaanse nationaliteit heb EN de geselecteerde tweede nationaliteit")
        
        if st.form_submit_button(" Registreren", width="stretch"):
            if not first_name or not last_name or not email or not nationality_2:
                st.error(t("error_fill_required"))
            elif len(languages) < 2:
                st.error("Selecteer minstens 2 talen")
            elif not agree:
                st.error("Bevestig uw nationaliteiten")
            else:
                volunteer_id = generate_uuid("VOL")
                fandorp_id = fandorp_options.get(fandorp_selection) if fandorp_selection else None
                
                success = run_query("""
                    INSERT INTO fandorp_volunteers
                    (volunteer_id, first_name, last_name, email, phone, 
                     nationality_1, nationality_2, languages, role, fandorp_id,
                     clearance_level, verified, background_check, training_completed,
                     status, registered_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'Moroccan', ?, ?, ?, ?, 
                            'BASIC', 0, 0, 0, 'PENDING', ?, ?)
                """, (volunteer_id, first_name, last_name, email, phone,
                      nationality_2, ", ".join(languages), role, fandorp_id,
                      datetime.now().isoformat(), datetime.now().isoformat()))
                
                if success:
                    log_audit(username, "VOLUNTEER_REGISTERED", volunteer_id)
                    st.success(f"""
                         **Registratie Succesvol!**
                        
                        Uw aanvraag is ingediend. U ontvangt bericht wanneer:
                        1.  Uw identiteit is geverifieerd
                        2.  Uw achtergrondcontrole is afgerond
                        3.  U wordt uitgenodigd voor training
                        
                        **Vrijwilliger ID:** `{volunteer_id}`
                    """)
                else:
                    st.error(" Registratie mislukt")


# ============================================================================
# DIENSTEN / SHIFTS
# ============================================================================

def render_shifts(username: str):
    """Diensten planning en beheer."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(66, 153, 225, 0.3);'>
            <h3 style='color: {COLORS["info"]}; margin: 0;'> Diensten Planning</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Shift management voor vrijwilligers
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t("overview"), " Nieuwe Dienst"])
    
    with tab1:
        df = get_data("fandorp_shifts")
        
        if not df.empty:
            # Upcoming shifts
            st.markdown("###  Geplande Diensten")
            
            for _, shift in df.iterrows():
                status_color = {
                    'SCHEDULED': COLORS['info'],
                    'IN_PROGRESS': COLORS['warning'],
                    'COMPLETED': COLORS['success'],
                    'CANCELLED': COLORS['error']
                }.get(shift.get('status', 'SCHEDULED'), COLORS['text_muted'])
                
                with st.expander(f" {shift['shift_date']} - {shift['shift_type']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Vrijwilliger ID:** {shift['volunteer_id']}")
                        st.write(f"**FanDorp ID:** {shift['fandorp_id']}")
                        st.write(f"**Type:** {shift['shift_type']}")
                    with col2:
                        st.write(f"**Start:** {shift.get('start_time', 'N/A')}")
                        st.write(f"**Einde:** {shift.get('end_time', 'N/A')}")
                        st.markdown(f"**Status:** <span style='color: {status_color};'>{shift.get('status', 'SCHEDULED')}</span>", unsafe_allow_html=True)
        else:
            st.info("Nog geen diensten gepland.")
    
    with tab2:
        st.markdown("###  Nieuwe Dienst Plannen")
        
        volunteers_df = get_data("fandorp_volunteers", "status = 'ACTIVE'")
        fandorpen_df = get_data("fandorpen")
        
        if volunteers_df.empty:
            st.warning("Geen actieve vrijwilligers beschikbaar")
            return
        
        if fandorpen_df.empty:
            st.warning("Geen FanDorpen beschikbaar")
            return
        
        with st.form("new_shift"):
            volunteer_options = {f"{row['first_name']} {row['last_name']}": row['volunteer_id'] 
                               for _, row in volunteers_df.iterrows()}
            fandorp_options = {f"{row['country_flag']} {row['country_name']}": row['fandorp_id'] 
                             for _, row in fandorpen_df.iterrows()}
            
            col1, col2 = st.columns(2)
            
            with col1:
                volunteer = st.selectbox("Vrijwilliger", list(volunteer_options.keys()))
                fandorp = st.selectbox("FanDorp", list(fandorp_options.keys()))
                shift_date = st.date_input("Datum", min_value=date.today())
            
            with col2:
                shift_type = st.selectbox("Type", [s[0] for s in SHIFT_TYPES])
                start_time = st.time_input("Starttijd")
                end_time = st.time_input("Eindtijd")
            
            notes = st.text_area("Notities")
            
            if st.form_submit_button(" Plannen", width="stretch"):
                shift_id = generate_uuid("SHF")
                
                success = run_query("""
                    INSERT INTO fandorp_shifts
                    (shift_id, volunteer_id, fandorp_id, shift_date, shift_type,
                     start_time, end_time, status, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 'SCHEDULED', ?, ?)
                """, (shift_id, volunteer_options[volunteer], fandorp_options[fandorp],
                      str(shift_date), shift_type, str(start_time), str(end_time),
                      notes, datetime.now().isoformat()))
                
                if success:
                    log_audit(username, "SHIFT_CREATED", shift_id)
                    st.success(" Dienst gepland!")
                    st.rerun()


# ============================================================================
# INCIDENTEN
# ============================================================================

def render_incidents(username: str):
    """Incident management."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(245, 101, 101, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(245, 101, 101, 0.3);'>
            <h3 style='color: {COLORS["error"]}; margin: 0;'> Incident Management</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Traceerbare afhandeling van problemen en incidenten
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([" Incidenten", " Nieuw Incident"])
    
    with tab1:
        df = get_data("fandorp_incidents")
        
        if not df.empty:
            # Stats
            open_count = len(df[df['status'] == 'OPEN'])
            resolved_count = len(df[df['status'] == 'RESOLVED'])
            escalated_count = len(df[df['status'] == 'ESCALATED'])
            
            col1, col2, col3 = st.columns(3)
            col1.metric(" Open", open_count)
            col2.metric(" Opgelost", resolved_count)
            col3.metric(" Geëscaleerd", escalated_count)
            
            st.markdown("---")
            
            # Filter
            status_filter = st.selectbox("Filter Status", ["Alle", "OPEN", "RESOLVED", "ESCALATED"])
            
            filtered_df = df if status_filter == "Alle" else df[df['status'] == status_filter]
            
            for _, inc in filtered_df.iterrows():
                severity_color = {
                    'LOW': COLORS['info'],
                    'MEDIUM': COLORS['warning'],
                    'HIGH': COLORS['error'],
                    'CRITICAL': '#FF0000'
                }.get(inc.get('severity', 'LOW'), COLORS['text_muted'])
                
                with st.expander(f" {inc['incident_type']} - {inc.get('severity', 'LOW')} - {inc.get('status', 'OPEN')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {inc['incident_type']}")
                        st.write(f"**Beschrijving:** {inc.get('description', 'N/A')}")
                        st.write(f"**Supporter Nationaliteit:** {inc.get('supporter_nationality', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**Ernst:** <span style='color: {severity_color};'>{inc.get('severity', 'LOW')}</span>", unsafe_allow_html=True)
                        st.write(f"**Status:** {inc.get('status', 'OPEN')}")
                        st.write(f"**Gemeld:** {inc.get('reported_at', 'N/A')[:16] if inc.get('reported_at') else 'N/A'}")
                    
                    if inc.get('resolution'):
                        st.success(f"**Oplossing:** {inc['resolution']}")
                    
                    # Resolution form
                    if inc.get('status') == 'OPEN':
                        st.markdown("---")
                        resolution = st.text_area("Oplossing", key=f"res_{inc['incident_id']}")
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if st.button(" Oplossen", key=f"resolve_{inc['incident_id']}"):
                                run_query("""
                                    UPDATE fandorp_incidents 
                                    SET status = 'RESOLVED', resolution = ?, resolved_at = ?
                                    WHERE incident_id = ?
                                """, (resolution, datetime.now().isoformat(), inc['incident_id']))
                                log_audit(username, "INCIDENT_RESOLVED", inc['incident_id'])
                                st.rerun()
                        
                        with col_b:
                            escalate_to = st.selectbox("Escaleren naar", 
                                                       ["Consulaat", "Politie", "Medisch", "VIP Support"],
                                                       key=f"esc_{inc['incident_id']}")
                            if st.button(" Escaleren", key=f"escalate_{inc['incident_id']}"):
                                run_query("""
                                    UPDATE fandorp_incidents 
                                    SET status = 'ESCALATED', escalated_to = ?
                                    WHERE incident_id = ?
                                """, (escalate_to, inc['incident_id']))
                                log_audit(username, "INCIDENT_ESCALATED", f"{inc['incident_id']} -> {escalate_to}")
                                st.rerun()
        else:
            st.success(" Geen incidenten gemeld!")
    
    with tab2:
        st.markdown("###  Nieuw Incident Melden")
        
        fandorpen_df = get_data("fandorpen")
        
        with st.form("new_incident"):
            col1, col2 = st.columns(2)
            
            with col1:
                if not fandorpen_df.empty:
                    fandorp_options = {f"{row['country_flag']} {row['country_name']}": row['fandorp_id'] 
                                     for _, row in fandorpen_df.iterrows()}
                    fandorp = st.selectbox("FanDorp", list(fandorp_options.keys()))
                else:
                    fandorp = None
                    st.warning("Geen FanDorpen beschikbaar")
                
                incident_type = st.selectbox("Type Incident", INCIDENT_TYPES)
                supporter_nat = st.selectbox("Supporter Nationaliteit", [c[0] for c in WK2030_COUNTRIES])
            
            with col2:
                severity = st.selectbox("Ernst", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                description = st.text_area("Beschrijving *")
            
            if st.form_submit_button(" Melden", width="stretch"):
                if not description:
                    st.error("Beschrijving is verplicht")
                elif not fandorp:
                    st.error("Selecteer een FanDorp")
                else:
                    incident_id = generate_uuid("INC")
                    
                    success = run_query("""
                        INSERT INTO fandorp_incidents
                        (incident_id, fandorp_id, incident_type, description,
                         supporter_nationality, severity, status, reported_at)
                        VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?)
                    """, (incident_id, fandorp_options[fandorp], incident_type,
                          description, supporter_nat, severity, datetime.now().isoformat()))
                    
                    if success:
                        log_audit(username, "INCIDENT_REPORTED", incident_id)
                        st.success(" Incident gemeld!")
                        st.rerun()


# ============================================================================
# TRAINING & BADGES
# ============================================================================

def render_training_badges(username: str):
    """Training modules en badge systeem."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(236, 201, 75, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(236, 201, 75, 0.3);'>
            <h3 style='color: {COLORS["warning"]}; margin: 0;'> Training & Certificering</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Online training modules en badge systeem voor vrijwilligers
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([" Training Modules", " Badges", " Voortgang"])
    
    with tab1:
        st.markdown("###  Beschikbare Training Modules")
        
        for mod_id, mod_name, mod_desc, mod_duration in TRAINING_MODULES:
            with st.expander(f" {mod_name} ({mod_duration} min)"):
                st.write(f"**Beschrijving:** {mod_desc}")
                st.write(f"**Duur:** {mod_duration} minuten")
                st.write(f"**Minimale score:** 70%")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f" Start Training", key=f"start_{mod_id}"):
                        st.info(f"Training '{mod_name}' wordt geladen...")
                        # Simuleer training completion
                        import random
                        score = random.randint(65, 100)
                        passed = score >= 70
                        
                        # Log training
                        training_id = generate_uuid("TRN")
                        run_query("""
                            INSERT INTO fandorp_training 
                            (training_id, volunteer_id, module_name, module_type, score, passed, completed_at)
                            VALUES (?, ?, ?, 'ONLINE', ?, ?, ?)
                        """, (training_id, username, mod_name, score, 1 if passed else 0, datetime.now().isoformat()))
                        
                        if passed:
                            st.success(f" Training voltooid! Score: {score}%")
                        else:
                            st.warning(f" Score: {score}% - Minimaal 70% nodig. Probeer opnieuw.")
                
                with col2:
                    st.write(f"**Module ID:** `{mod_id}`")
        
        # Training records
        st.markdown("---")
        st.markdown("###  Mijn Training Historie")
        
        training_df = get_data("fandorp_training")
        if not training_df.empty:
            # Filter op username (als volunteer_id)
            for _, tr in training_df.head(10).iterrows():
                status_icon = "" if tr.get('passed', 0) else ""
                st.write(f"{status_icon} **{tr['module_name']}** - Score: {tr.get('score', 0)}% - {tr.get('completed_at', '')[:10]}")
        else:
            st.info("Nog geen trainingen afgerond.")
    
    with tab2:
        st.markdown("###  Badge Systeem")
        st.markdown("""
            Verdien badges door trainingen te voltooien en goed te presteren als vrijwilliger.
            Badges worden automatisch toegekend wanneer je aan de criteria voldoet.
        """)
        
        # Display all available badges
        cols = st.columns(3)
        for idx, (badge_id, (emoji, name, criteria)) in enumerate(BADGES.items()):
            col_idx = idx % 3
            with cols[col_idx]:
                st.markdown(f"""
                    <div style='background: {COLORS["bg_card"]}; padding: 1rem; border-radius: 8px;
                                border: 1px solid rgba(212, 175, 55, 0.2); margin-bottom: 1rem; text-align: center;'>
                        <div style='font-size: 2rem;'>{emoji}</div>
                        <div style='color: {COLORS["gold"]}; font-weight: 600;'>{name}</div>
                        <div style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>{criteria}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Check earned badges for current user
        st.markdown("---")
        st.markdown("###  Mijn Badges")
        
        volunteers_df = get_data("fandorp_volunteers")
        if not volunteers_df.empty:
            # Find user's badges
            user_badges = volunteers_df[volunteers_df['email'].str.contains(username, na=False) | 
                                        volunteers_df['first_name'].str.contains(username, na=False)]
            if not user_badges.empty:
                badges_str = user_badges.iloc[0].get('badges', '')
                if badges_str:
                    st.success(f"**Verdiende badges:** {badges_str}")
                else:
                    st.info("Nog geen badges verdiend. Voltooi trainingen om badges te verdienen!")
            else:
                st.info("Registreer als vrijwilliger om badges te kunnen verdienen.")
        else:
            st.info("Geen vrijwilliger data beschikbaar.")
    
    with tab3:
        st.markdown("###  Training Voortgang")
        
        training_df = get_data("fandorp_training")
        volunteers_df = get_data("fandorp_volunteers")
        
        if not training_df.empty:
            # Overall stats
            total_trainings = len(training_df)
            passed_trainings = len(training_df[training_df['passed'] == 1])
            avg_score = training_df['score'].mean()
            
            col1, col2, col3 = st.columns(3)
            col1.metric(" Totaal Trainingen", total_trainings)
            col2.metric(" Geslaagd", f"{passed_trainings} ({100*passed_trainings/total_trainings:.0f}%)")
            col3.metric(" Gemiddelde Score", f"{avg_score:.1f}%")
            
            # Module breakdown
            st.markdown("---")
            st.markdown("####  Per Module")
            module_stats = training_df.groupby('module_name').agg({
                'score': ['mean', 'count'],
                'passed': 'sum'
            }).round(1)
            
            for mod in module_stats.index:
                avg = module_stats.loc[mod, ('score', 'mean')]
                count = module_stats.loc[mod, ('score', 'count')]
                passed = module_stats.loc[mod, ('passed', 'sum')]
                st.write(f"**{mod}:** {count} deelnemers, {avg:.1f}% gem. score, {passed} geslaagd")
        else:
            st.info("Nog geen training data beschikbaar.")


# ============================================================================
# QR CHECK-IN
# ============================================================================

def render_qr_checkin(username: str):
    """QR code check-in systeem voor vrijwilligers."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(72, 187, 120, 0.3);'>
            <h3 style='color: {COLORS["success"]}; margin: 0;'> QR Check-in Systeem</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Scan je QR code om in/uit te checken voor je shift
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([" Check-in/out", " Mijn QR Code", " Aanwezigheid"])
    
    with tab1:
        st.markdown("###  Handmatige Check-in")
        st.markdown("Voer je vrijwilliger ID of QR code in om in of uit te checken.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            qr_input = st.text_input("QR Code of Vrijwilliger ID", placeholder="VOL-... of QR code")
            
            if st.button(" Check IN", width="stretch", type="primary"):
                if qr_input:
                    # Find volunteer by ID or QR
                    volunteers_df = get_data("fandorp_volunteers")
                    match = volunteers_df[
                        (volunteers_df['volunteer_id'].str.contains(qr_input, na=False)) |
                        (volunteers_df['qr_code'] == qr_input.upper())
                    ]
                    
                    if not match.empty:
                        vol = match.iloc[0]
                        # Find today's shift
                        today = date.today().isoformat()
                        shifts_df = get_data("fandorp_shifts", f"volunteer_id = '{vol['volunteer_id']}' AND shift_date = '{today}'")
                        
                        if not shifts_df.empty:
                            shift = shifts_df.iloc[0]
                            run_query("""
                                UPDATE fandorp_shifts 
                                SET check_in = ?, status = 'IN_PROGRESS'
                                WHERE shift_id = ?
                            """, (datetime.now().isoformat(), shift['shift_id']))
                            
                            st.success(f"""
                                 **Check-in succesvol!**
                                
                                **Vrijwilliger:** {vol['first_name']} {vol['last_name']}
                                **Shift:** {shift['shift_type']}
                                **Tijd:** {datetime.now().strftime('%H:%M:%S')}
                            """)
                            log_audit(username, "VOLUNTEER_CHECKIN", vol['volunteer_id'])
                        else:
                            st.warning("Geen shift gevonden voor vandaag.")
                    else:
                        st.error("Vrijwilliger niet gevonden.")
                else:
                    st.warning("Voer een QR code of ID in.")
        
        with col2:
            qr_out = st.text_input("QR Code of ID (check-out)", placeholder="VOL-... of QR code", key="qr_out")
            
            if st.button(" Check OUT", width="stretch"):
                if qr_out:
                    volunteers_df = get_data("fandorp_volunteers")
                    match = volunteers_df[
                        (volunteers_df['volunteer_id'].str.contains(qr_out, na=False)) |
                        (volunteers_df['qr_code'] == qr_out.upper())
                    ]
                    
                    if not match.empty:
                        vol = match.iloc[0]
                        # Find active shift
                        shifts_df = get_data("fandorp_shifts", f"volunteer_id = '{vol['volunteer_id']}' AND status = 'IN_PROGRESS'")
                        
                        if not shifts_df.empty:
                            shift = shifts_df.iloc[0]
                            run_query("""
                                UPDATE fandorp_shifts 
                                SET check_out = ?, status = 'COMPLETED'
                                WHERE shift_id = ?
                            """, (datetime.now().isoformat(), shift['shift_id']))
                            
                            st.success(f"""
                                 **Check-out succesvol!**
                                
                                **Vrijwilliger:** {vol['first_name']} {vol['last_name']}
                                **Tijd:** {datetime.now().strftime('%H:%M:%S')}
                            """)
                            log_audit(username, "VOLUNTEER_CHECKOUT", vol['volunteer_id'])
                        else:
                            st.warning("Geen actieve shift gevonden.")
                    else:
                        st.error("Vrijwilliger niet gevonden.")
    
    with tab2:
        st.markdown("###  Mijn Persoonlijke QR Code")
        
        volunteers_df = get_data("fandorp_volunteers")
        if not volunteers_df.empty:
            # Show sample QR code display
            sample_vol = volunteers_df.iloc[0]
            qr_code = sample_vol.get('qr_code', 'N/A')
            
            st.markdown(f"""
                <div style='background: white; padding: 2rem; border-radius: 12px; 
                            text-align: center; max-width: 300px; margin: 0 auto;'>
                    <div style='background: #000; color: white; padding: 1rem; border-radius: 8px;
                                font-family: monospace; font-size: 1.2rem; letter-spacing: 2px;'>
                        {qr_code}
                    </div>
                    <p style='color: #666; margin-top: 1rem; font-size: 0.9rem;'>
                        {sample_vol['first_name']} {sample_vol['last_name']}<br>
                        {sample_vol.get('role', 'Vrijwilliger')}
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.info("""
                 **Tip:** Toon deze code aan de coördinator bij aankomst op je FanDorp.
                De code wordt gescand voor automatische check-in.
            """)
            
            # Generate actual QR code
            try:
                import qrcode
                from io import BytesIO
                
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(qr_code)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buf = BytesIO()
                img.save(buf, format='PNG')
                
                st.image(buf.getvalue(), caption="Scan deze QR code", width=200)
            except:
                st.info("QR code generatie niet beschikbaar. Gebruik de code hierboven.")
        else:
            st.warning("Registreer eerst als vrijwilliger om een QR code te krijgen.")
    
    with tab3:
        st.markdown("###  Aanwezigheid Overzicht")
        
        shifts_df = get_data("fandorp_shifts")
        
        if not shifts_df.empty:
            # Today's stats
            today = date.today().isoformat()
            today_shifts = shifts_df[shifts_df['shift_date'] == today]
            
            if not today_shifts.empty:
                checked_in = len(today_shifts[today_shifts['status'] == 'IN_PROGRESS'])
                completed = len(today_shifts[today_shifts['status'] == 'COMPLETED'])
                scheduled = len(today_shifts[today_shifts['status'] == 'SCHEDULED'])
                
                col1, col2, col3 = st.columns(3)
                col1.metric(" Gepland", scheduled)
                col2.metric(" Ingecheckt", checked_in)
                col3.metric(" Voltooid", completed)
            
            st.markdown("---")
            st.markdown("####  Recente Check-ins")
            
            recent = shifts_df[shifts_df['check_in'].notna()].tail(10)
            for _, shift in recent.iterrows():
                st.write(f" **{shift['shift_date']}** - {shift['shift_type']} - Check-in: {shift.get('check_in', 'N/A')[:16] if shift.get('check_in') else 'N/A'}")
        else:
            st.info("Nog geen shift data beschikbaar.")


# ============================================================================
# CHAT / COMMUNICATIE
# ============================================================================

def render_chat(username: str):
    """Real-time chat en communicatie systeem."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(66, 153, 225, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(66, 153, 225, 0.3);'>
            <h3 style='color: {COLORS["info"]}; margin: 0;'> Communicatie Centrum</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Chat met andere vrijwilligers en ontvang belangrijke updates
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([" Chat", " Alerts", " Broadcast"])
    
    with tab1:
        st.markdown("###  FanDorp Chat")
        
        # Select FanDorp
        fandorpen_df = get_data("fandorpen")
        if not fandorpen_df.empty:
            fandorp_options = {f"{row['country_flag']} FanDorp {row['country_name']}": row['fandorp_id'] 
                             for _, row in fandorpen_df.iterrows()}
            selected_fandorp = st.selectbox("Selecteer FanDorp", list(fandorp_options.keys()))
            fandorp_id = fandorp_options[selected_fandorp]
            
            # Display messages
            messages_df = get_data("fandorp_messages", f"fandorp_id = '{fandorp_id}'")
            
            st.markdown("---")
            
            # Chat container
            chat_container = st.container()
            
            with chat_container:
                if not messages_df.empty:
                    for _, msg in messages_df.tail(20).iterrows():
                        priority_color = {
                            'NORMAL': COLORS['text_secondary'],
                            'HIGH': COLORS['warning'],
                            'URGENT': COLORS['error']
                        }.get(msg.get('priority', 'NORMAL'), COLORS['text_secondary'])
                        
                        msg_type_icon = {
                            'CHAT': '',
                            'ALERT': '',
                            'UPDATE': ''
                        }.get(msg.get('message_type', 'CHAT'), '')
                        
                        st.markdown(f"""
                            <div style='background: {COLORS["bg_card"]}; padding: 0.75rem; border-radius: 8px;
                                        margin-bottom: 0.5rem; border-left: 3px solid {priority_color};'>
                                <div style='display: flex; justify-content: space-between;'>
                                    <span style='color: {COLORS["gold"]}; font-weight: 600;'>
                                        {msg_type_icon} {msg.get('sender_name', 'Anoniem')}
                                    </span>
                                    <span style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>
                                        {msg.get('created_at', '')[:16] if msg.get('created_at') else ''}
                                    </span>
                                </div>
                                <p style='color: {COLORS["text_primary"]}; margin: 0.5rem 0 0 0;'>
                                    {msg.get('content', '')}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Nog geen berichten in deze chat.")
            
            # Message input
            st.markdown("---")
            with st.form("send_message", clear_on_submit=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    new_message = st.text_input("Typ een bericht...", placeholder="Je bericht hier")
                
                with col2:
                    priority = st.selectbox("", ["NORMAL", "HIGH", "URGENT"], label_visibility="collapsed")
                
                if st.form_submit_button(" Verstuur", width="stretch"):
                    if new_message:
                        message_id = generate_uuid("MSG")
                        run_query("""
                            INSERT INTO fandorp_messages 
                            (message_id, fandorp_id, sender_id, sender_name, message_type, content, priority, created_at)
                            VALUES (?, ?, ?, ?, 'CHAT', ?, ?, ?)
                        """, (message_id, fandorp_id, username, username, new_message, priority, datetime.now().isoformat()))
                        
                        log_audit(username, "MESSAGE_SENT", message_id)
                        st.rerun()
        else:
            st.warning("Geen FanDorpen beschikbaar voor chat.")
    
    with tab2:
        st.markdown("###  Belangrijke Alerts")
        
        messages_df = get_data("fandorp_messages", "message_type = 'ALERT' OR priority = 'URGENT'")
        
        if not messages_df.empty:
            for _, alert in messages_df.tail(10).iterrows():
                severity_color = COLORS['error'] if alert.get('priority') == 'URGENT' else COLORS['warning']
                
                st.markdown(f"""
                    <div style='background: linear-gradient(135deg, {severity_color}22 0%, {severity_color}11 100%);
                                padding: 1rem; border-radius: 8px; margin-bottom: 0.5rem;
                                border: 1px solid {severity_color}44;'>
                        <div style='color: {severity_color}; font-weight: 600;'>
                             {alert.get('priority', 'ALERT')}
                        </div>
                        <p style='color: {COLORS["text_primary"]}; margin: 0.5rem 0;'>
                            {alert.get('content', '')}
                        </p>
                        <div style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>
                            {alert.get('sender_name', 'System')} • {alert.get('created_at', '')[:16] if alert.get('created_at') else ''}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.success(" Geen urgente alerts op dit moment.")
    
    with tab3:
        st.markdown("###  Broadcast Bericht")
        st.markdown("Stuur een bericht naar alle vrijwilligers in een FanDorp.")
        
        if check_permission(["SuperAdmin", "Official", "COORDINATOR"], silent=True):
            fandorpen_df = get_data("fandorpen")
            
            if not fandorpen_df.empty:
                with st.form("broadcast"):
                    fandorp_options = {f"{row['country_flag']} {row['country_name']}": row['fandorp_id'] 
                                     for _, row in fandorpen_df.iterrows()}
                    fandorp_options[" ALLE FANDORPEN"] = "ALL"
                    
                    target = st.selectbox("Doelgroep", list(fandorp_options.keys()))
                    message_type = st.selectbox("Type", ["UPDATE", "ALERT"])
                    priority = st.selectbox("Prioriteit", ["NORMAL", "HIGH", "URGENT"])
                    content = st.text_area("Bericht *", placeholder="Typ je broadcast bericht...")
                    
                    if st.form_submit_button(" Broadcast Versturen", width="stretch"):
                        if content:
                            fandorp_id = fandorp_options[target]
                            
                            if fandorp_id == "ALL":
                                # Send to all fandorpen
                                for _, fp in fandorpen_df.iterrows():
                                    msg_id = generate_uuid("MSG")
                                    run_query("""
                                        INSERT INTO fandorp_messages 
                                        (message_id, fandorp_id, sender_id, sender_name, message_type, content, priority, created_at)
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                    """, (msg_id, fp['fandorp_id'], username, f" {username}", message_type, content, priority, datetime.now().isoformat()))
                            else:
                                msg_id = generate_uuid("MSG")
                                run_query("""
                                    INSERT INTO fandorp_messages 
                                    (message_id, fandorp_id, sender_id, sender_name, message_type, content, priority, created_at)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (msg_id, fandorp_id, username, f" {username}", message_type, content, priority, datetime.now().isoformat()))
                            
                            log_audit(username, "BROADCAST_SENT", f"{target}: {content[:50]}...")
                            st.success(" Broadcast verzonden!")
                        else:
                            st.error("Voer een bericht in.")
        else:
            st.warning(" Alleen coördinatoren en admins kunnen broadcasts versturen.")


# ============================================================================
# DASHBOARD
# ============================================================================

def render_dashboard(username: str):
    """FanDorpen analytics dashboard."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(212, 175, 55, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(139, 92, 246, 0.3);'>
            <h3 style='color: {COLORS["purple"]}; margin: 0;'> FanDorpen Dashboard</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Real-time overzicht van alle FanDorpen activiteiten
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get all data
    fandorpen_df = get_data("fandorpen")
    volunteers_df = get_data("fandorp_volunteers")
    shifts_df = get_data("fandorp_shifts")
    incidents_df = get_data("fandorp_incidents")
    services_df = get_data("fandorp_services")
    
    # Overview cards
    st.markdown("###  Overzicht per FanDorp")
    
    if not fandorpen_df.empty:
        cols = st.columns(min(3, len(fandorpen_df)))
        
        for idx, (_, fp) in enumerate(fandorpen_df.iterrows()):
            col_idx = idx % 3
            
            # Count volunteers for this fandorp
            vol_count = len(volunteers_df[volunteers_df['fandorp_id'] == fp['fandorp_id']]) if not volunteers_df.empty else 0
            active_vol = len(volunteers_df[(volunteers_df['fandorp_id'] == fp['fandorp_id']) & (volunteers_df['status'] == 'ACTIVE')]) if not volunteers_df.empty else 0
            
            with cols[col_idx]:
                st.markdown(f"""
                    <div style='background: {COLORS["bg_card"]}; padding: 1rem; border-radius: 8px;
                                border: 1px solid rgba(212, 175, 55, 0.2); margin-bottom: 1rem;'>
                        <h4 style='color: {COLORS["gold"]}; margin: 0;'>
                            {fp.get('country_flag', '')} FanDorp {fp['country_name']}
                        </h4>
                        <p style='color: {COLORS["text_muted"]}; font-size: 0.9rem; margin: 0.25rem 0;'>
                             {fp['location']}
                        </p>
                        <hr style='border-color: rgba(212,175,55,0.2); margin: 0.5rem 0;'>
                        <p style='color: {COLORS["text_secondary"]}; margin: 0.25rem 0;'>
                             Vrijwilligers: <strong>{vol_count}</strong> ({active_vol} actief)
                        </p>
                        <p style='color: {COLORS["text_secondary"]}; margin: 0.25rem 0;'>
                             {fp.get('languages', 'N/A')}
                        </p>
                        <p style='color: {COLORS["text_secondary"]}; margin: 0.25rem 0;'>
                             Capaciteit: {fp.get('capacity', 500)}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Statistics
    st.markdown("---")
    st.markdown("###  Statistieken")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Volunteers by nationality
        if not volunteers_df.empty:
            st.markdown("####  Vrijwilligers per Tweede Nationaliteit")
            nat_counts = volunteers_df['nationality_2'].value_counts().head(10)
            st.bar_chart(nat_counts)
    
    with col2:
        # Incidents by type
        if not incidents_df.empty:
            st.markdown("####  Incidenten per Type")
            inc_counts = incidents_df['incident_type'].value_counts()
            st.bar_chart(inc_counts)
    
    # WK2030 Countdown
    st.markdown("---")
    wk_date = datetime(2030, 6, 13)
    days_left = (wk_date - datetime.now()).days
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #D4AF37 0%, #9B7B2E 100%);
                    padding: 2rem; border-radius: 12px; text-align: center;'>
            <span style='font-size: 1rem; color: #1a1a1a;'> WK 2030 MOROCCO - FANDORPEN READY</span>
            <div style='font-size: 3rem; font-weight: 700; color: #1a1a1a; font-family: Rajdhani, sans-serif;'>
                {days_left:,} DAGEN
            </div>
            <span style='font-size: 0.9rem; color: #1a1a1a;'>
                {len(fandorpen_df)} FanDorpen | {len(volunteers_df)} Vrijwilligers Geregistreerd
            </span>
        </div>
    """, unsafe_allow_html=True)
