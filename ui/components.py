# ============================================================================
# PROINVESTIX UI COMPONENTS - FANDORPEN STYLE (LIGHT THEME)
# ============================================================================
# Alle componenten gebruiken nu de lichte FanDorpen stijl:
# - Lichte achtergrond (#FAF9FF)
# - Paarse gradient headers
# - Witte kaarten met subtiele borders
# - Donkere tekst op lichte achtergrond
# ============================================================================

import streamlit as st
import pandas as pd
from typing import List, Tuple, Optional

from ui.styles import COLORS, GRADIENTS


def metric_row(metrics: List[Tuple], columns: int = None):
    """
    Render a row of metric cards.
    
    Args:
        metrics: List of tuples (label, value) or (label, value, delta)
        columns: Number of columns (default: len(metrics))
    """
    cols = st.columns(columns or len(metrics))
    
    for col, metric in zip(cols, metrics):
        if len(metric) == 2:
            label, value = metric
            delta = None
        else:
            label, value, delta = metric
        
        with col:
            st.metric(label=label, value=value, delta=delta)


def page_header(title: str, subtitle: str, icon: str = None):
    """
    Render a page header - FANDORPEN STYLE.
    Exact dezelfde stijl als premium_header() in ui/styles.py
    """
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    subtitle_html = f"<p style='color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 0.95rem;'>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 50%, #C4B5FD 100%);
            padding: 30px 35px;
            border-radius: 16px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(139, 92, 246, 0.2);
        '>
            <h1 style='
                color: white;
                margin: 0;
                font-size: 1.8rem;
                font-weight: 700;
            '>{icon_html}{title}</h1>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def data_table_with_empty_state(df: pd.DataFrame, empty_message: str = "No data available.", **kwargs):
    """
    Render a dataframe with an empty state message.
    
    Args:
        df: DataFrame to display
        empty_message: Message to show when empty
        **kwargs: Additional args for st.dataframe
    """
    if df.empty:
        st.info(empty_message)
    else:
        st.dataframe(df, **kwargs)


def status_badge(status: str, status_type: str = "default") -> str:
    """
    Generate HTML for a status badge - LIGHT THEME.
    
    Args:
        status: The status text
        status_type: 'success', 'warning', 'error', 'info', or 'default'
    
    Returns:
        HTML string for the badge
    """
    colors = {
        'success': ('#10B981', '#D1FAE5'),
        'warning': ('#F59E0B', '#FEF3C7'),
        'error': ('#EF4444', '#FEE2E2'),
        'info': ('#3B82F6', '#DBEAFE'),
        'default': ('#8B5CF6', '#EDE9FE'),
    }
    
    text_color, bg_color = colors.get(status_type, colors['default'])
    
    return f"""
        <span style='
            background: {bg_color};
            color: {text_color};
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid {text_color}33;
        '>{status}</span>
    """


def card(title: str, content: str, icon: str = None, footer: str = None):
    """
    Render a card component - FANDORPEN STYLE (white card, light border).
    
    Args:
        title: Card title
        content: Card content (can be HTML)
        icon: Optional emoji icon
        footer: Optional footer text
    """
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    footer_html = f"""
        <div style='
            margin-top: 1rem;
            padding-top: 0.75rem;
            border-top: 1px solid #EDE9FE;
            color: #6B7280;
            font-size: 0.8rem;
        '>{footer}</div>
    """ if footer else ""
    
    st.markdown(f"""
        <div style='
            background: #FFFFFF;
            border: 1px solid #EDE9FE;
            border-radius: 14px;
            padding: 1.5rem;
            height: 100%;
            box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);
        '>
            <h4 style='
                color: #4C1D95;
                margin: 0 0 1rem 0;
                font-weight: 600;
            '>{icon_html}{title}</h4>
            <div style='
                color: #1F2937;
                font-size: 0.95rem;
                line-height: 1.6;
            '>{content}</div>
            {footer_html}
        </div>
    """, unsafe_allow_html=True)


def paginated_dataframe(df: pd.DataFrame, per_page: int = 20, key_prefix: str = "page", 
                        empty_message: str = "No data available."):
    """
    Render a dataframe with pagination.
    
    Args:
        df: DataFrame to paginate
        per_page: Rows per page
        key_prefix: Unique key prefix for pagination
        empty_message: Message when empty
    """
    if df.empty:
        st.info(empty_message)
        return
    
    total_rows = len(df)
    total_pages = (total_rows - 1) // per_page + 1
    
    # Initialize page state
    page_key = f"{key_prefix}_current_page"
    if page_key not in st.session_state:
        st.session_state[page_key] = 0
    
    current_page = st.session_state[page_key]
    
    # Calculate slice
    start_idx = current_page * per_page
    end_idx = min(start_idx + per_page, total_rows)
    
    # Display current page
    st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
    
    # Pagination controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮ First", key=f"{key_prefix}_first", disabled=current_page == 0):
            st.session_state[page_key] = 0
            st.rerun()
    
    with col2:
        if st.button(" Prev", key=f"{key_prefix}_prev", disabled=current_page == 0):
            st.session_state[page_key] = current_page - 1
            st.rerun()
    
    with col3:
        st.markdown(f"""
            <div style='text-align: center; color: #6B7280; padding: 0.5rem;'>
                Page {current_page + 1} of {total_pages} | Rows {start_idx + 1}-{end_idx} of {total_rows}
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.button("Next ", key=f"{key_prefix}_next", disabled=current_page >= total_pages - 1):
            st.session_state[page_key] = current_page + 1
            st.rerun()
    
    with col5:
        if st.button("Last ⏭", key=f"{key_prefix}_last", disabled=current_page >= total_pages - 1):
            st.session_state[page_key] = total_pages - 1
            st.rerun()


def progress_ring(value: int, max_value: int = 100, label: str = "", size: int = 100):
    """
    Render a circular progress indicator.
    
    Args:
        value: Current value
        max_value: Maximum value
        label: Label to display
        size: Size in pixels
    """
    percentage = min(100, (value / max_value) * 100)
    circumference = 2 * 3.14159 * 40  # radius = 40
    dash_offset = circumference * (1 - percentage / 100)
    
    st.markdown(f"""
        <div style='text-align: center;'>
            <svg width="{size}" height="{size}" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#EDE9FE" stroke-width="8"/>
                <circle cx="50" cy="50" r="40" fill="none" stroke="#8B5CF6" stroke-width="8"
                        stroke-linecap="round" stroke-dasharray="{circumference}" 
                        stroke-dashoffset="{dash_offset}" transform="rotate(-90 50 50)"/>
                <text x="50" y="50" text-anchor="middle" dy="0.35em" 
                      style="font-size: 1.5rem; font-weight: 700; fill: #4C1D95;">
                    {int(percentage)}%
                </text>
            </svg>
            <div style='color: #6B7280; font-size: 0.85rem; margin-top: 0.5rem;'>{label}</div>
        </div>
    """, unsafe_allow_html=True)


def stat_comparison(label: str, current: float, previous: float, format_str: str = "{:,.0f}"):
    """
    Render a stat with comparison to previous value - LIGHT THEME.
    
    Args:
        label: Stat label
        current: Current value
        previous: Previous value for comparison
        format_str: Format string for values
    """
    if previous > 0:
        change = ((current - previous) / previous) * 100
        change_color = '#10B981' if change >= 0 else '#EF4444'
        change_icon = "↑" if change >= 0 else "↓"
        change_html = f"<span style='color: {change_color};'>{change_icon} {abs(change):.1f}%</span>"
    else:
        change_html = ""
    
    st.markdown(f"""
        <div style='
            background: #FFFFFF;
            border: 1px solid #EDE9FE;
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);
        '>
            <div style='color: #6B7280; font-size: 0.85rem;'>{label}</div>
            <div style='
                font-size: 1.75rem;
                font-weight: 700;
                color: #4C1D95;
            '>{format_str.format(current)}</div>
            {change_html}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PREMIUM KPI CARDS - FANDORPEN STYLE
# ============================================================================

def premium_kpi_card(icon: str, label: str, value: str, subtitle: str = None, color: str = None):
    """
    Render a premium KPI card with hover effects - FANDORPEN STYLE.
    
    Args:
        icon: Emoji icon
        label: KPI label
        value: KPI value
        subtitle: Optional subtitle
        color: Optional accent color (default: purple)
    """
    accent = color or '#8B5CF6'
    subtitle_html = f"<div style='color: #6B7280; font-size: 0.75rem; margin-top: 0.25rem;'>{subtitle}</div>" if subtitle else ""
    
    st.markdown(f"""
        <div style='
            background: #FFFFFF;
            border: 1px solid #EDE9FE;
            border-radius: 14px;
            padding: 1.25rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: default;
            box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);
        ' onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 8px 25px rgba(139, 92, 246, 0.15)';"
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 10px rgba(139, 92, 246, 0.05)';">
            <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
            <div style='color: {accent}; font-size: 1.75rem; font-weight: 700;'>{value}</div>
            <div style='color: #4C1D95; font-size: 0.9rem; font-weight: 500;'>{label}</div>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


def premium_kpi_row(kpis: List[Tuple]):
    """
    Render a row of premium KPI cards.
    
    Args:
        kpis: List of tuples (icon, label, value, subtitle)
    """
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        with col:
            if len(kpi) == 3:
                icon, label, value = kpi
                subtitle = None
            else:
                icon, label, value, subtitle = kpi
            premium_kpi_card(icon, label, value, subtitle)


# ============================================================================
# FORM SECTIONS - FANDORPEN STYLE
# ============================================================================

def form_section(title: str, icon: str = None):
    """
    Render a form section header - LIGHT THEME.
    
    Args:
        title: Section title
        icon: Optional emoji icon
    """
    icon_html = f"{icon} " if icon else ""
    st.markdown(f"""
        <div style='
            background: linear-gradient(90deg, #EDE9FE 0%, #FAF9FF 100%);
            border-left: 3px solid #8B5CF6;
            padding: 0.75rem 1rem;
            margin: 1.5rem 0 1rem 0;
            border-radius: 0 8px 8px 0;
        '>
            <span style='
                font-size: 1.1rem;
                font-weight: 600;
                color: #4C1D95;
            '>{icon_html}{title}</span>
        </div>
    """, unsafe_allow_html=True)


def success_message(message: str, details: str = None):
    """
    Render a premium success message.
    
    Args:
        message: Main message
        details: Optional details
    """
    details_html = f"<div style='font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem; color: #065F46;'>{details}</div>" if details else ""
    st.markdown(f"""
        <div style='
            background: #D1FAE5;
            border: 1px solid #A7F3D0;
            border-left: 4px solid #10B981;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        '>
            <div style='color: #065F46; font-weight: 600;'>
                 {message}
            </div>
            {details_html}
        </div>
    """, unsafe_allow_html=True)


def error_message(message: str, details: str = None):
    """
    Render a premium error message.
    
    Args:
        message: Main message
        details: Optional details
    """
    details_html = f"<div style='font-size: 0.85rem; opacity: 0.9; margin-top: 0.5rem; color: #991B1B;'>{details}</div>" if details else ""
    st.markdown(f"""
        <div style='
            background: #FEE2E2;
            border: 1px solid #FECACA;
            border-left: 4px solid #EF4444;
            border-radius: 8px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        '>
            <div style='color: #991B1B; font-weight: 600;'>
                 {message}
            </div>
            {details_html}
        </div>
    """, unsafe_allow_html=True)


def info_box(title: str, content: str, icon: str = "ℹ"):
    """
    Render an info box - LIGHT THEME.
    
    Args:
        title: Box title
        content: Box content
        icon: Emoji icon
    """
    st.markdown(f"""
        <div style='
            background: #DBEAFE;
            border: 1px solid #BFDBFE;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        '>
            <div style='color: #1E40AF; font-weight: 600; margin-bottom: 0.5rem;'>
                {icon} {title}
            </div>
            <div style='color: #1E3A8A; font-size: 0.9rem; line-height: 1.5;'>
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)


def warning_box(title: str, content: str):
    """
    Render a warning box - LIGHT THEME.
    
    Args:
        title: Box title
        content: Box content
    """
    st.markdown(f"""
        <div style='
            background: #FEF3C7;
            border: 1px solid #FDE68A;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        '>
            <div style='color: #92400E; font-weight: 600; margin-bottom: 0.5rem;'>
                 {title}
            </div>
            <div style='color: #78350F; font-size: 0.9rem; line-height: 1.5;'>
                {content}
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# DATA DISPLAY - FANDORPEN STYLE
# ============================================================================

def detail_row(label: str, value: str, icon: str = None):
    """
    Render a detail row for displaying key-value pairs.
    
    Args:
        label: Field label
        value: Field value
        icon: Optional emoji icon
    """
    icon_html = f"<span style='margin-right: 0.5rem;'>{icon}</span>" if icon else ""
    st.markdown(f"""
        <div style='
            display: flex;
            justify-content: space-between;
            padding: 0.5rem 0;
            border-bottom: 1px solid #EDE9FE;
        '>
            <span style='color: #6B7280;'>{icon_html}{label}</span>
            <span style='color: #4C1D95; font-weight: 500;'>{value}</span>
        </div>
    """, unsafe_allow_html=True)


def score_bar(label: str, score: float, max_score: float = 100):
    """
    Render a horizontal score bar.
    
    Args:
        label: Score label
        score: Current score
        max_score: Maximum score
    """
    percentage = min(100, (score / max_score) * 100)
    
    # Color based on score
    if percentage >= 80:
        color = '#10B981'
    elif percentage >= 60:
        color = '#8B5CF6'
    elif percentage >= 40:
        color = '#F59E0B'
    else:
        color = '#EF4444'
    
    st.markdown(f"""
        <div style='margin: 0.5rem 0;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.25rem;'>
                <span style='color: #6B7280; font-size: 0.85rem;'>{label}</span>
                <span style='color: {color}; font-weight: 600;'>{score:.1f}</span>
            </div>
            <div style='
                background: #EDE9FE;
                border-radius: 4px;
                height: 8px;
                overflow: hidden;
            '>
                <div style='
                    background: linear-gradient(90deg, {color} 0%, {color}88 100%);
                    width: {percentage}%;
                    height: 100%;
                    border-radius: 4px;
                    transition: width 0.5s ease;
                '></div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def timeline_item(date: str, title: str, description: str = None, status: str = "default"):
    """
    Render a timeline item.
    
    Args:
        date: Date string
        title: Event title
        description: Optional description
        status: 'success', 'warning', 'error', or 'default'
    """
    colors = {
        'success': '#10B981',
        'warning': '#F59E0B',
        'error': '#EF4444',
        'default': '#8B5CF6',
    }
    dot_color = colors.get(status, colors['default'])
    desc_html = f"<div style='color: #6B7280; font-size: 0.85rem; margin-top: 0.25rem;'>{description}</div>" if description else ""
    
    st.markdown(f"""
        <div style='
            display: flex;
            padding: 0.75rem 0;
            border-left: 2px solid #EDE9FE;
            margin-left: 0.5rem;
            padding-left: 1rem;
            position: relative;
        '>
            <div style='
                position: absolute;
                left: -6px;
                top: 1rem;
                width: 10px;
                height: 10px;
                background: {dot_color};
                border-radius: 50%;
                border: 2px solid #FFFFFF;
            '></div>
            <div>
                <div style='color: #6B7280; font-size: 0.75rem;'>{date}</div>
                <div style='color: #4C1D95; font-weight: 500;'>{title}</div>
                {desc_html}
            </div>
        </div>
    """, unsafe_allow_html=True)


def action_button_row(buttons: List[Tuple]):
    """
    Render a row of styled action buttons.
    
    Args:
        buttons: List of tuples (label, key, type) where type is 'primary', 'secondary', or 'danger'
    """
    cols = st.columns(len(buttons))
    results = {}
    
    for col, button in zip(cols, buttons):
        label, key, btn_type = button
        with col:
            if btn_type == 'primary':
                results[key] = st.button(label, key=key, type="primary", use_container_width=True)
            elif btn_type == 'danger':
                # Custom red button via markdown + button
                results[key] = st.button(f"🗑 {label}", key=key, use_container_width=True)
            else:
                results[key] = st.button(label, key=key, use_container_width=True)
    
    return results


# ============================================================================
# SECTION HEADERS - FANDORPEN STYLE
# ============================================================================

def section_header(title: str, subtitle: str = "", color: str = "purple"):
    """
    Render a section header - FANDORPEN STYLE.
    
    Args:
        title: Section title
        subtitle: Optional subtitle
        color: Color scheme ('purple', 'gold', 'green', 'blue')
    """
    color_map = {
        'purple': ('#8B5CF6', '#EDE9FE', '#DDD6FE'),
        'gold': ('#F59E0B', '#FEF3C7', '#FDE68A'),
        'green': ('#10B981', '#D1FAE5', '#A7F3D0'),
        'blue': ('#3B82F6', '#DBEAFE', '#BFDBFE'),
    }
    
    main_color, bg_start, border_color = color_map.get(color, color_map['purple'])
    subtitle_html = f"<p style='color: #6B7280; margin: 0.5rem 0 0 0; font-size: 0.9rem;'>{subtitle}</p>" if subtitle else ""
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, {bg_start} 0%, #FAF9FF 100%);
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            border: 1px solid {border_color};
        '>
            <h3 style='color: {main_color}; margin: 0; font-weight: 600;'>{title}</h3>
            {subtitle_html}
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# LOADING STATES & SPINNERS
# ============================================================================

def loading_spinner(message: str = "Loading...", size: str = "medium"):
    """
    Render a custom loading spinner.
    
    Args:
        message: Loading message to display
        size: 'small', 'medium', or 'large'
    """
    sizes = {
        'small': ('30px', '3px', '0.8rem'),
        'medium': ('50px', '4px', '1rem'),
        'large': ('80px', '5px', '1.2rem'),
    }
    spinner_size, border_width, font_size = sizes.get(size, sizes['medium'])
    
    st.markdown(f"""
        <div style='
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem;
        '>
            <div style='
                width: {spinner_size};
                height: {spinner_size};
                border: {border_width} solid #EDE9FE;
                border-top: {border_width} solid #8B5CF6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            '></div>
            <p style='
                color: #6B7280;
                margin-top: 1rem;
                font-size: {font_size};
            '>{message}</p>
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    """, unsafe_allow_html=True)


def skeleton_loader(lines: int = 3, show_avatar: bool = False):
    """
    Render skeleton loading placeholder.
    
    Args:
        lines: Number of text lines to show
        show_avatar: Whether to show avatar placeholder
    """
    avatar_html = """
        <div style='
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(90deg, #EDE9FE 25%, #F5F3FF 50%, #EDE9FE 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            margin-right: 1rem;
        '></div>
    """ if show_avatar else ""
    
    lines_html = "".join([f"""
        <div style='
            height: 12px;
            border-radius: 6px;
            background: linear-gradient(90deg, #EDE9FE 25%, #F5F3FF 50%, #EDE9FE 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            margin-bottom: 0.75rem;
            width: {90 - i * 10}%;
        '></div>
    """ for i in range(lines)])
    
    st.markdown(f"""
        <div style='
            display: flex;
            align-items: flex-start;
            padding: 1rem;
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #EDE9FE;
        '>
            {avatar_html}
            <div style='flex: 1;'>
                {lines_html}
            </div>
        </div>
        <style>
            @keyframes shimmer {{
                0% {{ background-position: -200% 0; }}
                100% {{ background-position: 200% 0; }}
            }}
        </style>
    """, unsafe_allow_html=True)


def loading_card(title: str = "Loading data..."):
    """
    Render a loading card placeholder.
    
    Args:
        title: Loading message
    """
    st.markdown(f"""
        <div style='
            background: #FFFFFF;
            border: 1px solid #EDE9FE;
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
        '>
            <div style='
                width: 40px;
                height: 40px;
                border: 3px solid #EDE9FE;
                border-top: 3px solid #8B5CF6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 0 auto 1rem auto;
            '></div>
            <p style='color: #6B7280; margin: 0;'>{title}</p>
        </div>
        <style>
            @keyframes spin {{
                0% {{ transform: rotate(0deg); }}
                100% {{ transform: rotate(360deg); }}
            }}
        </style>
    """, unsafe_allow_html=True)


def progress_bar_animated(progress: int, label: str = "", show_percentage: bool = True):
    """
    Render an animated progress bar.
    
    Args:
        progress: Progress value (0-100)
        label: Optional label
        show_percentage: Show percentage text
    """
    progress = max(0, min(100, progress))
    
    # Color based on progress
    if progress >= 80:
        color = '#10B981'
    elif progress >= 50:
        color = '#8B5CF6'
    elif progress >= 25:
        color = '#F59E0B'
    else:
        color = '#EF4444'
    
    label_html = f"<span style='color: #6B7280;'>{label}</span>" if label else ""
    percentage_html = f"<span style='color: {color}; font-weight: 600;'>{progress}%</span>" if show_percentage else ""
    
    st.markdown(f"""
        <div style='margin: 1rem 0;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 0.5rem;'>
                {label_html}
                {percentage_html}
            </div>
            <div style='
                background: #EDE9FE;
                border-radius: 8px;
                height: 12px;
                overflow: hidden;
            '>
                <div style='
                    background: linear-gradient(90deg, {color} 0%, {color}CC 100%);
                    width: {progress}%;
                    height: 100%;
                    border-radius: 8px;
                    transition: width 0.5s ease;
                    animation: pulse 2s infinite;
                '></div>
            </div>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.8; }}
            }}
        </style>
    """, unsafe_allow_html=True)


# ============================================================================
# TOOLTIPS & HELP
# ============================================================================

def tooltip(text: str, help_text: str, icon: str = "ℹ️"):
    """
    Render text with a tooltip icon.
    
    Args:
        text: Main text to display
        help_text: Tooltip help text
        icon: Tooltip icon
    """
    st.markdown(f"""
        <div style='display: inline-flex; align-items: center; gap: 0.5rem;'>
            <span>{text}</span>
            <span title="{help_text}" style='
                cursor: help;
                color: #8B5CF6;
                font-size: 0.9rem;
            '>{icon}</span>
        </div>
    """, unsafe_allow_html=True)


def help_icon(help_text: str):
    """
    Render a standalone help icon with tooltip.
    
    Args:
        help_text: Help text to show on hover
    """
    st.markdown(f"""
        <span title="{help_text}" style='
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #EDE9FE;
            color: #8B5CF6;
            font-size: 0.75rem;
            cursor: help;
            margin-left: 0.5rem;
        '>?</span>
    """, unsafe_allow_html=True)


def form_field_with_help(label: str, help_text: str):
    """
    Render a form field label with help icon.
    
    Args:
        label: Field label
        help_text: Help text
    
    Returns:
        The label HTML (use with st.markdown)
    """
    return f"""
        <div style='
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.25rem;
        '>
            <span style='color: #4C1D95; font-weight: 500;'>{label}</span>
            <span title="{help_text}" style='
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #EDE9FE;
                color: #8B5CF6;
                font-size: 0.65rem;
                cursor: help;
            '>?</span>
        </div>
    """


def info_tooltip_card(title: str, content: str, tips: list = None):
    """
    Render an expandable info card with tips.
    
    Args:
        title: Card title
        content: Main content
        tips: List of tip strings
    """
    tips_html = ""
    if tips:
        tips_items = "".join([f"<li style='margin: 0.25rem 0; color: #4B5563;'>{tip}</li>" for tip in tips])
        tips_html = f"<ul style='margin: 0.75rem 0 0 0; padding-left: 1.25rem;'>{tips_items}</ul>"
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #EDE9FE 0%, #F5F3FF 100%);
            border: 1px solid #DDD6FE;
            border-radius: 10px;
            padding: 1rem 1.25rem;
            margin: 1rem 0;
        '>
            <div style='
                display: flex;
                align-items: center;
                gap: 0.5rem;
                color: #5B21B6;
                font-weight: 600;
                margin-bottom: 0.5rem;
            '>
                <span style='font-size: 1.1rem;'>💡</span>
                {title}
            </div>
            <div style='color: #6B7280; font-size: 0.9rem; line-height: 1.5;'>
                {content}
                {tips_html}
            </div>
        </div>
    """, unsafe_allow_html=True)
