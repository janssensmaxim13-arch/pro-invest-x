# ============================================================================
# FRMF MODULE - Federation Royale Marocaine de Football
# RefereeChain + VAR Vault + Match Officials
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from ui.styles import COLORS
from ui.components import page_header, premium_kpi_row, info_box, warning_box, success_message
from database.connection import get_data, run_query
from utils.helpers import generate_uuid
from auth.security import log_audit

# =============================================================================
# CONSTANTS
# =============================================================================

REFEREE_LEVELS = [
    ("FIFA", "FIFA International"),
    ("CAF", "CAF Continental"),
    ("FRMF_A", "FRMF Category A"),
    ("FRMF_B", "FRMF Category B"),
    ("REGIONAL", "Regional"),
    ("YOUTH", "Youth Specialist")
]

COMPETITIONS = [
    "Botola Pro", "Botola 2", "Coupe du Trone", 
    "CAF Champions League", "CAF Confederation Cup",
    "Arab Club Championship", "Friendly International",
    "CHAN", "World Cup Qualifier", "AFCON Qualifier"
]

VAR_DECISIONS = [
    ("GOAL", "Goal Decision"),
    ("PENALTY", "Penalty Decision"),
    ("RED_CARD", "Red Card Decision"),
    ("MISTAKEN_IDENTITY", "Mistaken Identity"),
    ("OFFSIDE", "Offside Check")
]

VAR_OUTCOMES = ["CONFIRMED", "OVERTURNED", "REVIEW_COMPLETE"]

INCIDENT_TYPES = [
    "Yellow Card", "Red Card", "Penalty Awarded", "Penalty Denied",
    "Goal Disallowed", "VAR Review", "Injury Time Added", "Match Abandoned"
]

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_frmf_tables():
    """Initialize FRMF-specific tables."""
    import sqlite3
    from config import DB_FILE
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Referees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_referees (
            referee_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT DEFAULT 'Moroccan',
            license_level TEXT NOT NULL,
            license_number TEXT UNIQUE,
            license_expiry TEXT,
            fifa_badge INTEGER DEFAULT 0,
            years_experience INTEGER DEFAULT 0,
            total_matches INTEGER DEFAULT 0,
            avg_rating REAL DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            region TEXT,
            phone TEXT,
            email TEXT,
            photo_url TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Match assignments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_match_assignments (
            assignment_id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            competition TEXT NOT NULL,
            match_date TEXT NOT NULL,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            venue TEXT,
            referee_id TEXT,
            assistant_1_id TEXT,
            assistant_2_id TEXT,
            fourth_official_id TEXT,
            var_referee_id TEXT,
            avar_referee_id TEXT,
            status TEXT DEFAULT 'SCHEDULED',
            created_at TEXT NOT NULL,
            FOREIGN KEY (referee_id) REFERENCES frmf_referees(referee_id)
        )
    ''')
    
    # VAR decisions vault
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_var_vault (
            var_id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            assignment_id TEXT,
            minute INTEGER,
            decision_type TEXT NOT NULL,
            original_decision TEXT,
            var_recommendation TEXT,
            final_decision TEXT,
            outcome TEXT,
            review_duration_seconds INTEGER,
            video_url TEXT,
            screenshot_hash TEXT,
            var_referee_id TEXT,
            notes TEXT,
            is_controversial INTEGER DEFAULT 0,
            media_attention INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (assignment_id) REFERENCES frmf_match_assignments(assignment_id)
        )
    ''')
    
    # Referee performance ratings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_referee_ratings (
            rating_id TEXT PRIMARY KEY,
            referee_id TEXT NOT NULL,
            match_id TEXT NOT NULL,
            assignment_id TEXT,
            overall_rating REAL,
            decision_accuracy REAL,
            game_management REAL,
            fitness_score REAL,
            communication_score REAL,
            var_usage_score REAL,
            rated_by TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (referee_id) REFERENCES frmf_referees(referee_id)
        )
    ''')
    
    # Match incidents log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_match_incidents (
            incident_id TEXT PRIMARY KEY,
            match_id TEXT NOT NULL,
            assignment_id TEXT,
            minute INTEGER,
            incident_type TEXT NOT NULL,
            team TEXT,
            player_name TEXT,
            description TEXT,
            referee_decision TEXT,
            var_involved INTEGER DEFAULT 0,
            card_shown TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Indexes
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referee_level ON frmf_referees(license_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignment_date ON frmf_match_assignments(match_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_var_match ON frmf_var_vault(match_id)")
    except:
        pass
    
    conn.commit()
    conn.close()

# =============================================================================
# DEMO DATA GENERATORS
# =============================================================================

def generate_demo_referees():
    """Generate demo referee data."""
    referees = []
    
    names = [
        ("Redouane", "Jiyed", "FIFA"), ("Samir", "Guezzaz", "FIFA"),
        ("Jalal", "Jayed", "CAF"), ("Noureddine", "El Jaafari", "CAF"),
        ("Mustapha", "Ghorbal", "FRMF_A"), ("Bouchra", "Karboubi", "FRMF_A"),
        ("Youssef", "Essrayri", "FRMF_B"), ("Ahmed", "Bennani", "FRMF_B"),
        ("Khalid", "Rahmouni", "REGIONAL"), ("Omar", "Filali", "YOUTH")
    ]
    
    for i, (first, last, level) in enumerate(names):
        referees.append({
            "referee_id": f"REF-{100+i}",
            "name": f"{first} {last}",
            "license_level": level,
            "fifa_badge": 1 if level == "FIFA" else 0,
            "total_matches": random.randint(50, 500),
            "avg_rating": round(random.uniform(7.0, 9.5), 1),
            "years_experience": random.randint(5, 25),
            "status": "ACTIVE"
        })
    
    return pd.DataFrame(referees)

def generate_demo_matches():
    """Generate demo match assignments."""
    matches = []
    
    teams = [
        "Wydad AC", "Raja CA", "AS FAR", "RS Berkane", 
        "FUS Rabat", "MAS Fes", "Ittihad Tanger", "Hassania Agadir"
    ]
    
    for i in range(15):
        home = random.choice(teams)
        away = random.choice([t for t in teams if t != home])
        date = datetime.now() + timedelta(days=random.randint(-30, 30))
        
        matches.append({
            "match_id": f"MATCH-{1000+i}",
            "competition": random.choice(COMPETITIONS[:4]),
            "match_date": date.strftime("%Y-%m-%d"),
            "home_team": home,
            "away_team": away,
            "venue": f"Stade {home.split()[0]}",
            "referee": f"Referee {i+1}",
            "status": "COMPLETED" if date < datetime.now() else "SCHEDULED"
        })
    
    return pd.DataFrame(matches)

def generate_demo_var_decisions():
    """Generate demo VAR decisions."""
    decisions = []
    
    for i in range(20):
        decision_type = random.choice(VAR_DECISIONS)
        outcome = random.choice(VAR_OUTCOMES)
        
        decisions.append({
            "var_id": f"VAR-{2000+i}",
            "match_id": f"MATCH-{1000+random.randint(0,14)}",
            "minute": random.randint(1, 90),
            "decision_type": decision_type[1],
            "outcome": outcome,
            "review_duration": random.randint(30, 180),
            "is_controversial": random.randint(0, 1),
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat()
        })
    
    return pd.DataFrame(decisions)

# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_referee_registry(username: str):
    """Render referee registry tab."""
    st.markdown("### Referee Registry")
    st.caption("Complete database of licensed match officials")
    
    # Try to get real data first
    df = get_data("frmf_referees")
    if df.empty:
        df = generate_demo_referees()
        info_box("Demo Mode", "Showing demo data. Add referees to see real data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Referees", len(df))
    with col2:
        fifa_count = len(df[df['license_level'] == 'FIFA']) if 'license_level' in df.columns else 0
        st.metric("FIFA Badge", fifa_count)
    with col3:
        avg_rating = df['avg_rating'].mean() if 'avg_rating' in df.columns else 0
        st.metric("Avg Rating", f"{avg_rating:.1f}")
    with col4:
        active = len(df[df['status'] == 'ACTIVE']) if 'status' in df.columns else len(df)
        st.metric("Active", active)
    
    st.divider()
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        level_filter = st.selectbox("License Level", ["All"] + [l[1] for l in REFEREE_LEVELS])
    with col2:
        status_filter = st.selectbox(t("status"), ["All", "ACTIVE", "INACTIVE", "SUSPENDED"])
    
    # Apply filters
    filtered_df = df.copy()
    if level_filter != "All" and 'license_level' in df.columns:
        code = next((l[0] for l in REFEREE_LEVELS if l[1] == level_filter), None)
        if code:
            filtered_df = filtered_df[filtered_df['license_level'] == code]
    if status_filter != "All" and 'status' in df.columns:
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, width="stretch", hide_index=True)
    
    # Add referee
    with st.expander("Add New Referee", expanded=False):
        with st.form("add_referee"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                dob = st.date_input("Date of Birth")
            with col2:
                level = st.selectbox("License Level *", [l[1] for l in REFEREE_LEVELS])
                experience = st.number_input("Years Experience", 0, 40, 5)
                region = st.text_input("Region")
            
            if st.form_submit_button("Register Referee", type="primary", width="stretch"):
                if first_name and last_name:
                    referee_id = generate_uuid("REF")
                    level_code = next((l[0] for l in REFEREE_LEVELS if l[1] == level), "FRMF_B")
                    
                    success = run_query("""
                        INSERT INTO frmf_referees 
                        (referee_id, first_name, last_name, date_of_birth, license_level, 
                         years_experience, region, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (referee_id, first_name, last_name, str(dob), level_code,
                          experience, region, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Referee Registered!", referee_id)
                        log_audit(username, "REFEREE_REGISTERED", "FRMF", referee_id)
                        st.rerun()
                else:
                    st.error("First name and last name are required")


def render_match_assignments(username: str):
    """Render match assignments tab."""
    st.markdown("### Match Assignments")
    st.caption("Assign officials to upcoming matches")
    
    df = get_data("frmf_match_assignments")
    if df.empty:
        df = generate_demo_matches()
        info_box("Demo Mode", "Showing demo data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Matches", len(df))
    with col2:
        scheduled = len(df[df['status'] == 'SCHEDULED']) if 'status' in df.columns else 0
        st.metric("Upcoming", scheduled)
    with col3:
        completed = len(df[df['status'] == 'COMPLETED']) if 'status' in df.columns else 0
        st.metric("Completed", completed)
    with col4:
        st.metric("This Week", random.randint(3, 8))
    
    st.divider()
    
    # Upcoming matches
    st.markdown("#### Upcoming Matches")
    upcoming = df[df['status'] == 'SCHEDULED'] if 'status' in df.columns else df.head(5)
    
    if not upcoming.empty:
        for _, match in upcoming.head(5).iterrows():
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{match.get('home_team', 'TBD')}** vs **{match.get('away_team', 'TBD')}**")
                    st.caption(f"{match.get('competition', '')} | {match.get('venue', '')}")
                with col2:
                    st.markdown(f"**{match.get('match_date', '')}**")
                with col3:
                    st.markdown(f"Ref: {match.get('referee', 'Not assigned')}")
                st.divider()
    
    # Create assignment
    with st.expander("Create Match Assignment", expanded=False):
        with st.form("create_assignment"):
            col1, col2 = st.columns(2)
            with col1:
                competition = st.selectbox("Competition *", COMPETITIONS)
                match_date = st.date_input("Match Date *")
                home_team = st.text_input("Home Team *")
                away_team = st.text_input("Away Team *")
            with col2:
                venue = st.text_input("Venue")
                # Get referees for dropdown
                ref_df = get_data("frmf_referees")
                if not ref_df.empty and 'referee_id' in ref_df.columns:
                    ref_options = ["-- Select --"] + ref_df['referee_id'].tolist()
                else:
                    ref_options = ["-- Select --", "REF-101", "REF-102", "REF-103"]
                referee = st.selectbox("Main Referee", ref_options)
                var_referee = st.selectbox("VAR Referee", ref_options)
            
            if st.form_submit_button("Create Assignment", type="primary", width="stretch"):
                if home_team and away_team:
                    assignment_id = generate_uuid("ASSIGN")
                    match_id = generate_uuid("MATCH")
                    
                    success = run_query("""
                        INSERT INTO frmf_match_assignments 
                        (assignment_id, match_id, competition, match_date, home_team, away_team,
                         venue, referee_id, var_referee_id, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'SCHEDULED', ?)
                    """, (assignment_id, match_id, competition, str(match_date), home_team, away_team,
                          venue, referee if referee != "-- Select --" else None,
                          var_referee if var_referee != "-- Select --" else None,
                          datetime.now().isoformat()))
                    
                    if success:
                        success_message("Assignment Created!", assignment_id)
                        log_audit(username, "MATCH_ASSIGNED", "FRMF", f"{home_team} vs {away_team}")
                        st.rerun()
                else:
                    st.error("Home and away teams are required")


def render_var_vault(username: str):
    """Render VAR decisions vault."""
    st.markdown("### VAR Vault")
    st.caption("Immutable archive of all VAR decisions")
    
    df = get_data("frmf_var_vault")
    if df.empty:
        df = generate_demo_var_decisions()
        info_box("Demo Mode", "Showing demo VAR decisions.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        overturned = len(df[df['outcome'] == 'OVERTURNED']) if 'outcome' in df.columns else 0
        st.metric("Overturned", overturned)
    with col3:
        confirmed = len(df[df['outcome'] == 'CONFIRMED']) if 'outcome' in df.columns else 0
        st.metric("Confirmed", confirmed)
    with col4:
        controversial = len(df[df['is_controversial'] == 1]) if 'is_controversial' in df.columns else 0
        st.metric("Controversial", controversial)
    
    st.divider()
    
    # Filter
    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.selectbox("Decision Type", ["All"] + [d[1] for d in VAR_DECISIONS])
    with col2:
        outcome_filter = st.selectbox("Outcome", ["All"] + VAR_OUTCOMES)
    
    # Table
    st.dataframe(df, width="stretch", hide_index=True)
    
    # Log VAR decision
    with st.expander("Log VAR Decision", expanded=False):
        with st.form("log_var"):
            col1, col2 = st.columns(2)
            with col1:
                match_id = st.text_input("Match ID *")
                minute = st.number_input("Minute", 1, 120, 45)
                decision_type = st.selectbox("Decision Type *", [d[1] for d in VAR_DECISIONS])
            with col2:
                original_decision = st.text_input("Original Decision")
                var_recommendation = st.text_input("VAR Recommendation")
                final_decision = st.text_input("Final Decision")
                outcome = st.selectbox("Outcome", VAR_OUTCOMES)
            
            review_duration = st.slider("Review Duration (seconds)", 10, 300, 60)
            is_controversial = st.checkbox("Mark as Controversial")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Log VAR Decision", type="primary", width="stretch"):
                if match_id:
                    var_id = generate_uuid("VAR")
                    decision_code = next((d[0] for d in VAR_DECISIONS if d[1] == decision_type), "GOAL")
                    
                    # Generate screenshot hash for authenticity
                    screenshot_hash = hashlib.sha256(
                        f"{var_id}|{match_id}|{minute}|{datetime.now().isoformat()}".encode()
                    ).hexdigest()[:16]
                    
                    success = run_query("""
                        INSERT INTO frmf_var_vault 
                        (var_id, match_id, minute, decision_type, original_decision, 
                         var_recommendation, final_decision, outcome, review_duration_seconds,
                         screenshot_hash, is_controversial, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (var_id, match_id, minute, decision_code, original_decision,
                          var_recommendation, final_decision, outcome, review_duration,
                          screenshot_hash, 1 if is_controversial else 0, notes,
                          datetime.now().isoformat()))
                    
                    if success:
                        success_message("VAR Decision Logged!", f"{var_id} | Hash: {screenshot_hash}")
                        log_audit(username, "VAR_LOGGED", "FRMF", f"Match {match_id} - {decision_type}")
                        st.rerun()
                else:
                    st.error("Match ID is required")


def render_referee_performance(username: str):
    """Render referee performance tab."""
    st.markdown("### Referee Performance")
    st.caption("Track and rate referee performance")
    
    df_referees = get_data("frmf_referees")
    if df_referees.empty:
        df_referees = generate_demo_referees()
    
    df_ratings = get_data("frmf_referee_ratings")
    
    # Top performers
    st.markdown("#### Top Performers")
    
    if 'avg_rating' in df_referees.columns:
        top_refs = df_referees.nlargest(5, 'avg_rating')
        
        for i, (_, ref) in enumerate(top_refs.iterrows()):
            col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
            with col1:
                st.markdown(f"**#{i+1}**")
            with col2:
                st.markdown(f"**{ref.get('name', 'Unknown')}**")
                st.caption(f"{ref.get('license_level', '')} | {ref.get('total_matches', 0)} matches")
            with col3:
                st.metric("Rating", f"{ref.get('avg_rating', 0):.1f}")
            with col4:
                if ref.get('fifa_badge', 0):
                    st.markdown("FIFA")
            st.divider()
    
    # Rate referee
    with st.expander("Rate Referee Performance", expanded=False):
        with st.form("rate_referee"):
            col1, col2 = st.columns(2)
            with col1:
                if not df_referees.empty:
                    ref_options = df_referees['name'].tolist() if 'name' in df_referees.columns else []
                else:
                    ref_options = ["Referee 1", "Referee 2"]
                referee = st.selectbox("Referee *", ref_options)
                match_id = st.text_input("Match ID *")
            with col2:
                overall = st.slider("Overall Rating", 1.0, 10.0, 7.0, 0.1)
                decision_accuracy = st.slider("Decision Accuracy", 1.0, 10.0, 7.0, 0.1)
            
            col3, col4 = st.columns(2)
            with col3:
                game_management = st.slider("Game Management", 1.0, 10.0, 7.0, 0.1)
                fitness = st.slider("Fitness", 1.0, 10.0, 7.0, 0.1)
            with col4:
                communication = st.slider("Communication", 1.0, 10.0, 7.0, 0.1)
                var_usage = st.slider("VAR Usage", 1.0, 10.0, 7.0, 0.1)
            
            notes = st.text_area("Performance Notes")
            
            if st.form_submit_button("Submit Rating", type="primary", width="stretch"):
                if match_id:
                    rating_id = generate_uuid("RATE")
                    
                    # Find referee_id
                    ref_row = df_referees[df_referees['name'] == referee] if 'name' in df_referees.columns else pd.DataFrame()
                    referee_id = ref_row.iloc[0]['referee_id'] if not ref_row.empty else None
                    
                    success = run_query("""
                        INSERT INTO frmf_referee_ratings 
                        (rating_id, referee_id, match_id, overall_rating, decision_accuracy,
                         game_management, fitness_score, communication_score, var_usage_score,
                         rated_by, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (rating_id, referee_id, match_id, overall, decision_accuracy,
                          game_management, fitness, communication, var_usage,
                          username, notes, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Rating Submitted!", rating_id)
                        log_audit(username, "REFEREE_RATED", "FRMF", f"{referee} - {overall}")
                        st.rerun()
                else:
                    st.error("Match ID is required")


def render_match_incidents(username: str):
    """Render match incidents tab."""
    st.markdown("### Match Incidents Log")
    st.caption("Complete record of match incidents and decisions")
    
    df = get_data("frmf_match_incidents")
    
    if df.empty:
        # Generate demo incidents
        incidents = []
        for i in range(15):
            incidents.append({
                "incident_id": f"INC-{3000+i}",
                "match_id": f"MATCH-{1000+random.randint(0,14)}",
                "minute": random.randint(1, 90),
                "incident_type": random.choice(INCIDENT_TYPES),
                "team": random.choice(["Home", "Away"]),
                "player_name": f"Player {random.randint(1, 30)}",
                "var_involved": random.randint(0, 1),
                "created_at": datetime.now().isoformat()
            })
        df = pd.DataFrame(incidents)
        info_box("Demo Mode", "Showing demo incidents.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Incidents", len(df))
    with col2:
        red_cards = len(df[df['incident_type'] == 'Red Card']) if 'incident_type' in df.columns else 0
        st.metric("Red Cards", red_cards)
    with col3:
        var_reviews = len(df[df['var_involved'] == 1]) if 'var_involved' in df.columns else 0
        st.metric("VAR Reviews", var_reviews)
    with col4:
        penalties = len(df[df['incident_type'].str.contains('Penalty', na=False)]) if 'incident_type' in df.columns else 0
        st.metric("Penalties", penalties)
    
    st.divider()
    st.dataframe(df, width="stretch", hide_index=True)
    
    # Log incident
    with st.expander("Log Match Incident", expanded=False):
        with st.form("log_incident"):
            col1, col2 = st.columns(2)
            with col1:
                match_id = st.text_input("Match ID *")
                minute = st.number_input("Minute", 1, 120, 45)
                incident_type = st.selectbox("Incident Type *", INCIDENT_TYPES)
            with col2:
                team = st.selectbox("Team", ["Home", "Away"])
                player_name = st.text_input("Player Name")
                var_involved = st.checkbox("VAR Involved")
            
            description = st.text_area("Description")
            
            if st.form_submit_button("Log Incident", type="primary", width="stretch"):
                if match_id:
                    incident_id = generate_uuid("INC")
                    
                    success = run_query("""
                        INSERT INTO frmf_match_incidents 
                        (incident_id, match_id, minute, incident_type, team, player_name,
                         description, var_involved, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (incident_id, match_id, minute, incident_type, team, player_name,
                          description, 1 if var_involved else 0, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Incident Logged!", incident_id)
                        log_audit(username, "INCIDENT_LOGGED", "FRMF", f"{incident_type} at {minute}'")
                        st.rerun()
                else:
                    st.error("Match ID is required")


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render(username: str):
    """Render the FRMF module."""
    
    # Initialize tables
    init_frmf_tables()
    
    page_header(
        "FRMF Officials Hub",
        "RefereeChain + VAR Vault - Complete Match Officials Management",
        icon=""
    )
    
    # KPIs
    df_refs = get_data("frmf_referees")
    df_matches = get_data("frmf_match_assignments")
    df_var = get_data("frmf_var_vault")
    
    ref_count = len(df_refs) if not df_refs.empty else 10
    match_count = len(df_matches) if not df_matches.empty else 15
    var_count = len(df_var) if not df_var.empty else 20
    
    premium_kpi_row([
        ("", "Licensed Referees", str(ref_count), "Active officials"),
        ("", "Match Assignments", str(match_count), "This season"),
        ("", "VAR Decisions", str(var_count), "Archived"),
        ("", "Avg Rating", "8.2", "Season average")
    ])
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Referee Registry",
        " Match Assignments", 
        " VAR Vault",
        " Performance",
        " Incidents"
    ])
    
    with tab1:
        render_referee_registry(username)
    
    with tab2:
        render_match_assignments(username)
    
    with tab3:
        render_var_vault(username)
    
    with tab4:
        render_referee_performance(username)
    
    with tab5:
        render_match_incidents(username)
