import streamlit as st
import pandas as pd
import os
import sqlite3
import re
import uuid
import base64
import hashlib
import hmac
import time # Nodig voor de refresh
from io import BytesIO
from datetime import datetime

# --- NIEUW: Dit zorgt dat je .env bestand gelezen wordt ---
# Dit is essentieel voor productie-beveiliging
try:
    from dotenv import load_dotenv
    load_dotenv()  # Dit laadt de sleutel uit je .env bestand
except ImportError:
    # Als de library er niet is, is dat geen ramp, we gaan door
    pass 
# -----------------------------------------------------------

# QR Code with graceful degradation
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

# ============================================================================
# 1. CONSTANTS & SYSTEM SETUP
# ============================================================================

VAULT_DIR = "consular_vault"
DB_FILE = "proinvestix_core.db"
MAX_FILE_SIZE_MB = 50

# Extended table list with TicketChain tables
ALLOWED_TABLES = [
    'consular_registry', 'identity_shield', 'financial_records', 
    'sport_records', 'mobility_records', 'health_records',
    'ticketchain_events', 'ticketchain_tickets', 'fiscal_ledger'
]

LOGO_TEXT = "logo_text.jpg"
LOGO_SHIELD = "logo_shield.jpg"

# SECURITY: Environment-based secret key
# Nu pakt hij hem AUTOMATISCH uit je .env bestand als je die hebt gemaakt!
BLOCKCHAIN_SECRET = os.getenv('TICKETCHAIN_SECRET', 'DEV_SECRET_CHANGE_IN_PRODUCTION_' + uuid.uuid4().hex)

# Tax rate for fiscal integration
TAX_RATE = 0.15  # 15% VAT

# Create directories
if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

# ============================================================================
# 2. DATABASE SETUP (OPTIMIZED WITH INDEXES)
# ============================================================================

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # --- EXISTING TABLES ---
    c.execute('''CREATE TABLE IF NOT EXISTS consular_registry
                 (id TEXT PRIMARY KEY, doc_type TEXT, filename TEXT, status TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS identity_shield
                 (id TEXT PRIMARY KEY, name TEXT, role TEXT, country TEXT, risk_level TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS financial_records
                 (id TEXT PRIMARY KEY, entity_id TEXT, amount REAL, type TEXT, sector TEXT, status TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sport_records
                 (id TEXT PRIMARY KEY, identity_id TEXT, discipline TEXT, club TEXT, status TEXT, contract_end TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS mobility_records
                 (id TEXT PRIMARY KEY, asset_name TEXT, type TEXT, region TEXT, status TEXT, last_maint TEXT, timestamp TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS health_records
                 (id TEXT PRIMARY KEY, identity_id TEXT, checkup_type TEXT, medical_status TEXT, expiry_date TEXT, timestamp TEXT)''')
    
    # --- TICKETCHAIN TABLES (ENHANCED) ---
    
    # Events database
    c.execute('''CREATE TABLE IF NOT EXISTS ticketchain_events
                 (event_id TEXT PRIMARY KEY, 
                  name TEXT NOT NULL, 
                  location TEXT NOT NULL, 
                  date TEXT NOT NULL, 
                  capacity INTEGER NOT NULL, 
                  tickets_sold INTEGER DEFAULT 0,
                  timestamp TEXT NOT NULL)''')
    
    # Tickets Ledger (The "Blockchain")
    c.execute('''CREATE TABLE IF NOT EXISTS ticketchain_tickets
                 (ticket_hash TEXT PRIMARY KEY, 
                  event_id TEXT NOT NULL, 
                  owner_id TEXT NOT NULL, 
                  seat_info TEXT NOT NULL, 
                  price REAL NOT NULL, 
                  status TEXT NOT NULL DEFAULT 'VALID', 
                  minted_at TEXT NOT NULL,
                  used_at TEXT,
                  qr_generated INTEGER DEFAULT 1)''')
    
    # Fiscal Ledger for tax tracking
    c.execute('''CREATE TABLE IF NOT EXISTS fiscal_ledger
                 (fiscal_id TEXT PRIMARY KEY,
                  ticket_hash TEXT,
                  gross_amount REAL,
                  tax_amount REAL,
                  net_amount REAL,
                  timestamp TEXT)''')
    
    # ========================================================================
    # PERFORMANCE OPTIMIZATION: CREATE INDEXES
    # ========================================================================
    
    # TicketChain indexes for fast queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_event ON ticketchain_tickets(event_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_owner ON ticketchain_tickets(owner_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_status ON ticketchain_tickets(status)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_seat ON ticketchain_tickets(event_id, seat_info)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_tickets_timestamp ON ticketchain_tickets(minted_at)")
    
    # Events indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON ticketchain_events(date)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON ticketchain_events(timestamp)")
    
    # Financial indexes for portfolio queries
    c.execute("CREATE INDEX IF NOT EXISTS idx_financial_entity ON financial_records(entity_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_financial_sector ON financial_records(sector)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_financial_timestamp ON financial_records(timestamp)")
    
    # Sport/Health indexes for identity linking
    c.execute("CREATE INDEX IF NOT EXISTS idx_sport_identity ON sport_records(identity_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_health_identity ON health_records(identity_id)")
    
    # Fiscal indexes for tax reports
    c.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_ticket ON fiscal_ledger(ticket_hash)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_fiscal_timestamp ON fiscal_ledger(timestamp)")

    conn.commit()
    conn.close()

init_db()

# ============================================================================
# 3. CORE SECURE FUNCTIONS
# ============================================================================

def sanitize_id(doc_id):
    """
    Secure ID sanitization with minimum length check.
    Prevents path traversal and SQL injection.
    """
    if not doc_id: 
        return None
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', doc_id)
    return safe_id if len(safe_id) >= 3 else None

def sanitize_filename(filename):
    """
    Secure filename sanitization.
    Removes path components and dangerous characters.
    """
    if not filename: 
        return None
    filename = os.path.basename(filename)
    return re.sub(r'[^\w\s.-]', '', filename)

def sanitize_text(text):
    """
    General text sanitization for names, descriptions, etc.
    Allows spaces, alphanumeric, basic punctuation.
    """
    if not text: 
        return None
    return re.sub(r'[^a-zA-Z0-9\s_.-]', '', text)

def check_duplicate_id(doc_id, table):
    """
    Check if ID already exists in table.
    Handles different primary key names across tables.
    """
    if table not in ALLOWED_TABLES: 
        return True
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Special handling for different primary key columns
        if table == 'ticketchain_tickets':
            c.execute(f"SELECT 1 FROM {table} WHERE ticket_hash = ?", (doc_id,))
        elif table == 'ticketchain_events':
            c.execute(f"SELECT 1 FROM {table} WHERE event_id = ?", (doc_id,))
        elif table == 'fiscal_ledger':
            c.execute(f"SELECT 1 FROM {table} WHERE fiscal_id = ?", (doc_id,))
        else:
            c.execute(f"SELECT 1 FROM {table} WHERE id = ?", (doc_id,))
        
        res = c.fetchone()
        return res is not None
    except Exception as e:
        st.error(f"Duplicate check error: {e}")
        return True  # Fail safe
    finally:
        conn.close()

def run_query(sql, params=()):
    """
    Execute SQL query with error handling and rollback.
    Returns success boolean.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute(sql, params)
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        st.error(f"Database Error: {e}")
        return False
    finally:
        conn.close()

def get_data(table):
    """
    Secure table data retrieval with whitelist protection.
    Optimized with proper indexing.
    """
    if table not in ALLOWED_TABLES: 
        raise ValueError(f"Unauthorized table access: {table}")
    
    conn = sqlite3.connect(DB_FILE)
    try:
        # Try to sort by timestamp if column exists (indexes make this fast)
        df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY timestamp DESC", conn)
    except:
        # Fallback if no timestamp column
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        except Exception as e:
            st.error(f"Data retrieval error: {e}")
            df = pd.DataFrame()
    finally:
        conn.close()
    
    return df

def get_identity_names_map():
    """
    Retrieve list of identities for dropdown linking.
    Returns dict of {id: name} pairs.
    """
    try:
        df = get_data("identity_shield")
        return dict(zip(df['id'], df['name'])) if not df.empty else {}
    except Exception as e:
        st.error(f"Error loading identities: {e}")
        return {}

# ============================================================================
# 4. TICKETCHAIN BLOCKCHAIN FUNCTIONS (SECURED & ENHANCED)
# ============================================================================

def generate_ticket_hash(event_id, owner_id, seat, timestamp):
    """
    Generate cryptographically secure ticket hash using HMAC-SHA256.
    Industry standard used by Bitcoin, Ethereum, etc.
    
    HMAC prevents hash prediction even if algorithm is known.
    """
    message = f"{event_id}|{owner_id}|{seat}|{timestamp}"
    secret_key = BLOCKCHAIN_SECRET.encode()
    return hmac.new(secret_key, message.encode(), hashlib.sha256).hexdigest()

def generate_qr_code(ticket_hash):
    """
    Generate QR code for ticket with graceful degradation.
    Returns bytes if successful, None if library unavailable.
    """
    if not QR_AVAILABLE:
        return None
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=4,
        )
        qr.add_data(ticket_hash)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="#2e0d43", back_color="white")
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except Exception as e:
        st.error(f"QR generation error: {e}")
        return None

def check_event_capacity(event_id):
    """
    Check if event has reached capacity.
    Returns (capacity, sold, available, is_full)
    Optimized with event_id index.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Get event capacity
        c.execute("SELECT capacity FROM ticketchain_events WHERE event_id = ?", (event_id,))
        result = c.fetchone()
        
        if not result:
            return (0, 0, 0, True)  # Event not found
        
        capacity = result[0]
        
        # Count tickets (fast with idx_tickets_event index)
        c.execute("SELECT COUNT(*) FROM ticketchain_tickets WHERE event_id = ? AND status IN ('VALID', 'USED')", (event_id,))
        sold = c.fetchone()[0]
        
        available = capacity - sold
        is_full = sold >= capacity
        
        return (capacity, sold, available, is_full)
    
    except Exception as e:
        st.error(f"Capacity check error: {e}")
        return (0, 0, 0, True)  # Fail safe
    finally:
        conn.close()

def check_seat_availability(event_id, seat_info):
    """
    Check if seat is already assigned for this event.
    Returns (is_taken, owner_id)
    Optimized with composite index on (event_id, seat_info).
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        # Fast lookup with idx_tickets_seat composite index
        c.execute("""SELECT owner_id FROM ticketchain_tickets 
                     WHERE event_id = ? AND seat_info = ? AND status IN ('VALID', 'USED')""", 
                  (event_id, seat_info))
        result = c.fetchone()
        
        if result:
            return (True, result[0])  # Seat is taken
        else:
            return (False, None)  # Seat is available
    
    except Exception as e:
        st.error(f"Seat check error: {e}")
        return (True, "ERROR")  # Fail safe
    finally:
        conn.close()

def update_event_ticket_count(event_id):
    """
    Update tickets_sold counter in events table.
    Keeps counter in sync with actual ticket count.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    try:
        c.execute("SELECT COUNT(*) FROM ticketchain_tickets WHERE event_id = ? AND status IN ('VALID', 'USED')", (event_id,))
        count = c.fetchone()[0]
        
        c.execute("UPDATE ticketchain_events SET tickets_sold = ? WHERE event_id = ?", (count, event_id))
        conn.commit()
    except Exception as e:
        st.error(f"Counter update error: {e}")
        conn.rollback()
    finally:
        conn.close()

def log_fiscal_transaction(ticket_hash, gross_amount):
    """
    Log fiscal transaction for tax compliance.
    Calculates tax and net amount, stores in fiscal ledger.
    """
    tax_amount = gross_amount * TAX_RATE
    net_amount = gross_amount - tax_amount
    
    fiscal_id = f"TAX-{uuid.uuid4().hex[:8].upper()}"
    
    success = run_query(
        "INSERT INTO fiscal_ledger VALUES (?, ?, ?, ?, ?, ?)",
        (fiscal_id, ticket_hash, gross_amount, tax_amount, net_amount, datetime.now().isoformat())
    )
    
    return (success, tax_amount, net_amount)

# ============================================================================
# 5. UI/UX STYLING (PROFESSIONAL & ACCESSIBLE)
# ============================================================================

st.set_page_config(page_title="ProInvestiX - National Architecture", layout="wide")
st.markdown("""
    <style>
    /* BACKGROUND: Very light grey for maximum contrast */
    .stApp { 
        background-color: #f8f9fa !important;
        color: #1a1a1a !important;
    }
    
    /* SIDEBAR: Dark purple brand color */
    [data-testid="stSidebar"] { 
        background-color: #2e0d43 !important; 
        box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    }
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span { 
        color: #ffffff !important; 
        font-weight: 500;
    }
    
    /* Collapse button - white for visibility */
    [data-testid="stSidebarCollapseButton"] { 
        color: #ffffff !important; 
    }
    [data-testid="stSidebarCollapseButton"] svg { 
        fill: #ffffff !important; 
    }
    
    /* INPUTS & DROPDOWNS */
    .stTextInput input, 
    .stSelectbox div[data-baseweb="select"], 
    .stNumberInput input, 
    .stDateInput input,
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #ced4da !important;
        border-radius: 6px !important;
    }

    /* DROPDOWN POPOVER FIX */
    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #ffffff !important;
        border: 1px solid #dee2e6 !important;
    }
    div[data-baseweb="popover"] li, 
    div[data-baseweb="menu"] div {
        color: #1a1a1a !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] div:hover {
        background-color: #f8f9fa !important;
    }

    /* METRIC CARDS */
    .stMetric { 
        background-color: #ffffff; 
        border-radius: 8px;
        padding: 20px; 
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08); 
        border: 1px solid #e9ecef;
    }
    [data-testid="stMetricLabel"] { 
        color: #495057 !important; 
        font-weight: 600;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    } 
    [data-testid="stMetricValue"] { 
        color: #2e0d43 !important;
        font-size: 2em !important;
        font-weight: 700 !important;
    }

    /* TABS STYLING */
    .stTabs [data-baseweb="tab-list"] { 
        gap: 2px; 
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #ffffff;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #495057;
        border: 1px solid #dee2e6;
        border-bottom: none;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f8f9fa;
        color: #2e0d43;
        border-top: 3px solid #2e0d43;
        font-weight: 700;
    }

    /* BUTTONS */
    .stButton>button {
        background: linear-gradient(90deg, #4a148c 0%, #6a1b9a 100%);
        color: white !important;
        border-radius: 6px;
        border: none;
        font-weight: 600;
        padding: 10px 24px;
        box-shadow: 0 2px 6px rgba(74, 20, 140, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 4px 12px rgba(74, 20, 140, 0.3);
        transform: translateY(-1px);
        background: linear-gradient(90deg, #6a1b9a 0%, #8e24aa 100%);
    }

    /* MESSAGES */
    .stSuccess {
        background-color: #d4edda;
        color: #155724 !important;
        border-left: 4px solid #28a745;
        padding: 12px;
        border-radius: 4px;
    }
    .stError {
        background-color: #f8d7da;
        color: #721c24 !important;
        border-left: 4px solid #dc3545;
        padding: 12px;
        border-radius: 4px;
    }
    .stInfo {
        background-color: #d1ecf1;
        color: #0c5460 !important;
        border-left: 4px solid #17a2b8;
        padding: 12px;
        border-radius: 4px;
    }
    .stWarning {
        background-color: #fff3cd;
        color: #856404 !important;
        border-left: 4px solid #ffc107;
        padding: 12px;
        border-radius: 4px;
    }

    /* CODE BLOCKS */
    code {
        background-color: #f4f4f4 !important;
        color: #2e0d43 !important;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
    }

    /* DATAFRAMES */
    .stDataFrame {
        border: 1px solid #dee2e6;
        border-radius: 6px;
        overflow: hidden;
    }

    /* EXPANDER */
    .streamlit-expanderHeader {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        font-weight: 600;
        color: #2e0d43 !important;
    }

    /* TEXT */
    h1, h2, h3, h4, h5, h6, p, label, span, div { 
        color: #1a1a1a !important; 
    }
    
    input::placeholder, textarea::placeholder {
        color: #6c757d !important;
        opacity: 0.7;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# 6. MAIN APPLICATION
# ============================================================================

if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False

# ============================================================================
# LOGIN SCREEN
# ============================================================================

if not st.session_state['ingelogd']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Logo
        if os.path.exists(LOGO_TEXT): 
            st.image(LOGO_TEXT, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #2e0d43;'>PRO INVEST X</h1>", 
                        unsafe_allow_html=True)
        
        # Login form
        st.markdown("""
            <div style='background-color: #ffffff; 
                        padding: 30px; 
                        border-radius: 10px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.08); 
                        margin-top: 30px; 
                        border: 1px solid #e9ecef;'>
        """, unsafe_allow_html=True)
        
        with st.form("login"):
            st.markdown("<h3 style='text-align: center; margin-bottom: 20px; color: #2e0d43;'>SECURE LOGIN</h3>", 
                        unsafe_allow_html=True)
            u = st.text_input("Username", placeholder="Enter username")
            p = st.text_input("Access Key", type="password", placeholder="Enter password")
            
            if st.form_submit_button("AUTHENTICATE", use_container_width=True):
                if u == "admin" and p == "invest2025":
                    st.session_state.ingelogd = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Security notice
        st.markdown("""
            <div style='text-align: center; margin-top: 20px; color: #6c757d; font-size: 0.85em;'>
                🔒 Secured by ProInvestiX IT-CELL<br>
                v5.0.4 Ultimate Production Edition • Optimized & Indexed
            </div>
        """, unsafe_allow_html=True)
        
        # QR Library check
        if not QR_AVAILABLE:
            st.warning("⚠️ QR code library not installed. Tickets will show hash only. Install with: `pip install qrcode[pil]`")

# ============================================================================
# MAIN APPLICATION (LOGGED IN)
# ============================================================================

else:
    # SIDEBAR
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logo
        if os.path.exists(LOGO_TEXT): 
            st.image(LOGO_TEXT, use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center; color: #ffffff;'>PRO INVEST X</h2>", 
                        unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Shield logo (optional)
        if os.path.exists(LOGO_SHIELD):
            c1, c2, c3 = st.columns([0.5, 2, 0.5])
            with c2: 
                st.image(LOGO_SHIELD, use_container_width=True)
        
        st.markdown("<br><p style='font-weight: bold; letter-spacing: 1px; color: #ffffff;'>OPERATIONAL MODULES</p>", 
                    unsafe_allow_html=True)
        
        # MENU
        menu = st.radio("NAVIGATION", [
            "Dashboard", 
            "Identity Shield", 
            "TicketChain Adapter", 
            "Financial Adapter", 
            "Sport Adapter", 
            "Mobility Adapter", 
            "Health Adapter", 
            "Consular Vault"
        ], label_visibility="collapsed")
        
        st.divider()
        
        # Logout button
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.ingelogd = False
            st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; font-size: 0.75em; color: rgba(255,255,255,0.7);'>
                © 2025 PRO INVEST X<br>
                IT-CELL | v5.0.4 Ultimate<br>
                ⚡ Optimized & Indexed
            </div>
        """, unsafe_allow_html=True)

    # ========================================================================
    # DASHBOARD MODULE
    # ========================================================================
    
    if menu == "Dashboard":
        st.title("National Operations Dashboard")
        st.markdown("<p style='text-align: center; color: #6c757d; margin-bottom: 30px;'>Real-time System Intelligence</p>", 
                    unsafe_allow_html=True)
        
        # Fetch all data
        df_f = get_data("financial_records")
        df_i = get_data("identity_shield")
        df_c = get_data("consular_registry")
        df_t = get_data("ticketchain_tickets")
        df_e = get_data("ticketchain_events")
        
        # Top metrics
        c1, c2, c3, c4 = st.columns(4, gap="large")
        c1.metric("Verified Identities", len(df_i))
        c2.metric("Total Capital Pool", f"€ {df_f['amount'].sum():,.0f}" if not df_f.empty else "€ 0")
        c3.metric("Tickets Minted", len(df_t) if not df_t.empty else 0)
        c4.metric("Active Events", len(df_e) if not df_e.empty else 0)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Financial Distribution")
            if not df_f.empty:
                sector_data = df_f.groupby("sector")["amount"].sum()
                st.bar_chart(sector_data)
            else:
                st.info("No financial data yet")
        
        with col2:
            st.subheader("🛡️ Identity Risk Overview")
            if not df_i.empty:
                risk_counts = df_i['risk_level'].value_counts()
                st.bar_chart(risk_counts)
            else:
                st.info("No identity data yet")

    # ========================================================================
    # IDENTITY SHIELD MODULE
    # ========================================================================
    
    elif menu == "Identity Shield":
        st.title("Identity Shield")
        st.info("📋 Institutional Identity Verification & Risk Assessment")
        
        # Registration form
        with st.expander("👤 Register New Identity", expanded=False):
            with st.form("id_reg"):
                col1, col2 = st.columns(2)
                
                with col1:
                    raw_id = st.text_input("ID/Passport Number", help="Unique identifier")
                    name = st.text_input("Full Legal Name")
                
                with col2:
                    role = st.selectbox("Role", ["Official", "Investor", "Athlete", "Partner", "Fan"])
                    country = st.text_input("Country of Origin")
                
                if st.form_submit_button("VERIFY & STORE", use_container_width=True):
                    sid = sanitize_id(raw_id)
                    
                    if not sid:
                        st.error("Invalid ID. Min 3 characters, alphanumeric only.")
                    elif not name:
                        st.error("Name is required.")
                    elif check_duplicate_id(sid, 'identity_shield'):
                        st.error(f"ID '{sid}' already exists.")
                    else:
                        risk = "MEDIUM" if role == "Investor" else "LOW"
                        
                        success = run_query(
                            "INSERT INTO identity_shield VALUES (?, ?, ?, ?, ?, ?)",
                            (sid, name, role, country, risk, datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Identity '{name}' secured with risk level: {risk}")
                            st.rerun()
        
        st.divider()
        
        # Display identities
        st.write("### Verified Identities Registry")
        df = get_data("identity_shield")
        
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No verified identities yet. Register the first identity above.")

    # ========================================================================
    # TICKETCHAIN™ ADAPTER (OPTIMIZED)
    # ========================================================================
    
    elif menu == "TicketChain Adapter":
        st.title("TicketChain™ Blockchain Ticketing")
        st.info("🎫 Fraud-Proof Smart Ticketing with Cryptographic Validation")
        
        # QR availability check
        if not QR_AVAILABLE:
            st.warning("⚠️ QR code generation unavailable. Install with: `pip install qrcode[pil]`")
        
        # Three tabs
        tab1, tab2, tab3 = st.tabs([
            "🏟️ Event Management", 
            "🎟️ Box Office (Minting)", 
            "✅ Ticket Validator"
        ])
        
        # TAB 1: EVENT MANAGEMENT
        with tab1:
            st.subheader("Create New Event")
            
            with st.form("new_event"):
                col1, col2 = st.columns(2)
                
                with col1:
                    e_name = st.text_input("Event Name", placeholder="e.g., Derby Casablanca")
                    e_loc = st.text_input("Location", placeholder="e.g., Mohamed V Stadium")
                
                with col2:
                    e_date = st.date_input("Event Date")
                    e_cap = st.number_input("Capacity", min_value=100, step=100, value=1000)
                
                if st.form_submit_button("🚀 DEPLOY EVENT CONTRACT", use_container_width=True):
                    if not e_name or not e_loc:
                        st.error("❌ Event name and location are required.")
                    else:
                        eid = f"EVT-{uuid.uuid4().hex[:6].upper()}"
                        
                        success = run_query(
                            "INSERT INTO ticketchain_events VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (eid, e_name, e_loc, str(e_date), e_cap, 0, datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Event Contract Deployed: {eid}")
                            st.balloons()
                            st.rerun()
            
            st.divider()
            
            # Display events
            st.write("### Active Events")
            df_events = get_data("ticketchain_events")
            
            if not df_events.empty:
                for index, row in df_events.iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
                        
                        col1.markdown(f"**{row['name']}**")
                        col2.write(f"📍 {row['location']}")
                        col3.write(f"📅 {row['date']}")
                        
                        sold = row['tickets_sold'] if 'tickets_sold' in row else 0
                        capacity = row['capacity']
                        
                        if sold >= capacity:
                            col4.markdown("🔴 **SOLD OUT**")
                        else:
                            col4.markdown(f"🟢 {sold}/{capacity}")
                        
                        st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
            else:
                st.info("📭 No events yet. Create your first event above.")
        
        # TAB 2: MINTING (OPTIMIZED WITH INDEXES)
        with tab2:
            st.subheader("Mint Smart Tickets on Blockchain")
            
            events_df = get_data("ticketchain_events")
            id_map = get_identity_names_map()
            
            if events_df.empty:
                st.warning("⚠️ No events available. Please create an event first in Event Management tab.")
            elif not id_map:
                st.warning("⚠️ No verified identities found. Please register buyers in Identity Shield first.")
            else:
                event_options = dict(zip(events_df['event_id'], events_df['name']))
                
                with st.form("mint_ticket"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        sel_event_id = st.selectbox(
                            "Select Event", 
                            list(event_options.keys()), 
                            format_func=lambda x: f"{event_options[x]} ({x})"
                        )
                        
                        sel_owner_id = st.selectbox(
                            "Select Buyer (Verified Identity)", 
                            list(id_map.keys()), 
                            format_func=lambda x: f"{id_map[x]} ({x})"
                        )
                    
                    with col2:
                        seat_info = st.text_input("Seat / Zone Assignment", placeholder="e.g., VIP Row 5 Seat 12")
                        price = st.number_input("Price (MAD)", min_value=0.0, step=10.0, value=100.0)
                    
                    # Show capacity (fast with indexes)
                    capacity, sold, available, is_full = check_event_capacity(sel_event_id)
                    st.info(f"📊 Event Capacity: {sold}/{capacity} tickets sold • {available} remaining")
                    
                    if st.form_submit_button("🎫 MINT TICKET ON BLOCKCHAIN", use_container_width=True):
                        
                        # SECURITY VALIDATION
                        if is_full:
                            st.error(f"❌ EVENT SOLD OUT! All {capacity} tickets have been minted.")
                        elif not seat_info.strip():
                            st.error("❌ Seat assignment is required.")
                        else:
                            seat_taken, existing_owner = check_seat_availability(sel_event_id, seat_info)
                            
                            if seat_taken:
                                st.error(f"❌ Seat '{seat_info}' is already assigned to {existing_owner}")
                            else:
                                # All validations passed
                                ts = datetime.now().isoformat()
                                t_hash = generate_ticket_hash(sel_event_id, sel_owner_id, seat_info, ts)
                                
                                try:
                                    # Insert ticket
                                    success = run_query(
                                        "INSERT INTO ticketchain_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                        (t_hash, sel_event_id, sel_owner_id, seat_info, price, "VALID", ts, None, 1)
                                    )
                                    
                                    if success:
                                        # Update counter
                                        update_event_ticket_count(sel_event_id)
                                        
                                        # Log fiscal
                                        fiscal_success, tax, net = log_fiscal_transaction(t_hash, price)
                                        
                                        # Generate QR
                                        qr_bytes = generate_qr_code(t_hash)
                                        
                                        # Success display
                                        st.success("✅ TICKET SUCCESSFULLY MINTED!")
                                        st.balloons()
                                        
                                        # --- LAYOUT UPDATE VOOR BETER ZICHTBARE HASH ---
                                        
                                        col_a, col_b = st.columns(2)
                                        
                                        with col_a:
                                            st.markdown("#### 🎫 Ticket Details")
                                            st.text(f"""
Event: {event_options[sel_event_id]}
Owner: {id_map[sel_owner_id]}
Seat:  {seat_info}
Price: {price:.2f} MAD
                                            """)
                                        
                                        with col_b:
                                            if fiscal_success:
                                                st.markdown("#### 💰 Fiscal Breakdown")
                                                st.write(f"**Gross:** {price:.2f} MAD")
                                                st.write(f"**Tax (15%):** {tax:.2f} MAD")
                                                st.write(f"**Net Revenue:** {net:.2f} MAD")
                                        
                                        # 2. DE HASH NU GROOT OVER VOLLE BREEDTE
                                        st.markdown("---")
                                        st.markdown("### 🔐 Blockchain Hash (Unique ID)")
                                        # We gebruiken st.code voor een opvallende box
                                        st.code(t_hash, language="text") 
                                        st.caption("👆 Dit is de onveranderlijke sleutel van dit ticket op de blockchain.")
                                        st.markdown("---")

                                        # 3. QR Code
                                        if qr_bytes:
                                            col_qr1, col_qr2 = st.columns([1, 3])
                                            with col_qr1:
                                                st.image(qr_bytes, caption="Entry Scan", width=150)
                                            with col_qr2:
                                                st.markdown("#### 📱 Digital Asset Ready")
                                                st.write("Scan this code at the venue entrance.")
                                                st.download_button(
                                                    "📥 Download PNG Ticket",
                                                    qr_bytes,
                                                    f"ticket_{t_hash[:8]}.png",
                                                    "image/png"
                                                )
                                        else:
                                            st.info("📱 QR code unavailable.")
                                        
                                        st.success(f"✅ Tickets remaining for this event: {available - 1}")
                                
                                except Exception as e:
                                    st.error(f"❌ Minting failed: {str(e)}")
                
                st.divider()
                
                # Display ledger
                st.write("### 📋 Blockchain Ticket Ledger")
                df_tickets = get_data("ticketchain_tickets")
                
                if not df_tickets.empty:
                    display_df = df_tickets.copy()
                    display_df['price'] = display_df['price'].apply(lambda x: f"{x:.2f} MAD")
                    display_df['hash_preview'] = display_df['ticket_hash'].apply(lambda x: f"{x[:16]}...")
                    
                    cols_to_show = ['hash_preview', 'event_id', 'owner_id', 'seat_info', 'price', 'status', 'minted_at']
                    st.dataframe(display_df[cols_to_show], use_container_width=True, hide_index=True)
                else:
                    st.info("📭 No tickets minted yet.")
        
        # TAB 3: VALIDATOR
        with tab3:
            st.subheader("Verify Ticket Authenticity")
            st.markdown("Scan QR code or manually input ticket hash to verify against the blockchain ledger.")
            
            check_hash = st.text_input("🔍 Input Ticket Hash (64 characters)", 
                                       placeholder="Enter full ticket hash...")
            
            col_v1, col_v2 = st.columns([1, 1])
            
            with col_v1:
                if st.button("✅ VERIFY AUTHENTICITY", use_container_width=True):
                    if not check_hash or len(check_hash.strip()) != 64:
                        st.error("❌ Invalid hash format. Hash must be 64 characters.")
                    else:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("SELECT * FROM ticketchain_tickets WHERE ticket_hash = ?", (check_hash.strip(),))
                        res = c.fetchone()
                        conn.close()
                        
                        if res:
                            ticket_status = res[5]
                            
                            if ticket_status == "VALID":
                                st.success("✅ TICKET IS VALID AND AUTHENTIC")
                                st.json({
                                    "Event ID": res[1],
                                    "Owner ID": res[2],
                                    "Seat": res[3],
                                    "Price": f"{res[4]:.2f} MAD",
                                    "Status": res[5],
                                    "Minted At": res[6],
                                    "Used At": res[7] if res[7] else "Not used yet"
                                })
                            elif ticket_status == "USED":
                                st.warning("⚠️ TICKET HAS ALREADY BEEN USED")
                                st.write(f"Used at: {res[7]}")
                            elif ticket_status == "CANCELLED":
                                st.error("❌ TICKET HAS BEEN CANCELLED")
                            else:
                                st.info(f"ℹ️ Ticket status: {ticket_status}")
                        else:
                            st.error("❌ INVALID TICKET - NOT FOUND IN BLOCKCHAIN")
                            st.warning("⚠️ POSSIBLE FRAUD ATTEMPT DETECTED")
            
            with col_v2:
                if st.button("🎟️ MARK AS USED", use_container_width=True):
                    if not check_hash or len(check_hash.strip()) != 64:
                        st.error("❌ Invalid hash format.")
                    else:
                        conn = sqlite3.connect(DB_FILE)
                        c = conn.cursor()
                        c.execute("SELECT status FROM ticketchain_tickets WHERE ticket_hash = ?", (check_hash.strip(),))
                        res = c.fetchone()
                        
                        if not res:
                            st.error("❌ Ticket not found.")
                        elif res[0] == "USED":
                            st.warning("⚠️ Ticket already marked as used.")
                        elif res[0] == "CANCELLED":
                            st.error("❌ Cannot use cancelled ticket.")
                        else:
                            c.execute("UPDATE ticketchain_tickets SET status = 'USED', used_at = ? WHERE ticket_hash = ?",
                                    (datetime.now().isoformat(), check_hash.strip()))
                            conn.commit()
                            st.success("✅ Ticket successfully marked as USED")
                            st.info("Entry granted. Enjoy the event!")
                            # Refresh to update status immediately
                            time.sleep(1)
                            st.rerun()
                        
                        conn.close()
            
            st.divider()
            
            # Statistics
            st.write("### 📊 Validation Statistics")
            df_all_tickets = get_data("ticketchain_tickets")
            
            if not df_all_tickets.empty:
                col_s1, col_s2, col_s3 = st.columns(3)
                
                total_tickets = len(df_all_tickets)
                valid_tickets = len(df_all_tickets[df_all_tickets['status'] == 'VALID'])
                used_tickets = len(df_all_tickets[df_all_tickets['status'] == 'USED'])
                
                col_s1.metric("Total Minted", total_tickets)
                col_s2.metric("Valid (Not Used)", valid_tickets)
                col_s3.metric("Already Used", used_tickets)

    # ========================================================================
    # SPORT ADAPTER
    # ========================================================================
    
    elif menu == "Sport Adapter":
        st.title("Sport Adapter (National AMS)")
        st.info("🏆 Athlete Management System - FRMF Integration Ready")
        
        id_map = get_identity_names_map()
        
        with st.expander("➕ Register Athlete Record", expanded=False):
            with st.form("sport_reg"):
                col1, col2 = st.columns(2)
                
                with col1:
                    athlete_id = st.selectbox("Select Verified Identity", 
                                                list(id_map.keys()), 
                                                format_func=lambda x: id_map.get(x, x))
                    discipline = st.text_input("Discipline/Position", placeholder="e.g., Forward")
                
                with col2:
                    club = st.text_input("Current Club", placeholder="e.g., Raja Casablanca")
                    stat = st.selectbox("Status", ["Active", "Injured", "Transfer", "Retired"])
                
                c_end = st.date_input("Contract End Date")
                
                if st.form_submit_button("UPDATE RECORD", use_container_width=True):
                    if not athlete_id:
                        st.error("❌ Please select an identity.")
                    elif not discipline:
                        st.error("❌ Discipline is required.")
                    else:
                        s_id = f"ATH-{uuid.uuid4().hex[:4].upper()}"
                        
                        success = run_query(
                            "INSERT INTO sport_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (s_id, athlete_id, discipline, club, stat, str(c_end), datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success("✅ Athlete Management System Updated")
                            st.rerun()
        
        st.divider()
        st.write("### Registered Athletes")
        st.dataframe(get_data("sport_records"), use_container_width=True, hide_index=True)

    # ========================================================================
    # FINANCIAL ADAPTER
    # ========================================================================
    
    elif menu == "Financial Adapter":
        st.title("Financial Adapter (Foundation Bank)")
        st.info("💰 Institutional Investment Tracking & Portfolio Management")
        
        id_map = get_identity_names_map()
        
        with st.expander("➕ Log New Transaction", expanded=False):
            with st.form("fin_reg"):
                col1, col2 = st.columns(2)
                
                with col1:
                    e_id = st.selectbox("Linked Entity", 
                                        list(id_map.keys()), 
                                        format_func=lambda x: id_map.get(x, x))
                    amt = st.number_input("Amount (€)", min_value=0.0, step=1000.0)
                
                with col2:
                    sector = st.selectbox("Sector", ["Energy", "Tech", "Real Estate", "Sports", "Infrastructure"])
                    tx_type = st.selectbox("Type", ["Investment Inbound", "Dividend Payout", "Operational Cost"])
                
                if st.form_submit_button("LOG TRANSACTION", use_container_width=True):
                    if not e_id: 
                        st.error("❌ Identity required.")
                    elif amt <= 0: 
                        st.error("❌ Amount must be positive.")
                    else:
                        tx_id = f"TX-{uuid.uuid4().hex[:5].upper()}"
                        
                        success = run_query(
                            "INSERT INTO financial_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (tx_id, e_id, amt, tx_type, sector, "Approved", datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Transaction {tx_id} logged: € {amt:,.2f}")
                            st.rerun()
        
        st.divider()
        
        # Portfolio overview
        df = get_data("financial_records")
        
        if not df.empty:
            st.write("### 📊 Portfolio Overview")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Volume", f"€ {df['amount'].sum():,.0f}")
            col2.metric("Avg Transaction", f"€ {df['amount'].mean():,.0f}")
            col3.metric("Total Transactions", len(df))
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            c_a, c_b = st.columns(2)
            with c_a:
                st.write("#### 📊 Sector Distribution")
                st.bar_chart(df.groupby("sector")["amount"].sum())
            with c_b:
                st.write("#### 💼 Transaction Types")
                st.bar_chart(df.groupby("type")["amount"].sum())
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("### 📋 Transaction Ledger")
            
            disp_df = df.copy()
            disp_df['amount'] = disp_df['amount'].apply(lambda x: f"€ {x:,.2f}")
            st.dataframe(disp_df, use_container_width=True, hide_index=True)
        else:
            st.info("📭 No transactions logged yet.")

    # ========================================================================
    # CONSULAR VAULT
    # ========================================================================
    
    elif menu == "Consular Vault":
        st.title("Consular Vault (Digital Consulate Hub)")
        st.info("📄 Secure Sovereign Document Management")
        
        # Upload form
        with st.expander("➕ Upload Sovereign Document", expanded=False):
            with st.form("vault_upload"):
                col1, col2 = st.columns(2)
                
                with col1:
                    doc_id = st.text_input("Document ID", placeholder="e.g., PIX-2025-001")
                    doc_type = st.selectbox("Type", ["Passport", "Visa Application", "Contract", "Birth Certificate"])
                
                with col2:
                    status = st.selectbox("Initial Status", ["Pending", "Approved", "Under Review"])
                    file = st.file_uploader("Select File", type=['pdf', 'jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("🔐 EXECUTE INSERT", use_container_width=True):
                    sid = sanitize_id(doc_id)
                    
                    if not file:
                        st.error("❌ Please select a file.")
                    elif not sid:
                        st.error("❌ Invalid ID. Min 3 characters.")
                    elif check_duplicate_id(sid, 'consular_registry'):
                        st.error(f"❌ ID '{sid}' already exists.")
                    elif file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        st.error(f"❌ File exceeds {MAX_FILE_SIZE_MB}MB limit.")
                    else:
                        fname = sanitize_filename(file.name)
                        unique_fname = f"{uuid.uuid4().hex[:8]}_{fname}"
                        fpath = os.path.join(VAULT_DIR, f"{sid}_{unique_fname}")
                        
                        with open(fpath, "wb") as f: 
                            f.write(file.getbuffer())
                        
                        success = run_query(
                            "INSERT INTO consular_registry VALUES (?, ?, ?, ?, ?)",
                            (sid, doc_type, unique_fname, status, datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Document '{fname}' secured with ID: {sid}")
                            st.rerun()
        
        st.divider()
        
        # Search and filter
        col_search, col_status = st.columns([3, 1])
        with col_search:
            search_q = st.text_input("🔍 Search by ID or Filename", "", placeholder="Type to search...")
        with col_status:
            status_filter = st.selectbox("Filter", ["All", "Pending", "Approved", "Under Review"])
        
        df = get_data("consular_registry")
        
        if not df.empty:
            filtered_df = df.copy()
            
            if search_q:
                q = search_q.lower()
                filtered_df = filtered_df[
                    filtered_df['id'].str.lower().str.contains(q) | 
                    filtered_df['filename'].str.lower().str.contains(q)
                ]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if filtered_df.empty:
                st.info("🔍 No documents match your search criteria.")
            else:
                st.write(f"### 📂 Documents ({len(filtered_df)} found)")
                
                for index, row in filtered_df.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 0.5])
                    
                    c1.write(f"**`{row['id']}`**")
                    
                    display_name = row['filename'].split('_', 1)[-1] if '_' in row['filename'] else row['filename']
                    c2.write(f"{display_name} • {row['doc_type']}")
                    c3.write(row['status'])
                    
                    fpath = os.path.join(VAULT_DIR, f"{row['id']}_{row['filename']}")
                    
                    if os.path.exists(fpath):
                        try:
                            with open(fpath, "rb") as f:
                                c4.download_button("📥 Download", f.read(), file_name=display_name, key=f"dl_{row['id']}")
                        except:
                            c4.write("❌")
                    else:
                        c4.write("⚠️")
                    
                    if c5.button("🗑️", key=f"del_{row['id']}"):
                        try:
                            if os.path.exists(fpath): 
                                os.remove(fpath)
                            run_query("DELETE FROM consular_registry WHERE id = ?", (row['id'],))
                            st.success(f"✅ Document {row['id']} deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        else:
            st.info("📭 Vault is empty.")

    # ========================================================================
    # MOBILITY ADAPTER
    # ========================================================================
    
    elif menu == "Mobility Adapter":
        st.title("Mobility Adapter (National Logistics)")
        st.info("🚚 Infrastructure & Fleet Asset Management")
        
        with st.expander("➕ Deploy New Asset", expanded=False):
            with st.form("mob"):
                col1, col2 = st.columns(2)
                
                with col1:
                    asset = st.text_input("Asset Name", placeholder="e.g., Hub Alpha")
                    m_type = st.selectbox("Type", ["Vehicle", "Fleet Unit", "Logistics Hub", "Infrastructure"])
                
                with col2:
                    region = st.text_input("Region", placeholder="e.g., Casablanca")
                    m_stat = st.selectbox("Status", ["Operational", "Maintenance", "In Transit"])
                
                if st.form_submit_button("DEPLOY", use_container_width=True):
                    if not asset or not region:
                        st.error("❌ Asset Name and Region required.")
                    else:
                        mid = f"MOB-{uuid.uuid4().hex[:4].upper()}"
                        
                        success = run_query(
                            "INSERT INTO mobility_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (mid, asset, m_type, region, m_stat, datetime.now().strftime("%Y-%m-%d"), datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Asset '{asset}' deployed")
                            st.rerun()
        
        st.divider()
        st.write("### 🚗 Operational Fleet")
        st.dataframe(get_data("mobility_records"), use_container_width=True, hide_index=True)

    # ========================================================================
    # HEALTH ADAPTER
    # ========================================================================
    
    elif menu == "Health Adapter":
        st.title("Health Adapter")
        st.info("⚕️ Secure Health Information Management")
        
        id_map = get_identity_names_map()
        
        with st.expander("➕ Register Health Record", expanded=False):
            with st.form("health"):
                col1, col2 = st.columns(2)
                
                with col1:
                    p_id = st.selectbox("Identity", list(id_map.keys()), format_func=lambda x: id_map.get(x, x))
                    h_type = st.selectbox("Checkup", ["Bio-Scan", "General Health", "Sports Medical"])
                
                with col2:
                    h_stat = st.selectbox("Clearance", ["CLEARED", "RESTRICTED", "PENDING"])
                    exp_date = st.date_input("Expiry Date")
                
                if st.form_submit_button("COMMIT", use_container_width=True):
                    if not p_id: 
                        st.error("❌ Identity required.")
                    else:
                        hid = f"HLT-{uuid.uuid4().hex[:4].upper()}"
                        
                        success = run_query(
                            "INSERT INTO health_records VALUES (?, ?, ?, ?, ?, ?)",
                            (hid, p_id, h_type, h_stat, str(exp_date), datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success("✅ Health record secured")
                            st.rerun()
        
        st.divider()
        st.write("### 🏥 Medical Records")
        st.dataframe(get_data("health_records"), use_container_width=True, hide_index=True)

    # Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align: center; color: #6c757d; font-size: 0.85em;'>
            © 2025 PRO INVEST X IT-CELL | v5.0.4 Ultimate Production Edition<br>
            Secure • Scalable • Sovereign • Blockchain-Ready • ⚡ Optimized
        </div>
    """, unsafe_allow_html=True)
