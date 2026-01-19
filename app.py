# ============================================================================
# PROINVESTIX v5.1.2 ULTIMATE - INVESTOR READY EDITION
# ============================================================================
# Premium Platform met:
# - Public Landing Page (geen login nodig)
# - WK 2030 Countdown
# - Live KPI Counters
# - Masterplan Showcase
# - Investor Portal
# ============================================================================

import streamlit as st
import os
import time
from datetime import datetime, timedelta

# --- Page Config MUST be first ---
st.set_page_config(
    page_title="ProInvestiX | National Investment Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Configuratie ---
from config import VERSION, VERSION_NAME, APP_NAME, LOGO_TEXT, LOGO_SHIELD, Messages

# --- Database ---
from database.setup import init_db

# --- Authenticatie ---
from auth.security import verify_user, register_user, get_user_role, log_audit, BCRYPT_AVAILABLE

# --- UI Styling ---
from ui.styles import apply_custom_css, get_footer_html, COLORS

# --- Pages ---
from views.landing import render_landing_page
from views.investor_portal import render_investor_portal

# --- Modules ---
from modules import identity_shield
from modules import ticketchain
from modules import foundation_bank
from modules import consulate_hub
from modules import analytics
from modules.security_admin import render_security_center, render_admin_panel
from modules import ntsp
from modules import transfers
from modules import transfer_market
from modules import academy
from modules import diaspora_wallet
from modules import hayat
from modules import inclusion
from modules import antihate
from modules import subscriptions
from modules import mobility
from modules import fandorpen
from modules import maroc_id_shield
from modules import nil  # Dossier 28: Narrative Integrity Layer
from modules import antilobby  # Dossier 41: Anti-Lobby Hub
from modules import frmf  # FRMF Officials Hub: RefereeChain + VAR Vault
from modules import pma_logistics  # PMA Logistics: Supply Chain Management

# --- Translations ---
from translations import get_text, get_language_options, get_language_code, LANGUAGES, is_rtl, get_current_language

def t(key):
    return get_text(key, get_current_language())

# ============================================================================
# SESSION STATE (moet EERST)
# ============================================================================

if 'page' not in st.session_state:
    st.session_state['page'] = 'landing'
if 'ingelogd' not in st.session_state:
    st.session_state['ingelogd'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = ""
if 'show_login' not in st.session_state:
    st.session_state['show_login'] = False
if 'language' not in st.session_state:
    st.session_state['language'] = 'en'
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

# ============================================================================
# APPLY STYLING (na session state)
# ============================================================================

apply_custom_css(st.session_state.get('dark_mode', False))
init_db()


## ============================================================================
# NAVIGATION HELPER
# ============================================================================

def navigate_to(page: str):
    """Navigate to a specific page."""
    st.session_state['page'] = page
    st.rerun()


# ============================================================================
# TOP NAVIGATION BAR (Always visible)
# ============================================================================

def render_top_navbar():
    """Render the top navigation bar."""
    
    col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 2])
    
    with col1:
        # Logo
        if os.path.exists(LOGO_TEXT):
            st.image(LOGO_TEXT, width=180)
        else:
            st.markdown(f"""
                <span style='font-family: Rajdhani, sans-serif; font-size: 1.5rem; font-weight: 700;'>
                    <span style='color: #1F2937;'>PROINVESTI</span><span style='color: #8B5CF6;'>X</span>
                </span>
            """, unsafe_allow_html=True)
    
    with col2:
        if st.button(" Home", use_container_width=True, key="nav_home"):
            navigate_to('landing')
    
    with col3:
        if st.button(" Investors", use_container_width=True, key="nav_investors"):
            navigate_to('investor_portal')
    
    with col4:
        if st.button(" Masterplan", use_container_width=True, key="nav_masterplan"):
            navigate_to('masterplan')
    
    with col5:
        if st.session_state['ingelogd']:
            col_user, col_logout = st.columns([2, 1])
            with col_user:
                st.markdown(f"""
                    <div style='text-align: right; padding: 0.5rem;'>
                        <span style='color: {COLORS['purple_light']};'> {st.session_state['username']}</span>
                    </div>
                """, unsafe_allow_html=True)
            with col_logout:
                if st.button("", key="nav_logout"):
                    log_audit(st.session_state['username'], "LOGOUT", "Authentication")
                    st.session_state['ingelogd'] = False
                    st.session_state['username'] = ""
                    st.session_state['user_role'] = ""
                    st.session_state['page'] = 'landing'
                    st.rerun()
        else:
            col_login, col_register = st.columns(2)
            with col_login:
                if st.button(" Login", use_container_width=True, key="nav_login"):
                    st.session_state['show_login'] = True
                    st.session_state['page'] = 'login'
                    st.rerun()
            with col_register:
                if st.button(" Register", use_container_width=True, key="nav_register"):
                    st.session_state['page'] = 'register'
                    st.rerun()
    
    st.markdown("<hr style='margin: 0.5rem 0; border-color: rgba(139, 92, 246, 0.2);'>", unsafe_allow_html=True)


# ============================================================================
# LOGIN MODAL
# ============================================================================

def render_login_page():
    """Render dedicated login page."""
    
    # CSS voor login pagina
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 30%, #C4B5FD 50%, #A78BFA 70%, #8B5CF6 100%);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 15px 50px rgba(139, 92, 246, 0.4), inset 0 1px 0 rgba(255,255,255,0.3);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .login-logo {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .login-logo-dark {
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .login-logo-light {
        color: #DDD6FE;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .login-title {
        text-align: center;
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    .login-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    .login-form-container {
        background: rgba(255,255,255,0.15);
        border-radius: 16px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    .login-hint {
        text-align: center;
        margin-top: 1rem;
        padding: 0.8rem;
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        color: rgba(255,255,255,0.9);
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start paars metallic container
        secure_text = t("auth_secure_access").upper()
        credentials_text = t("auth_enter_credentials")
        
        st.markdown(f'''<div class="login-container">
<div class="login-logo"><span class="login-logo-dark">PROINVESTI</span><span class="login-logo-light">X</span></div>
<div class="login-title">🔐 {secure_text}</div>
<div class="login-subtitle">{credentials_text}</div>
</div>''', unsafe_allow_html=True)
        
        # Formulier apart (Streamlit form werkt niet goed in HTML)
        st.markdown("<div style='max-width: 500px; margin: -2rem auto 0 auto;'>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(t("username"), placeholder=t("auth_username_placeholder"))
            password = st.text_input(t("password"), type="password", placeholder=t("auth_password_placeholder"))
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(f"🔐 {t('auth_login_button')}", use_container_width=True)
            with col_btn2:
                if st.form_submit_button(f"← {t('auth_back')}", use_container_width=True):
                    navigate_to('landing')
            
            if submit:
                if verify_user(username, password):
                    st.session_state['ingelogd'] = True
                    st.session_state['username'] = username
                    st.session_state['user_role'] = get_user_role(username)
                    st.session_state['page'] = 'dashboard'
                    st.toast(f"{t('auth_welcome')}, {username}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(t("error_invalid_credentials"))
        
        # Demo credentials hint
        st.markdown(f"""
            <div style='text-align: center; margin-top: 1rem; padding: 1rem; max-width: 500px; margin-left: auto; margin-right: auto;
                        background: rgba(139, 92, 246, 0.15); border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);'>
                <p style='color: #6B7280; font-size: 0.85rem; margin: 0;'>
                    🔑 {t("auth_demo_hint")}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_register_page():
    """Render dedicated registration page."""
    
    # CSS voor register pagina (zelfde als login)
    st.markdown("""
    <style>
    .register-container {
        background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 30%, #C4B5FD 50%, #A78BFA 70%, #8B5CF6 100%);
        border-radius: 24px;
        padding: 3rem 2rem;
        margin: 2rem auto;
        max-width: 500px;
        box-shadow: 0 15px 50px rgba(139, 92, 246, 0.4), inset 0 1px 0 rgba(255,255,255,0.3);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .register-logo {
        text-align: center;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .register-logo-dark {
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .register-logo-light {
        color: #DDD6FE;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .register-title {
        text-align: center;
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        letter-spacing: 2px;
        margin-bottom: 0.5rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
    }
    .register-subtitle {
        text-align: center;
        color: rgba(255,255,255,0.85);
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Start paars metallic container
        create_text = t("auth_create_account").upper()
        join_text = t("auth_join_platform")
        
        st.markdown(f'''<div class="register-container">
<div class="register-logo"><span class="register-logo-dark">PROINVESTI</span><span class="register-logo-light">X</span></div>
<div class="register-title">✨ {create_text}</div>
<div class="register-subtitle">{join_text}</div>
</div>''', unsafe_allow_html=True)
        
        # Formulier apart
        st.markdown("<div style='max-width: 500px; margin: -2rem auto 0 auto;'>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            new_username = st.text_input(t("username"), placeholder=t("auth_min_chars"))
            new_email = st.text_input(t("email"), placeholder="your@email.com")
            new_password = st.text_input(t("password"), type="password", placeholder=t("auth_min_password"))
            confirm_password = st.text_input(t("auth_confirm_password"), type="password")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(f"✨ {t('auth_register_button')}", use_container_width=True)
            with col_btn2:
                if st.form_submit_button(f"← {t('auth_back')}", use_container_width=True):
                    navigate_to('landing')
            
            if submit:
                if len(new_username) < 3:
                    st.error(t("error_username_short"))
                elif len(new_password) < 8:
                    st.error(t("error_password_short"))
                elif new_password != confirm_password:
                    st.error(t("error_passwords_mismatch"))
                else:
                    success = register_user(new_username, new_password, "Official", new_email)
                    if success:
                        st.success(t("success_account_created"))
                        st.info(t("auth_login_now"))
                        time.sleep(2)
                        navigate_to('login')
                    else:
                        st.error(t("error_username_exists"))
        
        st.markdown("</div>", unsafe_allow_html=True)


# ============================================================================
# MAIN APPLICATION (Logged in)
# ============================================================================

def render_main_app():
    """Render the main application for logged-in users."""
    
    # Initialize module state if not present
    if 'current_module' not in st.session_state:
        st.session_state['current_module'] = 'dashboard'
    
    def set_module(module_name):
        st.session_state['current_module'] = module_name
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("<br>", unsafe_allow_html=True)
        
        if os.path.exists(LOGO_SHIELD):
            st.image(LOGO_SHIELD, use_container_width=True)
        
        # === SETTINGS ROW: Language + Theme ===
        col_lang, col_theme = st.columns([3, 1])
        
        with col_lang:
            lang_options = get_language_options()
            current_lang = st.session_state.get('language', 'en')
            current_selection = f"{LANGUAGES[current_lang]['flag']} {LANGUAGES[current_lang]['name']}"
            
            selected_lang = st.selectbox(
                " Language",
                options=lang_options,
                index=lang_options.index(current_selection) if current_selection in lang_options else 0,
                key="lang_selector",
                label_visibility="collapsed"
            )
            new_lang = get_language_code(selected_lang)
            if new_lang != current_lang:
                st.session_state['language'] = new_lang
                st.rerun()
        
        with col_theme:
            # Theme Toggle Button
            theme_icon = "" if st.session_state.get('dark_mode', False) else ""
            if st.button(theme_icon, key="theme_toggle", help="Toggle Dark/Light Mode"):
                st.session_state['dark_mode'] = not st.session_state.get('dark_mode', False)
                st.rerun()
        
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem; margin: 1rem 0;
                        background: rgba(139, 92, 246, 0.1); border-radius: 8px;'>
                <div style='color: {COLORS['purple_light']}; font-weight: 600;'>
                    {st.session_state['username']}
                </div>
                <div style='color: {COLORS['text_muted']}; font-size: 0.8rem;'>
                    {st.session_state['user_role']}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # === DASHBOARD (Always visible) ===
        lang = st.session_state.get('language', 'en')
        
        if st.button(get_text('dashboard', lang), use_container_width=True, 
                     type="primary" if st.session_state['current_module'] == 'dashboard' else "secondary"):
            set_module('dashboard')
            st.rerun()
        
        if st.button(get_text('analytics', lang), use_container_width=True,
                     type="primary" if st.session_state['current_module'] == 'analytics' else "secondary"):
            set_module('analytics')
            st.rerun()
        
        st.markdown("<hr style='margin: 0.5rem 0; border-color: rgba(139, 92, 246, 0.2);'>", unsafe_allow_html=True)
        
        # === GOVERNANCE & INTEGRITY ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_governance', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nil_monitor', lang), use_container_width=True, key="nil_monitor"):
            set_module('nil')
            st.rerun()
        if st.button(get_text('antilobby', lang), use_container_width=True, key="antilobby"):
            set_module('antilobby')
            st.rerun()
        if st.button("FRMF Officials", use_container_width=True, key="nav_frmf"):
            set_module('frmf')
            st.rerun()
        if st.button("PMA Logistics", use_container_width=True, key="nav_pma"):
            set_module('pma')
            st.rerun()
        
        # === FINANCIAL ECOSYSTEM ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_financial', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nav_ticketchain', lang), use_container_width=True, key="nav_ticket"):
            set_module('ticketchain')
            st.rerun()
        if st.button(get_text('nav_foundation', lang), use_container_width=True, key="nav_foundation"):
            set_module('foundation')
            st.rerun()
        if st.button(get_text('nav_wallet', lang), use_container_width=True, key="nav_wallet"):
            set_module('wallet')
            st.rerun()
        if st.button(get_text('nav_subscriptions', lang), use_container_width=True, key="nav_subs"):
            set_module('subscriptions')
            st.rerun()
        
        # === SPORT DIVISION ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_sport', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nav_ntsp', lang), use_container_width=True, key="nav_ntsp"):
            set_module('ntsp')
            st.rerun()
        if st.button(get_text('nav_transfers', lang), use_container_width=True, key="nav_transfers"):
            set_module('transfers')
            st.rerun()
        if st.button(get_text('nav_academy', lang), use_container_width=True, key="nav_academy"):
            set_module('academy')
            st.rerun()
        if st.button(get_text('nav_transfer_market', lang), use_container_width=True, key="nav_transfer_market"):
            set_module('transfer_market')
            st.rerun()
        
        # === WK2030 & DIASPORA ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_wk2030', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nav_fandorpen', lang), use_container_width=True, key="nav_fandorpen"):
            set_module('fandorpen')
            st.rerun()
        if st.button(get_text('nav_consulate', lang), use_container_width=True, key="nav_consulate"):
            set_module('consulate')
            st.rerun()
        if st.button(get_text('nav_mobility', lang), use_container_width=True, key="nav_mobility"):
            set_module('mobility')
            st.rerun()
        
        # === SOCIAL IMPACT ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_social', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nav_hayat', lang), use_container_width=True, key="nav_hayat"):
            set_module('hayat')
            st.rerun()
        if st.button(get_text('nav_inclusion', lang), use_container_width=True, key="nav_inclusion"):
            set_module('inclusion')
            st.rerun()
        if st.button(get_text('nav_antihate', lang), use_container_width=True, key="nav_antihate"):
            set_module('antihate')
            st.rerun()
        
        # === IDENTITY & SECURITY ===
        st.markdown(f"<p style='color: {COLORS['gold']}; font-size: 0.7rem; font-weight: 600; margin: 0.75rem 0 0.25rem 0; text-transform: uppercase; letter-spacing: 1px;'>{get_text('section_security', lang)}</p>", unsafe_allow_html=True)
        if st.button(get_text('nav_maroc_id', lang), use_container_width=True, key="nav_maroc_id", type="primary" if st.session_state['current_module'] == 'maroc_id' else "secondary"):
            set_module('maroc_id')
            st.rerun()
        if st.button(get_text('nav_identity', lang), use_container_width=True, key="nav_identity"):
            set_module('identity')
            st.rerun()
        if st.session_state['user_role'] in ["SuperAdmin", "Security Staff", "Admin"]:
            if st.button(get_text('nav_security', lang), use_container_width=True, key="nav_security"):
                set_module('security')
                st.rerun()
            if st.button(get_text('nav_admin', lang), use_container_width=True, key="nav_admin"):
                set_module('admin')
                st.rerun()
        
        st.markdown("<hr style='margin: 0.5rem 0; border-color: rgba(139, 92, 246, 0.2);'>", unsafe_allow_html=True)
        
        if st.button(get_text('logout', lang).upper(), use_container_width=True):
            log_audit(st.session_state['username'], "LOGOUT", "Authentication")
            st.session_state['ingelogd'] = False
            st.session_state['username'] = ""
            st.session_state['user_role'] = ""
            st.session_state['page'] = 'landing'
            st.session_state['current_module'] = 'dashboard'
            st.rerun()
        
        # Version badge
        st.markdown(f"""
            <div style='text-align: center; margin-top: 1rem; padding: 0.5rem;
                        background: rgba(139, 92, 246, 0.1); border-radius: 8px;'>
                <span style='color: {COLORS['text_muted']}; font-size: 0.7rem;'>
                    v{VERSION} | {VERSION_NAME}
                </span>
            </div>
        """, unsafe_allow_html=True)
    
    # === CONTENT ROUTING ===
    module = st.session_state['current_module']
    
    if module == "dashboard":
        render_interactive_dashboard(set_module)
    elif module == "analytics":
        analytics.render()
    elif module == "ntsp":
        ntsp.render(st.session_state['username'])
    elif module == "transfers":
        transfers.render(st.session_state['username'])
    elif module == "academy":
        academy.render(st.session_state['username'])
    elif module == "transfer_market":
        transfer_market.render(st.session_state['username'])
    elif module == "wallet":
        diaspora_wallet.render(st.session_state['username'])
    elif module == "consulate":
        consulate_hub.render(st.session_state['username'])
    elif module == "hayat":
        hayat.render(st.session_state['username'])
    elif module == "inclusion":
        inclusion.render(st.session_state['username'])
    elif module == "antihate":
        antihate.render(st.session_state['username'])
    elif module == "ticketchain":
        ticketchain.render(st.session_state['username'])
    elif module == "foundation":
        foundation_bank.render(st.session_state['username'])
    elif module == "subscriptions":
        subscriptions.render(st.session_state['username'])
    elif module == "mobility":
        mobility.render(st.session_state['username'])
    elif module == "fandorpen":
        fandorpen.render(st.session_state['username'])
    elif module == "maroc_id":
        maroc_id_shield.render(st.session_state['username'])
    elif module == "identity":
        identity_shield.render(st.session_state['username'])
    elif module == "nil":
        nil.render(st.session_state['username'])
    elif module == "antilobby":
        antilobby.render(st.session_state['username'])
    elif module == "frmf":
        frmf.render(st.session_state['username'])
    elif module == "pma":
        pma_logistics.render(st.session_state['username'])
    elif module == "security":
        render_security_center(st.session_state['username'], st.session_state['user_role'])
    elif module == "admin":
        render_admin_panel(st.session_state['username'], st.session_state['user_role'])
    else:
        render_interactive_dashboard(set_module)


# ============================================================================
# INTERACTIVE DASHBOARD
# ============================================================================

def render_interactive_dashboard(set_module):
    """Render interactive dashboard with clickable module cards."""
    
    from database.connection import count_records, aggregate_sum, get_data
    
    # Header - Metallic Paars
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 30%, #C4B5FD 50%, #A78BFA 70%, #8B5CF6 100%);
                    padding: 2rem; border-radius: 16px; margin-bottom: 2rem;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    box-shadow: 0 10px 40px rgba(139, 92, 246, 0.3), inset 0 1px 0 rgba(255,255,255,0.3);'>
            <h1 style='color: white; font-family: Rajdhani, sans-serif; margin: 0; text-shadow: 0 2px 4px rgba(0,0,0,0.2);'>
                📊 EXECUTIVE DASHBOARD
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
                Welcome back, <strong style='color: #FDE68A;'>{st.session_state['username']}</strong> | 
                Click any card to navigate to that module
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # === WK 2030 COUNTDOWN ===
    wk_date = datetime(2030, 6, 13)
    delta = wk_date - datetime.now()
    days_left = delta.days
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #D4AF37 0%, #F4E5B2 50%, #D4AF37 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem; text-align: center;
                    border: 2px solid #B8860B; box-shadow: 0 8px 25px rgba(212, 175, 55, 0.3);'>
            <span style='font-size: 0.9rem; color: #4B5563; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;'>WK 2030 MOROCCO</span>
            <div style='font-size: 2.5rem; font-weight: 700; color: #1F2937; font-family: Rajdhani, sans-serif;'>
                {days_left:,} DAYS
            </div>
            <span style='font-size: 0.8rem; color: #4B5563;'>Until Opening Ceremony</span>
        </div>
    """, unsafe_allow_html=True)
    
    # === FETCH REAL DATA ===
    try:
        talents = count_records('ntsp_talent_profiles')
        tickets = count_records('ticketchain_tickets')
        wallets = count_records('diaspora_wallets')
        identities = count_records('identity_shield')
        transfers_count = count_records('transfers')
        academies = count_records('academies')
        donations = count_records('foundation_donations')
        contributions = count_records('foundation_contributions')
        
        ticket_revenue = aggregate_sum('fiscal_ledger', 'gross_amount') or 0
        foundation_total = aggregate_sum('foundation_contributions', 'amount') or 0
        wallet_balance = aggregate_sum('diaspora_wallets', 'balance') or 0
        transfer_value = aggregate_sum('transfers', 'total_fee') or 0
    except:
        talents = tickets = wallets = identities = transfers_count = academies = donations = contributions = 0
        ticket_revenue = foundation_total = wallet_balance = transfer_value = 0
    
    # === CLICKABLE MODULE CARDS ===
    st.markdown(f"""
        <p style='font-family: Rajdhani, sans-serif; font-weight: 600; 
                  letter-spacing: 2px; color: {COLORS['gold']}; 
                  font-size: 1rem; margin: 1.5rem 0 1rem 0;'>
             FINANCIAL ECOSYSTEM
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f" TicketChain™\n\n**{tickets:,}** Tickets\n€{ticket_revenue:,.0f} Revenue", 
                     use_container_width=True, key="dash_ticket"):
            set_module('ticketchain')
            st.rerun()
    
    with col2:
        if st.button(f" Foundation Bank\n\n**{donations + contributions:,}** Transactions\n€{foundation_total:,.0f} Sadaka", 
                     use_container_width=True, key="dash_foundation"):
            set_module('foundation')
            st.rerun()
    
    with col3:
        if st.button(f" Diaspora Wallet\n\n**{wallets:,}** Wallets\n€{wallet_balance:,.0f} Balance", 
                     use_container_width=True, key="dash_wallet"):
            set_module('wallet')
            st.rerun()
    
    with col4:
        if st.button(f" Subscriptions\n\nManage Plans\n& Billing", 
                     use_container_width=True, key="dash_subs"):
            set_module('subscriptions')
            st.rerun()
    
    # === SPORT DIVISION ===
    st.markdown(f"""
        <p style='font-family: Rajdhani, sans-serif; font-weight: 600; 
                  letter-spacing: 2px; color: {COLORS['gold']}; 
                  font-size: 1rem; margin: 1.5rem 0 1rem 0;'>
             SPORT DIVISION
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button(f" NTSP™\n\n**{talents:,}** Talents\nScouting Platform", 
                     use_container_width=True, key="dash_ntsp"):
            set_module('ntsp')
            st.rerun()
    
    with col2:
        if st.button(f" Transfers\n\n**{transfers_count:,}** Transfers\n€{transfer_value:,.0f} Value", 
                     use_container_width=True, key="dash_transfers"):
            set_module('transfers')
            st.rerun()
    
    with col3:
        if st.button(f" Academy\n\n**{academies:,}** Academies\nNational Network", 
                     use_container_width=True, key="dash_academy"):
            set_module('academy')
            st.rerun()
    
    with col4:
        # Get FanDorpen stats
        try:
            fandorpen_count = count_records('fandorpen')
            volunteers_count = count_records('fandorp_volunteers')
        except:
            fandorpen_count = volunteers_count = 0
        
        if st.button(f" FanDorpen\n\n**{fandorpen_count}** Dorpen\n{volunteers_count} Vrijwilligers", 
                     use_container_width=True, key="dash_fandorpen"):
            set_module('fandorpen')
            st.rerun()
    
    # === WK2030 & DIASPORA ===
    st.markdown(f"""
        <p style='font-family: Rajdhani, sans-serif; font-weight: 600; 
                  letter-spacing: 2px; color: {COLORS['gold']}; 
                  font-size: 1rem; margin: 1.5rem 0 1rem 0;'>
             WK2030 & DIASPORA
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f" Consulate Hub\n\nDigital Services\nFor 5,5M Diaspora", 
                     use_container_width=True, key="dash_consulate"):
            set_module('consulate')
            st.rerun()
    
    with col2:
        if st.button(f" WK 2030 Travel\n\nMobility Packages\nTransport & Hotels", 
                     use_container_width=True, key="dash_mobility"):
            set_module('mobility')
            st.rerun()
    
    with col3:
        if st.button(f" Identity Shield\n\n**{identities:,}** Protected\n24/7 Monitoring", 
                     use_container_width=True, key="dash_identity"):
            set_module('identity')
            st.rerun()
    
    # === SOCIAL IMPACT ===
    st.markdown(f"""
        <p style='font-family: Rajdhani, sans-serif; font-weight: 600; 
                  letter-spacing: 2px; color: {COLORS['gold']}; 
                  font-size: 1rem; margin: 1.5rem 0 1rem 0;'>
             SOCIAL IMPACT
        </p>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f" Hayat Health\n\nHealth Initiative\nWellbeing Programs", 
                     use_container_width=True, key="dash_hayat"):
            set_module('hayat')
            st.rerun()
    
    with col2:
        if st.button(f" Women & Para\n\nInclusion Programs\nEqual Opportunities", 
                     use_container_width=True, key="dash_inclusion"):
            set_module('inclusion')
            st.rerun()
    
    with col3:
        if st.button(f" Anti-Hate Shield\n\nContent Protection\nDigital Peace", 
                     use_container_width=True, key="dash_antihate"):
            set_module('antihate')
            st.rerun()
    
    # === QUICK STATS ===
    st.markdown("<hr style='margin: 2rem 0; border-color: rgba(212, 175, 55, 0.3);'>", unsafe_allow_html=True)
    
    st.markdown(f"""
        <p style='font-family: Rajdhani, sans-serif; font-weight: 600; 
                  letter-spacing: 2px; color: {COLORS['gold']}; 
                  font-size: 1rem; margin: 1rem 0;'>
             PLATFORM OVERVIEW
        </p>
    """, unsafe_allow_html=True)
    
    # Summary metrics
    total_records = talents + tickets + wallets + identities + donations + contributions
    total_value = ticket_revenue + foundation_total + wallet_balance + transfer_value
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" Total Records", f"{total_records:,}")
    col2.metric(" Total Value", f"€{total_value:,.0f}")
    col3.metric(" Diaspora Reach", "5,5M+")
    col4.metric(" WK 2030", f"{days_left} days")


# ============================================================================
# MAIN ROUTING
# ============================================================================

def main():
    """Main application routing."""
    
    current_page = st.session_state.get('page', 'landing')
    
    # Public pages (no login required)
    if current_page == 'landing':
        render_landing_page(navigate_to)
    
    elif current_page == 'investor_portal':
        render_investor_portal(navigate_to)
    
    elif current_page == 'masterplan':
        from views.masterplan import render_masterplan_page
        render_masterplan_page(navigate_to)
    
    elif current_page == 'login':
        render_login_page()
    
    elif current_page == 'register':
        render_register_page()
    
    # Protected pages (login required)
    elif current_page == 'dashboard':
        if st.session_state['ingelogd']:
            render_main_app()
        else:
            st.warning(t("auth_please_login"))
            navigate_to('login')
    
    else:
        # Default to landing
        render_landing_page(navigate_to)


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    main()
