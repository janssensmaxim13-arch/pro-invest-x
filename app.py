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

# LOGO FILENAMES (optional - work without them)
LOGO_TEXT = "logo_text.jpg"
LOGO_SHIELD = "logo_shield.jpg"

if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

# 2. DATABASE SETUP (Complete with all 3 active tables)
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Consular Registry
    c.execute('''CREATE TABLE IF NOT EXISTS consular_registry
                 (id TEXT PRIMARY KEY, doc_type TEXT, filename TEXT, status TEXT, timestamp TEXT)''')
    
    # Identity Shield (Enhanced with country)
    c.execute('''CREATE TABLE IF NOT EXISTS identity_shield
                 (id TEXT PRIMARY KEY, name TEXT, role TEXT, country TEXT, risk_level TEXT, timestamp TEXT)''')
    
    # Financial Records (NEW - Links to Identity)
    c.execute('''CREATE TABLE IF NOT EXISTS financial_records
                 (id TEXT PRIMARY KEY, entity_name TEXT, amount REAL, type TEXT, 
                  sector TEXT, status TEXT, timestamp TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="ProInvestiX - Institutional Platform", layout="wide")

# 3. STYLING - Subtle Prestige Theme (Improved Contrast)
st.markdown("""
    <style>
    /* Main App Background */
    .stApp { 
        background: linear-gradient(135deg, #ffffff 0%, #f3e5f5 100%); 
        color: #2e0d43; 
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { 
        background-color: #2e0d43 !important; 
        box-shadow: 5px 0 15px rgba(0,0,0,0.1); 
    }
    [data-testid="stSidebar"] *, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span { 
        color: #ffffff !important; 
        font-weight: 500; 
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4a148c 0%, #6a1b9a 100%);
        color: white; 
        border-radius: 8px; 
        border: none; 
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(46, 13, 67, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 6px 12px rgba(46, 13, 67, 0.3);
        transform: translateY(-2px);
    }
    
    /* Metrics - IMPROVED CONTRAST */
    [data-testid="stMetric"] {
        background-color: #ffffff; 
        border-radius: 15px; 
        padding: 25px;
        text-align: center; 
        box-shadow: 0 10px 25px rgba(46, 13, 67, 0.08);
    }
    [data-testid="stMetricLabel"] { 
        color: #4a148c !important;  /* DARKER for better contrast */
        font-weight: 700; 
        font-size: 0.95em;
    }
    [data-testid="stMetricValue"] { 
        color: #2e0d43 !important; 
        font-size: 2.5em !important; 
        font-weight: 800 !important; 
    }
    
    /* Risk Labels */
    .risk-low { 
        background-color: #e8f5e9; 
        color: #2e7d32; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-weight: bold; 
        font-size: 0.9em;
        display: inline-block;
    } 
    .risk-medium { 
        background-color: #fff3e0; 
        color: #ef6c00; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-weight: bold; 
        font-size: 0.9em;
        display: inline-block;
    } 
    .risk-high { 
        background-color: #ffebee; 
        color: #c62828; 
        padding: 4px 12px; 
        border-radius: 20px; 
        font-weight: bold; 
        font-size: 0.9em;
        display: inline-block;
    }
    
    /* Input Fields */
    input, textarea, select {
        border-radius: 8px !important;
    }
    
    /* Expander Headers */
    .streamlit-expanderHeader {
        background-color: rgba(74, 20, 140, 0.05);
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. CORE SECURE FUNCTIONS (Restored from v3.1) ---

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
    filename = os.path.basename(filename)  # Remove path
    return re.sub(r'[^\w\s.-]', '', filename)

def sanitize_text(text):
    """
    General text sanitization for names, descriptions, etc.
    Allows spaces, alphanumeric, basic punctuation.
    """
    if not text: 
        return None
    return re.sub(r'[^a-zA-Z0-9\s_.-]', '', text)

def check_duplicate_id(doc_id, table='consular_registry'):
    """
    Check if ID already exists in table.
    Prevents duplicate primary keys.
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table: {table}")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT 1 FROM {table} WHERE id = ?", (doc_id,))
    result = c.fetchone()
    conn.close()
    return result is not None

def get_data(table):
    """
    Secure table data retrieval with whitelist protection.
    """
    if table not in ALLOWED_TABLES:
        raise ValueError(f"Unauthorized table access: {table}")
    
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(f"SELECT * FROM {table} ORDER BY timestamp DESC", conn)
    conn.close()
    return df

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

def inject_centered_watermark(image_path):
    """
    Inject watermark image as background.
    Optional - works without logo files.
    """
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as img_file:
                img_b64 = base64.b64encode(img_file.read()).decode()
            st.markdown(
                f"""<style>
                .watermark-container {{ 
                    position: fixed; 
                    top: 50%; 
                    left: 55%; 
                    transform: translate(-50%, -50%); 
                    opacity: 0.12;  /* Slightly more visible */
                    z-index: 0; 
                    pointer-events: none; 
                    width: 45vw; 
                }}
                </style>
                <img src="data:image/png;base64,{img_b64}" class="watermark-container">""", 
                unsafe_allow_html=True)
        except Exception:
            pass  # Silent fail if logo not found

def get_identity_names():
    """
    Retrieve list of names from Identity Shield for dropdown.
    Enables cross-adapter linking.
    """
    try:
        df = get_data("identity_shield")
        if df.empty: 
            return []
        return df['name'].tolist()
    except Exception:
        return []

# --- 5. MAIN APP ---

if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False

# === LOGIN SCREEN ===
if not st.session_state['ingelogd']:
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        
        # Show logo if available
        if os.path.exists(LOGO_TEXT): 
            st.image(LOGO_TEXT, use_container_width=True)
        else:
            st.markdown("<h1 style='text-align: center; color: #2e0d43;'>PRO INVEST X</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; color: #4a148c; margin-top: 20px;'>AUTHORIZED ACCESS</h3>", 
                   unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            if st.form_submit_button("SECURE LOGIN", use_container_width=True):
                # RESTORED: Actual authentication check
                if username == "admin" and password == "invest2025":
                    st.session_state.ingelogd = True
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")

# === MAIN APPLICATION ===
else:
    # === SIDEBAR ===
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Logo
        if os.path.exists(LOGO_TEXT): 
            st.image(LOGO_TEXT, use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center;'>PRO INVEST X</h2>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Shield logo
        if os.path.exists(LOGO_SHIELD):
            c1, c2, c3 = st.columns([0.5, 2, 0.5])
            with c2: 
                st.image(LOGO_SHIELD, use_container_width=True)
        
        st.markdown("<br><br><p style='font-weight: bold; letter-spacing: 1px;'>MODULES</p>", 
                   unsafe_allow_html=True)
        
        menu = st.radio("NAVIGATION", [
            "📊 System Dashboard",
            "🛡️ Identity Shield", 
            "📈 Financial Adapter",
            "🛂 Consular Vault"
        ], label_visibility="collapsed")
        
        st.divider()
        
        st.markdown("""<div style='text-align: center; font-size: 0.8em; opacity: 0.8;'>
                    © 2025 PRO INVEST X<br>IT-CELL | v4.1 Corporate Edition
                    </div>""", unsafe_allow_html=True)
        
        if st.button("LOGOUT", use_container_width=True):
            st.session_state.ingelogd = False
            st.rerun()

    # === DASHBOARD MODULE ===
    if menu == "📊 System Dashboard":
        inject_centered_watermark(LOGO_SHIELD)
        
        st.markdown("<h1 style='text-align: center;'>📈 Institutional Dashboard</h1>", 
                   unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.7;'>Real-time System Intelligence</p>", 
                   unsafe_allow_html=True)
        
        # Fetch all data
        df_consular = get_data("consular_registry")
        df_identity = get_data("identity_shield")
        df_finance = get_data("financial_records")
        
        # Calculate total capital
        total_funds = df_finance['amount'].sum() if not df_finance.empty else 0
        
        # Top metrics
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="large")
        c1.metric("Secured Documents", len(df_consular))
        c2.metric("Verified Identities", len(df_identity))
        c3.metric("Total Capital Pool", f"€ {total_funds:,.0f}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Detailed views
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Financial Distribution")
            if not df_finance.empty:
                sector_data = df_finance.groupby("sector")["amount"].sum()
                st.bar_chart(sector_data)
            else:
                st.info("No financial data yet")
        
        with col2:
            st.subheader("🛡️ Identity Risk Overview")
            if not df_identity.empty:
                risk_counts = df_identity['risk_level'].value_counts()
                st.bar_chart(risk_counts)
            else:
                st.info("No identity data yet")

    # === IDENTITY SHIELD MODULE ===
    elif menu == "🛡️ Identity Shield":
        st.title("🛡️ Identity Shield")
        st.info("📋 Institutional Identity Verification & Risk Assessment")
        
        # Registration form
        with st.expander("👤 Register New Identity", expanded=False):
            with st.form("identity_form"):
                c1, c2 = st.columns(2)
                with c1:
                    person_id = st.text_input("ID / Passport Number", help="Unique identifier")
                    full_name = st.text_input("Full Legal Name")
                with c2:
                    role = st.selectbox("Role", ["Official", "Investor", "Diaspora Member", "Athlete", "Partner"])
                    country = st.text_input("Country of Origin")
                
                if st.form_submit_button("VERIFY & STORE", use_container_width=True):
                    if person_id and full_name:
                        # Sanitize inputs
                        safe_id = sanitize_id(person_id)
                        safe_name = sanitize_text(full_name)
                        safe_country = sanitize_text(country) if country else "Unknown"
                        
                        if not safe_id:
                            st.error("❌ Invalid ID. Min 3 characters, alphanumeric only.")
                        elif not safe_name:
                            st.error("❌ Invalid name.")
                        elif check_duplicate_id(safe_id, 'identity_shield'):
                            st.error(f"❌ ID '{safe_id}' already exists.")
                        else:
                            # IMPROVED: Better risk calculation
                            risk_map = {
                                "Official": "LOW",
                                "Diaspora Member": "LOW",
                                "Athlete": "LOW",
                                "Investor": "MEDIUM",
                                "Partner": "MEDIUM"
                            }
                            risk = risk_map.get(role, "HIGH")
                            
                            success = run_query(
                                "INSERT INTO identity_shield VALUES (?, ?, ?, ?, ?, ?)", 
                                (safe_id, safe_name, role, safe_country, risk, datetime.now().isoformat())
                            )
                            
                            if success:
                                st.success(f"✅ Identity '{safe_name}' secured with risk level: {risk}")
                                st.rerun()
                    else:
                        st.error("❌ Please fill all required fields.")
        
        st.divider()
        
        # Display identities
        df = get_data("identity_shield")
        
        if not df.empty:
            st.write(f"### Verified Identities ({len(df)})")
            
            for index, row in df.iterrows():
                c1, c2, c3, c4 = st.columns([1, 2, 1.5, 1])
                
                c1.write(f"**{row['id']}**")
                c2.write(f"**{row['name']}** • {row['role']}")
                c3.write(f"🌍 {row['country']}")
                
                # Risk badge
                risk_color = {
                    "LOW": "risk-low",
                    "MEDIUM": "risk-medium", 
                    "HIGH": "risk-high"
                }.get(row['risk_level'], "risk-high")
                
                c4.markdown(f"<span class='{risk_color}'>{row['risk_level']}</span>", 
                           unsafe_allow_html=True)
        else:
            st.info("📭 No verified identities yet. Register the first identity above.")

    # === FINANCIAL ADAPTER MODULE ===
    elif menu == "📈 Financial Adapter":
        st.title("📈 Financial Adapter")
        st.info("💰 Institutional Investment Tracking & Portfolio Management")
        
        # Tabs for organization
        tab1, tab2 = st.tabs(["➕ New Transaction", "📊 Portfolio Overview"])
        
        # === TAB 1: NEW TRANSACTION ===
        with tab1:
            with st.form("finance_form"):
                st.subheader("Register Financial Transaction")
                
                c1, c2 = st.columns(2)
                
                with c1:
                    # SMART: Link to Identity Shield
                    identities = get_identity_names()
                    
                    if not identities:
                        st.warning("⚠️ No verified identities found. Please register a person first in Identity Shield.")
                        entity_name = st.text_input("Entity Name (Manual Entry)")
                    else:
                        use_dropdown = st.checkbox("Link to verified identity", value=True)
                        if use_dropdown:
                            entity_name = st.selectbox("Linked Entity / Investor", identities)
                        else:
                            entity_name = st.text_input("Entity Name (Manual Entry)")
                    
                    amount = st.number_input("Amount (€)", min_value=0.0, step=1000.0, format="%.2f")
                
                with c2:
                    tx_type = st.selectbox("Transaction Type", [
                        "Investment Inbound", 
                        "Dividend Payout", 
                        "Operational Cost",
                        "Capital Transfer",
                        "Advisory Fee"
                    ])
                    
                    sector = st.selectbox("Target Sector", [
                        "Energy", 
                        "Real Estate", 
                        "Technology", 
                        "Sports", 
                        "Infrastructure",
                        "Healthcare",
                        "Agriculture"
                    ])
                
                status = st.selectbox("Compliance Status", [
                    "Pending Compliance",
                    "Approved",
                    "Under Review",
                    "Flagged"
                ])
                
                notes = st.text_area("Transaction Notes (Optional)", placeholder="Additional details...")
                
                if st.form_submit_button("LOG TRANSACTION", use_container_width=True):
                    if entity_name and amount > 0:
                        # Generate unique transaction ID
                        tx_id = f"TX-{uuid.uuid4().hex[:6].upper()}"
                        
                        # Sanitize entity name if manual
                        safe_entity = sanitize_text(entity_name) if entity_name not in identities else entity_name
                        
                        success = run_query(
                            "INSERT INTO financial_records VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (tx_id, safe_entity, amount, tx_type, sector, status, datetime.now().isoformat())
                        )
                        
                        if success:
                            st.success(f"✅ Transaction {tx_id} logged for {safe_entity} • € {amount:,.2f}")
                            st.rerun()
                    else:
                        st.error("❌ Please enter entity name and amount > 0")
        
        # === TAB 2: PORTFOLIO OVERVIEW ===
        with tab2:
            df = get_data("financial_records")
            
            if not df.empty:
                # Summary stats
                col1, col2, col3 = st.columns(3)
                
                total = df['amount'].sum()
                avg_tx = df['amount'].mean()
                num_tx = len(df)
                
                col1.metric("Total Volume", f"€ {total:,.0f}")
                col2.metric("Average Transaction", f"€ {avg_tx:,.0f}")
                col3.metric("Total Transactions", num_tx)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Visualizations
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.write("### 📊 Sector Distribution")
                    sector_data = df.groupby("sector")["amount"].sum().sort_values(ascending=False)
                    st.bar_chart(sector_data)
                
                with col_b:
                    st.write("### 💼 Transaction Types")
                    type_data = df.groupby("type")["amount"].sum()
                    st.bar_chart(type_data)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Transaction ledger
                st.write("### 📋 Transaction Ledger")
                
                # Format the dataframe for display
                display_df = df.copy()
                display_df['amount'] = display_df['amount'].apply(lambda x: f"€ {x:,.2f}")
                display_df = display_df[['id', 'entity_name', 'amount', 'type', 'sector', 'status', 'timestamp']]
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            else:
                st.info("📭 No financial transactions yet. Log your first transaction above.")

    # === CONSULAR VAULT MODULE ===
    elif menu == "🛂 Consular Vault":
        st.title("🛂 Consular Document Vault")
        st.info("📄 Secure Sovereign Document Management")
        
        # Upload form
        with st.expander("➕ Register New Sovereign Document", expanded=False):
            with st.form("consular_form"):
                c1, c2 = st.columns(2)
                
                with c1:
                    raw_id = st.text_input("Application ID", placeholder="e.g., PIX-2025-001")
                    doc_type = st.selectbox("Document Type", [
                        "Passport", 
                        "Visa Application", 
                        "Contract", 
                        "Diaspora ID",
                        "Birth Certificate",
                        "Legal Document"
                    ])
                
                with c2:
                    status = st.selectbox("Initial Status", ["Pending", "Approved", "Rejected", "Under Review"])
                    file = st.file_uploader("Select File", type=['pdf', 'jpg', 'png', 'jpeg'])
                
                if st.form_submit_button("EXECUTE SECURE INSERT", use_container_width=True):
                    # Validate inputs
                    safe_id = sanitize_id(raw_id)
                    
                    if not file:
                        st.error("❌ Please select a file.")
                    elif not safe_id:
                        st.error("❌ Invalid ID. Min 3 characters, alphanumeric/-/_ only.")
                    elif check_duplicate_id(safe_id):
                        st.error(f"❌ ID '{safe_id}' already exists.")
                    elif file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                        st.error(f"❌ File exceeds {MAX_FILE_SIZE_MB}MB limit.")
                    else:
                        try:
                            # Generate unique filename
                            safe_filename = sanitize_filename(file.name)
                            unique_filename = f"{uuid.uuid4().hex[:8]}_{safe_filename}"
                            file_path = os.path.join(VAULT_DIR, f"{safe_id}_{unique_filename}")
                            
                            # Save file
                            with open(file_path, "wb") as f:
                                f.write(file.getbuffer())
                            
                            # Save to database
                            success = run_query(
                                "INSERT INTO consular_registry (id, doc_type, filename, status, timestamp) VALUES (?, ?, ?, ?, ?)",
                                (safe_id, doc_type, unique_filename, status, datetime.now().isoformat())
                            )
                            
                            if success:
                                st.success(f"✅ Document '{safe_filename}' secured with ID: {safe_id}")
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Upload error: {str(e)}")
        
        st.divider()
        
        # Search and display
        col_search, col_status = st.columns([3, 1])
        with col_search:
            search_q = st.text_input("🔍 Search Vault (ID or Filename)", placeholder="Type to search...")
        with col_status:
            status_filter = st.selectbox("Filter by Status", ["All", "Pending", "Approved", "Rejected", "Under Review"])
        
        df = get_data("consular_registry")
        
        if not df.empty:
            # Apply filters
            filtered_df = df.copy()
            
            # Search filter
            if search_q:
                search_q_lower = search_q.lower()
                filtered_df = filtered_df[
                    filtered_df['id'].str.lower().str.contains(search_q_lower) | 
                    filtered_df['filename'].str.lower().str.contains(search_q_lower)
                ]
            
            # Status filter
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            # Display results
            if filtered_df.empty:
                st.info("🔍 No documents match your search criteria.")
            else:
                st.write(f"### 📂 Documents ({len(filtered_df)} found)")
                
                for index, row in filtered_df.iterrows():
                    col1, col2, col3, col4, col5 = st.columns([1, 2, 1.5, 1, 0.5])
                    
                    col1.write(f"**`{row['id']}`**")
                    
                    # Display filename without UUID prefix
                    display_name = row['filename'].split('_', 1)[-1] if '_' in row['filename'] else row['filename']
                    col2.write(f"{display_name} • {row['doc_type']}")
                    
                    # Status update dropdown
                    new_status = col3.selectbox(
                        "", 
                        ["Pending", "Approved", "Rejected", "Under Review"], 
                        index=["Pending", "Approved", "Rejected", "Under Review"].index(row['status']), 
                        key=f"st_{row['id']}", 
                        label_visibility="collapsed"
                    )
                    
                    if new_status != row['status']:
                        run_query("UPDATE consular_registry SET status = ? WHERE id = ?", (new_status, row['id']))
                        st.rerun()
                    
                    # Download button
                    file_path = os.path.join(VAULT_DIR, f"{row['id']}_{row['filename']}")
                    if os.path.exists(file_path):
                        try:
                            with open(file_path, "rb") as f:
                                file_data = f.read()
                            col4.download_button(
                                "📥 Download", 
                                file_data, 
                                file_name=display_name, 
                                key=f"dl_{row['id']}"
                            )
                        except Exception:
                            col4.write("❌ Error")
                    else:
                        col4.write("⚠️ Missing")
                    
                    # Delete button
                    if col5.button("🗑️", key=f"del_{row['id']}"):
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            run_query("DELETE FROM consular_registry WHERE id = ?", (row['id'],))
                            st.success(f"✅ Document {row['id']} deleted.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Delete error: {str(e)}")
        else:
            st.info("📭 Vault is empty. Upload your first document above.")

    # Footer
    st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""<div style='text-align: center; opacity: 0.6; font-size: 0.85em;'>
                © 2025 PRO INVEST X IT-CELL | v4.1 Gold Standard | Secure • Scalable • Sovereign
                </div>""", unsafe_allow_html=True)