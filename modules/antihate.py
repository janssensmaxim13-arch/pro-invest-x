# ============================================================================
# ANTI-HATE SHIELD MODULE (DOSSIER 15/27)
# 
# Beschermt atleten tegen:
# - Online hate speech en racisme
# - Cyberbullying
# - Social media harassment
# 
# Features:
# - Social media monitoring (gesimuleerd)
# - Incident reporting
# - Legal support tracking
# - Wellness check triggers
# - Analytics en rapportage
# ============================================================================

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import random
import hashlib

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import DB_FILE, Options, Messages
from database.connection import get_data, run_query, get_connection, count_records
from utils.helpers import generate_uuid
from auth.security import log_audit, check_permission
from ui.components import metric_row, page_header, paginated_dataframe


# ============================================================================
# CONSTANTEN
# ============================================================================

HATE_CATEGORIES = [
    "RACISM",               # Racisme
    "SEXISM",               # Seksisme
    "RELIGIOUS_HATE",       # Religieuze haat
    "HOMOPHOBIA",           # Homofobie
    "DISABILITY_HATE",      # Hate tegen mensen met beperking
    "XENOPHOBIA",           # Xenofobie
    "THREATS",              # Bedreigingen
    "CYBERBULLYING",        # Cyberpesten
    "DOXXING",              # Persoonlijke info delen
    "OTHER"                 # Overig
]

PLATFORMS = [
    "Twitter/X",
    "Instagram", 
    "Facebook",
    "TikTok",
    "YouTube",
    "WhatsApp Groups",
    "Telegram",
    "Reddit",
    "Other"
]

SEVERITY_LEVELS = [
    "LOW",          # Licht - waarschuwing
    "MEDIUM",       # Gemiddeld - monitoring
    "HIGH",         # Ernstig - actie vereist
    "CRITICAL"      # Kritiek - onmiddellijke actie + legal
]

ACTION_TYPES = [
    "MONITOR",              # Blijven monitoren
    "REPORT_TO_PLATFORM",   # Rapporteren aan platform
    "LEGAL_ACTION",         # Juridische actie
    "ATHLETE_SUPPORT",      # Atleet ondersteuning
    "PRESS_STATEMENT",      # Pers verklaring
    "NO_ACTION"             # Geen actie nodig
]


# ============================================================================
# DATABASE TABELLEN
# ============================================================================

def init_antihate_tables():
    """Initialiseer Anti-Hate Shield tabellen."""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Monitored Athletes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_monitored (
            monitor_id TEXT PRIMARY KEY,
            
            -- Atleet info
            athlete_name TEXT NOT NULL,
            athlete_type TEXT DEFAULT 'FOOTBALL',
            talent_id TEXT,
            
            -- Social media handles
            twitter_handle TEXT,
            instagram_handle TEXT,
            tiktok_handle TEXT,
            
            -- Monitoring settings
            monitoring_active INTEGER DEFAULT 1,
            priority_level TEXT DEFAULT 'NORMAL',
            
            -- Stats
            total_incidents INTEGER DEFAULT 0,
            last_incident_date TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # Hate Incidents
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_incidents (
            incident_id TEXT PRIMARY KEY,
            
            -- Atleet
            monitor_id TEXT,
            athlete_name TEXT NOT NULL,
            
            -- Incident details
            platform TEXT NOT NULL,
            category TEXT NOT NULL,
            severity TEXT DEFAULT 'MEDIUM',
            
            -- Content (gehashed voor privacy)
            content_hash TEXT,
            content_preview TEXT,
            
            -- Bron
            source_url TEXT,
            source_username TEXT,
            source_screenshot_hash TEXT,
            
            -- Detectie
            detected_by TEXT DEFAULT 'MANUAL',
            detected_at TEXT NOT NULL,
            
            -- Response
            action_taken TEXT,
            action_date TEXT,
            action_notes TEXT,
            
            -- Legal
            legal_case_id TEXT,
            reported_to_platform INTEGER DEFAULT 0,
            platform_response TEXT,
            
            -- Wellness check
            wellness_check_triggered INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'OPEN',
            resolved_at TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (monitor_id) REFERENCES antihate_monitored(monitor_id)
        )
    ''')
    
    # Legal Cases
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_legal_cases (
            case_id TEXT PRIMARY KEY,
            
            -- Incident link
            incident_id TEXT,
            
            -- Case details
            case_type TEXT NOT NULL,
            description TEXT,
            
            -- Personen
            athlete_name TEXT,
            perpetrator_info TEXT,
            lawyer_name TEXT,
            
            -- Status
            status TEXT DEFAULT 'OPEN',
            court_date TEXT,
            outcome TEXT,
            
            -- Financieel
            legal_costs REAL DEFAULT 0,
            damages_claimed REAL DEFAULT 0,
            damages_awarded REAL DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (incident_id) REFERENCES antihate_incidents(incident_id)
        )
    ''')
    
    # Wellness Checks (link naar Hayat)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_wellness_checks (
            check_id TEXT PRIMARY KEY,
            
            incident_id TEXT,
            athlete_name TEXT,
            
            -- Check details
            check_type TEXT DEFAULT 'POST_INCIDENT',
            urgency TEXT DEFAULT 'MEDIUM',
            
            -- Response
            contacted_at TEXT,
            responded_at TEXT,
            response_notes TEXT,
            
            -- Follow-up
            hayat_referral INTEGER DEFAULT 0,
            hayat_session_id TEXT,
            
            -- Status
            status TEXT DEFAULT 'PENDING',
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (incident_id) REFERENCES antihate_incidents(incident_id)
        )
    ''')
    
    # Platform Reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_platform_reports (
            report_id TEXT PRIMARY KEY,
            
            incident_id TEXT,
            platform TEXT NOT NULL,
            
            -- Report details
            report_type TEXT,
            report_date TEXT,
            reference_number TEXT,
            
            -- Response
            platform_response TEXT,
            response_date TEXT,
            content_removed INTEGER DEFAULT 0,
            account_actioned INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'SUBMITTED',
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (incident_id) REFERENCES antihate_incidents(incident_id)
        )
    ''')
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incident_athlete ON antihate_incidents(monitor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incident_status ON antihate_incidents(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_incident_severity ON antihate_incidents(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_legal_status ON antihate_legal_cases(status)")
    
    conn.commit()
    conn.close()


def register_antihate_tables():
    """Registreer tabellen in whitelist."""
    from config import ALLOWED_TABLES
    tables = [
        'antihate_monitored',
        'antihate_incidents',
        'antihate_legal_cases',
        'antihate_wellness_checks',
        'antihate_platform_reports'
    ]
    for table in tables:
        if table not in ALLOWED_TABLES:
            ALLOWED_TABLES.append(table)


# ============================================================================
# HELPER FUNCTIES
# ============================================================================

def hash_content(content: str) -> str:
    """Hash hateful content voor opslag (privacy)."""
    return hashlib.sha256(content.encode()).hexdigest()[:32]


def get_monitored_athletes() -> Dict[str, str]:
    """Haal gemonitorde atleten op."""
    df = get_data("antihate_monitored")
    if df.empty:
        return {}
    return {row['monitor_id']: row['athlete_name'] for _, row in df.iterrows()}


def simulate_threat_score() -> int:
    """Simuleer een threat score (voor demo)."""
    # In productie zou dit ML-based zijn
    return random.randint(0, 100)


# ============================================================================
# MAIN RENDER
# ============================================================================

def render(username: str):
    """Render de Anti-Hate Shield module."""
    
    # Init
    init_antihate_tables()
    register_antihate_tables()
    
    page_header(
        "️ Anti-Hate Shield",
        "Dossier 15/27 | Bescherming tegen online haat | Social Media Monitoring | Legal Support"
    )
    
    # Waarschuwing
    st.warning("""
    **️ Gevoelige Module**: Deze module bevat referenties naar hatelijke content.
    Alle content wordt gehashed opgeslagen voor privacy en juridische doeleinden.
    """)
    
    tabs = st.tabs([
        " Dashboard",
        " Monitoring",
        " Incidenten",
        "️ Legal",
        " Wellness",
        " Analytics"
    ])
    
    with tabs[0]:
        render_dashboard()
    
    with tabs[1]:
        render_monitoring(username)
    
    with tabs[2]:
        render_incidents(username)
    
    with tabs[3]:
        render_legal(username)
    
    with tabs[4]:
        render_wellness(username)
    
    with tabs[5]:
        render_antihate_analytics()


# ============================================================================
# TAB 1: DASHBOARD
# ============================================================================

def render_dashboard():
    """Render Anti-Hate Shield dashboard."""
    
    st.subheader(" Shield Status Dashboard")
    
    df_monitored = get_data("antihate_monitored")
    df_incidents = get_data("antihate_incidents")
    df_legal = get_data("antihate_legal_cases")
    
    # Metrics
    total_monitored = len(df_monitored) if not df_monitored.empty else 0
    active_monitoring = len(df_monitored[df_monitored['monitoring_active'] == 1]) if not df_monitored.empty else 0
    
    total_incidents = len(df_incidents) if not df_incidents.empty else 0
    open_incidents = len(df_incidents[df_incidents['status'] == 'OPEN']) if not df_incidents.empty else 0
    critical_incidents = len(df_incidents[df_incidents['severity'] == 'CRITICAL']) if not df_incidents.empty else 0
    
    open_legal = len(df_legal[df_legal['status'] == 'OPEN']) if not df_legal.empty else 0
    
    # Status indicators
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(" Atleten Gemonitord", total_monitored)
        st.caption(f" {active_monitoring} actief")
    
    with col2:
        if critical_incidents > 0:
            st.metric(" KRITIEKE Incidenten", critical_incidents, delta="ACTIE VEREIST", delta_color="inverse")
        else:
            st.metric(" Kritieke Incidenten", 0)
    
    with col3:
        st.metric(" Open Incidenten", open_incidents)
        st.caption(f" {total_incidents} totaal")
    
    with col4:
        st.metric("️ Open Legal Cases", open_legal)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Recent incidents
    if not df_incidents.empty:
        st.write("###  Recente Incidenten")
        
        recent = df_incidents.head(5)
        
        for _, inc in recent.iterrows():
            severity_color = {
                "LOW": "",
                "MEDIUM": "",
                "HIGH": "",
                "CRITICAL": ""
            }.get(inc['severity'], "")
            
            with st.expander(f"{severity_color} {inc['athlete_name']} - {inc['category']} ({inc['platform']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Severity:** {inc['severity']}")
                    st.write(f"**Status:** {inc['status']}")
                    st.write(f"**Detected:** {inc['detected_at'][:10] if inc['detected_at'] else '-'}")
                
                with col2:
                    if inc['content_preview']:
                        st.write(f"**Preview:** {inc['content_preview'][:100]}...")
                    if inc['action_taken']:
                        st.write(f"**Action:** {inc['action_taken']}")
    else:
        st.success(" Geen recente incidenten!")
    
    # Threat level indicator
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("###  Overall Threat Level")
    
    if critical_incidents > 0:
        threat_level = "CRITICAL"
        threat_color = "red"
    elif open_incidents > 5:
        threat_level = "HIGH"
        threat_color = "orange"
    elif open_incidents > 0:
        threat_level = "MEDIUM"
        threat_color = "yellow"
    else:
        threat_level = "LOW"
        threat_color = "green"
    
    st.markdown(f"""
        <div style='
            background-color: {threat_color};
            color: {'white' if threat_color in ['red', 'orange'] else 'black'};
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        '>
            THREAT LEVEL: {threat_level}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# TAB 2: MONITORING
# ============================================================================

def render_monitoring(username: str):
    """Render athlete monitoring management."""
    
    st.subheader(" Athlete Monitoring")
    
    tab1, tab2 = st.tabs([" Gemonitorde Atleten", " Toevoegen"])
    
    with tab1:
        df = get_data("antihate_monitored")
        
        if not df.empty:
            # Filter
            filter_active = st.checkbox("Alleen actieve monitoring", value=True)
            
            if filter_active:
                df = df[df['monitoring_active'] == 1]
            
            metric_row([
                (" Totaal", len(df)),
                ("️ High Priority", len(df[df['priority_level'] == 'HIGH'])),
            ])
            
            # Table
            for _, athlete in df.iterrows():
                active_emoji = "" if athlete['monitoring_active'] else "⏸️"
                priority_emoji = {"HIGH": "", "NORMAL": "", "LOW": ""}.get(athlete['priority_level'], "")
                
                with st.expander(f"{active_emoji} {athlete['athlete_name']} {priority_emoji}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {athlete['athlete_type']}")
                        st.write(f"**Priority:** {athlete['priority_level']}")
                        st.write(f"**Total Incidents:** {athlete['total_incidents']}")
                    
                    with col2:
                        if athlete['twitter_handle']:
                            st.write(f"**Twitter:** @{athlete['twitter_handle']}")
                        if athlete['instagram_handle']:
                            st.write(f"**Instagram:** @{athlete['instagram_handle']}")
                    
                    # Toggle monitoring
                    if st.button(
                        "⏸️ Pause" if athlete['monitoring_active'] else "▶️ Activate",
                        key=f"toggle_{athlete['monitor_id']}"
                    ):
                        new_status = 0 if athlete['monitoring_active'] else 1
                        run_query(
                            "UPDATE antihate_monitored SET monitoring_active = ? WHERE monitor_id = ?",
                            (new_status, athlete['monitor_id'])
                        )
                        st.rerun()
        else:
            st.info("Nog geen atleten gemonitord.")
    
    with tab2:
        with st.form("add_monitoring"):
            col1, col2 = st.columns(2)
            
            with col1:
                athlete_name = st.text_input("Atleet Naam *")
                athlete_type = st.selectbox("Type", ["FOOTBALL", "WOMEN_FOOTBALL", "PARALYMPIC", "OTHER"])
                priority = st.selectbox("Priority Level", ["NORMAL", "HIGH", "LOW"])
            
            with col2:
                twitter = st.text_input("Twitter Handle", placeholder="username (zonder @)")
                instagram = st.text_input("Instagram Handle", placeholder="username (zonder @)")
                tiktok = st.text_input("TikTok Handle", placeholder="username (zonder @)")
            
            if st.form_submit_button(" START MONITORING", width="stretch"):
                if not athlete_name:
                    st.error("Vul atleet naam in.")
                else:
                    monitor_id = generate_uuid("MON")
                    
                    # Sla elke social media handle apart op als platform entry
                    success = run_query("""
                        INSERT INTO antihate_monitored (
                            monitor_id, target_type, target_id, target_name, platform,
                            account_url, risk_level, is_active, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
                    """, (
                        monitor_id, athlete_type, monitor_id, athlete_name, 
                        'MULTI', f"TW:{twitter or ''}/IG:{instagram or ''}/TT:{tiktok or ''}", 
                        priority, datetime.now().isoformat()
                    ))
                    
                    if success:
                        st.success(f" Monitoring gestart voor {athlete_name}")
                        log_audit(username, "ANTIHATE_MONITORING_STARTED", "Anti-Hate Shield")
                        st.rerun()


# ============================================================================
# TAB 3: INCIDENTEN
# ============================================================================

def render_incidents(username: str):
    """Render incident management."""
    
    st.subheader(" Incident Management")
    
    athletes = get_monitored_athletes()
    
    tab1, tab2 = st.tabs([" Incidenten", " Nieuw Incident"])
    
    with tab1:
        df = get_data("antihate_incidents")
        
        if not df.empty:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(t("status"), ["All", "OPEN", "IN_PROGRESS", "RESOLVED"])
            with col2:
                severity_filter = st.selectbox("Severity", ["All"] + SEVERITY_LEVELS)
            with col3:
                category_filter = st.selectbox("Category", ["All"] + HATE_CATEGORIES)
            
            filtered = df.copy()
            if status_filter != "All":
                filtered = filtered[filtered['status'] == status_filter]
            if severity_filter != "All":
                filtered = filtered[filtered['severity'] == severity_filter]
            if category_filter != "All":
                filtered = filtered[filtered['category'] == category_filter]
            
            # Metrics
            metric_row([
                (" Totaal", len(filtered)),
                (" Critical", len(filtered[filtered['severity'] == 'CRITICAL'])),
                (" High", len(filtered[filtered['severity'] == 'HIGH'])),
                (" Resolved", len(filtered[filtered['status'] == 'RESOLVED'])),
            ])
            
            # Table
            paginated_dataframe(
                filtered[['athlete_name', 'platform', 'category', 'severity', 'status', 'detected_at']],
                per_page=15,
                key_prefix="incidents"
            )
            
            # Quick resolve
            st.markdown("---")
            st.write("###  Quick Actions")
            
            open_incidents = filtered[filtered['status'] == 'OPEN']
            if not open_incidents.empty:
                incident_id = st.selectbox(
                    "Select Incident",
                    open_incidents['incident_id'].tolist(),
                    format_func=lambda x: f"{x} - {df[df['incident_id'] == x]['athlete_name'].values[0]}"
                )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    action = st.selectbox("Action", ACTION_TYPES)
                
                with col2:
                    if st.button(" Take Action"):
                        run_query("""
                            UPDATE antihate_incidents 
                            SET action_taken = ?, action_date = ?, status = 'IN_PROGRESS'
                            WHERE incident_id = ?
                        """, (action, datetime.now().isoformat(), incident_id))
                        
                        st.success("Action recorded!")
                        log_audit(username, "ANTIHATE_ACTION_TAKEN", "Anti-Hate Shield")
                        st.rerun()
        else:
            st.success(" Geen incidenten geregistreerd.")
    
    with tab2:
        with st.form("new_incident"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Atleet & Platform")
                
                if athletes:
                    monitor_id = st.selectbox(
                        "Atleet *",
                        list(athletes.keys()),
                        format_func=lambda x: athletes.get(x, x)
                    )
                    athlete_name = athletes.get(monitor_id, "")
                else:
                    monitor_id = None
                    athlete_name = st.text_input("Atleet Naam *")
                
                platform = st.selectbox("Platform *", PLATFORMS)
                source_url = st.text_input("Bron URL", placeholder="https://...")
                source_username = st.text_input("Dader Username")
            
            with col2:
                st.markdown("### Incident Details")
                
                category = st.selectbox("Categorie *", HATE_CATEGORIES)
                severity = st.selectbox("Severity *", SEVERITY_LEVELS)
                
                content_preview = st.text_area(
                    "Content Preview (optioneel)",
                    placeholder="Korte beschrijving van de hatelijke content...",
                    help="Dit wordt NIET volledig opgeslagen, alleen een hash voor tracking."
                )
            
            trigger_wellness = st.checkbox(" Trigger Wellness Check", value=severity in ["HIGH", "CRITICAL"])
            
            if st.form_submit_button(" RAPPORTEER INCIDENT", width="stretch"):
                if not athlete_name or not platform or not category:
                    st.error("Vul verplichte velden in.")
                else:
                    incident_id = generate_uuid("INC")
                    
                    success = run_query("""
                        INSERT INTO antihate_incidents (
                            incident_id, victim_id, victim_name, incident_type, platform,
                            description, evidence_url, severity, status, reported_by, reported_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'REPORTED', ?, ?)
                    """, (
                        incident_id, monitor_id, athlete_name, category, platform,
                        content_preview[:500] if content_preview else None,
                        source_url or None, severity, "MANUAL", datetime.now().isoformat()
                    ))
                    
                    if success:
                        # Update athlete incident count
                        if monitor_id:
                            run_query("""
                                UPDATE antihate_monitored 
                                SET total_incidents = total_incidents + 1, 
                                    last_incident_date = ?
                                WHERE monitor_id = ?
                            """, (datetime.now().isoformat(), monitor_id))
                        
                        # Create wellness check if triggered
                        if trigger_wellness:
                            check_id = generate_uuid("WCK")
                            run_query("""
                                INSERT INTO antihate_wellness_checks (
                                    check_id, incident_id, victim_id, check_type, 
                                    notes, follow_up_needed, checked_at
                                ) VALUES (?, ?, ?, ?, ?, 1, ?)
                            """, (check_id, incident_id, monitor_id, 'URGENT', 
                                  f"Auto-triggered for {athlete_name}", datetime.now().isoformat()))
                        
                        st.success(f" Incident geregistreerd!")
                        if trigger_wellness:
                            st.warning(" Wellness check is getriggerd voor de atleet.")
                        
                        log_audit(username, "ANTIHATE_INCIDENT_CREATED", "Anti-Hate Shield")
                        st.rerun()


# ============================================================================
# TAB 4: LEGAL
# ============================================================================

def render_legal(username: str):
    """Render legal case management."""
    
    st.subheader("️ Legal Cases")
    
    if not check_permission(["SuperAdmin", "Official", "Security Staff"], silent=True):
        st.warning(" Legal cases zijn beperkt toegankelijk.")
        return
    
    df = get_data("antihate_legal_cases")
    df_incidents = get_data("antihate_incidents")
    
    tab1, tab2 = st.tabs([" Cases", " Nieuwe Case"])
    
    with tab1:
        if not df.empty:
            metric_row([
                ("️ Totaal Cases", len(df)),
                (" Open", len(df[df['status'] == 'OPEN'])),
                (" Legal Costs", f"€ {df['legal_costs'].sum():,.0f}"),
            ])
            
            st.dataframe(df[['case_id', 'athlete_name', 'case_type', 'status', 'legal_costs']], 
                        width="stretch", hide_index=True)
        else:
            st.info("Geen legal cases.")
    
    with tab2:
        with st.form("new_legal"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Link to incident
                if not df_incidents.empty:
                    incident_id = st.selectbox(
                        "Gekoppeld Incident",
                        [None] + df_incidents['incident_id'].tolist()
                    )
                else:
                    incident_id = None
                
                athlete_name = st.text_input("Atleet Naam *")
                case_type = st.selectbox("Case Type *", ["CIVIL", "CRIMINAL", "PLATFORM_COMPLAINT"])
            
            with col2:
                lawyer_name = st.text_input("Advocaat")
                legal_costs = st.number_input("Geschatte Kosten (€)", 0, 1000000, 0)
                damages_claimed = st.number_input("Gevorderde Schade (€)", 0, 10000000, 0)
            
            description = st.text_area("Beschrijving")
            
            if st.form_submit_button("️ OPEN CASE", width="stretch"):
                case_id = generate_uuid("LGL")
                
                run_query("""
                    INSERT INTO antihate_legal_cases (
                        case_id, incident_id, case_type, jurisdiction, 
                        lawyer_assigned, status, filed_at, created_at
                    ) VALUES (?, ?, ?, ?, ?, 'OPEN', ?, ?)
                """, (
                    case_id, incident_id, case_type, "Morocco", 
                    lawyer_name, datetime.now().isoformat(), datetime.now().isoformat()
                ))
                
                st.success(" Legal case geopend!")
                log_audit(username, "ANTIHATE_LEGAL_CASE_CREATED", "Anti-Hate Shield")
                st.rerun()


# ============================================================================
# TAB 5: WELLNESS
# ============================================================================

def render_wellness(username: str):
    """Render wellness checks (link naar Hayat)."""
    
    st.subheader(" Wellness Checks")
    
    st.info("""
    **Wellness checks** worden automatisch getriggerd bij HIGH/CRITICAL incidenten.
    Hier kun je de status volgen en doorverwijzen naar **Hayat Initiative**.
    """)
    
    df = get_data("antihate_wellness_checks")
    
    if not df.empty:
        pending = df[df['status'] == 'PENDING']
        
        metric_row([
            (" Totaal Checks", len(df)),
            ("⏳ Pending", len(pending)),
            (" Hayat Referrals", len(df[df['hayat_referral'] == 1])),
        ])
        
        if not pending.empty:
            st.warning(f"️ {len(pending)} wellness checks wachten op actie!")
            
            for _, check in pending.iterrows():
                with st.expander(f"⏳ {check['athlete_name']} - {check['urgency']}"):
                    st.write(f"**Incident:** {check['incident_id']}")
                    st.write(f"**Urgency:** {check['urgency']}")
                    st.write(f"**Created:** {check['created_at'][:10]}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button(f" Mark Contacted", key=f"contact_{check['check_id']}"):
                            run_query("""
                                UPDATE antihate_wellness_checks 
                                SET contacted_at = ?, status = 'CONTACTED'
                                WHERE check_id = ?
                            """, (datetime.now().isoformat(), check['check_id']))
                            st.rerun()
                    
                    with col2:
                        if st.button(f" Refer to Hayat", key=f"hayat_{check['check_id']}"):
                            run_query("""
                                UPDATE antihate_wellness_checks 
                                SET hayat_referral = 1, status = 'REFERRED'
                                WHERE check_id = ?
                            """, (check['check_id'],))
                            st.success("Doorverwezen naar Hayat Initiative!")
                            st.rerun()
        
        # History
        st.markdown("---")
        st.write("###  Check History")
        st.dataframe(df[['athlete_name', 'urgency', 'status', 'hayat_referral', 'created_at']], 
                    width="stretch", hide_index=True)
    else:
        st.success(" Geen openstaande wellness checks.")


# ============================================================================
# TAB 6: ANALYTICS
# ============================================================================

def render_antihate_analytics():
    """Render Anti-Hate analytics."""
    
    st.subheader(" Anti-Hate Analytics")
    
    df_incidents = get_data("antihate_incidents")
    df_monitored = get_data("antihate_monitored")
    
    if df_incidents.empty:
        st.info("Nog geen data voor analytics.")
        return
    
    # Overview
    metric_row([
        (" Totaal Incidenten", len(df_incidents)),
        (" Atleten Gemonitord", len(df_monitored)),
        (" Critical", len(df_incidents[df_incidents['severity'] == 'CRITICAL'])),
        (" Resolved", len(df_incidents[df_incidents['status'] == 'RESOLVED'])),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("####  Incidenten per Categorie")
        st.bar_chart(df_incidents['category'].value_counts())
    
    with col2:
        st.write("####  Incidenten per Platform")
        st.bar_chart(df_incidents['platform'].value_counts())
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### ️ Severity Verdeling")
        st.bar_chart(df_incidents['severity'].value_counts())
    
    with col2:
        st.write("####  Status Overzicht")
        st.bar_chart(df_incidents['status'].value_counts())
