import streamlit as st
import pandas as pd
import os

# 1. PAGINA INSTELLINGEN
st.set_page_config(page_title="Pro Invest X - Secure Backbone", layout="wide")

# 2. DESIGN & STYLING (Deep Purple High-Tech)
st.markdown("""
    <style>
    .stApp { background-color: #1a0633; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #0d021f !important; border-right: 1px solid #bf00ff; }
    h1, h2, h3, label, .stMarkdown { color: #ffffff !important; }
    .stButton>button { background-color: #8a2be2; color: white; border-radius: 8px; font-weight: bold; border: none; height: 3em; }
    .stTextInput>div>div>input { background-color: #2e0d54 !important; color: white !important; border: 1px solid #6a0dad !important; }
    [data-testid="stMetricValue"] { color: #bf00ff !important; font-size: 2rem !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SECURITY & SESSION LOGICA ---
if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False

def check_login():
    st.markdown("<center><h1 style='color: #bf00ff; font-size: 3rem;'>🛡️ PRO INVEST X</h1><p>Institutional Security Gateway</p></center>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown("<div style='background-color: #0d021f; padding: 30px; border-radius: 15px; border: 1px solid #8a2be2;'>", unsafe_allow_html=True)
        user = st.text_input("Username")
        pw = st.text_input("Password", type="password")
        if st.button("AUTHORIZE ACCESS"):
            if user == "admin" and pw == "invest2025":
                st.session_state['ingelogd'] = True
                st.rerun()
            else:
                st.error("Invalid Credentials")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 4. DATABASE HANDLER ---
def save_to_db(data_list, columns, filename):
    df_new = pd.DataFrame([data_list], columns=columns)
    if not os.path.isfile(filename):
        df_new.to_csv(filename, index=False)
    else:
        df_new.to_csv(filename, mode='a', header=False, index=False)

# --- 5. MAIN APPLICATION ---
if not st.session_state['ingelogd']:
    check_login()
else:
    # ZIJBALK
    with st.sidebar:
        st.markdown("<h2 style='color: #bf00ff;'>🔮 NAVIGATOR</h2>", unsafe_allow_html=True)
        keuze = st.radio("SELECT ADAPTER:", [
            "🛡️ Identity Shield", "📈 Financial Adapter", "⚽ Sport Adapter",
            "🛂 Consular Adapter", "🚗 Mobility Adapter", "🏥 Health Adapter"
        ])
        st.divider()
        if st.button("🔒 SECURE LOGOUT"):
            st.session_state['ingelogd'] = False
            st.rerun()

    # MODULES LOGICA
    if keuze == "🛡️ Identity Shield":
        st.title("🛡️ Identity Shield")
        st.subheader("Official Registration Layer")
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Full Name")
            l = st.text_input("Country")
        with c2:
            r = st.selectbox("Role", ["Investor", "Diaspora", "Authority"])
        if st.button("REGISTER ENTRY"):
            if n:
                save_to_db([n, r, l], ['Name', 'Role', 'Country'], 'identity_db.csv')
                st.success("Entry Secured.")
        if os.path.isfile('identity_db.csv'):
            st.dataframe(pd.read_csv('identity_db.csv'), use_container_width=True)

    elif keuze == "📈 Financial Adapter":
        st.title("📈 Financial Adapter")
        st.header("Capital & Asset Tracking")
        m1, m2, m3 = st.columns(3)
        m1.metric("Current Capital", "€ 42.5M", "+2.5M")
        m2.metric("Active Projects", "14")
        m3.metric("Growth Index", "8.4%")
        st.bar_chart({"Sector": ["Energy", "Tech", "Agro", "Sport"], "Value": [15, 12, 8, 7]}, x="Sector", y="Value")

    elif keuze == "⚽ Sport Adapter":
        st.title("⚽ Sport Adapter")
        st.subheader("Athletic Excellence Registry")
        atleet = st.text_input("Athlete Name")
        sport = st.selectbox("Sport", ["Football", "Athletics", "Basketball"])
        if st.button("ENROLL ATHLETE"):
            if atleet:
                save_to_db([atleet, sport], ['Name', 'Sport'], 'atleten_db.csv')
                st.success("Athlete Enrolled.")
        if os.path.isfile('atleten_db.csv'):
            st.dataframe(pd.read_csv('atleten_db.csv'), use_container_width=True)

    elif keuze == "🛂 Consular Adapter":
        st.title("🛂 Consular Adapter")
        st.info("Diplomatic Support Services")
        st.text_input("Tracking ID")
        st.file_uploader("Upload Documents")

    elif keuze == "🚗 Mobility Adapter":
        st.title("🚗 Mobility Adapter")
        st.subheader("Infrastructure Progress")
        st.progress(65, text="Project 'Alpha Road' 65%")
        st.metric("Active Sites", "4 Logistics Hubs")

    elif keuze == "🏥 Health Adapter":
        st.title("🏥 Health Adapter")
        st.warning("Secure Health Environment Access")
        st.write("Regional Hospital Status: **Optimal**")

    st.markdown("<br><hr><center>© 2025 PRO INVEST X | ACCESS GRANTED</center>", unsafe_allow_html=True)s