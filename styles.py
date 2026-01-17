"""
ProInvestiX UI Styles
"""

COLORS = {
    'primary': '#8B5CF6',
    'secondary': '#F5F3FF', 
    'accent': '#FFD700',
    'success': '#00ff88',
    'warning': '#FFB800',
    'error': '#ff6b6b',
    'text': '#F8FAFC',
    'muted': '#888888',
    'background': '#FAF9FF',
    'card': '#FFFFFF',
    'purple': '#8B5CF6',
    'gold': '#FFD700',
    'green': '#00ff88',
    'red': '#ff6b6b',
    'blue': '#3B82F6',
}


def apply_custom_css():
    """Apply custom CSS styling"""
    import streamlit as st
    
    st.markdown(f"""
    <style>
        .stApp {{
            background-color: {COLORS['background']};
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, {COLORS['primary']} 0%, #6366f1 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
        }}
        
        .stButton > button:hover {{
            opacity: 0.9;
        }}
        
        .metric-card {{
            background: {COLORS['card']};
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid {COLORS['accent']};
        }}
        
        h1, h2, h3 {{
            color: {COLORS['text']};
        }}
        
        .sidebar .sidebar-content {{
            background: {COLORS['secondary']};
        }}
        
        /* Category headers in sidebar */
        .category-header {{
            color: {COLORS['gold']};
            font-weight: bold;
            font-size: 12px;
            margin: 15px 0 5px 0;
            padding: 5px;
            border-bottom: 1px solid {COLORS['gold']}33;
        }}
    </style>
    """, unsafe_allow_html=True)


def get_footer_html():
    """Get footer HTML"""
    return f"""
    <div style='text-align: center; padding: 20px; color: {COLORS['muted']};'>
        <p>ProInvestiX v5.4.1 | Masterplan 2026-2050</p>
        <p>Sadaka Jaaria - For Morocco, With Morocco</p>
    </div>
    """
