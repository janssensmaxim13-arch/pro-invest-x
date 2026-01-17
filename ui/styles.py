"""
ProInvestiX UI Styles - Soft Pastel Purple Theme
Consistent styling across all modules - FanDorpen style
"""

# =============================================================================
# KLEUREN PALET - SOFT PASTEL PURPLE (LIGHT THEME)
# =============================================================================

COLORS = {
    # Primary purple shades
    'primary': '#8B5CF6',
    'primary_dark': '#7C3AED',
    'primary_light': '#A78BFA',
    'purple': '#8B5CF6',
    'purple_light': '#A78BFA',
    'purple_primary': '#8B5CF6',
    'purple_bright': '#C4B5FD',
    
    # Backgrounds - LIGHT
    'background': '#FAF9FF',
    'sidebar_bg': '#F5F3FF',
    'card': '#FFFFFF',
    'card_hover': '#F5F3FF',
    'bg_dark': '#FAF9FF',
    'bg_card': '#FFFFFF',
    
    # Secondary colors
    'secondary': '#EDE9FE',
    'border': '#DDD6FE',
    'border_light': '#EDE9FE',
    
    # Accent colors
    'accent': '#FBBF24',
    'gold': '#F59E0B',
    
    # Text colors - DARK on light
    'text': '#1F2937',
    'text_dark': '#4C1D95',
    'text_muted': '#6B7280',
    'text_light': '#9CA3AF',
    'text_primary': '#4C1D95',
    'text_secondary': '#6B7280',
    
    # Status colors
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'info': '#3B82F6',
    
    # Legacy
    'muted': '#6B7280',
    'green': '#10B981',
    'red': '#EF4444',
    'blue': '#3B82F6',
}


# =============================================================================
# GRADIENT DEFINITIONS
# =============================================================================

GRADIENTS = {
    'header': 'linear-gradient(135deg, #8B5CF6 0%, #A78BFA 50%, #C4B5FD 100%)',
    'gold': 'linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%)',
    'card_purple': 'linear-gradient(135deg, #EDE9FE 0%, #F5F3FF 100%)',
    'card_success': 'linear-gradient(135deg, #D1FAE5 0%, #ECFDF5 100%)',
    'card_warning': 'linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%)',
    'sidebar': 'linear-gradient(180deg, #F5F3FF 0%, #FAF9FF 100%)',
}


# =============================================================================
# CSS INJECTION
# =============================================================================

def apply_custom_css(dark_mode=False):
    """Apply Soft Pastel Purple theme CSS - matches FanDorpen style"""
    import streamlit as st
    
    # Note: dark_mode parameter reserved for future use
    st.markdown("""
    <style>
        /* ===========================================
           GLOBAL BACKGROUND
           =========================================== */
        .stApp {
            background: #FAF9FF !important;
        }
        
        /* ===========================================
           SIDEBAR
           =========================================== */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #F5F3FF 0%, #FAF9FF 100%) !important;
            border-right: 1px solid #DDD6FE !important;
        }
        
        [data-testid="stSidebar"] * {
            color: #1F2937 !important;
        }
        
        [data-testid="stSidebar"] .stButton > button {
            background: #EDE9FE !important;
            color: #4C1D95 !important;
            border: 1px solid #DDD6FE !important;
            border-radius: 10px !important;
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            background: #DDD6FE !important;
            color: #7C3AED !important;
        }
        
        /* ===========================================
           MAIN BUTTONS
           =========================================== */
        .stButton > button {
            background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.2) !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(139, 92, 246, 0.3) !important;
        }
        
        /* ===========================================
           TABS - NO UNDERLINES
           =========================================== */
        .stTabs [data-baseweb="tab-list"] {
            background: #EDE9FE !important;
            border-radius: 12px !important;
            padding: 5px !important;
            gap: 8px !important;
            border: none !important;
        }
        
        .stTabs [data-baseweb="tab-list"]::after,
        .stTabs [data-baseweb="tab-list"]::before,
        .stTabs [data-baseweb="tab-border"],
        .stTabs [data-baseweb="tab-highlight"] {
            display: none !important;
            background: none !important;
            height: 0 !important;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            color: #6B7280 !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 24px !important;
            font-weight: 500 !important;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            color: #7C3AED !important;
            background: #DDD6FE !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: white !important;
            color: #4C1D95 !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.15) !important;
        }
        
        /* ===========================================
           METRICS
           =========================================== */
        [data-testid="stMetricValue"] {
            color: #4C1D95 !important;
            font-weight: 700 !important;
        }
        
        [data-testid="stMetricLabel"] {
            color: #6B7280 !important;
        }
        
        [data-testid="stMetricDelta"] {
            color: #10B981 !important;
        }
        
        /* ===========================================
           INPUTS & FORMS
           =========================================== */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextArea > div > div > textarea,
        .stNumberInput > div > div > input {
            background: white !important;
            border: 1px solid #DDD6FE !important;
            border-radius: 10px !important;
            color: #1F2937 !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: #8B5CF6 !important;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1) !important;
        }
        
        .stTextInput > label,
        .stSelectbox > label,
        .stMultiSelect > label,
        .stTextArea > label,
        .stNumberInput > label {
            color: #4C1D95 !important;
            font-weight: 500 !important;
        }
        
        /* ===========================================
           EXPANDERS
           =========================================== */
        .streamlit-expanderHeader {
            background: white !important;
            border: 1px solid #EDE9FE !important;
            border-radius: 10px !important;
            color: #4C1D95 !important;
        }
        
        .streamlit-expanderContent {
            background: white !important;
            border: 1px solid #EDE9FE !important;
            border-top: none !important;
        }
        
        /* ===========================================
           DATAFRAMES & TABLES
           =========================================== */
        .stDataFrame {
            background: white !important;
            border-radius: 10px !important;
            border: 1px solid #EDE9FE !important;
        }
        
        /* ===========================================
           HEADINGS
           =========================================== */
        h1, h2, h3, h4, h5, h6 {
            color: #4C1D95 !important;
        }
        
        p, span, div, label {
            color: #1F2937;
        }
        
        /* ===========================================
           ALERTS
           =========================================== */
        .stAlert {
            border-radius: 10px !important;
        }
        
        /* ===========================================
           DIVIDERS
           =========================================== */
        hr {
            border: none !important;
            border-top: 1px solid #EDE9FE !important;
        }
        
        /* ===========================================
           SCROLLBAR
           =========================================== */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #EDE9FE;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #DDD6FE;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #A78BFA;
        }
        
        /* ===========================================
           HIDE STREAMLIT BRANDING (maar niet header)
           =========================================== */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* ===========================================
           SIDEBAR COLLAPSE BUTTON - ZICHTBAAR MAKEN
           =========================================== */
        [data-testid="collapsedControl"] {
            background: #8B5CF6 !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3) !important;
        }
        
        [data-testid="collapsedControl"]:hover {
            background: #7C3AED !important;
        }
        
        [data-testid="collapsedControl"] svg {
            fill: white !important;
            stroke: white !important;
        }
        
        /* Sidebar toggle arrow altijd zichtbaar */
        button[kind="header"] {
            visibility: visible !important;
            opacity: 1 !important;
        }
        
        [data-testid="stSidebarCollapsedControl"] {
            visibility: visible !important;
            background: #8B5CF6 !important;
            color: white !important;
        }
        
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_footer_html():
    """Get footer HTML"""
    return f"""
    <div style='text-align: center; padding: 20px; color: #6B7280; 
                background: #EDE9FE; border-radius: 10px; margin-top: 30px;'>
        <p style='margin: 0; font-size: 0.85rem; color: #4C1D95;'>ProInvestiX v5.4.1 | Masterplan 2026-2050</p>
        <p style='margin: 5px 0 0 0; font-size: 0.8rem; color: #6B7280;'>Sadaka Jaaria - For Morocco, With Morocco</p>
    </div>
    """


def get_header_gradient():
    """Get header gradient CSS"""
    return GRADIENTS['header']


def get_gold_gradient():
    """Get gold gradient CSS"""
    return GRADIENTS['gold']


def premium_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a premium styled header - FanDorpen style"""
    import streamlit as st
    
    icon_html = f"{icon} " if icon else ""
    subtitle_html = f"<p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95rem;'>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
    <div style='background: {GRADIENTS['header']};
                padding: 30px 35px; border-radius: 16px; margin-bottom: 25px;
                box-shadow: 0 8px 30px rgba(139, 92, 246, 0.2);'>
        <h1 style='color: white; margin: 0; font-size: 1.8rem; font-weight: 700;'>{icon_html}{title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(metrics: list):
    """Render a row of KPI metric cards - FanDorpen style"""
    import streamlit as st
    
    cols = st.columns(len(metrics))
    
    for i, metric in enumerate(metrics):
        with cols[i]:
            label = metric[0]
            value = metric[1]
            delta = metric[2] if len(metric) > 2 else None
            
            delta_html = ""
            if delta:
                delta_color = '#10B981' if str(delta).startswith('+') or (isinstance(delta, (int, float)) and delta > 0) else '#EF4444'
                delta_html = f"<p style='color: {delta_color}; font-size: 0.8rem; margin: 5px 0 0 0;'>{delta}</p>"
            
            st.markdown(f"""
            <div style='background: white; padding: 20px; border-radius: 14px;
                        border: 1px solid #EDE9FE; text-align: center;
                        box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);'>
                <p style='color: #6B7280; font-size: 0.8rem; margin: 0;'>{label}</p>
                <p style='color: #4C1D95; font-size: 1.5rem; font-weight: 700; margin: 8px 0 0 0;'>{value}</p>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)


def section_header(title: str, subtitle: str = "", color: str = "purple"):
    """Render a section header like FanDorpen module"""
    import streamlit as st
    
    color_map = {
        'purple': ('#8B5CF6', '#EDE9FE', '#DDD6FE'),
        'gold': ('#F59E0B', '#FEF3C7', '#FDE68A'),
        'green': ('#10B981', '#D1FAE5', '#A7F3D0'),
        'blue': ('#3B82F6', '#DBEAFE', '#BFDBFE'),
    }
    
    main_color, bg_start, border_color = color_map.get(color, color_map['purple'])
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {bg_start} 0%, #FAF9FF 100%);
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                border: 1px solid {border_color};'>
        <h3 style='color: {main_color}; margin: 0; font-weight: 600;'>{title}</h3>
        <p style='color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def card(content: str, title: str = ""):
    """Render a card like FanDorpen module"""
    import streamlit as st
    
    title_html = f"<h4 style='color: #4C1D95; margin: 0 0 10px 0;'>{title}</h4>" if title else ""
    
    st.markdown(f"""
    <div style='background: white; padding: 20px; border-radius: 14px;
                border: 1px solid #EDE9FE; margin-bottom: 15px;
                box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);'>
        {title_html}
        <div style='color: #1F2937;'>{content}</div>
    </div>
    """, unsafe_allow_html=True)
