import streamlit as st
import pandas as pd
import os
import sqlite3
import re
import uuid
import base64
from datetime import datetime

# 1. CONSTANTS & SYSTEM SETUP
VAULT_DIR = "consular_vault"
DB_FILE = "proinvestix_core.db"
MAX_FILE_SIZE_MB = 50
ALLOWED_TABLES = ['consular_registry', 'identity_shield', 'financial_records', 
                  'sport_records', 'mobility_records', 'health_records']

LOGO_TEXT = "logo_text.jpg"
LOGO_SHIELD = "logo_shield.jpg"

if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

# 2. DATABASE SETUP
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Consular
    c.execute('''CREATE TABLE IF NOT EXISTS consular_registry
                 (id TEXT PRIMARY KEY, doc_type TEXT, filename TEXT, status TEXT, timestamp TEXT)''')
    # Identity
    c.execute('''CREATE TABLE IF NOT EXISTS identity_shield
                 (id TEXT PRIMARY KEY, name TEXT, role TEXT, country TEXT, risk_level TEXT, timestamp TEXT)''')
    # Financial
    c.execute('''CREATE TABLE IF NOT EXISTS financial_records
                 (id TEXT PRIMARY KEY, entity_id TEXT, amount REAL, type TEXT, sector TEXT, status TEXT, timestamp TEXT)''')
    # Sport
    c.execute('''CREATE TABLE IF NOT EXISTS sport_records
                 (id TEXT PRIMARY KEY, identity_id TEXT, discipline TEXT, club TEXT, status TEXT, contract_end TEXT, timestamp TEXT)''')
    # Mobility
    c.execute('''CREATE TABLE IF NOT EXISTS mobility_records
                 (id TEXT PRIMARY KEY, asset_name TEXT, type TEXT, region TEXT, status TEXT, last_maint TEXT, timestamp TEXT)''')
    # Health
    c.execute('''CREATE TABLE IF NOT EXISTS health_records
                 (id TEXT PRIMARY KEY, identity_id TEXT, checkup_type TEXT, medical_status TEXT, expiry_date TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. CORE SECURE FUNCTIONS ---
def sanitize_id(doc_id):
    if not doc_id: return None
    safe_id = re.sub(r'[^a-zA-Z0-9_-]', '', doc_id)
    return safe_id if len(safe_id) >= 3 else None

def sanitize_filename(filename):
    if not filename: return None
    filename = os.path.basename(filename)
    return re.sub(r'[^\w\s.-]', '', filename)

def sanitize_text(text):
    if not text: return None
    return re.sub(r'[^a-zA-Z0-9\s_.-]', '', text)

def check_duplicate_id(doc_id, table):
    if table not in ALLOWED_TABLES: return True
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT 1 FROM {table} WHERE id = ?", (doc_id,))
    res = c.fetchone()
    conn.close()
    return res is not None

def run_query(sql, params=()):
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
    if table not in ALLOWED_TABLES: raise ValueError("Unauthorized")
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY timestamp DESC", conn)
    conn.close()
    return df

def get_identity_names_map():
    df = get_data("identity_shield")
    return dict(zip(df['id'], df['name'])) if not df.empty else {}

# --- 4. UI/UX STYLING (FIXED COLORS - PERFECT CONTRAST) ---
st.set_page_config(page_title="ProInvestiX - National Architecture", layout="wide")
st.markdown("""
    <style>
    /* Main App Background - Light gradient */
    .stApp { 
        background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); 
        color: #1a1a1a; 
    }
    
    /* Sidebar - Dark purple with white text */
    [data-testid="stSidebar"] { 
        background-color: #2e0d43 !important; 
        box-shadow: 5px 0 15px rgba(0,0,0,0.1);
    }
    
    /* Sidebar text - All white for contrast */
    [data-testid="stSidebar"] * { 
        color: #ffffff !important; 
        font-weight: 500;
    }
    
    /* Sidebar radio buttons - better visibility */
    [data-testid="stSidebar"] .stRadio > label {
        color: #ffffff !important;
        font-size: 0.95em;
    }
    
    /* Sidebar radio selected state */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label[data-checked="true"] {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: 700;
    }
    
    /* Main content text - Dark for readability */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #1a1a1a !important;
    }
    
    /* Buttons - Purple gradient with white text */
    .stButton>button {
        background: linear-gradient(90deg, #4a148c 0%, #6a1b9a 100%);
        color: white !important;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(46, 13, 67, 0.2);
        transition: all 0.3s ease;
        padding: 10px 24px;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 12px rgba(46, 13, 67, 0.3);
        transform: translateY(-2px);
        background: linear-gradient(90deg, #6a1b9a 0%, #8e24aa 100%);
    }
    
    /* Metrics - White cards with dark text */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e0e0;
    }
    
    [data-testid="stMetricLabel"] { 
        color: #4a148c !important;
        font-weight: 700;
        font-size: 0.9em;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricValue"] { 
        color: #1a1a1a !important;
        font-size: 2.2em !important;
        font-weight: 800 !important;
    }
    
    /* Input fields - White background with dark text */
    input, textarea, select {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #d0d0d0 !important;
        border-radius: 6px !important;
        padding: 8px 12px !important;
    }
    
    input::placeholder, textarea::placeholder {
        color: #757575 !important;
    }
    
    /* Dropdown/Select - Better contrast */
    [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="select"] * {
        color: #1a1a1a !important;
    }
    
    /* Dataframe/Tables - Clean styling */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    /* Expander headers - Light background */
    .streamlit-expanderHeader {
        background-color: #f5f5f5 !important;
        border-radius: 8px;
        font-weight: 600;
        color: #1a1a1a !important;
        border: 1px solid #e0e0e0;
    }
    
    /* Success/Error/Info messages - Good contrast */
    .stSuccess {
        background-color: #e8f5e9;
        color: #1b5e20 !important;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #4caf50;
    }
    
    .stError {
        background-color: #ffebee;
        color: #c62828 !important;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #f44336;
    }
    
    .stInfo {
        background-color: #e3f2fd;
        color: #0d47a1 !important;
        padding: 12px;
        border-radius: 6px;
        border-left: 4px solid #2196f3;
    }
    
    /* Download buttons - Small and subtle */
    .stDownloadButton button {
        background-color: #4a148c !important;
        color: white !important;
        padding: 6px 12px !important;
        font-size: 0.85em !important;
    }
    
    /* Form labels - Dark and bold */
    label {
        color: #1a1a1a !important;
        font-weight: 600 !important;
        font-size: 0.9em !important;
    }
    
    /* Divider lines */
    hr {
        border-color: #e0e0e0 !important;
    }
    
    /* Footer text */
    footer {
        color: #757575 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 5. MAIN APP ---
if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False

if not st.session_state['ingelogd']:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_TEXT): st.image(LOGO_TEXT)
        else:
            st.markdown("<h1 style='text-align: center; color: #2e0d43;'>PRO INVEST X</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: #4a148c; margin-top: 20px;'>AUTHORIZED ACCESS</h3>", 
                   unsafe_allow_html=True)
        
        with st.form("login"):
            u = st.text_input("Username", placeholder="Enter your username")
            p = st.text_input("Access Key", type="password", placeholder="Enter your password")
            if st.form_submit_button("🔐 AUTHENTICATE", use_container_width=True):
                if u == "admin" and p == "invest2025":
                    st.session_state.ingelogd = True
                    st.rerun()
                else:
                    st.error("❌ Invalid Credentials")
else:
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        if os.path.exists(LOGO_TEXT): 
            st.image(LOGO_TEXT)
        else:
            st.markdown("<h2 style='text-align: center; color: #ffffff;'>PRO INVEST X</h2>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if os.path.exists(LOGO_SHIELD):
            c1, c2, c3 = st.columns([0.5, 2, 0.5])
            with c2: 
                st.image(LOGO_SHIELD)
        
        st.markdown("<br><p style='font-weight: bold; letter-spacing: 1px; color: #ffffff;'>OPERATIONAL MODULES</p>", 
                   unsafe_allow_html=True)
        
        menu = st.radio("NAVIGATION", [
            "📊 Dashboard", 
            "🛡️ Identity Shield", 
            "📈 Financial", 
            "⚽ Sport", 
            "🚗 Mobility", 
            "🏥 Health", 
            "🛂 Consular Vault"
        ], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🔒 LOGOUT", use_container_width=True):
            st.session_state.ingelogd = False
            st.rerun()
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""<div style='text-align: center; font-size: 0.75em; color: rgba(255,255,255,0.7);'>
                    © 2025 PRO INVEST X<br>IT-CELL | v4.6 Production
                    </div>""", unsafe_allow_html=True)

    # --- DASHBOARD ---
    if menu == "📊 Dashboard":
        st.title("🏛️ National Operations Dashboard")
        st.markdown("<p style='text-align: center; color: #666; margin-bottom: 30px;'>Real-time System Intelligence</p>", 
                   unsafe_allow_html=True)
        
        # Fetch all data
        df_f = get_data("financial_records")
        df_i = get_data("identity_shield")
        df_c = get_data("consular_registry")
        df_s = get_data("sport_records")
        
        # Top metrics (4 columns)
        c1, c2, c3, c4 = st.columns(4, gap="large")
        c1.metric("Verified Identities", len(df_i))
        c2.metric("Total Capital Pool", f"€ {df_f['amount'].sum():,.0f}")
        c3.metric("Secured Documents", len(df_c))
        c4.metric("Active Modules", "6/6")
        
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

    # --- IDENTITY SHIELD ---
    elif menu == "🛡️ Identity Shield":
        st.title("🛡️ Identity Shield")
        st.info("📋 Institutional Identity Verification & Risk Assessment")
        
        with st.expander("👤 Register New Identity", expanded=False):
            with st.form("id_reg"):
                col1, col2 = st.columns(2)
                with col1:
                    raw_id = st.text_input("ID/Passport Number", help="Unique identifier")
                    name = st.text_input("Full Legal Name")
                with col2:
                    role = st.selectbox("Role", ["Official", "Investor", "Athlete", "Partner"])
                    country = st.text_input("Country of Origin")
                
                if st.form_submit_button("VERIFY & STORE", use_container_width=True):
                    sid = sanitize_id(raw_id)
                    if not sid:
                        st.error("❌ Invalid ID. Min 3 characters, alphanumeric only.")
                    elif not name:
                        st.error("❌ Name is required.")
                    elif check_duplicate_id(sid, 'identity_shield'):
                        st.error(f"❌ ID '{sid}' already exists.")
                    else:
                        risk = "MEDIUM" if role == "Investor" else "LOW"
                        run_query("INSERT INTO identity_shield VALUES (?, ?, ?, ?, ?, ?)",
                                  (sid, name, role, country, risk, datetime.now().isoformat()))
                        st.success(f"✅ Identity '{name}' secured with risk level: {risk}")
                        st.rerun()
        
        st.divider()
        st.write("### Verified Identities Registry")
        st.dataframe(get_data("identity_shield"), use_container_width=True, hide_index=True)

    # --- SPORT ADAPTER ---
    elif menu == "⚽ Sport":
        st.title("⚽ Sport Adapter (National AMS)")
        st.info("🏆 Athlete Management System - FRMF Integration Ready")
        
        id_map = get_identity_names_map()
        
        with st.expander("➕ Register Athlete Record", expanded=False):
            with st.form("sport_reg"):
                if not id_map:
                    st.warning("⚠️ No verified identities found. Please register a person first in Identity Shield.")
                
                col1, col2 = st.columns(2)
                with col1:
                    athlete_id = st.selectbox("Select Verified Identity", list(id_map.keys()), format_func=lambda x: id_map.get(x, x))
                    discipline = st.text_input("Discipline/Position", placeholder="e.g., Forward, Midfielder")
                with col2:
                    club = st.text_input("Current Club", placeholder="e.g., Raja Casablanca")
                    stat = st.selectbox("Status", ["Active", "Injured", "Transfer", "Retired"])
                
                c_end = st.date_input("Contract End Date")
                
                if st.form_submit_button("UPDATE ATHLETE RECORD", use_container_width=True):
                    if not athlete_id:
                        st.error("❌ Please select an identity.")
                    elif not discipline:
                        st.error("❌ Discipline is required.")
                    else:
                        s_id = f"ATH-{uuid.uuid4().hex[:4].upper()}"
                        run_query("INSERT INTO sport_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (s_id, athlete_id, discipline, club, stat, str(c_end), datetime.now().isoformat()))
                        st.success("✅ Athlete Management System Updated")
                        st.rerun()
        
        st.divider()
        st.write("### Registered Athletes")
        st.dataframe(get_data("sport_records"), use_container_width=True, hide_index=True)

    # --- FINANCIAL ADAPTER ---
    elif menu == "📈 Financial":
        st.title("📈 Financial Adapter (Foundation Bank)")
        st.info("💰 Institutional Investment Tracking & Portfolio Management")
        
        id_map = get_identity_names_map()
        
        # Form
        with st.expander("➕ Log New Transaction", expanded=False):
            with st.form("fin_reg"):
                if not id_map:
                    st.warning("⚠️ No verified identities found. Please register entities first in Identity Shield.")
                
                col1, col2 = st.columns(2)
                with col1:
                    e_id = st.selectbox("Linked Entity / Investor", list(id_map.keys()), format_func=lambda x: id_map.get(x, x))
                    amt = st.number_input("Amount (€)", min_value=0.0, step=1000.0, format="%.2f")
                with col2:
                    sector = st.selectbox("Target Sector", ["Energy", "Tech", "Real Estate", "Sports", "Infrastructure"])
                    tx_type = st.selectbox("Transaction Type", ["Investment Inbound", "Dividend Payout", "Operational Cost"])
                
                if st.form_submit_button("LOG TRANSACTION", use_container_width=True):
                    if not e_id: 
                        st.error("❌ Identity required.")
                    elif amt <= 0: 
                        st.error("❌ Amount must be positive.")
                    else:
                        tx_id = f"TX-{uuid.uuid4().hex[:5].upper()}"
                        run_query("INSERT INTO financial_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (tx_id, e_id, amt, tx_type, sector, "Approved", datetime.now().isoformat()))
                        st.success(f"✅ Transaction {tx_id} logged: € {amt:,.2f}")
                        st.rerun()
        
        st.divider()
        
        # Advanced Charts & Metrics
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
            st.info("📭 No financial transactions yet. Log your first transaction above.")

    # --- CONSULAR VAULT ---
    elif menu == "🛂 Consular Vault":
        st.title("🛂 Consular Vault (Digital Consulate Hub)")
        st.info("📄 Secure Sovereign Document Management System")
        
        # Upload
        with st.expander("➕ Upload Sovereign Document", expanded=False):
            with st.form("vault_upload"):
                col1, col2 = st.columns(2)
                with col1:
                    doc_id = st.text_input("Document ID", placeholder="e.g., PIX-2025-001")
                    doc_type = st.selectbox("Document Type", ["Passport", "Visa Application", "Contract", "Birth Certificate", "Legal Document"])
                with col2:
                    status = st.selectbox("Initial Status", ["Pending", "Approved", "Under Review"])
                    file = st.file_uploader("Select File", type=['pdf', 'jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("🔐 EXECUTE SECURE INSERT", use_container_width=True):
                    sid = sanitize_id(doc_id)
                    if not file:
                        st.error("❌ Please select a file.")
                    elif not sid:
                        st.error("❌ Invalid ID. Min 3 characters, alphanumeric/-/_ only.")
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
                        
                        run_query("INSERT INTO consular_registry VALUES (?, ?, ?, ?, ?)",
                                 (sid, doc_type, unique_fname, status, datetime.now().isoformat()))
                        st.success(f"✅ Document '{fname}' secured with ID: {sid}")
                        st.rerun()
        
        st.divider()
        
        # Search, Filter, Download, Delete
        col_search, col_status = st.columns([3, 1])
        with col_search:
            search_q = st.text_input("🔍 Search by ID or Filename", "", placeholder="Type to search...")
        with col_status:
            status_filter = st.selectbox("Filter Status", ["All", "Pending", "Approved", "Under Review"])
        
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
                st.write(f"### 📂 Documents Registry ({len(filtered_df)} found)")
                
                for index, row in filtered_df.iterrows():
                    c1, c2, c3, c4, c5 = st.columns([1, 2, 1, 1, 0.5])
                    
                    c1.write(f"**`{row['id']}`**")
                    
                    # Display filename without UUID
                    display_name = row['filename'].split('_', 1)[-1] if '_' in row['filename'] else row['filename']
                    c2.write(f"{display_name} • {row['doc_type']}")
                    
                    c3.write(f"**{row['status']}**")
                    
                    # Download
                    fpath = os.path.join(VAULT_DIR, f"{row['id']}_{row['filename']}")
                    if os.path.exists(fpath):
                        try:
                            with open(fpath, "rb") as f:
                                c4.download_button("📥 Download", f.read(), file_name=display_name, key=f"dl_{row['id']}")
                        except:
                            c4.write("❌ Error")
                    else:
                        c4.write("⚠️ Missing")
                    
                    # Delete
                    if c5.button("🗑️", key=f"del_{row['id']}"):
                        try:
                            if os.path.exists(fpath): 
                                os.remove(fpath)
                            run_query("DELETE FROM consular_registry WHERE id = ?", (row['id'],))
                            st.success(f"✅ Document {row['id']} deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Delete error: {str(e)}")
        else:
            st.info("📭 Vault is empty. Upload your first document above.")

    # --- MOBILITY ADAPTER ---
    elif menu == "🚗 Mobility":
        st.title("🚗 Mobility Adapter (National Logistics)")
        st.info("🚚 Infrastructure & Fleet Asset Management")
        
        with st.expander("➕ Deploy New Asset", expanded=False):
            with st.form("mob"):
                col1, col2 = st.columns(2)
                with col1:
                    asset = st.text_input("Asset Name", placeholder="e.g., Hub Alpha, Truck-01")
                    m_type = st.selectbox("Asset Type", ["Vehicle", "Fleet Unit", "Logistics Hub", "Infrastructure"])
                with col2:
                    region = st.text_input("Operational Region", placeholder="e.g., Casablanca, Rabat")
                    m_stat = st.selectbox("Current Status", ["Operational", "Maintenance", "In Transit", "Standby"])
                
                if st.form_submit_button("DEPLOY ASSET", use_container_width=True):
                    if not asset or not region:
                        st.error("❌ Asset Name and Region are required.")
                    else:
                        mid = f"MOB-{uuid.uuid4().hex[:4].upper()}"
                        run_query("INSERT INTO mobility_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (mid, asset, m_type, region, m_stat, datetime.now().strftime("%Y-%m-%d"), datetime.now().isoformat()))
                        st.success(f"✅ Asset '{asset}' deployed successfully")
                        st.rerun()
        
        st.divider()
        st.write("### 🚗 Operational Fleet & Infrastructure")
        st.dataframe(get_data("mobility_records"), use_container_width=True, hide_index=True)

    # --- HEALTH ADAPTER ---
    elif menu == "🏥 Health":
        st.title("🏥 Health Adapter (Medical Records)")
        st.info("⚕️ Secure Health Information Management System")
        
        id_map = get_identity_names_map()
        
        with st.expander("➕ Register Health Record", expanded=False):
            with st.form("health"):
                if not id_map:
                    st.warning("⚠️ No verified identities found. Please register individuals first in Identity Shield.")
                
                col1, col2 = st.columns(2)
                with col1:
                    p_id = st.selectbox("Linked Identity", list(id_map.keys()), format_func=lambda x: id_map.get(x, x))
                    h_type = st.selectbox("Checkup Type", ["Bio-Scan", "General Health", "Pre-Employment", "Sports Medical"])
                with col2:
                    h_stat = st.selectbox("Medical Clearance", ["CLEARED", "RESTRICTED", "PENDING REVIEW"])
                    exp_date = st.date_input("Certificate Expiry Date")
                
                if st.form_submit_button("COMMIT RECORD", use_container_width=True):
                    if not p_id: 
                        st.error("❌ Identity required.")
                    else:
                        hid = f"HLT-{uuid.uuid4().hex[:4].upper()}"
                        run_query("INSERT INTO health_records VALUES (?, ?, ?, ?, ?, ?)",
                                (hid, p_id, h_type, h_stat, str(exp_date), datetime.now().isoformat()))
                        st.success("✅ Health record secured")
                        st.rerun()
        
        st.divider()
        st.write("### 🏥 Medical Records Registry")
        st.dataframe(get_data("health_records"), use_container_width=True, hide_index=True)

    # Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center; color: #999; font-size: 0.85em;'>
                © 2025 PRO INVEST X IT-CELL | v4.6 Production Ready | Secure • Scalable • Sovereign
                </div>""", unsafe_allow_html=True)