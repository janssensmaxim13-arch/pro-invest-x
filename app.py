import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. PAGINA INSTELLINGEN
st.set_page_config(page_title="ProInvestiX - Rule-Based Engine", layout="wide")

# 2. DESIGN & STYLING (Institutional Purple)
st.markdown("""
    <style>
    .stApp { background-color: #1a0633; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0d021f !important; border-right: 1px solid #bf00ff; }
    h1, h2, h3, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button { background-color: #8a2be2; color: white; border-radius: 8px; font-weight: bold; border: none; }
    .stTextInput>div>div>input { background-color: #2e0d54 !important; color: white !important; border: 1px solid #6a0dad !important; }
    .risk-low { color: #00ff00; font-weight: bold; }
    .risk-med { color: #ffa500; font-weight: bold; }
    .risk-high { color: #ff0000; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. RULE-BASED EVALUATION LOGIC (Sectie 2.4) ---
def evaluate_risk(data_type, value):
    """Past institutionele regels toe op invoerdata."""
    if data_type == "identity":
        if value == "Official":
            return "LOW", "✅ Geautoriseerde status gedetecteerd."
        elif value == "Diaspora Member":
            return "LOW", "ℹ️ Diaspora status vereist standaard validatie."
        else:
            return "MEDIUM", "⚠️ Onbekende status: extra screening aanbevolen."
            
    if data_type == "finance":
        try:
            amount = float(value)
            if amount > 1000000:
                return "HIGH", "🚨 ALERT: Transactie boven drempelwaarde (€1M). Escalatie naar Board vereist."
            elif amount > 500000:
                return "MEDIUM", "⚠️ Verhoogd toezicht vereist voor bedragen boven €500k."
            else:
                return "LOW", "✅ Bedrag binnen reguliere operationele marges."
        except:
            return "HIGH", "❌ Ongeldige financiële data gedetecteerd."

# --- 4. DATABASE & SECURITY (Bestaande functies) ---
if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False

def save_to_db(data_list, columns, filename):
    data_list.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if 'Timestamp' not in columns: columns.append('Timestamp')
    df_new = pd.DataFrame([data_list], columns=columns)
    if not os.path.isfile(filename): df_new.to_csv(filename, index=False)
    else: df_new.to_csv(filename, mode='a', header=False, index=False)

# --- 5. MAIN APP ---
if not st.session_state['ingelogd']:
    # Inlogscherm (vereenvoudigd voor overzicht)
    st.title("🛡️ PRO INVEST X")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("AUTHORIZE"):
        if user == "admin" and pw == "invest2025":
            st.session_state['ingelogd'] = True
            st.rerun()
else:
    with st.sidebar:
        st.markdown("<h2 style='color: #bf00ff;'>🔮 ADAPTERS</h2>", unsafe_allow_html=True)
        keuze = st.radio("SELECT MODULE:", ["🛡️ Identity Shield", "📈 Financial Adapter", "⚽ Sport Adapter"])
        if st.button("🔒 LOGOUT"):
            st.session_state['ingelogd'] = False
            st.rerun()

    # --- EVALUATION LAYER IN ACTIE ---

    if keuze == "🛡️ Identity Shield":
        st.title("🛡️ Identity Shield")
        st.subheader("2.4.1 Official Identification Layer")
        
        naam = st.text_input("Volledige Naam")
        rol = st.selectbox("Status", ["Official", "Diaspora Member", "Investor", "Other"])
        
        # Live Evaluatie
        risk_level, message = evaluate_risk("identity", rol)
        st.markdown(f"**Systeem Evaluatie:** <span class='risk-{risk_level.lower()}'>{message}</span>", unsafe_allow_html=True)
        
        if st.button("REGISTREER"):
            save_to_db([naam, rol, risk_level], ['Naam', 'Rol', 'RiskLevel'], 'identity_db.csv')
            st.success("Data opgeslagen inclusief Risk Assessment.")

    elif keuze == "📈 Financial Adapter":
        st.title("📈 Financial Adapter")
        st.subheader("2.4.2 Financial Consistency Layer")
        
        bedrag = st.text_input("Investering Bedrag (€)", "0")
        
        # Live Evaluatie van kapitaalstromen
        risk_level, message = evaluate_risk("finance", bedrag)
        st.info(message)
        
        if risk_level == "HIGH":
            st.warning("De 'Decision & Escalation Layer' is geactiveerd voor deze invoer.")

    elif keuze == "⚽ Sport Adapter":
        st.title("⚽ Sport Adapter")
        st.write("Systeem is operationeel. Geen actieve evaluatieregels voor deze module.")

    st.markdown("<br><hr><center>© 2025 PRO INVEST X IT-CELL | Evaluation Engine Active</center>", unsafe_allow_html=True)
