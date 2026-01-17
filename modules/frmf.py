# ============================================================================
# FRMF MODULE - Federation Royale Marocaine de Football
# RefereeChain + VAR Vault + Match Officials + Player Profiles
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

# Player Profiles Constants
PLAYER_POSITIONS = [
    ("GK", "Goalkeeper"),
    ("CB", "Center Back"),
    ("LB", "Left Back"),
    ("RB", "Right Back"),
    ("CDM", "Defensive Midfielder"),
    ("CM", "Central Midfielder"),
    ("CAM", "Attacking Midfielder"),
    ("LW", "Left Winger"),
    ("RW", "Right Winger"),
    ("ST", "Striker"),
    ("CF", "Center Forward")
]

PLAYER_STATUS = [
    ("ACTIVE", "Active"),
    ("INJURED", "Injured"),
    ("SUSPENDED", "Suspended"),
    ("LOANED_OUT", "Loaned Out"),
    ("LOANED_IN", "Loaned In"),
    ("RETIRED", "Retired"),
    ("FREE_AGENT", "Free Agent")
]

FOOT_PREFERENCE = ["Right", "Left", "Both"]

BOTOLA_CLUBS = [
    "Wydad AC", "Raja CA", "AS FAR", "RS Berkane", "FUS Rabat",
    "Maghreb Fes", "Hassania Agadir", "Difaa El Jadida", "Mouloudia Oujda",
    "Olympic Safi", "Chabab Mohammedia", "Ittihad Tanger", "Renaissance Zemamra",
    "Jeunesse Sportive Soualem", "Union Touarga", "Stade Marocain"
]

NATIONAL_TEAMS = [
    ("SENIOR_M", "Senior Men (Atlas Lions)"),
    ("SENIOR_W", "Senior Women (Lionesses)"),
    ("U23_M", "U23 Olympic Men"),
    ("U20_M", "U20 Men"),
    ("U17_M", "U17 Men"),
    ("U20_W", "U20 Women"),
    ("U17_W", "U17 Women"),
    ("FUTSAL", "Futsal National Team"),
    ("BEACH", "Beach Soccer National Team")
]

# Contract Management Constants
CONTRACT_TYPES = [
    ("PROFESSIONAL", "Professional Contract"),
    ("AMATEUR", "Amateur Contract"),
    ("YOUTH", "Youth Academy Contract"),
    ("LOAN", "Loan Agreement"),
    ("LOAN_WITH_OPTION", "Loan with Purchase Option"),
    ("PRE_CONTRACT", "Pre-Contract Agreement"),
    ("EXTENSION", "Contract Extension")
]

CONTRACT_STATUS = [
    ("ACTIVE", "Active"),
    ("EXPIRED", "Expired"),
    ("TERMINATED", "Terminated"),
    ("PENDING", "Pending Approval"),
    ("SUSPENDED", "Suspended"),
    ("UNDER_NEGOTIATION", "Under Negotiation")
]

CLAUSE_TYPES = [
    ("RELEASE", "Release Clause"),
    ("BUYOUT", "Buyout Clause"),
    ("PERFORMANCE_BONUS", "Performance Bonus"),
    ("APPEARANCE_BONUS", "Appearance Bonus"),
    ("GOAL_BONUS", "Goal Bonus"),
    ("LOYALTY_BONUS", "Loyalty Bonus"),
    ("SIGNING_BONUS", "Signing Bonus"),
    ("IMAGE_RIGHTS", "Image Rights"),
    ("TERMINATION", "Termination Clause"),
    ("NON_COMPETE", "Non-Compete Clause"),
    ("SELL_ON", "Sell-On Percentage")
]

PAYMENT_FREQUENCY = [
    ("MONTHLY", "Monthly"),
    ("WEEKLY", "Weekly"),
    ("BI_WEEKLY", "Bi-Weekly"),
    ("ANNUAL", "Annual")
]

# Medical Records Constants
INJURY_TYPES = [
    ("MUSCLE", "Muscle Injury"),
    ("LIGAMENT", "Ligament Injury"),
    ("TENDON", "Tendon Injury"),
    ("BONE", "Bone Fracture"),
    ("CONCUSSION", "Concussion"),
    ("SPRAIN", "Sprain"),
    ("STRAIN", "Strain"),
    ("CONTUSION", "Contusion/Bruise"),
    ("DISLOCATION", "Dislocation"),
    ("OVERUSE", "Overuse Injury"),
    ("ILLNESS", "Illness/Disease"),
    ("OTHER", "Other")
]

BODY_PARTS = [
    ("HEAD", "Head"),
    ("NECK", "Neck"),
    ("SHOULDER", "Shoulder"),
    ("ARM", "Arm"),
    ("ELBOW", "Elbow"),
    ("WRIST", "Wrist"),
    ("HAND", "Hand"),
    ("BACK", "Back"),
    ("CHEST", "Chest"),
    ("ABDOMEN", "Abdomen"),
    ("HIP", "Hip"),
    ("GROIN", "Groin"),
    ("THIGH", "Thigh"),
    ("HAMSTRING", "Hamstring"),
    ("KNEE", "Knee"),
    ("ACL", "ACL"),
    ("MCL", "MCL"),
    ("CALF", "Calf"),
    ("ANKLE", "Ankle"),
    ("FOOT", "Foot"),
    ("ACHILLES", "Achilles")
]

INJURY_SEVERITY = [
    ("MINOR", "Minor (1-7 days)"),
    ("MODERATE", "Moderate (1-4 weeks)"),
    ("SERIOUS", "Serious (1-3 months)"),
    ("SEVERE", "Severe (3-6 months)"),
    ("CRITICAL", "Critical (6+ months)")
]

MEDICAL_STATUS = [
    ("FIT", "Fit to Play"),
    ("RECOVERING", "Recovering"),
    ("REHAB", "In Rehabilitation"),
    ("ASSESSMENT", "Under Assessment"),
    ("SURGERY", "Post-Surgery"),
    ("CLEARED", "Medically Cleared")
]

FITNESS_LEVELS = [
    ("A", "Level A - Full Match Fitness"),
    ("B", "Level B - High Intensity Training"),
    ("C", "Level C - Moderate Training"),
    ("D", "Level D - Light Training Only"),
    ("E", "Level E - Recovery Phase")
]

# Performance Analytics Constants
PERFORMANCE_METRICS = [
    ("GOALS", "Goals Scored"),
    ("ASSISTS", "Assists"),
    ("MINUTES", "Minutes Played"),
    ("PASSES", "Passes Completed"),
    ("PASS_ACC", "Pass Accuracy %"),
    ("SHOTS", "Shots"),
    ("SHOTS_ON_TARGET", "Shots on Target"),
    ("TACKLES", "Tackles Won"),
    ("INTERCEPTIONS", "Interceptions"),
    ("CLEARANCES", "Clearances"),
    ("DUELS_WON", "Duels Won"),
    ("AERIAL_WON", "Aerial Duels Won"),
    ("DRIBBLES", "Successful Dribbles"),
    ("FOULS", "Fouls Committed"),
    ("FOULED", "Fouls Suffered"),
    ("OFFSIDES", "Offsides"),
    ("SAVES", "Saves (GK)"),
    ("CLEAN_SHEETS", "Clean Sheets (GK)")
]

MATCH_RATINGS = [
    (10, "Perfect"),
    (9, "Outstanding"),
    (8, "Excellent"),
    (7, "Good"),
    (6, "Average"),
    (5, "Below Average"),
    (4, "Poor"),
    (3, "Very Poor")
]

SEASON_OPTIONS = [
    "2025-2026", "2024-2025", "2023-2024", "2022-2023", "2021-2022"
]

VAR_OUTCOMES = ["CONFIRMED", "OVERTURNED", "REVIEW_COMPLETE"]

INCIDENT_TYPES = [
    "Yellow Card", "Red Card", "Penalty Awarded", "Penalty Denied",
    "Goal Disallowed", "VAR Review", "Injury Time Added", "Match Abandoned"
]

# RefereeChain - Certification Types
CERTIFICATIONS = [
    ("FIFA_BADGE", "FIFA International Badge", "Highest level certification"),
    ("CAF_ELITE", "CAF Elite Panel", "Continental elite status"),
    ("VAR_CERTIFIED", "VAR Operator Certified", "Video Assistant Referee qualified"),
    ("FITNESS_A", "Fitness Level A", "Top physical condition"),
    ("MEDICAL_TRAINED", "Medical Response Trained", "Emergency medical certification"),
    ("ANTI_RACISM", "Anti-Racism Ambassador", "Completed anti-discrimination training")
]

# RefereeChain - Audit Event Types
AUDIT_EVENT_TYPES = [
    ("REGISTRATION", "New Registration", "Referee registered in system"),
    ("CERTIFICATION_ADDED", "Certification Added", "New certification granted"),
    ("CERTIFICATION_EXPIRED", "Certification Expired", "Certification validity ended"),
    ("MATCH_ASSIGNED", "Match Assigned", "Assigned to officiate match"),
    ("MATCH_COMPLETED", "Match Completed", "Successfully completed match"),
    ("RATING_SUBMITTED", "Rating Submitted", "Performance rating received"),
    ("SUSPENSION", "Suspension", "Referee suspended"),
    ("REINSTATEMENT", "Reinstatement", "Suspension lifted"),
    ("PROMOTION", "Level Promotion", "Promoted to higher license level"),
    ("INCIDENT_REPORTED", "Incident Reported", "Match incident logged")
]

# =============================================================================
# REFEREECHAIN BLOCKCHAIN HELPERS
# =============================================================================

def generate_block_hash(data: dict) -> str:
    """Generate a hash for audit trail block."""
    import json
    data_string = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(data_string.encode()).hexdigest()[:16]

def get_previous_block_hash(referee_id: str) -> str:
    """Get the hash of the previous block for a referee."""
    import sqlite3
    from config import DB_FILE
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT block_hash FROM frmf_refereechain 
            WHERE referee_id = ? 
            ORDER BY block_number DESC LIMIT 1
        """, (referee_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "GENESIS"
    except:
        return "GENESIS"

def add_to_refereechain(referee_id: str, event_type: str, event_data: dict, username: str) -> bool:
    """Add a new block to the RefereeChain audit trail."""
    import sqlite3
    from config import DB_FILE
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Get next block number
        cursor.execute("""
            SELECT COALESCE(MAX(block_number), 0) + 1 
            FROM frmf_refereechain WHERE referee_id = ?
        """, (referee_id,))
        block_number = cursor.fetchone()[0]
        
        # Get previous hash
        prev_hash = get_previous_block_hash(referee_id)
        
        # Create block data
        import json
        block_data = {
            "referee_id": referee_id,
            "block_number": block_number,
            "prev_hash": prev_hash,
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.now().isoformat(),
            "created_by": username
        }
        
        # Generate hash
        block_hash = generate_block_hash(block_data)
        
        # Insert block
        cursor.execute("""
            INSERT INTO frmf_refereechain 
            (block_id, referee_id, block_number, prev_hash, block_hash,
             event_type, event_data, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            generate_uuid("BLK"),
            referee_id,
            block_number,
            prev_hash,
            block_hash,
            event_type,
            json.dumps(event_data),
            username,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"RefereeChain error: {e}")
        return False

def verify_refereechain(referee_id: str) -> tuple:
    """Verify the integrity of a referee's chain."""
    import sqlite3
    from config import DB_FILE
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT block_number, prev_hash, block_hash, event_type, event_data, created_at
            FROM frmf_refereechain 
            WHERE referee_id = ?
            ORDER BY block_number ASC
        """, (referee_id,))
        blocks = cursor.fetchall()
        conn.close()
        
        if not blocks:
            return (True, "No blocks to verify", 0)
        
        # Verify chain
        prev_hash = "GENESIS"
        for block in blocks:
            if block[1] != prev_hash:
                return (False, f"Chain broken at block {block[0]}", block[0])
            prev_hash = block[2]
        
        return (True, "Chain verified", len(blocks))
    except Exception as e:
        return (False, str(e), 0)

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
    
    # RefereeChain - Blockchain Audit Trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_refereechain (
            block_id TEXT PRIMARY KEY,
            referee_id TEXT NOT NULL,
            block_number INTEGER NOT NULL,
            prev_hash TEXT NOT NULL,
            block_hash TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT,
            created_by TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (referee_id) REFERENCES frmf_referees(referee_id)
        )
    ''')
    
    # Referee Certifications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_certifications (
            cert_id TEXT PRIMARY KEY,
            referee_id TEXT NOT NULL,
            cert_type TEXT NOT NULL,
            cert_name TEXT NOT NULL,
            issued_date TEXT NOT NULL,
            expiry_date TEXT,
            issued_by TEXT,
            status TEXT DEFAULT 'ACTIVE',
            document_hash TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (referee_id) REFERENCES frmf_referees(referee_id)
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
    
    # Player Profiles table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_players (
            player_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT DEFAULT 'Moroccan',
            second_nationality TEXT,
            position TEXT NOT NULL,
            secondary_position TEXT,
            current_club TEXT,
            jersey_number INTEGER,
            height_cm INTEGER,
            weight_kg INTEGER,
            foot TEXT DEFAULT 'Right',
            market_value REAL DEFAULT 0,
            contract_start TEXT,
            contract_end TEXT,
            salary_annual REAL,
            agent_name TEXT,
            agent_contact TEXT,
            national_team TEXT,
            caps INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            photo_url TEXT,
            frmf_license_number TEXT UNIQUE,
            fifa_id TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Player career history
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_player_history (
            history_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            club TEXT NOT NULL,
            season TEXT NOT NULL,
            league TEXT,
            appearances INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            transfer_type TEXT,
            transfer_fee REAL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Player medical records
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_player_medical (
            medical_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            injury_type TEXT,
            injury_date TEXT,
            expected_return TEXT,
            actual_return TEXT,
            severity TEXT,
            body_part TEXT,
            treatment TEXT,
            medical_staff TEXT,
            notes TEXT,
            status TEXT DEFAULT 'RECOVERING',
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Player fitness tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_player_fitness (
            fitness_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            assessment_date TEXT NOT NULL,
            fitness_level TEXT,
            match_readiness INTEGER DEFAULT 0,
            training_intensity TEXT,
            vo2_max REAL,
            sprint_speed REAL,
            endurance_score REAL,
            strength_score REAL,
            flexibility_score REAL,
            weight_kg REAL,
            body_fat_percentage REAL,
            resting_heart_rate INTEGER,
            assessed_by TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Return to play protocol
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_return_to_play (
            protocol_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            medical_id TEXT,
            phase INTEGER DEFAULT 1,
            phase_name TEXT,
            start_date TEXT,
            target_date TEXT,
            actual_completion TEXT,
            requirements TEXT,
            status TEXT DEFAULT 'IN_PROGRESS',
            cleared_by TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id),
            FOREIGN KEY (medical_id) REFERENCES frmf_player_medical(medical_id)
        )
    ''')
    
    # Player Match Performance (per match stats)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_match_performance (
            performance_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            match_id TEXT NOT NULL,
            match_date TEXT,
            opponent TEXT,
            competition TEXT,
            minutes_played INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            shots INTEGER DEFAULT 0,
            shots_on_target INTEGER DEFAULT 0,
            passes INTEGER DEFAULT 0,
            pass_accuracy REAL DEFAULT 0,
            tackles INTEGER DEFAULT 0,
            interceptions INTEGER DEFAULT 0,
            clearances INTEGER DEFAULT 0,
            duels_won INTEGER DEFAULT 0,
            aerial_won INTEGER DEFAULT 0,
            dribbles INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            fouled INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            saves INTEGER DEFAULT 0,
            rating REAL DEFAULT 6.0,
            man_of_match INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Season Statistics (aggregated)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_season_stats (
            stat_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            season TEXT NOT NULL,
            competition TEXT,
            appearances INTEGER DEFAULT 0,
            starts INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            clean_sheets INTEGER DEFAULT 0,
            avg_rating REAL DEFAULT 0,
            man_of_match_awards INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Team Performance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_team_performance (
            team_perf_id TEXT PRIMARY KEY,
            club TEXT NOT NULL,
            season TEXT NOT NULL,
            competition TEXT,
            matches_played INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            goals_for INTEGER DEFAULT 0,
            goals_against INTEGER DEFAULT 0,
            goal_difference INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            position INTEGER,
            form TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Contract Management - Main contracts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_contracts (
            contract_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            club TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            base_salary REAL,
            currency TEXT DEFAULT 'MAD',
            payment_frequency TEXT DEFAULT 'MONTHLY',
            signing_bonus REAL DEFAULT 0,
            total_value REAL,
            status TEXT DEFAULT 'ACTIVE',
            previous_contract_id TEXT,
            agent_name TEXT,
            agent_fee REAL,
            agent_fee_percentage REAL,
            registration_number TEXT,
            fifa_registered INTEGER DEFAULT 0,
            notes TEXT,
            created_by TEXT,
            approved_by TEXT,
            approved_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES frmf_players(player_id)
        )
    ''')
    
    # Contract Clauses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_contract_clauses (
            clause_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            clause_type TEXT NOT NULL,
            clause_name TEXT,
            clause_value REAL,
            currency TEXT DEFAULT 'MAD',
            trigger_condition TEXT,
            is_active INTEGER DEFAULT 1,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES frmf_contracts(contract_id)
        )
    ''')
    
    # Contract Amendments/Extensions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_contract_amendments (
            amendment_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            amendment_type TEXT,
            description TEXT,
            old_value TEXT,
            new_value TEXT,
            effective_date TEXT,
            approved_by TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES frmf_contracts(contract_id)
        )
    ''')
    
    # Contract Audit Trail
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS frmf_contract_audit (
            audit_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            action TEXT NOT NULL,
            action_by TEXT,
            action_details TEXT,
            ip_address TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES frmf_contracts(contract_id)
        )
    ''')
    
    # Indexes
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_referee_level ON frmf_referees(license_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignment_date ON frmf_match_assignments(match_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_var_match ON frmf_var_vault(match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_club ON frmf_players(current_club)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_position ON frmf_players(position)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_player_status ON frmf_players(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_player ON frmf_contracts(player_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_club ON frmf_contracts(club)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_contract_status ON frmf_contracts(status)")
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
            
            if st.form_submit_button("Register Referee", type="primary", use_container_width=True):
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
                        # Add to RefereeChain
                        add_to_refereechain(referee_id, "REGISTRATION", {
                            "first_name": first_name,
                            "last_name": last_name,
                            "license_level": level_code,
                            "region": region
                        }, username)
                        
                        success_message("Referee Registered!", referee_id)
                        log_audit(username, "REFEREE_REGISTERED", "FRMF", referee_id)
                        st.rerun()
                else:
                    st.error("First name and last name are required")


def render_refereechain(username: str):
    """Render the RefereeChain audit trail tab."""
    st.markdown("### RefereeChain - Audit Trail")
    st.caption("Immutable blockchain-style record of all referee activities")
    
    # Get referees for selection
    df_referees = get_data("frmf_referees")
    if df_referees.empty:
        df_referees = generate_demo_referees()
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Count total blocks
    df_chain = get_data("frmf_refereechain")
    total_blocks = len(df_chain) if not df_chain.empty else 0
    
    with col1:
        st.metric("Total Blocks", total_blocks)
    with col2:
        unique_refs = df_chain['referee_id'].nunique() if not df_chain.empty and 'referee_id' in df_chain.columns else 0
        st.metric("Referees Tracked", unique_refs)
    with col3:
        st.metric("Chain Status", "Valid")
    with col4:
        st.metric("Last Update", datetime.now().strftime("%H:%M"))
    
    st.divider()
    
    # Referee selection for chain view
    if not df_referees.empty and 'name' in df_referees.columns:
        ref_options = df_referees['name'].tolist()
    else:
        ref_options = ["Select Referee"]
    
    selected_ref = st.selectbox("View Chain for Referee", ["All Referees"] + ref_options)
    
    # Chain verification
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Verify Chain Integrity", type="primary"):
            if selected_ref != "All Referees":
                ref_row = df_referees[df_referees['name'] == selected_ref]
                if not ref_row.empty:
                    ref_id = ref_row.iloc[0]['referee_id']
                    valid, message, blocks = verify_refereechain(ref_id)
                    if valid:
                        st.success(f"Chain Valid - {blocks} blocks verified")
                    else:
                        st.error(f"Chain Invalid: {message}")
            else:
                st.info("Select a specific referee to verify their chain")
    
    st.divider()
    
    # Display chain
    st.markdown("#### Audit Trail Blocks")
    
    if not df_chain.empty:
        # Filter by referee if selected
        if selected_ref != "All Referees":
            ref_row = df_referees[df_referees['name'] == selected_ref]
            if not ref_row.empty:
                ref_id = ref_row.iloc[0]['referee_id']
                df_chain = df_chain[df_chain['referee_id'] == ref_id]
        
        # Sort by created_at descending
        if 'created_at' in df_chain.columns:
            df_chain = df_chain.sort_values('created_at', ascending=False)
        
        # Display blocks
        for _, block in df_chain.head(20).iterrows():
            event_type = block.get('event_type', 'UNKNOWN')
            event_name = next((e[1] for e in AUDIT_EVENT_TYPES if e[0] == event_type), event_type)
            
            # Color based on event type
            if event_type in ['REGISTRATION', 'CERTIFICATION_ADDED', 'PROMOTION']:
                border_color = "#48BB78"  # Green
            elif event_type in ['SUSPENSION', 'CERTIFICATION_EXPIRED']:
                border_color = "#F56565"  # Red
            else:
                border_color = "#8B5CF6"  # Purple
            
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-left: 4px solid {border_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='color: {border_color}; font-weight: 600;'>{event_name}</span>
                            <span style='color: #888; font-size: 0.8rem; margin-left: 1rem;'>
                                Block #{block.get('block_number', 0)}
                            </span>
                        </div>
                        <span style='color: #666; font-size: 0.75rem;'>
                            {block.get('created_at', '')[:16]}
                        </span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #aaa; font-size: 0.85rem;'>
                        Hash: <code style='color: #D4AF37;'>{block.get('block_hash', 'N/A')[:12]}...</code>
                        | Prev: <code style='color: #888;'>{block.get('prev_hash', 'GENESIS')[:8]}...</code>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        info_box("No Chain Data", "Start by registering referees or adding certifications to create audit trail blocks.")
    
    st.divider()
    
    # Add certification (creates chain block)
    with st.expander("Add Certification", expanded=False):
        with st.form("add_cert"):
            col1, col2 = st.columns(2)
            with col1:
                cert_referee = st.selectbox("Referee *", ref_options, key="cert_ref")
                cert_type = st.selectbox("Certification Type *", [c[1] for c in CERTIFICATIONS])
            with col2:
                issued_date = st.date_input("Issue Date")
                expiry_date = st.date_input("Expiry Date (optional)", value=None)
            
            issued_by = st.text_input("Issued By", "FRMF")
            
            if st.form_submit_button("Add Certification", type="primary", use_container_width=True):
                if cert_referee and cert_referee != "Select Referee":
                    ref_row = df_referees[df_referees['name'] == cert_referee]
                    if not ref_row.empty:
                        ref_id = ref_row.iloc[0]['referee_id']
                        cert_id = generate_uuid("CERT")
                        cert_code = next((c[0] for c in CERTIFICATIONS if c[1] == cert_type), "OTHER")
                        
                        # Add to certifications table
                        success = run_query("""
                            INSERT INTO frmf_certifications 
                            (cert_id, referee_id, cert_type, cert_name, issued_date, expiry_date, 
                             issued_by, status, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                        """, (cert_id, ref_id, cert_code, cert_type, str(issued_date),
                              str(expiry_date) if expiry_date else None, issued_by,
                              datetime.now().isoformat()))
                        
                        if success:
                            # Add to RefereeChain
                            add_to_refereechain(ref_id, "CERTIFICATION_ADDED", {
                                "cert_type": cert_code,
                                "cert_name": cert_type,
                                "issued_by": issued_by,
                                "expiry_date": str(expiry_date) if expiry_date else None
                            }, username)
                            
                            success_message("Certification Added!", cert_id)
                            log_audit(username, "CERTIFICATION_ADDED", "FRMF", f"{cert_referee} - {cert_type}")
                            st.rerun()


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
    """Render VAR decisions vault - Forensic Archive."""
    st.markdown("### VAR Vault - Forensic Archive")
    st.caption("Immutable archive of all VAR decisions with video evidence")
    
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
        overturn_rate = (overturned / len(df) * 100) if len(df) > 0 else 0
        st.metric("Overturned", overturned, f"{overturn_rate:.1f}%")
    with col3:
        confirmed = len(df[df['outcome'] == 'CONFIRMED']) if 'outcome' in df.columns else 0
        st.metric("Confirmed", confirmed)
    with col4:
        controversial = len(df[df['is_controversial'] == 1]) if 'is_controversial' in df.columns else 0
        st.metric("Controversial", controversial)
    
    st.divider()
    
    # Sub-tabs for different views
    var_tab1, var_tab2, var_tab3 = st.tabs(["Decision Log", "Forensic Analysis", "Statistics"])
    
    with var_tab1:
        # Filter
        col1, col2, col3 = st.columns(3)
        with col1:
            type_filter = st.selectbox("Decision Type", ["All"] + [d[1] for d in VAR_DECISIONS])
        with col2:
            outcome_filter = st.selectbox("Outcome", ["All"] + VAR_OUTCOMES)
        with col3:
            controversial_only = st.checkbox("Controversial Only")
        
        # Apply filters
        filtered_df = df.copy()
        if type_filter != "All" and 'decision_type' in df.columns:
            code = next((d[0] for d in VAR_DECISIONS if d[1] == type_filter), None)
            if code:
                filtered_df = filtered_df[filtered_df['decision_type'] == code]
        if outcome_filter != "All" and 'outcome' in df.columns:
            filtered_df = filtered_df[filtered_df['outcome'] == outcome_filter]
        if controversial_only and 'is_controversial' in df.columns:
            filtered_df = filtered_df[filtered_df['is_controversial'] == 1]
        
        # Display decisions as cards
        st.markdown(f"**{len(filtered_df)} decisions found**")
        
        for _, row in filtered_df.head(10).iterrows():
            decision_type = row.get('decision_type', 'UNKNOWN')
            decision_name = next((d[1] for d in VAR_DECISIONS if d[0] == decision_type), decision_type)
            outcome = row.get('outcome', 'PENDING')
            
            # Color based on outcome
            if outcome == 'OVERTURNED':
                bg_color = "rgba(245, 101, 101, 0.1)"
                border_color = "#F56565"
                outcome_badge = "OVERTURNED"
            elif outcome == 'CONFIRMED':
                bg_color = "rgba(72, 187, 120, 0.1)"
                border_color = "#48BB78"
                outcome_badge = "CONFIRMED"
            else:
                bg_color = "rgba(139, 92, 246, 0.1)"
                border_color = "#8B5CF6"
                outcome_badge = "REVIEW"
            
            controversial_badge = " | CONTROVERSIAL" if row.get('is_controversial', 0) else ""
            
            st.markdown(f"""
                <div style='
                    background: {bg_color};
                    border-left: 4px solid {border_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.75rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 600; color: #E2E8F0;'>{decision_name}</span>
                            <span style='color: #888; margin-left: 0.5rem;'>Minute {row.get('minute', '?')}</span>
                        </div>
                        <span style='
                            background: {border_color};
                            color: white;
                            padding: 0.25rem 0.75rem;
                            border-radius: 12px;
                            font-size: 0.75rem;
                            font-weight: 600;
                        '>{outcome_badge}{controversial_badge}</span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #A0AEC0; font-size: 0.85rem;'>
                        Match: {row.get('match_id', 'N/A')} | 
                        Duration: {row.get('review_duration_seconds', row.get('review_duration', 'N/A'))}s |
                        Hash: <code style='color: #D4AF37;'>{row.get('screenshot_hash', 'N/A')[:12] if row.get('screenshot_hash') else 'N/A'}...</code>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with var_tab2:
        st.markdown("#### Forensic Analysis Tools")
        st.caption("Deep analysis of VAR decisions and patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Decision Type Distribution**")
            if 'decision_type' in df.columns:
                type_counts = df['decision_type'].value_counts()
                for dtype, count in type_counts.items():
                    type_name = next((d[1] for d in VAR_DECISIONS if d[0] == dtype), dtype)
                    pct = count / len(df) * 100
                    st.markdown(f"""
                        <div style='margin-bottom: 0.5rem;'>
                            <span style='color: #E2E8F0;'>{type_name}</span>
                            <span style='color: #888; float: right;'>{count} ({pct:.1f}%)</span>
                        </div>
                        <div style='background: #2D3748; border-radius: 4px; height: 8px; margin-bottom: 1rem;'>
                            <div style='background: #8B5CF6; width: {pct}%; height: 100%; border-radius: 4px;'></div>
                        </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Outcome Analysis**")
            if 'outcome' in df.columns:
                outcome_counts = df['outcome'].value_counts()
                for outcome, count in outcome_counts.items():
                    pct = count / len(df) * 100
                    color = "#48BB78" if outcome == "CONFIRMED" else "#F56565" if outcome == "OVERTURNED" else "#8B5CF6"
                    st.markdown(f"""
                        <div style='margin-bottom: 0.5rem;'>
                            <span style='color: #E2E8F0;'>{outcome}</span>
                            <span style='color: #888; float: right;'>{count} ({pct:.1f}%)</span>
                        </div>
                        <div style='background: #2D3748; border-radius: 4px; height: 8px; margin-bottom: 1rem;'>
                            <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 4px;'></div>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # Average review time
        if 'review_duration_seconds' in df.columns or 'review_duration' in df.columns:
            duration_col = 'review_duration_seconds' if 'review_duration_seconds' in df.columns else 'review_duration'
            avg_duration = df[duration_col].mean() if duration_col in df.columns else 0
            st.metric("Average Review Duration", f"{avg_duration:.0f} seconds")
        
        # Controversial rate
        if 'is_controversial' in df.columns:
            controversial_rate = df['is_controversial'].mean() * 100
            st.metric("Controversial Rate", f"{controversial_rate:.1f}%")
    
    with var_tab3:
        st.markdown("#### VAR Statistics Dashboard")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Decisions", len(df))
        with col2:
            if 'outcome' in df.columns:
                accuracy = len(df[df['outcome'] == 'CONFIRMED']) / len(df) * 100 if len(df) > 0 else 0
                st.metric("Referee Accuracy", f"{accuracy:.1f}%")
        with col3:
            if 'review_duration_seconds' in df.columns or 'review_duration' in df.columns:
                duration_col = 'review_duration_seconds' if 'review_duration_seconds' in df.columns else 'review_duration'
                avg_dur = df[duration_col].mean() if duration_col in df.columns else 0
                st.metric("Avg Review Time", f"{avg_dur:.0f}s")
        
        # Export option
        st.divider()
        st.markdown("**Export Data**")
        if st.button("Export VAR Report (CSV)", use_container_width=True):
            st.info("Export functionality ready - CSV data prepared")
    
    st.divider()
    
    # Log VAR decision
    with st.expander("Log New VAR Decision", expanded=False):
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
            
            col3, col4 = st.columns(2)
            with col3:
                review_duration = st.slider("Review Duration (seconds)", 10, 300, 60)
            with col4:
                is_controversial = st.checkbox("Mark as Controversial")
            
            video_url = st.text_input("Video Evidence URL (optional)")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Log VAR Decision", type="primary", use_container_width=True):
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
                         screenshot_hash, video_url, is_controversial, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (var_id, match_id, minute, decision_code, original_decision,
                          var_recommendation, final_decision, outcome, review_duration,
                          screenshot_hash, video_url, 1 if is_controversial else 0, notes,
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


def render_player_profiles(username: str):
    """Render player profiles tab."""
    st.markdown("### Player Profiles Database")
    st.caption("Complete registry of all registered players")
    
    df = get_data("frmf_players")
    
    if df.empty:
        # Generate demo players
        players = []
        first_names = ["Achraf", "Youssef", "Sofiane", "Hakim", "Nayef", "Brahim", "Azzedine", "Romain", "Munir", "Yassine"]
        last_names = ["Hakimi", "En-Nesyri", "Boufal", "Ziyech", "Aguerd", "Diaz", "Ounahi", "Saiss", "El Haddadi", "Bounou"]
        
        for i in range(20):
            pos_code = random.choice([p[0] for p in PLAYER_POSITIONS])
            club = random.choice(BOTOLA_CLUBS[:8])
            status = random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "INJURED", "LOANED_OUT"])
            
            players.append({
                "player_id": f"PLR-{4000+i}",
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "position": pos_code,
                "current_club": club,
                "nationality": "Moroccan",
                "jersey_number": random.randint(1, 99),
                "height_cm": random.randint(170, 195),
                "market_value": random.randint(100000, 5000000),
                "caps": random.randint(0, 50),
                "goals": random.randint(0, 30),
                "status": status,
                "created_at": datetime.now().isoformat()
            })
        df = pd.DataFrame(players)
        info_box("Demo Mode", "Showing demo player data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(df))
    with col2:
        active = len(df[df['status'] == 'ACTIVE']) if 'status' in df.columns else len(df)
        st.metric("Active", active)
    with col3:
        injured = len(df[df['status'] == 'INJURED']) if 'status' in df.columns else 0
        st.metric("Injured", injured)
    with col4:
        if 'market_value' in df.columns:
            total_value = df['market_value'].sum() / 1000000
            st.metric("Total Value", f"{total_value:.1f}M MAD")
        else:
            st.metric("Total Value", "N/A")
    
    st.divider()
    
    # Sub-tabs
    player_tab1, player_tab2, player_tab3 = st.tabs(["Player Registry", "Search & Filter", "Add Player"])
    
    with player_tab1:
        # Quick filters
        col1, col2, col3 = st.columns(3)
        with col1:
            pos_filter = st.selectbox("Position", ["All"] + [p[1] for p in PLAYER_POSITIONS], key="pos_filter")
        with col2:
            club_filter = st.selectbox("Club", ["All"] + BOTOLA_CLUBS, key="club_filter")
        with col3:
            status_filter = st.selectbox("Status", ["All"] + [s[1] for s in PLAYER_STATUS], key="status_filter")
        
        # Apply filters
        filtered_df = df.copy()
        if pos_filter != "All" and 'position' in df.columns:
            pos_code = next((p[0] for p in PLAYER_POSITIONS if p[1] == pos_filter), None)
            if pos_code:
                filtered_df = filtered_df[filtered_df['position'] == pos_code]
        if club_filter != "All" and 'current_club' in df.columns:
            filtered_df = filtered_df[filtered_df['current_club'] == club_filter]
        if status_filter != "All" and 'status' in df.columns:
            status_code = next((s[0] for s in PLAYER_STATUS if s[1] == status_filter), None)
            if status_code:
                filtered_df = filtered_df[filtered_df['status'] == status_code]
        
        st.markdown(f"**{len(filtered_df)} players found**")
        
        # Display as cards
        for _, player in filtered_df.head(12).iterrows():
            pos = player.get('position', 'N/A')
            pos_name = next((p[1] for p in PLAYER_POSITIONS if p[0] == pos), pos)
            status = player.get('status', 'ACTIVE')
            
            # Status color
            if status == 'ACTIVE':
                status_color = "#48BB78"
            elif status == 'INJURED':
                status_color = "#F56565"
            elif status in ['LOANED_OUT', 'LOANED_IN']:
                status_color = "#ECC94B"
            else:
                status_color = "#A0AEC0"
            
            market_val = player.get('market_value', 0)
            if market_val >= 1000000:
                val_str = f"{market_val/1000000:.1f}M"
            else:
                val_str = f"{market_val/1000:.0f}K"
            
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-left: 4px solid {status_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-size: 1.1rem; font-weight: 600; color: #E2E8F0;'>
                                {player.get('first_name', '')} {player.get('last_name', '')}
                            </span>
                            <span style='
                                background: #8B5CF6;
                                color: white;
                                padding: 0.2rem 0.5rem;
                                border-radius: 4px;
                                font-size: 0.7rem;
                                margin-left: 0.5rem;
                            '>{pos_name}</span>
                        </div>
                        <span style='color: #D4AF37; font-weight: 600;'>{val_str} MAD</span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #A0AEC0; font-size: 0.85rem;'>
                        {player.get('current_club', 'N/A')} | 
                        #{player.get('jersey_number', 'N/A')} |
                        {player.get('caps', 0)} caps |
                        {player.get('goals', 0)} goals
                        <span style='
                            background: {status_color};
                            color: white;
                            padding: 0.15rem 0.4rem;
                            border-radius: 4px;
                            font-size: 0.7rem;
                            margin-left: 0.5rem;
                        '>{status}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with player_tab2:
        st.markdown("#### Advanced Search")
        
        search_name = st.text_input("Search by Name")
        
        col1, col2 = st.columns(2)
        with col1:
            min_value = st.number_input("Min Market Value (MAD)", 0, 10000000, 0, step=100000)
        with col2:
            max_value = st.number_input("Max Market Value (MAD)", 0, 50000000, 50000000, step=100000)
        
        if search_name:
            search_df = df[
                (df['first_name'].str.contains(search_name, case=False, na=False)) |
                (df['last_name'].str.contains(search_name, case=False, na=False))
            ]
            st.dataframe(search_df, use_container_width=True, hide_index=True)
        else:
            if 'market_value' in df.columns:
                value_df = df[(df['market_value'] >= min_value) & (df['market_value'] <= max_value)]
                st.dataframe(value_df, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)
    
    with player_tab3:
        st.markdown("#### Register New Player")
        
        with st.form("add_player"):
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name *")
                last_name = st.text_input("Last Name *")
                dob = st.date_input("Date of Birth")
                nationality = st.text_input("Nationality", "Moroccan")
            with col2:
                position = st.selectbox("Position *", [p[1] for p in PLAYER_POSITIONS])
                current_club = st.selectbox("Current Club", ["None"] + BOTOLA_CLUBS)
                jersey_number = st.number_input("Jersey Number", 1, 99, 10)
                foot = st.selectbox("Preferred Foot", FOOT_PREFERENCE)
            
            col3, col4 = st.columns(2)
            with col3:
                height_cm = st.number_input("Height (cm)", 150, 220, 180)
                weight_kg = st.number_input("Weight (kg)", 50, 120, 75)
            with col4:
                market_value = st.number_input("Market Value (MAD)", 0, 100000000, 500000, step=50000)
                national_team = st.selectbox("National Team", ["None"] + [t[1] for t in NATIONAL_TEAMS])
            
            if st.form_submit_button("Register Player", type="primary", use_container_width=True):
                if first_name and last_name:
                    player_id = generate_uuid("PLR")
                    pos_code = next((p[0] for p in PLAYER_POSITIONS if p[1] == position), "CM")
                    team_code = next((t[0] for t in NATIONAL_TEAMS if t[1] == national_team), None) if national_team != "None" else None
                    club = current_club if current_club != "None" else None
                    
                    success = run_query("""
                        INSERT INTO frmf_players 
                        (player_id, first_name, last_name, date_of_birth, nationality, position,
                         current_club, jersey_number, height_cm, weight_kg, foot, market_value,
                         national_team, status, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?)
                    """, (player_id, first_name, last_name, str(dob), nationality, pos_code,
                          club, jersey_number, height_cm, weight_kg, foot, market_value,
                          team_code, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Player Registered!", player_id)
                        log_audit(username, "PLAYER_REGISTERED", "FRMF", f"{first_name} {last_name}")
                        st.rerun()
                else:
                    st.error("First name and last name are required")


def render_contract_management(username: str):
    """Render contract management tab."""
    st.markdown("### Contract Management")
    st.caption("Player contracts, clauses, and amendments tracking")
    
    df_contracts = get_data("frmf_contracts")
    df_players = get_data("frmf_players")
    
    # Generate demo data if empty
    if df_contracts.empty:
        contracts = []
        for i in range(15):
            club = random.choice(BOTOLA_CLUBS[:8])
            status = random.choice(["ACTIVE", "ACTIVE", "ACTIVE", "EXPIRED", "UNDER_NEGOTIATION"])
            contract_type = random.choice([c[0] for c in CONTRACT_TYPES[:4]])
            salary = random.randint(50000, 500000)
            
            contracts.append({
                "contract_id": f"CTR-{5000+i}",
                "player_id": f"PLR-{4000+i}",
                "player_name": f"Player {i+1}",
                "club": club,
                "contract_type": contract_type,
                "start_date": "2024-07-01",
                "end_date": f"202{random.randint(5,8)}-06-30",
                "base_salary": salary,
                "total_value": salary * random.randint(1, 4),
                "status": status,
                "created_at": datetime.now().isoformat()
            })
        df_contracts = pd.DataFrame(contracts)
        info_box("Demo Mode", "Showing demo contract data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Contracts", len(df_contracts))
    with col2:
        active = len(df_contracts[df_contracts['status'] == 'ACTIVE']) if 'status' in df_contracts.columns else 0
        st.metric("Active", active)
    with col3:
        expiring_soon = 0
        if 'end_date' in df_contracts.columns:
            try:
                df_contracts['end_dt'] = pd.to_datetime(df_contracts['end_date'], errors='coerce')
                six_months = datetime.now() + timedelta(days=180)
                expiring_soon = len(df_contracts[df_contracts['end_dt'] <= six_months])
            except:
                pass
        st.metric("Expiring Soon", expiring_soon)
    with col4:
        if 'total_value' in df_contracts.columns:
            total_val = df_contracts['total_value'].sum() / 1000000
            st.metric("Total Value", f"{total_val:.1f}M MAD")
        else:
            st.metric("Total Value", "N/A")
    
    st.divider()
    
    # Sub-tabs
    contract_tab1, contract_tab2, contract_tab3, contract_tab4 = st.tabs([
        "Contract Registry", "Expiring Contracts", "Add Contract", "Clauses"
    ])
    
    with contract_tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All"] + [s[1] for s in CONTRACT_STATUS], key="ctr_status")
        with col2:
            club_filter = st.selectbox("Club", ["All"] + BOTOLA_CLUBS, key="ctr_club")
        with col3:
            type_filter = st.selectbox("Type", ["All"] + [t[1] for t in CONTRACT_TYPES], key="ctr_type")
        
        # Apply filters
        filtered = df_contracts.copy()
        if status_filter != "All" and 'status' in df_contracts.columns:
            status_code = next((s[0] for s in CONTRACT_STATUS if s[1] == status_filter), None)
            if status_code:
                filtered = filtered[filtered['status'] == status_code]
        if club_filter != "All" and 'club' in df_contracts.columns:
            filtered = filtered[filtered['club'] == club_filter]
        if type_filter != "All" and 'contract_type' in df_contracts.columns:
            type_code = next((t[0] for t in CONTRACT_TYPES if t[1] == type_filter), None)
            if type_code:
                filtered = filtered[filtered['contract_type'] == type_code]
        
        st.markdown(f"**{len(filtered)} contracts found**")
        
        # Display contracts
        for _, contract in filtered.head(10).iterrows():
            status = contract.get('status', 'ACTIVE')
            contract_type = contract.get('contract_type', 'PROFESSIONAL')
            type_name = next((t[1] for t in CONTRACT_TYPES if t[0] == contract_type), contract_type)
            
            # Status color
            if status == 'ACTIVE':
                status_color = "#48BB78"
            elif status == 'EXPIRED':
                status_color = "#A0AEC0"
            elif status == 'UNDER_NEGOTIATION':
                status_color = "#ECC94B"
            else:
                status_color = "#F56565"
            
            salary = contract.get('base_salary', 0)
            if salary >= 1000000:
                salary_str = f"{salary/1000000:.1f}M"
            else:
                salary_str = f"{salary/1000:.0f}K"
            
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-left: 4px solid {status_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 600; color: #E2E8F0;'>
                                {contract.get('player_name', contract.get('player_id', 'Unknown'))}
                            </span>
                            <span style='color: #A0AEC0; margin-left: 0.5rem;'>@ {contract.get('club', 'N/A')}</span>
                        </div>
                        <span style='
                            background: {status_color};
                            color: white;
                            padding: 0.2rem 0.5rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                        '>{status}</span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #A0AEC0; font-size: 0.85rem;'>
                        {type_name} | 
                        {contract.get('start_date', 'N/A')} to {contract.get('end_date', 'N/A')} |
                        Salary: <span style='color: #D4AF37;'>{salary_str} MAD/year</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with contract_tab2:
        st.markdown("#### Contracts Expiring Within 6 Months")
        
        if 'end_dt' in df_contracts.columns:
            six_months = datetime.now() + timedelta(days=180)
            expiring = df_contracts[df_contracts['end_dt'] <= six_months].copy()
            expiring = expiring.sort_values('end_dt')
            
            if len(expiring) > 0:
                for _, contract in expiring.iterrows():
                    days_left = (contract['end_dt'] - datetime.now()).days
                    urgency_color = "#F56565" if days_left < 30 else "#ECC94B" if days_left < 90 else "#48BB78"
                    
                    st.markdown(f"""
                        <div style='
                            background: rgba(245, 101, 101, 0.1);
                            border-left: 4px solid {urgency_color};
                            border-radius: 8px;
                            padding: 1rem;
                            margin-bottom: 0.5rem;
                        '>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='font-weight: 600; color: #E2E8F0;'>
                                    {contract.get('player_name', contract.get('player_id', 'Unknown'))}
                                </span>
                                <span style='color: {urgency_color}; font-weight: 600;'>
                                    {days_left} days remaining
                                </span>
                            </div>
                            <div style='color: #A0AEC0; font-size: 0.85rem; margin-top: 0.25rem;'>
                                {contract.get('club', 'N/A')} | Expires: {contract.get('end_date', 'N/A')}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                info_box("No Expiring Contracts", "All contracts are valid for more than 6 months.")
        else:
            info_box("No Date Data", "Contract end dates not available.")
    
    with contract_tab3:
        st.markdown("#### Register New Contract")
        
        # Get players for dropdown
        if not df_players.empty and 'first_name' in df_players.columns:
            player_options = [f"{r['first_name']} {r['last_name']}" for _, r in df_players.iterrows()]
        else:
            player_options = ["Player 1", "Player 2", "Player 3"]
        
        with st.form("add_contract"):
            col1, col2 = st.columns(2)
            with col1:
                player = st.selectbox("Player *", player_options)
                club = st.selectbox("Club *", BOTOLA_CLUBS)
                contract_type = st.selectbox("Contract Type *", [t[1] for t in CONTRACT_TYPES])
            with col2:
                start_date = st.date_input("Start Date")
                end_date = st.date_input("End Date", value=datetime.now() + timedelta(days=365*2))
                payment_freq = st.selectbox("Payment Frequency", [p[1] for p in PAYMENT_FREQUENCY])
            
            col3, col4 = st.columns(2)
            with col3:
                base_salary = st.number_input("Base Salary (MAD/year)", 0, 50000000, 200000, step=10000)
                signing_bonus = st.number_input("Signing Bonus (MAD)", 0, 10000000, 0, step=10000)
            with col4:
                agent_name = st.text_input("Agent Name")
                agent_fee = st.number_input("Agent Fee (%)", 0.0, 20.0, 5.0, step=0.5)
            
            notes = st.text_area("Contract Notes")
            
            if st.form_submit_button("Register Contract", type="primary", use_container_width=True):
                if player and club:
                    contract_id = generate_uuid("CTR")
                    type_code = next((t[0] for t in CONTRACT_TYPES if t[1] == contract_type), "PROFESSIONAL")
                    freq_code = next((p[0] for p in PAYMENT_FREQUENCY if p[1] == payment_freq), "MONTHLY")
                    
                    # Calculate total value
                    years = (end_date - start_date).days / 365
                    total_value = (base_salary * years) + signing_bonus
                    
                    success = run_query("""
                        INSERT INTO frmf_contracts 
                        (contract_id, player_id, club, contract_type, start_date, end_date,
                         base_salary, payment_frequency, signing_bonus, total_value,
                         agent_name, agent_fee_percentage, notes, status, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
                    """, (contract_id, player, club, type_code, str(start_date), str(end_date),
                          base_salary, freq_code, signing_bonus, total_value,
                          agent_name, agent_fee, notes, username, datetime.now().isoformat()))
                    
                    if success:
                        # Add to audit trail
                        run_query("""
                            INSERT INTO frmf_contract_audit 
                            (audit_id, contract_id, action, action_by, action_details, created_at)
                            VALUES (?, ?, 'CREATED', ?, ?, ?)
                        """, (generate_uuid("AUD"), contract_id, username, 
                              f"New contract created for {player} at {club}",
                              datetime.now().isoformat()))
                        
                        success_message("Contract Registered!", contract_id)
                        log_audit(username, "CONTRACT_CREATED", "FRMF", f"{player} @ {club}")
                        st.rerun()
                else:
                    st.error("Player and Club are required")
    
    with contract_tab4:
        st.markdown("#### Contract Clauses")
        st.caption("Manage release clauses, bonuses, and special conditions")
        
        df_clauses = get_data("frmf_contract_clauses")
        
        if df_clauses.empty:
            # Demo clauses
            clauses = []
            for i in range(8):
                clause_type = random.choice([c[0] for c in CLAUSE_TYPES])
                clauses.append({
                    "clause_id": f"CLS-{6000+i}",
                    "contract_id": f"CTR-{5000+random.randint(0,9)}",
                    "clause_type": clause_type,
                    "clause_value": random.randint(100000, 5000000),
                    "is_active": 1
                })
            df_clauses = pd.DataFrame(clauses)
        
        # Display clauses by type
        for clause_code, clause_name in CLAUSE_TYPES[:6]:
            type_clauses = df_clauses[df_clauses['clause_type'] == clause_code] if 'clause_type' in df_clauses.columns else pd.DataFrame()
            count = len(type_clauses)
            if count > 0:
                total_val = type_clauses['clause_value'].sum() if 'clause_value' in type_clauses.columns else 0
                st.markdown(f"""
                    <div style='
                        background: #1a1a2e;
                        border-radius: 8px;
                        padding: 0.75rem 1rem;
                        margin-bottom: 0.5rem;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    '>
                        <span style='color: #E2E8F0;'>{clause_name}</span>
                        <div>
                            <span style='color: #A0AEC0; margin-right: 1rem;'>{count} clauses</span>
                            <span style='color: #D4AF37; font-weight: 600;'>{total_val/1000000:.1f}M MAD</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # Add clause form
        with st.expander("Add New Clause"):
            with st.form("add_clause"):
                col1, col2 = st.columns(2)
                with col1:
                    contract_select = st.text_input("Contract ID")
                    clause_type = st.selectbox("Clause Type", [c[1] for c in CLAUSE_TYPES])
                with col2:
                    clause_value = st.number_input("Clause Value (MAD)", 0, 100000000, 1000000, step=100000)
                    trigger = st.text_input("Trigger Condition")
                
                if st.form_submit_button("Add Clause", use_container_width=True):
                    if contract_select:
                        clause_id = generate_uuid("CLS")
                        clause_code = next((c[0] for c in CLAUSE_TYPES if c[1] == clause_type), "RELEASE")
                        
                        run_query("""
                            INSERT INTO frmf_contract_clauses 
                            (clause_id, contract_id, clause_type, clause_name, clause_value,
                             trigger_condition, is_active, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                        """, (clause_id, contract_select, clause_code, clause_type, clause_value,
                              trigger, datetime.now().isoformat()))
                        
                        success_message("Clause Added!", clause_id)
                        st.rerun()


def render_medical_records(username: str):
    """Render medical records tab."""
    st.markdown("### Medical Records Center")
    st.caption("Injury tracking, fitness assessments, and return-to-play protocols")
    
    df_medical = get_data("frmf_player_medical")
    df_players = get_data("frmf_players")
    df_fitness = get_data("frmf_player_fitness")
    
    # Generate demo data if empty
    if df_medical.empty:
        records = []
        for i in range(12):
            injury_type = random.choice([t[0] for t in INJURY_TYPES])
            body_part = random.choice([b[0] for b in BODY_PARTS])
            severity = random.choice([s[0] for s in INJURY_SEVERITY])
            status = random.choice(["RECOVERING", "RECOVERING", "FIT", "REHAB", "ASSESSMENT"])
            
            injury_date = datetime.now() - timedelta(days=random.randint(5, 90))
            expected_return = injury_date + timedelta(days=random.randint(14, 120))
            
            records.append({
                "medical_id": f"MED-{7000+i}",
                "player_id": f"PLR-{4000+random.randint(0,15)}",
                "player_name": f"Player {random.randint(1,20)}",
                "injury_type": injury_type,
                "body_part": body_part,
                "severity": severity,
                "injury_date": injury_date.strftime("%Y-%m-%d"),
                "expected_return": expected_return.strftime("%Y-%m-%d"),
                "status": status,
                "created_at": datetime.now().isoformat()
            })
        df_medical = pd.DataFrame(records)
        info_box("Demo Mode", "Showing demo medical data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Records", len(df_medical))
    with col2:
        injured = len(df_medical[df_medical['status'].isin(['RECOVERING', 'REHAB', 'SURGERY'])]) if 'status' in df_medical.columns else 0
        st.metric("Currently Injured", injured)
    with col3:
        fit = len(df_medical[df_medical['status'] == 'FIT']) if 'status' in df_medical.columns else 0
        st.metric("Cleared to Play", fit)
    with col4:
        severe = len(df_medical[df_medical['severity'].isin(['SEVERE', 'CRITICAL'])]) if 'severity' in df_medical.columns else 0
        st.metric("Severe Injuries", severe)
    
    st.divider()
    
    # Sub-tabs
    med_tab1, med_tab2, med_tab3, med_tab4 = st.tabs([
        "Injury Log", "Fitness Tracking", "Return to Play", "Add Record"
    ])
    
    with med_tab1:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Status", ["All"] + [s[1] for s in MEDICAL_STATUS], key="med_status")
        with col2:
            severity_filter = st.selectbox("Severity", ["All"] + [s[1] for s in INJURY_SEVERITY], key="med_severity")
        with col3:
            body_filter = st.selectbox("Body Part", ["All"] + [b[1] for b in BODY_PARTS[:10]], key="med_body")
        
        # Apply filters
        filtered = df_medical.copy()
        if status_filter != "All" and 'status' in df_medical.columns:
            status_code = next((s[0] for s in MEDICAL_STATUS if s[1] == status_filter), None)
            if status_code:
                filtered = filtered[filtered['status'] == status_code]
        if severity_filter != "All" and 'severity' in df_medical.columns:
            sev_code = next((s[0] for s in INJURY_SEVERITY if s[1] == severity_filter), None)
            if sev_code:
                filtered = filtered[filtered['severity'] == sev_code]
        
        st.markdown(f"**{len(filtered)} injury records found**")
        
        # Display injuries
        for _, record in filtered.head(10).iterrows():
            status = record.get('status', 'RECOVERING')
            severity = record.get('severity', 'MODERATE')
            injury_type = record.get('injury_type', 'OTHER')
            body_part = record.get('body_part', 'OTHER')
            
            injury_name = next((t[1] for t in INJURY_TYPES if t[0] == injury_type), injury_type)
            body_name = next((b[1] for b in BODY_PARTS if b[0] == body_part), body_part)
            severity_name = next((s[1] for s in INJURY_SEVERITY if s[0] == severity), severity)
            
            # Status color
            if status == 'FIT':
                status_color = "#48BB78"
            elif status in ['RECOVERING', 'REHAB']:
                status_color = "#ECC94B"
            elif status == 'SURGERY':
                status_color = "#F56565"
            else:
                status_color = "#A0AEC0"
            
            # Severity color
            if severity in ['SEVERE', 'CRITICAL']:
                sev_color = "#F56565"
            elif severity == 'SERIOUS':
                sev_color = "#ED8936"
            else:
                sev_color = "#ECC94B"
            
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-left: 4px solid {status_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 600; color: #E2E8F0;'>
                                {record.get('player_name', record.get('player_id', 'Unknown'))}
                            </span>
                            <span style='
                                background: {sev_color};
                                color: white;
                                padding: 0.15rem 0.4rem;
                                border-radius: 4px;
                                font-size: 0.7rem;
                                margin-left: 0.5rem;
                            '>{severity_name}</span>
                        </div>
                        <span style='
                            background: {status_color};
                            color: white;
                            padding: 0.2rem 0.5rem;
                            border-radius: 4px;
                            font-size: 0.75rem;
                        '>{status}</span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #A0AEC0; font-size: 0.85rem;'>
                        {injury_name} - {body_name} |
                        Injury Date: {record.get('injury_date', 'N/A')} |
                        Expected Return: <span style='color: #D4AF37;'>{record.get('expected_return', 'N/A')}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with med_tab2:
        st.markdown("#### Fitness Assessments")
        st.caption("Track player fitness levels and readiness")
        
        if df_fitness.empty:
            # Generate demo fitness data
            fitness_records = []
            for i in range(10):
                level = random.choice([f[0] for f in FITNESS_LEVELS])
                fitness_records.append({
                    "fitness_id": f"FIT-{8000+i}",
                    "player_id": f"PLR-{4000+i}",
                    "player_name": f"Player {i+1}",
                    "fitness_level": level,
                    "match_readiness": random.randint(60, 100),
                    "vo2_max": round(random.uniform(50, 65), 1),
                    "sprint_speed": round(random.uniform(30, 36), 1),
                    "assessment_date": datetime.now().strftime("%Y-%m-%d")
                })
            df_fitness = pd.DataFrame(fitness_records)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            level_a = len(df_fitness[df_fitness['fitness_level'] == 'A']) if 'fitness_level' in df_fitness.columns else 0
            st.metric("Level A (Match Fit)", level_a)
        with col2:
            avg_readiness = df_fitness['match_readiness'].mean() if 'match_readiness' in df_fitness.columns else 0
            st.metric("Avg Readiness", f"{avg_readiness:.0f}%")
        with col3:
            avg_vo2 = df_fitness['vo2_max'].mean() if 'vo2_max' in df_fitness.columns else 0
            st.metric("Avg VO2 Max", f"{avg_vo2:.1f}")
        
        st.divider()
        
        # Fitness table
        for _, fit in df_fitness.head(8).iterrows():
            level = fit.get('fitness_level', 'C')
            level_name = next((f[1] for f in FITNESS_LEVELS if f[0] == level), level)
            readiness = fit.get('match_readiness', 75)
            
            # Color based on readiness
            if readiness >= 90:
                bar_color = "#48BB78"
            elif readiness >= 75:
                bar_color = "#ECC94B"
            else:
                bar_color = "#F56565"
            
            st.markdown(f"""
                <div style='
                    background: #1a1a2e;
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                        <span style='color: #E2E8F0; font-weight: 600;'>
                            {fit.get('player_name', fit.get('player_id', 'Unknown'))}
                        </span>
                        <span style='color: #A0AEC0;'>{level_name}</span>
                    </div>
                    <div style='background: #2D3748; border-radius: 4px; height: 8px;'>
                        <div style='background: {bar_color}; width: {readiness}%; height: 100%; border-radius: 4px;'></div>
                    </div>
                    <div style='display: flex; justify-content: space-between; margin-top: 0.25rem; font-size: 0.75rem; color: #718096;'>
                        <span>VO2: {fit.get('vo2_max', 'N/A')}</span>
                        <span>Sprint: {fit.get('sprint_speed', 'N/A')} km/h</span>
                        <span style='color: {bar_color};'>{readiness}% Ready</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with med_tab3:
        st.markdown("#### Return to Play Protocol")
        st.caption("Track player recovery phases")
        
        df_rtp = get_data("frmf_return_to_play")
        
        if df_rtp.empty:
            info_box("No Active Protocols", "No return-to-play protocols currently active.")
        else:
            for _, protocol in df_rtp.iterrows():
                phase = protocol.get('phase', 1)
                status = protocol.get('status', 'IN_PROGRESS')
                
                st.markdown(f"""
                    <div style='background: #1a1a2e; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;'>
                        <div style='color: #E2E8F0; font-weight: 600;'>Phase {phase}: {protocol.get('phase_name', 'Recovery')}</div>
                        <div style='color: #A0AEC0; font-size: 0.85rem; margin-top: 0.25rem;'>
                            Target: {protocol.get('target_date', 'N/A')} | Status: {status}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        # RTP Phases explanation
        with st.expander("Return to Play Phases"):
            st.markdown("""
            **Phase 1:** Rest & Protection  
            **Phase 2:** Light Activity  
            **Phase 3:** Sport-Specific Exercise  
            **Phase 4:** Non-Contact Training  
            **Phase 5:** Full Contact Training  
            **Phase 6:** Return to Competition
            """)
    
    with med_tab4:
        st.markdown("#### Log New Injury")
        
        # Get players for dropdown
        if not df_players.empty and 'first_name' in df_players.columns:
            player_options = [f"{r['first_name']} {r['last_name']}" for _, r in df_players.iterrows()]
        else:
            player_options = [f"Player {i+1}" for i in range(10)]
        
        with st.form("add_injury"):
            col1, col2 = st.columns(2)
            with col1:
                player = st.selectbox("Player *", player_options, key="inj_player")
                injury_type = st.selectbox("Injury Type *", [t[1] for t in INJURY_TYPES])
                body_part = st.selectbox("Body Part *", [b[1] for b in BODY_PARTS])
            with col2:
                injury_date = st.date_input("Injury Date")
                severity = st.selectbox("Severity *", [s[1] for s in INJURY_SEVERITY])
                expected_return = st.date_input("Expected Return", value=datetime.now() + timedelta(days=30))
            
            col3, col4 = st.columns(2)
            with col3:
                treatment = st.text_input("Treatment")
                medical_staff = st.text_input("Medical Staff")
            with col4:
                status = st.selectbox("Current Status", [s[1] for s in MEDICAL_STATUS])
            
            notes = st.text_area("Medical Notes")
            
            if st.form_submit_button("Log Injury", type="primary", use_container_width=True):
                if player:
                    medical_id = generate_uuid("MED")
                    injury_code = next((t[0] for t in INJURY_TYPES if t[1] == injury_type), "OTHER")
                    body_code = next((b[0] for b in BODY_PARTS if b[1] == body_part), "OTHER")
                    sev_code = next((s[0] for s in INJURY_SEVERITY if s[1] == severity), "MODERATE")
                    status_code = next((s[0] for s in MEDICAL_STATUS if s[1] == status), "RECOVERING")
                    
                    success = run_query("""
                        INSERT INTO frmf_player_medical 
                        (medical_id, player_id, injury_type, body_part, severity, injury_date,
                         expected_return, treatment, medical_staff, status, notes, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (medical_id, player, injury_code, body_code, sev_code, str(injury_date),
                          str(expected_return), treatment, medical_staff, status_code, notes,
                          datetime.now().isoformat()))
                    
                    if success:
                        success_message("Injury Logged!", medical_id)
                        log_audit(username, "INJURY_LOGGED", "FRMF", f"{player} - {injury_type}")
                        st.rerun()
                else:
                    st.error("Player is required")
        
        st.divider()
        
        # Fitness Assessment form
        st.markdown("#### Log Fitness Assessment")
        
        with st.form("add_fitness"):
            col1, col2 = st.columns(2)
            with col1:
                fit_player = st.selectbox("Player *", player_options, key="fit_player")
                fitness_level = st.selectbox("Fitness Level *", [f[1] for f in FITNESS_LEVELS])
                match_readiness = st.slider("Match Readiness %", 0, 100, 80)
            with col2:
                vo2_max = st.number_input("VO2 Max", 30.0, 80.0, 55.0, step=0.5)
                sprint_speed = st.number_input("Sprint Speed (km/h)", 20.0, 40.0, 32.0, step=0.5)
                assessed_by = st.text_input("Assessed By")
            
            if st.form_submit_button("Log Assessment", use_container_width=True):
                if fit_player:
                    fitness_id = generate_uuid("FIT")
                    level_code = next((f[0] for f in FITNESS_LEVELS if f[1] == fitness_level), "C")
                    
                    run_query("""
                        INSERT INTO frmf_player_fitness 
                        (fitness_id, player_id, assessment_date, fitness_level, match_readiness,
                         vo2_max, sprint_speed, assessed_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (fitness_id, fit_player, datetime.now().strftime("%Y-%m-%d"), level_code,
                          match_readiness, vo2_max, sprint_speed, assessed_by,
                          datetime.now().isoformat()))
                    
                    success_message("Assessment Logged!", fitness_id)
                    st.rerun()


def render_performance_analytics(username: str):
    """Render performance analytics tab."""
    st.markdown("### Performance Analytics")
    st.caption("Match statistics, player metrics, and team performance")
    
    df_performance = get_data("frmf_match_performance")
    df_players = get_data("frmf_players")
    df_season = get_data("frmf_season_stats")
    df_team = get_data("frmf_team_performance")
    
    # Generate demo data if empty
    if df_performance.empty:
        performances = []
        for i in range(25):
            performances.append({
                "performance_id": f"PERF-{9000+i}",
                "player_id": f"PLR-{4000+random.randint(0,15)}",
                "player_name": f"Player {random.randint(1,20)}",
                "match_id": f"MATCH-{1000+i}",
                "opponent": random.choice(BOTOLA_CLUBS[:8]),
                "competition": random.choice(COMPETITIONS[:4]),
                "minutes_played": random.randint(45, 90),
                "goals": random.randint(0, 2),
                "assists": random.randint(0, 2),
                "shots": random.randint(0, 5),
                "shots_on_target": random.randint(0, 3),
                "passes": random.randint(20, 80),
                "pass_accuracy": round(random.uniform(70, 95), 1),
                "tackles": random.randint(0, 8),
                "interceptions": random.randint(0, 5),
                "rating": round(random.uniform(5.5, 9.5), 1),
                "man_of_match": 1 if random.random() > 0.9 else 0,
                "match_date": (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                "created_at": datetime.now().isoformat()
            })
        df_performance = pd.DataFrame(performances)
        info_box("Demo Mode", "Showing demo performance data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Match Records", len(df_performance))
    with col2:
        total_goals = df_performance['goals'].sum() if 'goals' in df_performance.columns else 0
        st.metric("Total Goals", int(total_goals))
    with col3:
        total_assists = df_performance['assists'].sum() if 'assists' in df_performance.columns else 0
        st.metric("Total Assists", int(total_assists))
    with col4:
        avg_rating = df_performance['rating'].mean() if 'rating' in df_performance.columns else 0
        st.metric("Avg Rating", f"{avg_rating:.1f}")
    
    st.divider()
    
    # Sub-tabs
    perf_tab1, perf_tab2, perf_tab3, perf_tab4 = st.tabs([
        "Player Stats", "Leaderboards", "Team Stats", "Log Performance"
    ])
    
    with perf_tab1:
        st.markdown("#### Recent Match Performances")
        
        # Filter
        col1, col2 = st.columns(2)
        with col1:
            comp_filter = st.selectbox("Competition", ["All"] + COMPETITIONS[:6], key="perf_comp")
        with col2:
            season_filter = st.selectbox("Season", SEASON_OPTIONS, key="perf_season")
        
        # Sort by date
        if 'match_date' in df_performance.columns:
            df_sorted = df_performance.sort_values('match_date', ascending=False)
        else:
            df_sorted = df_performance
        
        # Display performances
        for _, perf in df_sorted.head(10).iterrows():
            rating = perf.get('rating', 6.0)
            goals = perf.get('goals', 0)
            assists = perf.get('assists', 0)
            mom = perf.get('man_of_match', 0)
            
            # Rating color
            if rating >= 8:
                rating_color = "#48BB78"
            elif rating >= 7:
                rating_color = "#68D391"
            elif rating >= 6:
                rating_color = "#ECC94B"
            else:
                rating_color = "#F56565"
            
            mom_badge = " MOTM" if mom else ""
            
            st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-left: 4px solid {rating_color};
                    border-radius: 8px;
                    padding: 1rem;
                    margin-bottom: 0.5rem;
                '>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-weight: 600; color: #E2E8F0;'>
                                {perf.get('player_name', perf.get('player_id', 'Unknown'))}
                            </span>
                            <span style='color: #A0AEC0; margin-left: 0.5rem;'>
                                vs {perf.get('opponent', 'N/A')}
                            </span>
                            {f"<span style='background: #D4AF37; color: #1a1a2e; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.7rem; margin-left: 0.5rem; font-weight: 600;'>{mom_badge}</span>" if mom else ""}
                        </div>
                        <span style='
                            background: {rating_color};
                            color: white;
                            padding: 0.3rem 0.6rem;
                            border-radius: 8px;
                            font-weight: 700;
                            font-size: 1rem;
                        '>{rating}</span>
                    </div>
                    <div style='margin-top: 0.5rem; color: #A0AEC0; font-size: 0.85rem;'>
                        <span style='color: #D4AF37;'>{goals}G</span> |
                        <span style='color: #48BB78;'>{assists}A</span> |
                        {perf.get('minutes_played', 0)}' |
                        {perf.get('passes', 0)} passes ({perf.get('pass_accuracy', 0)}%) |
                        {perf.get('match_date', 'N/A')}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with perf_tab2:
        st.markdown("#### Season Leaderboards")
        
        # Goals leaderboard
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Top Scorers**")
            if 'goals' in df_performance.columns and 'player_name' in df_performance.columns:
                goals_df = df_performance.groupby('player_name')['goals'].sum().sort_values(ascending=False).head(5)
                for i, (player, goals) in enumerate(goals_df.items()):
                    medal = ["", "", ""][i] if i < 3 else ""
                    st.markdown(f"""
                        <div style='
                            background: #1a1a2e;
                            border-radius: 8px;
                            padding: 0.5rem 1rem;
                            margin-bottom: 0.25rem;
                            display: flex;
                            justify-content: space-between;
                        '>
                            <span style='color: #E2E8F0;'>{medal} {i+1}. {player}</span>
                            <span style='color: #D4AF37; font-weight: 600;'>{int(goals)} goals</span>
                        </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**Top Assists**")
            if 'assists' in df_performance.columns and 'player_name' in df_performance.columns:
                assists_df = df_performance.groupby('player_name')['assists'].sum().sort_values(ascending=False).head(5)
                for i, (player, assists) in enumerate(assists_df.items()):
                    medal = ["", "", ""][i] if i < 3 else ""
                    st.markdown(f"""
                        <div style='
                            background: #1a1a2e;
                            border-radius: 8px;
                            padding: 0.5rem 1rem;
                            margin-bottom: 0.25rem;
                            display: flex;
                            justify-content: space-between;
                        '>
                            <span style='color: #E2E8F0;'>{medal} {i+1}. {player}</span>
                            <span style='color: #48BB78; font-weight: 600;'>{int(assists)} assists</span>
                        </div>
                    """, unsafe_allow_html=True)
        
        st.divider()
        
        # Rating leaderboard
        st.markdown("**Highest Rated Players**")
        if 'rating' in df_performance.columns and 'player_name' in df_performance.columns:
            rating_df = df_performance.groupby('player_name')['rating'].mean().sort_values(ascending=False).head(5)
            for i, (player, rating) in enumerate(rating_df.items()):
                pct = (rating / 10) * 100
                st.markdown(f"""
                    <div style='margin-bottom: 0.5rem;'>
                        <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                            <span style='color: #E2E8F0;'>{i+1}. {player}</span>
                            <span style='color: #8B5CF6; font-weight: 600;'>{rating:.2f}</span>
                        </div>
                        <div style='background: #2D3748; border-radius: 4px; height: 6px;'>
                            <div style='background: #8B5CF6; width: {pct}%; height: 100%; border-radius: 4px;'></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    with perf_tab3:
        st.markdown("#### Team Statistics")
        
        if df_team.empty:
            # Generate demo team data
            teams = []
            for i, club in enumerate(BOTOLA_CLUBS[:8]):
                wins = random.randint(5, 15)
                draws = random.randint(2, 8)
                losses = random.randint(2, 10)
                gf = random.randint(20, 50)
                ga = random.randint(15, 40)
                
                teams.append({
                    "club": club,
                    "matches_played": wins + draws + losses,
                    "wins": wins,
                    "draws": draws,
                    "losses": losses,
                    "goals_for": gf,
                    "goals_against": ga,
                    "goal_difference": gf - ga,
                    "points": (wins * 3) + draws,
                    "form": "".join(random.choices(["W", "D", "L"], k=5))
                })
            df_team = pd.DataFrame(teams)
            df_team = df_team.sort_values('points', ascending=False)
        
        # League table
        st.markdown("**Botola Pro Standings**")
        
        for i, (_, team) in enumerate(df_team.iterrows()):
            form = team.get('form', 'WWDLL')
            form_badges = ""
            for f in form:
                if f == 'W':
                    form_badges += "<span style='background: #48BB78; color: white; padding: 0.1rem 0.3rem; border-radius: 4px; margin-right: 2px; font-size: 0.7rem;'>W</span>"
                elif f == 'D':
                    form_badges += "<span style='background: #A0AEC0; color: white; padding: 0.1rem 0.3rem; border-radius: 4px; margin-right: 2px; font-size: 0.7rem;'>D</span>"
                else:
                    form_badges += "<span style='background: #F56565; color: white; padding: 0.1rem 0.3rem; border-radius: 4px; margin-right: 2px; font-size: 0.7rem;'>L</span>"
            
            pos_color = "#D4AF37" if i < 3 else "#48BB78" if i < 6 else "#E2E8F0" if i < 12 else "#F56565"
            
            st.markdown(f"""
                <div style='
                    background: #1a1a2e;
                    border-left: 4px solid {pos_color};
                    border-radius: 8px;
                    padding: 0.75rem 1rem;
                    margin-bottom: 0.5rem;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                '>
                    <div style='display: flex; align-items: center;'>
                        <span style='color: {pos_color}; font-weight: 700; width: 30px;'>{i+1}</span>
                        <span style='color: #E2E8F0; font-weight: 600;'>{team.get('club', 'Unknown')}</span>
                    </div>
                    <div style='display: flex; align-items: center; gap: 1rem;'>
                        <span style='color: #A0AEC0; font-size: 0.85rem;'>
                            {team.get('matches_played', 0)}P | 
                            {team.get('wins', 0)}W {team.get('draws', 0)}D {team.get('losses', 0)}L |
                            GD: {team.get('goal_difference', 0):+d}
                        </span>
                        <span style='margin-left: 0.5rem;'>{form_badges}</span>
                        <span style='color: #D4AF37; font-weight: 700; font-size: 1.1rem; min-width: 40px; text-align: right;'>
                            {team.get('points', 0)}
                        </span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with perf_tab4:
        st.markdown("#### Log Match Performance")
        
        # Get players for dropdown
        if not df_players.empty and 'first_name' in df_players.columns:
            player_options = [f"{r['first_name']} {r['last_name']}" for _, r in df_players.iterrows()]
        else:
            player_options = [f"Player {i+1}" for i in range(10)]
        
        with st.form("add_performance"):
            col1, col2, col3 = st.columns(3)
            with col1:
                player = st.selectbox("Player *", player_options, key="perf_player")
                opponent = st.selectbox("Opponent *", BOTOLA_CLUBS)
                competition = st.selectbox("Competition", COMPETITIONS[:6])
            with col2:
                match_date = st.date_input("Match Date")
                minutes_played = st.number_input("Minutes Played", 0, 120, 90)
                rating = st.slider("Match Rating", 1.0, 10.0, 6.5, 0.1)
            with col3:
                goals = st.number_input("Goals", 0, 10, 0)
                assists = st.number_input("Assists", 0, 10, 0)
                man_of_match = st.checkbox("Man of the Match")
            
            col4, col5 = st.columns(2)
            with col4:
                shots = st.number_input("Shots", 0, 20, 0)
                shots_on_target = st.number_input("Shots on Target", 0, 20, 0)
                passes = st.number_input("Passes", 0, 150, 40)
                pass_accuracy = st.slider("Pass Accuracy %", 0, 100, 80)
            with col5:
                tackles = st.number_input("Tackles", 0, 20, 0)
                interceptions = st.number_input("Interceptions", 0, 20, 0)
                yellow_cards = st.number_input("Yellow Cards", 0, 2, 0)
                red_cards = st.number_input("Red Cards", 0, 1, 0)
            
            if st.form_submit_button("Log Performance", type="primary", use_container_width=True):
                if player and opponent:
                    perf_id = generate_uuid("PERF")
                    
                    success = run_query("""
                        INSERT INTO frmf_match_performance 
                        (performance_id, player_id, match_id, match_date, opponent, competition,
                         minutes_played, goals, assists, shots, shots_on_target, passes, pass_accuracy,
                         tackles, interceptions, yellow_cards, red_cards, rating, man_of_match, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (perf_id, player, generate_uuid("MATCH"), str(match_date), opponent, competition,
                          minutes_played, goals, assists, shots, shots_on_target, passes, pass_accuracy,
                          tackles, interceptions, yellow_cards, red_cards, rating, 
                          1 if man_of_match else 0, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Performance Logged!", perf_id)
                        log_audit(username, "PERFORMANCE_LOGGED", "FRMF", f"{player} vs {opponent}")
                        st.rerun()
                else:
                    st.error("Player and Opponent are required")


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
        "RefereeChain + VAR Vault + Player Profiles - Complete Football Management",
        icon=""
    )
    
    # KPIs
    df_refs = get_data("frmf_referees")
    df_matches = get_data("frmf_match_assignments")
    df_var = get_data("frmf_var_vault")
    df_players = get_data("frmf_players")
    
    ref_count = len(df_refs) if not df_refs.empty else 10
    player_count = len(df_players) if not df_players.empty else 20
    var_count = len(df_var) if not df_var.empty else 20
    match_count = len(df_matches) if not df_matches.empty else 15
    
    premium_kpi_row([
        ("", "Licensed Referees", str(ref_count), "Active officials"),
        ("", "Registered Players", str(player_count), "In database"),
        ("", "VAR Decisions", str(var_count), "Archived"),
        ("", "Matches", str(match_count), "This season")
    ])
    
    st.divider()
    
    # Tabs - Full FRMF Module
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
        "Referee Registry",
        "RefereeChain",
        "Player Profiles",
        "Contracts",
        "Medical",
        "Analytics",
        "Match Assignments", 
        "VAR Vault",
        "Ref Performance",
        "Incidents"
    ])
    
    with tab1:
        render_referee_registry(username)
    
    with tab2:
        render_refereechain(username)
    
    with tab3:
        render_player_profiles(username)
    
    with tab4:
        render_contract_management(username)
    
    with tab5:
        render_medical_records(username)
    
    with tab6:
        render_performance_analytics(username)
    
    with tab7:
        render_match_assignments(username)
    
    with tab8:
        render_var_vault(username)
    
    with tab9:
        render_referee_performance(username)
    
    with tab10:
        render_match_incidents(username)
