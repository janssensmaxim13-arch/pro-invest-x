# ============================================================================
# HAYAT INITIATIVE MODULE (DOSSIER 5)
# "Hayat" = Leven in het Arabisch
# 
# Complete module voor mentale gezondheid en welzijn van atleten:
# - Psycholoog Dashboard
# - Anonieme Panic Button voor atleten
# - Burnout & Stress Monitoring
# - Revalidatie Tracking
# - Crisis Interventie
# - Confidentiële sessie logging
# ============================================================================

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Optional
import hashlib

from config import DB_FILE, Options, Messages, BLOCKCHAIN_SECRET
from database.connection import get_data, run_query, get_connection, count_records
from utils.helpers import generate_uuid, get_identity_names_map
from auth.security import log_audit, requires_role, check_permission, ROLE_GROUPS
from ui.components import metric_row, page_header


# ============================================================================
# DATABASE UITBREIDING - HAYAT SPECIFIEKE TABELLEN
# ============================================================================

def init_hayat_tables():
    """Initialiseer Hayat-specifieke tabellen."""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Crisis/Panic Button meldingen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_crisis_alerts (
            alert_id TEXT PRIMARY KEY,
            talent_id TEXT,
            
            -- Alert info
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'MEDIUM',
            is_anonymous INTEGER DEFAULT 0,
            anonymous_code TEXT,
            
            -- Beschrijving
            description TEXT,
            current_feelings TEXT,
            
            -- Locatie (optioneel)
            location TEXT,
            
            -- Response
            responder_id TEXT,
            responder_name TEXT,
            response_time TEXT,
            response_notes TEXT,
            
            -- Status
            status TEXT DEFAULT 'OPEN',
            resolved_at TEXT,
            resolution_notes TEXT,
            
            -- Follow-up
            follow_up_required INTEGER DEFAULT 0,
            follow_up_date TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # Therapie/Counseling sessies
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_sessions (
            session_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Sessie info
            psychologist_id TEXT,
            psychologist_name TEXT,
            session_date TEXT NOT NULL,
            session_type TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            
            -- Locatie
            location TEXT,
            is_remote INTEGER DEFAULT 0,
            
            -- Inhoud (geëncrypteerd/gehashed voor privacy)
            session_notes_hash TEXT,
            
            -- Scores na sessie
            mood_score INTEGER,
            anxiety_score INTEGER,
            progress_score INTEGER,
            
            -- Medicatie (indien relevant)
            medication_discussed INTEGER DEFAULT 0,
            medication_notes TEXT,
            
            -- Follow-up
            next_session_date TEXT,
            homework_assigned TEXT,
            
            -- Status
            status TEXT DEFAULT 'COMPLETED',
            no_show INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # Welzijn tracking (dagelijkse check-ins)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_wellbeing_logs (
            log_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Datum
            log_date TEXT NOT NULL,
            
            -- Scores (1-10)
            mood_score INTEGER,
            energy_score INTEGER,
            sleep_quality INTEGER,
            stress_level INTEGER,
            motivation_score INTEGER,
            
            -- Physical
            pain_level INTEGER DEFAULT 0,
            pain_location TEXT,
            
            -- Notities
            notes TEXT,
            
            -- Flags
            needs_attention INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # Revalidatie tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_rehabilitation (
            rehab_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Blessure/reden
            injury_type TEXT,
            injury_date TEXT,
            expected_recovery_date TEXT,
            
            -- Status
            rehab_phase TEXT DEFAULT 'INITIAL',
            progress_percentage INTEGER DEFAULT 0,
            
            -- Team
            physiotherapist TEXT,
            psychologist TEXT,
            medical_doctor TEXT,
            
            -- Mentale aspect
            mental_readiness_score INTEGER,
            fear_of_reinjury_score INTEGER,
            confidence_score INTEGER,
            
            -- Notities
            physical_notes TEXT,
            mental_notes TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            completed_at TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # Indexes - met try/except voor als kolommen niet bestaan
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crisis_talent ON hayat_crisis_alerts(talent_id)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_crisis_status ON hayat_crisis_alerts(status)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_session_talent ON hayat_sessions(talent_id)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_wellbeing_talent ON hayat_wellbeing_logs(talent_id)")
    except:
        pass
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rehab_talent ON hayat_rehabilitation(talent_id)")
    except:
        pass
    
    conn.commit()
    conn.close()


# Voeg tabellen toe aan ALLOWED_TABLES in config (runtime)
def register_hayat_tables():
    """Registreer Hayat tabellen in whitelist."""
    from config import ALLOWED_TABLES
    hayat_tables = [
        'hayat_crisis_alerts',
        'hayat_sessions', 
        'hayat_wellbeing_logs',
        'hayat_rehabilitation'
    ]
    for table in hayat_tables:
        if table not in ALLOWED_TABLES:
            ALLOWED_TABLES.append(table)


# ============================================================================
# HELPER FUNCTIES
# ============================================================================

def get_talents_for_hayat() -> Dict[str, str]:
    """Haal talenten op voor Hayat module."""
    df = get_data("ntsp_talent_profiles")
    if df.empty:
        return {}
    return {
        row['talent_id']: f"{row['first_name']} {row['last_name']}" 
        for _, row in df.iterrows()
    }


def generate_anonymous_code() -> str:
    """Genereer anonieme code voor panic button."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


def hash_session_notes(notes: str) -> str:
    """Hash sessie notities voor privacy (alleen hash wordt opgeslagen)."""
    if not notes:
        return ""
    return hashlib.sha256((notes + BLOCKCHAIN_SECRET).encode()).hexdigest()[:32]


def calculate_risk_level(stress: int, mood: int, sleep: int, burnout_risk: str) -> str:
    """Bereken risico niveau op basis van scores."""
    avg_score = (stress + (10 - mood) + (10 - sleep)) / 3
    
    if burnout_risk == "HIGH" or avg_score >= 7:
        return "HIGH"
    elif burnout_risk == "MEDIUM" or avg_score >= 5:
        return "MEDIUM"
    return "LOW"


# ============================================================================
# MAIN RENDER FUNCTIE
# ============================================================================

def render(username: str):
    """Render de Hayat Initiative module."""
    
    # Initialiseer tabellen
    init_hayat_tables()
    register_hayat_tables()
    
    page_header(
        " Hayat Initiative - حياة",
        "Dossier 5 | Mentale Gezondheid | Welzijn | Crisis Support | Revalidatie"
    )
    
    # Info banner
    st.info("""
    **Hayat (حياة)** betekent "Leven" in het Arabisch. Deze module ondersteunt het 
    mentale welzijn van onze atleten met 24/7 crisis support, professionele begeleiding, 
    en preventieve monitoring.
    """)
    
    tabs = st.tabs([
        "🆘 Crisis Center",
        " Welzijn Dashboard",
        " Sessies",
        " Revalidatie",
        " Analytics",
        " Beheer"
    ])
    
    with tabs[0]:
        render_crisis_center(username)
    
    with tabs[1]:
        render_wellbeing_dashboard(username)
    
    with tabs[2]:
        render_sessions(username)
    
    with tabs[3]:
        render_rehabilitation(username)
    
    with tabs[4]:
        render_hayat_analytics()
    
    with tabs[5]:
        render_hayat_admin(username)


# ============================================================================
# TAB 1: CRISIS CENTER (PANIC BUTTON)
# ============================================================================

def render_crisis_center(username: str):
    """Render Crisis Center met Panic Button."""
    
    st.subheader("🆘 Crisis Center")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("###  Hulp Nodig? (Panic Button)")
        
        st.warning("""
        **Voel je je niet goed?** Dit formulier is 100% vertrouwelijk.
        Je kunt ook anoniem hulp vragen.
        """)
        
        with st.form("panic_form"):
            is_anonymous = st.checkbox(" Ik wil anoniem blijven", value=False)
            
            if not is_anonymous:
                talents = get_talents_for_hayat()
                if talents:
                    talent_id = st.selectbox(
                        "Wie ben je?",
                        list(talents.keys()),
                        format_func=lambda x: talents.get(x, x)
                    )
                else:
                    talent_id = None
                    st.info("Selecteer 'anoniem' of registreer eerst in NTSP.")
            else:
                talent_id = None
            
            alert_type = st.selectbox(
                "Waar gaat het over?",
                [
                    "Ik voel me overweldigd/gestrest",
                    "Ik heb angst of paniek",
                    "Ik voel me depressief",
                    "Ik heb problemen met slapen",
                    "Ik heb conflicten (team/coach)",
                    "Ik heb heimwee",
                    "Ik wil met iemand praten",
                    "Anders/Meerdere dingen"
                ]
            )
            
            severity = st.select_slider(
                "Hoe urgent voelt het?",
                options=["Kan wachten", "Graag snel", "Dringend", "CRISIS"],
                value="Graag snel"
            )
            
            current_feelings = st.text_area(
                "Hoe voel je je nu? (optioneel)",
                placeholder="Beschrijf wat je voelt... Dit blijft vertrouwelijk.",
                height=100
            )
            
            location = st.text_input(
                "Waar ben je nu? (optioneel)",
                placeholder="Bijv: Academy, thuis, hotel..."
            )
            
            submitted = st.form_submit_button(
                "🆘 VERSTUUR HULPVRAAG",
                width='stretch',
                type="primary"
            )
            
            if submitted:
                alert_id = generate_uuid("CRS")
                anon_code = generate_anonymous_code() if is_anonymous else None
                
                # Map severity
                severity_map = {
                    "Kan wachten": "LOW",
                    "Graag snel": "MEDIUM", 
                    "Dringend": "HIGH",
                    "CRISIS": "CRITICAL"
                }
                
                success = run_query("""
                    INSERT INTO hayat_crisis_alerts (
                        alert_id, talent_id, alert_type, severity, is_anonymous,
                        anonymous_code, description, current_feelings, location,
                        status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert_id, talent_id, alert_type, severity_map.get(severity, "MEDIUM"),
                    1 if is_anonymous else 0, anon_code, alert_type, 
                    current_feelings or None, location or None,
                    "OPEN", datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" **Je hulpvraag is ontvangen!**")
                    
                    if is_anonymous:
                        st.info(f" Je anonieme code is: **{anon_code}**\n\nBewaar deze code om je status te checken.")
                    
                    st.markdown("""
                    **Wat nu?**
                    - Een psycholoog neemt zo snel mogelijk contact op
                    - Bij CRISIS word je binnen 1 uur gebeld
                    - Je bent niet alleen 
                    """)
                    
                    log_audit(username, "CRISIS_ALERT", "Hayat", 
                             details=f"Alert: {alert_id}, Severity: {severity}")
    
    with col2:
        st.markdown("###  Open Alerts")
        
        # Alleen voor staff
        if check_permission(["SuperAdmin", "Psychologist", "Medical Staff"], silent=True):
            df_alerts = get_data("hayat_crisis_alerts")
            
            if not df_alerts.empty:
                open_alerts = df_alerts[df_alerts['status'] == 'OPEN']
                
                critical = len(open_alerts[open_alerts['severity'] == 'CRITICAL'])
                high = len(open_alerts[open_alerts['severity'] == 'HIGH'])
                medium = len(open_alerts[open_alerts['severity'] == 'MEDIUM'])
                
                metric_row([
                    (" CRITICAL", critical),
                    (" HIGH", high),
                    (" MEDIUM", medium),
                    (" Totaal Open", len(open_alerts)),
                ])
                
                if not open_alerts.empty:
                    for _, alert in open_alerts.iterrows():
                        severity_emoji = {
                            "CRITICAL": "",
                            "HIGH": "",
                            "MEDIUM": "",
                            "LOW": ""
                        }.get(alert['severity'], "")
                        
                        with st.expander(f"{severity_emoji} {alert['alert_type'][:30]}... ({alert['created_at'][:10]})"):
                            st.write(f"**ID:** {alert['alert_id']}")
                            st.write(f"**Type:** {alert['alert_type']}")
                            st.write(f"**Severity:** {alert['severity']}")
                            st.write(f"**Anoniem:** {'Ja' if alert['is_anonymous'] else 'Nee'}")
                            
                            if alert['current_feelings']:
                                st.write(f"**Beschrijving:** {alert['current_feelings']}")
                            
                            if st.button(f" Oppakken", key=f"take_{alert['alert_id']}"):
                                run_query("""
                                    UPDATE hayat_crisis_alerts 
                                    SET status = 'IN_PROGRESS', responder_name = ?, response_time = ?
                                    WHERE alert_id = ?
                                """, (username, datetime.now().isoformat(), alert['alert_id']))
                                st.success("Alert opgepakt!")
                                st.rerun()
                else:
                    st.success(" Geen open alerts!")
            else:
                st.info("Nog geen alerts.")
        else:
            st.info(" Alert overzicht alleen voor Hayat team.")
            
            # Check status met anonieme code
            st.markdown("###  Check je status")
            check_code = st.text_input("Voer je anonieme code in:")
            
            if check_code and st.button("Check Status"):
                df = get_data("hayat_crisis_alerts")
                result = df[df['anonymous_code'] == check_code]
                
                if not result.empty:
                    alert = result.iloc[0]
                    st.write(f"**Status:** {alert['status']}")
                    if alert['response_notes']:
                        st.write(f"**Bericht:** {alert['response_notes']}")
                else:
                    st.error("Code niet gevonden.")


# ============================================================================
# TAB 2: WELZIJN DASHBOARD
# ============================================================================

def render_wellbeing_dashboard(username: str):
    """Render Welzijn Dashboard met check-ins."""
    
    st.subheader(" Welzijn Dashboard")
    
    talents = get_talents_for_hayat()
    
    if not talents:
        st.warning(t("warning_no_talents"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("###  Dagelijkse Check-in")
        
        with st.form("checkin_form"):
            talent_id = st.selectbox(
                "Talent",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
            
            log_date = st.date_input("Datum", value=date.today())
            
            st.markdown("**Hoe voel je je vandaag? (1-10)**")
            
            mood = st.slider(" Stemming", 1, 10, 5, help="1=Zeer slecht, 10=Uitstekend")
            energy = st.slider(" Energie", 1, 10, 5)
            sleep = st.slider(" Slaapkwaliteit", 1, 10, 5)
            stress = st.slider(" Stress niveau", 1, 10, 5, help="1=Geen stress, 10=Extreme stress")
            motivation = st.slider(" Motivatie", 1, 10, 5)
            
            pain = st.slider("🩹 Pijn niveau", 0, 10, 0)
            pain_location = st.text_input("Pijn locatie", placeholder="Bijv: knie, rug...")
            
            notes = st.text_area("Notities", placeholder="Hoe was je dag?")
            
            if st.form_submit_button(" OPSLAAN", width='stretch'):
                log_id = generate_uuid("WBL")
                needs_attention = 1 if (mood <= 3 or stress >= 8 or sleep <= 3) else 0
                
                success = run_query("""
                    INSERT INTO hayat_wellbeing_logs (
                        log_id, talent_id, log_date, mood_score, energy_score,
                        sleep_quality, stress_level, motivation_score,
                        pain_level, pain_location, notes, needs_attention, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log_id, talent_id, str(log_date), mood, energy, sleep, stress,
                    motivation, pain, pain_location or None, notes or None,
                    needs_attention, datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" Check-in opgeslagen!")
                    
                    if needs_attention:
                        st.warning(" Je scores wijzen op mogelijke problemen. Overweeg contact met een psycholoog.")
                    
                    log_audit(username, "WELLBEING_CHECKIN", "Hayat")
    
    with col2:
        st.markdown("###  Welzijn Overzicht")
        
        # Filter op talent
        selected_talent = st.selectbox(
            "Bekijk talent",
            list(talents.keys()),
            format_func=lambda x: talents.get(x, x),
            key="view_talent"
        )
        
        df = get_data("hayat_wellbeing_logs")
        
        if not df.empty:
            talent_data = df[df['talent_id'] == selected_talent]
            
            if not talent_data.empty:
                # Laatste 7 dagen
                recent = talent_data.head(7)
                
                # Gemiddelden
                avg_mood = recent['mood_score'].mean()
                avg_stress = recent['stress_level'].mean()
                avg_sleep = recent['sleep_quality'].mean()
                
                metric_row([
                    (" Gem. Stemming", f"{avg_mood:.1f}/10"),
                    (" Gem. Stress", f"{avg_stress:.1f}/10"),
                    (" Gem. Slaap", f"{avg_sleep:.1f}/10"),
                ])
                
                # Trend chart
                st.markdown("**Trend (laatste logs)**")
                chart_data = recent[['log_date', 'mood_score', 'stress_level', 'sleep_quality']].copy()
                chart_data = chart_data.set_index('log_date')
                st.line_chart(chart_data)
                
                # Alerts
                needs_attention = talent_data[talent_data['needs_attention'] == 1]
                if not needs_attention.empty:
                    st.warning(f" {len(needs_attention)} check-ins met zorgwekkende scores")
            else:
                st.info("Nog geen check-ins voor dit talent.")
        else:
            st.info("Nog geen welzijn data.")


# ============================================================================
# TAB 3: SESSIES (THERAPIE/COUNSELING)
# ============================================================================

def render_sessions(username: str):
    """Render therapie sessies."""
    
    st.subheader(" Therapie & Counseling Sessies")
    
    talents = get_talents_for_hayat()
    
    if not talents:
        st.warning(t("warning_no_talents"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("###  Nieuwe Sessie Loggen")
        
        with st.form("session_form"):
            talent_id = st.selectbox(
                "Talent *",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
            
            session_date = st.date_input("Datum *", value=date.today())
            
            session_type = st.selectbox(
                "Type Sessie *",
                [
                    "Initial Assessment",
                    "Regular Session",
                    "Follow-up",
                    "Crisis Intervention",
                    "Group Session",
                    "Family Session"
                ]
            )
            
            duration = st.number_input("Duur (minuten)", 15, 180, 60)
            is_remote = st.checkbox("Online/Remote sessie")
            
            st.markdown("**Scores na sessie (1-10)**")
            mood_score = st.slider("Stemming na sessie", 1, 10, 5)
            anxiety_score = st.slider("Angst niveau", 1, 10, 5, help="1=Geen, 10=Extreem")
            progress_score = st.slider("Voortgang", 1, 10, 5)
            
            next_session = st.date_input("Volgende sessie", value=None)
            homework = st.text_area("Huiswerk/Opdrachten", placeholder="Wat moet de atleet doen voor de volgende sessie?")
            
            # Notities worden gehashed voor privacy
            notes = st.text_area("Sessie Notities (vertrouwelijk)", placeholder="Deze worden geëncrypteerd opgeslagen...")
            
            no_show = st.checkbox("No-show (niet verschenen)")
            
            if st.form_submit_button(" SESSIE LOGGEN", width='stretch'):
                session_id = generate_uuid("SES")
                
                success = run_query("""
                    INSERT INTO hayat_sessions (
                        session_id, talent_id, psychologist_name, session_date,
                        session_type, duration_minutes, is_remote, session_notes_hash,
                        mood_score, anxiety_score, progress_score,
                        next_session_date, homework_assigned, status, no_show, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_id, talent_id, username, str(session_date),
                    session_type, duration, 1 if is_remote else 0,
                    hash_session_notes(notes) if notes else None,
                    mood_score, anxiety_score, progress_score,
                    str(next_session) if next_session else None,
                    homework or None,
                    "NO_SHOW" if no_show else "COMPLETED",
                    1 if no_show else 0,
                    datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" Sessie gelogd!")
                    log_audit(username, "SESSION_LOGGED", "Hayat", 
                             details=f"Talent: {talent_id}, Type: {session_type}")
    
    with col2:
        st.markdown("###  Sessie Geschiedenis")
        
        df = get_data("hayat_sessions")
        
        if not df.empty:
            # Filter
            filter_talent = st.selectbox(
                "Filter op talent",
                ["All"] + list(talents.keys()),
                format_func=lambda x: "Alle talenten" if x == "All" else talents.get(x, x),
                key="filter_session"
            )
            
            filtered = df if filter_talent == "All" else df[df['talent_id'] == filter_talent]
            
            if not filtered.empty:
                total_sessions = len(filtered)
                no_shows = len(filtered[filtered['no_show'] == 1])
                avg_progress = filtered['progress_score'].mean()
                
                metric_row([
                    (" Totaal Sessies", total_sessions),
                    (" No-shows", no_shows),
                    (" Gem. Voortgang", f"{avg_progress:.1f}/10"),
                ])
                
                # Display
                display_cols = ['session_date', 'talent_id', 'session_type', 'mood_score', 'progress_score', 'status']
                display_cols = [c for c in display_cols if c in filtered.columns]
                
                st.dataframe(filtered[display_cols].head(20), width='stretch', hide_index=True)
            else:
                st.info("Geen sessies gevonden.")
        else:
            st.info("Nog geen sessies gelogd.")


# ============================================================================
# TAB 4: REVALIDATIE
# ============================================================================

def render_rehabilitation(username: str):
    """Render revalidatie tracking."""
    
    st.subheader(" Revalidatie Tracking")
    
    st.info("""
    **Mentale Revalidatie:** Naast fysiek herstel is mentale begeleiding cruciaal.
    Fear of reinjury, verlies van identiteit, en depressie komen vaak voor bij geblesseerde atleten.
    """)
    
    talents = get_talents_for_hayat()
    
    if not talents:
        st.warning(t("warning_no_talents"))
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("###  Nieuwe Revalidatie")
        
        with st.form("rehab_form"):
            talent_id = st.selectbox(
                "Talent *",
                list(talents.keys()),
                format_func=lambda x: talents.get(x, x)
            )
            
            injury_type = st.text_input("Type Blessure *", placeholder="Bijv: Kruisband, Hamstring")
            injury_date = st.date_input("Blessure Datum")
            expected_recovery = st.date_input("Verwacht Herstel", value=None)
            
            rehab_phase = st.selectbox(
                "Fase",
                ["INITIAL", "EARLY_REHAB", "MID_REHAB", "LATE_REHAB", "RETURN_TO_PLAY", "COMPLETED"]
            )
            
            progress = st.slider("Voortgang %", 0, 100, 0)
            
            st.markdown("**Mentale Scores (1-10)**")
            mental_readiness = st.slider("Mentale Gereedheid", 1, 10, 5)
            fear_reinjury = st.slider("Angst voor Herblessure", 1, 10, 5, help="1=Geen angst, 10=Extreme angst")
            confidence = st.slider("Zelfvertrouwen", 1, 10, 5)
            
            physiotherapist = st.text_input("Fysiotherapeut")
            psychologist = st.text_input("Psycholoog")
            
            mental_notes = st.text_area("Mentale Observaties", placeholder="Hoe gaat de atleet mentaal om met de blessure?")
            
            if st.form_submit_button(" OPSLAAN", width='stretch'):
                rehab_id = generate_uuid("RHB")
                
                success = run_query("""
                    INSERT INTO hayat_rehabilitation (
                        rehab_id, talent_id, injury_type, injury_date, expected_recovery_date,
                        rehab_phase, progress_percentage, physiotherapist, psychologist,
                        mental_readiness_score, fear_of_reinjury_score, confidence_score,
                        mental_notes, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    rehab_id, talent_id, injury_type, str(injury_date),
                    str(expected_recovery) if expected_recovery else None,
                    rehab_phase, progress, physiotherapist or None, psychologist or None,
                    mental_readiness, fear_reinjury, confidence,
                    mental_notes or None, "ACTIVE",
                    datetime.now().isoformat()
                ))
                
                if success:
                    st.success(" Revalidatie geregistreerd!")
                    log_audit(username, "REHAB_CREATED", "Hayat")
    
    with col2:
        st.markdown("###  Actieve Revalidaties")
        
        df = get_data("hayat_rehabilitation")
        
        if not df.empty:
            active = df[df['status'] == 'ACTIVE']
            
            if not active.empty:
                for _, rehab in active.iterrows():
                    talent_name = talents.get(rehab['talent_id'], rehab['talent_id'])
                    
                    with st.expander(f" {talent_name} - {rehab['injury_type']} ({rehab['progress_percentage']}%)"):
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            st.write(f"**Fase:** {rehab['rehab_phase']}")
                            st.write(f"**Verwacht herstel:** {rehab.get('expected_recovery_date', '-')}")
                            st.progress(rehab['progress_percentage'] / 100)
                        
                        with col_b:
                            st.write(f"**Mentale Gereedheid:** {rehab['mental_readiness_score']}/10")
                            st.write(f"**Angst Herblessure:** {rehab['fear_of_reinjury_score']}/10")
                            st.write(f"**Zelfvertrouwen:** {rehab['confidence_score']}/10")
                        
                        if rehab['mental_notes']:
                            st.write(f"**Notities:** {rehab['mental_notes']}")
            else:
                st.success(" Geen actieve revalidaties!")
        else:
            st.info("Nog geen revalidaties geregistreerd.")


# ============================================================================
# TAB 5: ANALYTICS
# ============================================================================

def render_hayat_analytics():
    """Render Hayat analytics."""
    
    st.subheader(" Hayat Analytics")
    
    df_alerts = get_data("hayat_crisis_alerts")
    df_sessions = get_data("hayat_sessions")
    df_wellbeing = get_data("hayat_wellbeing_logs")
    df_rehab = get_data("hayat_rehabilitation")
    
    # Metrics
    total_alerts = len(df_alerts) if not df_alerts.empty else 0
    open_alerts = len(df_alerts[df_alerts['status'] == 'OPEN']) if not df_alerts.empty else 0
    total_sessions = len(df_sessions) if not df_sessions.empty else 0
    total_checkins = len(df_wellbeing) if not df_wellbeing.empty else 0
    active_rehab = len(df_rehab[df_rehab['status'] == 'ACTIVE']) if not df_rehab.empty else 0
    
    metric_row([
        ("🆘 Crisis Alerts", total_alerts),
        (" Open Alerts", open_alerts),
        (" Sessies", total_sessions),
        (" Check-ins", total_checkins),
        (" Actieve Revalidaties", active_rehab),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### 🆘 Alerts per Severity")
        if not df_alerts.empty:
            st.bar_chart(df_alerts['severity'].value_counts())
        else:
            st.info("Geen data.")
    
    with col2:
        st.write("####  Sessies per Type")
        if not df_sessions.empty:
            st.bar_chart(df_sessions['session_type'].value_counts())
        else:
            st.info("Geen data.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Welzijn trends
    if not df_wellbeing.empty:
        st.write("####  Welzijn Trends (alle atleten)")
        
        avg_by_date = df_wellbeing.groupby('log_date').agg({
            'mood_score': 'mean',
            'stress_level': 'mean',
            'sleep_quality': 'mean'
        }).reset_index()
        
        if not avg_by_date.empty:
            chart_data = avg_by_date.set_index('log_date')
            st.line_chart(chart_data)


# ============================================================================
# TAB 6: BEHEER
# ============================================================================

def render_hayat_admin(username: str):
    """Render Hayat beheer (alleen voor admins)."""
    
    st.subheader(" Hayat Beheer")
    
    if not check_permission(["SuperAdmin", "Psychologist"], silent=True):
        st.warning(" Alleen toegankelijk voor Hayat administrators.")
        return
    
    tab1, tab2 = st.tabs([" Alert Beheer", " Rapporten"])
    
    with tab1:
        df = get_data("hayat_crisis_alerts")
        
        if not df.empty:
            st.write("### Alle Alerts")
            
            filter_status = st.selectbox("Filter status", ["All", "OPEN", "IN_PROGRESS", "RESOLVED"])
            
            filtered = df if filter_status == "All" else df[df['status'] == filter_status]
            
            st.dataframe(filtered, width='stretch', hide_index=True)
            
            # Resolve alert
            st.write("###  Resolve Alert")
            
            open_alerts = df[df['status'].isin(['OPEN', 'IN_PROGRESS'])]
            
            if not open_alerts.empty:
                alert_id = st.selectbox(
                    "Selecteer alert",
                    open_alerts['alert_id'].tolist()
                )
                
                resolution = st.text_area("Resolution notes")
                
                if st.button(" Mark as Resolved"):
                    run_query("""
                        UPDATE hayat_crisis_alerts 
                        SET status = 'RESOLVED', resolved_at = ?, resolution_notes = ?
                        WHERE alert_id = ?
                    """, (datetime.now().isoformat(), resolution, alert_id))
                    st.success("Alert resolved!")
                    st.rerun()
        else:
            st.info("Geen alerts.")
    
    with tab2:
        st.write("###  Maandrapport Generator")
        
        report_month = st.date_input("Selecteer maand", value=date.today().replace(day=1))
        
        if st.button(" Genereer Rapport"):
            st.write(f"**Hayat Initiative - Maandrapport {report_month.strftime('%B %Y')}**")
            
            df_alerts = get_data("hayat_crisis_alerts")
            df_sessions = get_data("hayat_sessions")
            
            # Simple stats
            st.write(f"- Totaal alerts: {len(df_alerts) if not df_alerts.empty else 0}")
            st.write(f"- Totaal sessies: {len(df_sessions) if not df_sessions.empty else 0}")
            
            st.info("Volledige rapport functionaliteit komt in volgende versie.")
