"""
ProInvestiX UI Styles - v8.4
"""

# Light Theme Colors (default)
COLORS = {
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

# Alias for backward compatibility
COLORS_LIGHT = COLORS.copy()

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


def get_theme_colors(dark_mode=False):
    """Get colors based on theme setting"""
    if dark_mode:
        return COLORS_DARK
    return COLORS


def apply_custom_css(dark_mode=False):
    """Apply custom CSS styling"""
    try:
        import streamlit as st
        
        colors = get_theme_colors(dark_mode)
        
        css = f"""
        <style>
            .stApp {{
                background-color: {colors['background']};
            }}
            
            [data-testid="stSidebar"] {{
                background-color: {colors['sidebar_bg']};
            }}
            
            .stButton > button {{
                background: linear-gradient(135deg, {colors['primary']} 0%, {colors['purple_dark']} 100%);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
            }}
            
            .stButton > button:hover {{
                opacity: 0.9;
            }}
            
            .metric-card {{
                background: {colors['card']};
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid {colors['accent']};
            }}
            
            .category-header {{
                color: {colors['gold']} !important;
                font-weight: bold;
                font-size: 12px;
                margin: 15px 0 5px 0;
                padding: 5px;
                border-bottom: 1px solid {colors['gold']}33;
            }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except Exception:
        pass  # Silently fail if CSS cannot be applied


def get_footer_html(dark_mode=False):
    """Get footer HTML"""
    colors = get_theme_colors(dark_mode)
    return f"""
    <div style='text-align: center; padding: 20px; color: {colors['text_muted']};'>
        <p>ProInvestiX v8.4 | Masterplan 2026-2050</p>
        <p style='color: {colors['gold']};'>Sadaka Jaaria - For Morocco, With Morocco</p>
    </div>
    """
