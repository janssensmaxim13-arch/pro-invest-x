"""
ProInvestiX UI Styles - v8.2 with Dark/Light Mode
"""

# Light Theme Colors
COLORS_LIGHT = {
    'primary': '#8B5CF6',
    'secondary': '#F5F3FF', 
    'accent': '#D4AF37',
    'success': '#10B981',
    'warning': '#F59E0B',
    'error': '#EF4444',
    'text': '#1F2937',
    'text_muted': '#6B7280',
    'background': '#FAF9FF',
    'card': '#FFFFFF',
    'card_border': '#E5E7EB',
    'sidebar_bg': '#F5F3FF',
    'purple': '#8B5CF6',
    'purple_dark': '#4C1D95',
    'purple_light': '#A78BFA',
    'gold': '#D4AF37',
    'green': '#10B981',
    'red': '#EF4444',
    'blue': '#3B82F6',
}

# Dark Theme Colors
COLORS_DARK = {
    'primary': '#A78BFA',
    'secondary': '#1F1B2E', 
    'accent': '#FFD700',
    'success': '#34D399',
    'warning': '#FBBF24',
    'error': '#F87171',
    'text': '#F9FAFB',
    'text_muted': '#9CA3AF',
    'background': '#0F0D1A',
    'card': '#1F1B2E',
    'card_border': '#374151',
    'sidebar_bg': '#1A1625',
    'purple': '#A78BFA',
    'purple_dark': '#7C3AED',
    'purple_light': '#C4B5FD',
    'gold': '#FFD700',
    'green': '#34D399',
    'red': '#F87171',
    'blue': '#60A5FA',
}

# Default to light theme (for backward compatibility)
COLORS = COLORS_LIGHT.copy()


def get_theme_colors(dark_mode: bool = False) -> dict:
    """Get colors based on theme setting"""
    return COLORS_DARK if dark_mode else COLORS_LIGHT


def apply_custom_css(dark_mode: bool = False):
    """Apply custom CSS styling with theme support"""
    import streamlit as st
    
    colors = get_theme_colors(dark_mode)
    
    st.markdown(f"""
    <style>
        /* Main App Background */
        .stApp {{
            background-color: {colors['background']};
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {colors['sidebar_bg']};
        }}
        
        [data-testid="stSidebar"] * {{
            color: {colors['text']} !important;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: linear-gradient(135deg, {colors['primary']} 0%, {colors['purple_dark']} 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
        }}
        
        /* Text Colors */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text']} !important;
        }}
        
        p, span, label, .stMarkdown {{
            color: {colors['text']};
        }}
        
        /* Cards / Containers */
        [data-testid="stExpander"], 
        .stForm,
        [data-testid="stMetric"] {{
            background-color: {colors['card']};
            border: 1px solid {colors['card_border']};
            border-radius: 10px;
        }}
        
        /* Metric Cards */
        .metric-card {{
            background: {colors['card']};
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {colors['accent']};
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        /* Category headers in sidebar */
        .category-header {{
            color: {colors['gold']} !important;
            font-weight: bold;
            font-size: 12px;
            margin: 15px 0 5px 0;
            padding: 5px;
            border-bottom: 1px solid {colors['gold']}33;
        }}
        
        /* DataFrames */
        .stDataFrame {{
            background-color: {colors['card']};
        }}
        
        /* Inputs */
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea > div > div > textarea {{
            background-color: {colors['card']};
            color: {colors['text']};
            border-color: {colors['card_border']};
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: {colors['card']};
            border-radius: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            color: {colors['text_muted']};
        }}
        
        .stTabs [aria-selected="true"] {{
            color: {colors['primary']} !important;
            border-bottom-color: {colors['primary']} !important;
        }}
        
        /* Success/Error/Warning messages */
        .stSuccess {{
            background-color: {colors['success']}20;
            border-left-color: {colors['success']};
        }}
        
        .stError {{
            background-color: {colors['error']}20;
            border-left-color: {colors['error']};
        }}
        
        .stWarning {{
            background-color: {colors['warning']}20;
            border-left-color: {colors['warning']};
        }}
        
        /* Dividers */
        hr {{
            border-color: {colors['card_border']};
        }}
        
        /* Loading Spinner */
        .stSpinner > div {{
            border-top-color: {colors['primary']} !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_footer_html(dark_mode: bool = False):
    """Get footer HTML with theme support"""
    colors = get_theme_colors(dark_mode)
    return f"""
    <div style='text-align: center; padding: 20px; color: {colors['text_muted']};'>
        <p>ProInvestiX v8.2 | Masterplan 2026-2050</p>
        <p style='color: {colors['gold']};'>Sadaka Jaaria - For Morocco, With Morocco</p>
    </div>
    """
