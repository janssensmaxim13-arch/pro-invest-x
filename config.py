"""
ProInvestiX Configuration v5.4.1 - COMPLETE FIXED VERSION
All missing attributes added
"""

import os

# ============================================================================
# VERSION INFO
# ============================================================================
VERSION = "5.4.1"
VERSION_NAME = "DAY 10 UPDATE"
APP_NAME = "ProInvestiX"

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================
DB_FILE = "proinvestix_ultimate.db"
VAULT_DIR = "consular_vault"
ASSETS_DIR = "assets"
UPLOADS_DIR = "uploads"
BACKUP_DIR = "backups"
LOGS_DIR = "logs"

for dir_path in [VAULT_DIR, ASSETS_DIR, UPLOADS_DIR, BACKUP_DIR, LOGS_DIR]:
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

# ============================================================================
# FILE SETTINGS
# ============================================================================
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx']

# ============================================================================
# FINANCIAL SETTINGS
# ============================================================================
FOUNDATION_RATE = 0.005
TAX_RATE = 0.15
MAX_AGENT_FEE = 0.10
MIN_DONATION = 10
MAX_TRANSACTION = 100000

# ============================================================================
# BLOCKCHAIN / SECURITY
# ============================================================================
BLOCKCHAIN_SECRET = "PROINVESTIX_BLOCKCHAIN_2030"
HASH_ALGORITHM = "sha256"
SESSION_TIMEOUT = 3600
MAX_LOGIN_ATTEMPTS = 5

# ============================================================================
# ASSETS
# ============================================================================
LOGO_TEXT = "assets/logo_text.png"
LOGO_SHIELD = "assets/logo_shield.png"
DEFAULT_AVATAR = "assets/default_avatar.png"

# ============================================================================
# ROLES
# ============================================================================
ROLES = {
    'superadmin': {'level': 100, 'name': 'Super Administrator'},
    'admin': {'level': 90, 'name': 'Administrator'},
    'manager': {'level': 70, 'name': 'Manager'},
    'staff': {'level': 50, 'name': 'Staff'},
    'scout': {'level': 40, 'name': 'Scout'},
    'agent': {'level': 40, 'name': 'Agent'},
    'volunteer': {'level': 30, 'name': 'Volunteer'},
    'user': {'level': 10, 'name': 'User'},
    'guest': {'level': 0, 'name': 'Guest'},
}

# ============================================================================
# ALLOWED TABLES
# ============================================================================
ALLOWED_TABLES = [
    # Authentication & System
    'users', 'user_registry', 'audit_logs', 'sessions',
    
    # NTSP - National Talent Scouting Platform
    'ntsp_talent_profiles', 'ntsp_evaluations', 'ntsp_mental_evaluations',
    'ntsp_medical_records', 'ntsp_scouts', 'ntsp_watchlist',
    
    # Transfers & Academy
    'transfers', 'academies', 'academy_teams', 'academy_staff', 'academy_enrollments',
    'transfer_market_watchlist', 'contract_templates',
    
    # Transfer Market
    'tm_players', 'tm_transfers', 'tm_rumours', 'tm_watchlist', 'tm_statistics', 'tm_value_history',
    
    # TicketChain
    'ticketchain_events', 'ticketchain_tickets', 'fiscal_ledger', 'loyalty_points',
    
    # Financial
    'diaspora_wallets', 'wallet_transactions', 'diaspora_cards', 'diaspora_investments',
    'financial_records', 'foundation_contributions', 'foundation_donations',
    
    # Subscriptions
    'subscription_plans', 'user_subscriptions', 'subscriptions', 
    'subscription_payments', 'gift_subscriptions', 'scholarship_applications',
    
    # Identity & Security
    'identity_shield', 'fraud_alerts', 'verification_requests',
    
    # MAROC ID Shield
    'maroc_identities', 'maroc_organizations', 'maroc_role_certificates',
    'maroc_pma_queue', 'maroc_transaction_signatures', 'maroc_verification_requests',
    
    # FanDorpen
    'fandorpen', 'fandorp_volunteers', 'fandorp_training', 'fandorp_shifts',
    'fandorp_incidents', 'fandorp_services', 'fandorp_messages',
    
    # Health - Hayat
    'health_records', 'hayat_alerts', 'hayat_rehabilitation',
    'hayat_sessions', 'hayat_wellbeing_logs', 'hayat_crisis_alerts',
    
    # Anti-Hate
    'antihate_incidents', 'antihate_cases', 'antihate_legal_cases',
    'antihate_monitored', 'antihate_wellness_checks',
    
    # Inclusion
    'inclusion_athletes', 'inclusion_events', 'inclusion_programs',
    'paralympic_athletes', 'women_players', 'women_hubs',
    
    # Mobility
    'mobility_bookings', 'mobility_packages', 'mobility_records',
    
    # Consulate
    'consular_services', 'consular_appointments', 'consular_documents',
    'consular_registry', 'consular_assistance',
    
    # Sport Records
    'sport_records',
    
    # NIL - Narrative Integrity Layer
    'nil_signals', 'nil_sources', 'nil_evidence', 'nil_fact_cards',
    'nil_crisis_incidents', 'nil_forensics', 'nil_kpi_metrics', 'nil_playbook_templates',
    
    # FRMF - Federation Officials Hub
    'frmf_referees', 'frmf_match_assignments', 'frmf_var_vault',
    'frmf_referee_ratings', 'frmf_match_incidents',
    
    # PMA Logistics
    'pma_shipments', 'pma_warehouses', 'pma_inventory',
    'pma_fleet', 'pma_deliveries', 'pma_customs',
    
    # Esports (legacy)
    'esports_players', 'esports_teams', 'esports_tournaments',
]

# ============================================================================
# OPTIONS CLASS - COMPLETE WITH ALL ATTRIBUTES
# ============================================================================
class Options:
    """Dropdown options for forms - COMPLETE"""
    
    # === ROLES (for identity_shield.py) ===
    ROLES = ["SuperAdmin", "Admin", "Manager", "Staff", "Scout", "Agent", 
             "Volunteer", "User", "Guest", "Investor", "Partner", "Player", "Coach"]
    
    # === FRAUD & ALERTS (for identity_shield.py) ===
    FRAUD_ALERT_TYPES = ["Identity Theft", "Document Fraud", "Financial Fraud", 
                         "Ticket Fraud", "Bot Activity", "Suspicious Login", 
                         "Multiple Accounts", "Other"]
    
    URGENCY_LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # === AGE GROUPS (for academy.py) ===
    AGE_GROUPS = ["U13", "U14", "U15", "U16", "U17", "U18", "U19", "U21", "U23", "Senior"]
    
    # === POSITIONS ===
    POSITIONS = [
        "Goalkeeper", "Right-Back", "Centre-Back", "Left-Back",
        "Defensive Midfield", "Central Midfield", "Attacking Midfield",
        "Right Winger", "Left Winger", "Centre-Forward", "Second Striker"
    ]
    
    # === TALENT & TRANSFER ===
    TALENT_STATUSES = ["Active", "Inactive", "Injured", "Retired", "Pending", "Transferred"]
    TRANSFER_TYPES = ["Permanent", "Loan", "Loan with Option", "Free Transfer", "Youth", "Return"]
    TRANSFER_STATUSES = ["Pending", "Negotiating", "Agreed", "Medical", "Completed", "Cancelled", "Failed"]
    
    # === COUNTRIES & REGIONS ===
    DIASPORA_COUNTRIES = [
        "Netherlands", "Belgium", "France", "Germany", "Spain", "Italy",
        "UK", "USA", "Canada", "UAE", "Saudi Arabia", "Qatar", "Turkey", "Morocco"
    ]
    
    REGIONS_MOROCCO = [
        "Casablanca-Settat", "Rabat-Sale-Kenitra", "Marrakech-Safi",
        "Fes-Meknes", "Tanger-Tetouan-Al Hoceima", "Souss-Massa",
        "Oriental", "Beni Mellal-Khenifra", "Draa-Tafilalet",
        "Guelmim-Oued Noun", "Laayoune-Sakia El Hamra", "Dakhla-Oued Ed-Dahab"
    ]
    
    # === SECTORS & DONATIONS ===
    SECTORS = ["Sport", "Technology", "Real Estate", "Agriculture", "Tourism",
               "Healthcare", "Education", "Energy", "Finance", "Infrastructure"]
    
    DONATION_TYPES = ["One-time", "Monthly", "Annual", "Corporate", "Legacy", "In-kind"]
    
    # === NATIONALITIES ===
    NATIONALITIES = [
        "Moroccan", "Dutch", "Belgian", "French", "Spanish", "Italian", "German",
        "British", "American", "Canadian", "Portuguese", "Algerian", "Tunisian",
        "Egyptian", "Senegalese", "Brazilian", "Argentine", "Turkish", "Other"
    ]
    
    # === PLAYER ATTRIBUTES ===
    PREFERRED_FEET = ["Right", "Left", "Both"]
    PREFERRED_FOOT = PREFERRED_FEET
    
    # === WALLET & FINANCE (for diaspora_wallet.py) ===
    WALLET_TYPES = ["PERSONAL", "BUSINESS", "INVESTMENT", "FAMILY", "CLUB"]
    
    INVESTMENT_TYPES = [
        "FIXED_DEPOSIT", "GROWTH_FUND", "REAL_ESTATE", "SPORTS_BOND",
        "INFRASTRUCTURE", "GREEN_ENERGY", "TECHNOLOGY"
    ]
    
    TRANSACTION_TYPES = ["Deposit", "Withdrawal", "Transfer", "Investment", "Donation", "Fee", "Refund"]
    TRANSACTION_TYPES_WALLET = ["Deposit", "Withdrawal", "Transfer", "Investment", "Donation"]
    
    RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
    
    CARD_TYPES = ["Debit", "Credit", "Prepaid", "Virtual", "Premium"]
    
    # === VERIFICATION ===
    VERIFICATION_LEVELS = ["Guest", "Basic", "Strong", "Government"]
    
    # === TICKETS & EVENTS ===
    TICKET_TYPES = ["Standard", "Premium", "VIP", "Family", "Group", "Student", "Early Bird"]
    EVENT_CATEGORIES = ["Football Match", "WK 2030 Match", "Concert", "Festival", 
                        "Sports Event", "Conference", "Exhibition", "Other"]
    
    # === DOCUMENTS (for consulate_hub.py) ===
    DOCUMENT_TYPES = ["CNIE", "Passport", "Driver License", "Residence Permit", 
                      "Birth Certificate", "Marriage Certificate", "Diploma", "Other"]
    DOCUMENT_STATUSES = ["Pending", "Processing", "Verified", "Ready", "Collected", "Rejected", "Cancelled"]
    
    SERVICE_TYPES = ["Passport", "Visa", "Birth Certificate", "Marriage Certificate",
                     "Legal Document", "Notarization", "Translation", "Other"]
    
    APPOINTMENT_STATUSES = ["Scheduled", "Confirmed", "Completed", "Cancelled", "No-Show"]
    
    SCHOLARSHIP_TYPES = ["Academic", "Sports", "Arts", "Technical", "Research", "Full Scholarship", "Partial"]
    
    ASSISTANCE_TYPES = ["Legal Aid", "Financial Support", "Medical Emergency", 
                        "Repatriation", "Document Recovery", "Translation", "Other"]
    
    # === PERSONAL ===
    GENDERS = ["Male", "Female", "Other", "Prefer not to say"]
    LANGUAGES = ["Arabic", "French", "English", "Dutch", "German", "Spanish", "Italian"]
    
    # === NTSP EVALUATIONS ===
    PRIORITY_LEVELS = ["Low", "Medium", "High", "Critical", "Top Priority"]
    
    EVALUATION_RECOMMENDATIONS = [
        "Promote to First Team", "Continue Development", "Loan Recommended",
        "Transfer Listed", "Contract Extension", "Release", "Monitor Progress"
    ]
    
    MEDICAL_STATUSES = ["Fit", "Minor Issue", "Recovering", "Not Fit", "Long-term Injury", "Pending Checkup"]
    
    SCOUT_SPECIALIZATIONS = ["Youth", "First Team", "Goalkeeper", "Striker", "Defender", "Midfielder", "All-round"]
    
    COACHING_LICENSES = ["UEFA Pro", "UEFA A", "UEFA B", "UEFA C", "National A", "National B", "None"]
    
    # === ADAPTERS (for adapters.py) ===
    ATHLETE_STATUSES = ["Active", "Inactive", "Injured", "Retired", "Suspended"]
    ASSET_TYPES = ["Equipment", "Facility", "Vehicle", "Technology", "Other"]
    ASSET_STATUSES = ["Available", "In Use", "Maintenance", "Retired", "Lost"]
    CHECKUP_TYPES = ["Annual", "Pre-season", "Post-injury", "Routine", "Emergency"]
    
    # === ACADEMY (for academy.py) ===
    ACADEMY_TYPES = ["Youth Academy", "Professional Academy", "Development Center", 
                     "Training Center", "Regional Academy", "National Academy", "Elite Academy"]
    ACADEMY_STATUSES = ["Active", "Inactive", "Under Review", "Certified", "Suspended"]
    CERTIFICATION_LEVELS = ["Basic", "Bronze", "Silver", "Gold", "Elite", "FIFA Certified"]
    ENROLLMENT_TYPES = ["Full-time", "Part-time", "Trial", "Scholarship", "Exchange", "Summer Camp"]
    ACADEMY_STAFF_ROLES = ["Head Coach", "Assistant Coach", "Goalkeeper Coach", "Fitness Coach", 
                          "Physiotherapist", "Scout", "Technical Director", "Academy Director", 
                          "Youth Coordinator", "Video Analyst", "Team Manager"]


# ============================================================================
# MESSAGES CLASS - COMPLETE WITH ALL ATTRIBUTES
# ============================================================================
class Messages:
    """UI Messages - COMPLETE"""
    
    # === SUCCESS ===
    WELCOME = "Welcome to ProInvestiX"
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = "Logged out successfully"
    REGISTRATION_SUCCESS = "Account created successfully"
    PROFILE_UPDATED = "Profile updated successfully"
    DONATION_RECEIVED = "Thank you for your donation"
    TRANSFER_COMPLETED = "Transfer completed successfully"
    TICKET_MINTED = "Ticket minted successfully"
    BOOKING_CONFIRMED = "Booking confirmed"
    FILE_UPLOADED = "File uploaded successfully"
    DOCUMENT_SAVED = "Document saved successfully"
    
    # === ERRORS ===
    INVALID_CREDENTIALS = "Invalid username or password"
    ACCESS_DENIED = "Access denied"
    SESSION_EXPIRED = "Session expired, please login again"
    ERROR_GENERIC = "An error occurred"
    
    # === IDENTITY SHIELD ===
    IDENTITY_SECURED = "Identity '{}' secured with risk level: {}"
    ALERT_RESOLVED = "Alert resolved successfully"
    
    # === TRANSFERS ===
    TRANSFER_CREATED = "Transfer {} created successfully"
    
    # === NTSP ===
    TALENT_REGISTERED = "Talent '{}' registered successfully"
    EVALUATION_SAVED = "Evaluation saved for '{}'"
    
    # === WALLET ===
    WALLET_CREATED = "Wallet created for identity: {}"
    
    # === CONSULATE ===
    DOCUMENT_SECURED = "Document '{}' secured in vault"
    APPLICATION_SUBMITTED = "Application {} submitted successfully"
    ASSISTANCE_CREATED = "Assistance ticket {} created"
    
    # === ACADEMY ===
    ACADEMY_REGISTERED = "Academy '{}' registered successfully"
    
    # === ERRORS ===
    LOGIN_FAILED = "Invalid credentials"
    FORM_INCOMPLETE = "Please fill in all required fields"
    DATABASE_ERROR = "Database error occurred"
    CONNECTION_ERROR = "Connection error"
    UNAUTHORIZED = "You are not authorized"
    NOT_FOUND = "Record not found"
    VALIDATION_ERROR = "Validation error"
    FILE_TOO_LARGE = "File too large (max {}MB)"
    INVALID_FILE_TYPE = "Invalid file type"
    UPLOAD_FAILED = "File upload failed"
    INVALID_ID = "Invalid ID format"
    NAME_REQUIRED = "Name is required"
    DUPLICATE_ID = "Duplicate ID: {} already exists"
    FILE_REQUIRED = "File is required"
    
    # === INFO ===
    NO_DATA = "No data available"
    NO_DATA_AVAILABLE = "No data available"
    LOADING = "Loading..."
    PROCESSING = "Processing..."
    NO_RESULTS = "No results found"
    
    # === WARNING ===
    SESSION_EXPIRED = "Session expired"
    CONFIRM_ACTION = "Are you sure?"
    
    # === FOUNDATION ===
    FOUNDATION_INFO = "0.5% goes to Foundation (Sadaka Jaaria)"


# ============================================================================
# TRANSFER RULES - COMPLETE WITH ALL ATTRIBUTES
# ============================================================================
class TransferRules:
    """FIFA-compliant transfer rules - COMPLETE"""
    
    FOUNDATION_PERCENTAGE = 0.5
    MAX_AGENT_FEE_PERCENTAGE = 10
    TRAINING_COMPENSATION_YEARS = 12
    SOLIDARITY_PERCENTAGE = 5
    MIN_CONTRACT_MONTHS = 12
    MAX_LOAN_DURATION = 24
    
    # Training compensation per category (EUR per year)
    TRAINING_COMPENSATION_CAT_1 = 90000
    TRAINING_COMPENSATION_CAT_2 = 60000
    TRAINING_COMPENSATION_CAT_3 = 30000
    TRAINING_COMPENSATION_CAT_4 = 10000
    
    # Solidarity contribution percentages
    SOLIDARITY_PER_YEAR_12_15 = 0.25  # 0.25% per year aged 12-15
    SOLIDARITY_PER_YEAR_16_23 = 0.50  # 0.50% per year aged 16-23


# ============================================================================
# OTHER CLASSES
# ============================================================================
class LoyaltyTiers:
    BRONZE = {"name": "Bronze", "min_points": 0, "discount": 0, "benefits": "Basic access"}
    SILVER = {"name": "Silver", "min_points": 1000, "discount": 5, "benefits": "5% discount"}
    GOLD = {"name": "Gold", "min_points": 5000, "discount": 10, "benefits": "10% discount"}
    PLATINUM = {"name": "Platinum", "min_points": 15000, "discount": 15, "benefits": "15% discount"}
    DIAMOND = {"name": "Diamond", "min_points": 50000, "discount": 20, "benefits": "20% discount"}
    
    @classmethod
    def get_tier(cls, points):
        if points >= 50000: return cls.DIAMOND
        elif points >= 15000: return cls.PLATINUM
        elif points >= 5000: return cls.GOLD
        elif points >= 1000: return cls.SILVER
        return cls.BRONZE


class ScoreWeights:
    TECHNICAL = 0.30
    PHYSICAL = 0.25
    MENTAL = 0.20
    TACTICAL = 0.25
    
    @classmethod
    def calculate_total(cls, technical, physical, mental, tactical):
        return (technical * cls.TECHNICAL + physical * cls.PHYSICAL +
                mental * cls.MENTAL + tactical * cls.TACTICAL)


class MarocIDSettings:
    VERIFICATION_LEVELS = {
        0: {"name": "Guest", "arabic": "ضيف", "max_transaction": 0},
        1: {"name": "Basic", "arabic": "تحقق أساسي", "max_transaction": 500},
        2: {"name": "Strong", "arabic": "تحقق قوي", "max_transaction": 10000},
        3: {"name": "Government", "arabic": "درجة حكومية", "max_transaction": float('inf')}
    }
    DOCUMENT_TYPES = ["CNIE", "Passport", "Driver License", "Residence Permit", "Birth Certificate", "Other"]
    CERTIFICATE_TYPES = ["Volunteer", "Official", "Agent", "Scout", "Coach", "Medical",
                         "Security", "VIP Host", "Media", "Technical", "Transport", "Catering"]


class WK2030:
    START_DATE = "2030-06-13"
    END_DATE = "2030-07-13"
    HOST_CITIES = ["Casablanca", "Rabat", "Marrakech", "Tangier", "Fes", "Agadir"]
    STADIUMS = {
        "Casablanca": {"name": "Stade Mohammed V", "capacity": 67000},
        "Rabat": {"name": "Complexe Moulay Abdellah", "capacity": 53000},
        "Marrakech": {"name": "Stade de Marrakech", "capacity": 45240},
        "Tangier": {"name": "Grand Stade de Tanger", "capacity": 65000},
        "Fes": {"name": "Stade de Fes", "capacity": 45000},
        "Agadir": {"name": "Stade d'Agadir", "capacity": 45480},
    }


class FanDorpenSettings:
    LOCATIONS = [
        {"name": "Amsterdam", "country": "Netherlands", "capacity": 5000},
        {"name": "Brussels", "country": "Belgium", "capacity": 3000},
        {"name": "Paris", "country": "France", "capacity": 4000},
    ]
    SHIFT_TYPES = ["Morning", "Afternoon", "Evening", "Night"]
    TRAINING_MODULES = ["Welcome Protocol", "Cultural Sensitivity", "Emergency Procedures", "First Aid (EHBO)"]
    BADGE_TYPES = ["Welcome Expert", "Cultural Ambassador", "EHBO Certified", "Super Volunteer"]


class ConsularSettings:
    SERVICES = ["Passport Application", "Passport Renewal", "Visa Application",
                "Birth Registration", "Marriage Registration", "Legal Document Certification"]
    DOCUMENT_STATUS = ["Pending", "Processing", "Ready", "Collected", "Cancelled"]
    APPOINTMENT_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                         "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
