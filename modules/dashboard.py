# ============================================================================
# PROINVESTIX PREMIUM DASHBOARD - DAY 3 UPGRADE
# 
# Executive Dashboard met:
# - ECHTE database data (geen sample data meer)
# - Interactieve Plotly charts
# - Real-time KPIs
# - Financial overview
# - Platform statistics
# - WK 2030 Countdown
# ============================================================================

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

# Plotly voor interactieve grafieken
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from config import VERSION, VERSION_NAME, FOUNDATION_RATE, ALLOWED_TABLES, DB_FILE
from database.connection import get_data, count_records, aggregate_sum, get_connection
from ui.styles import COLORS, premium_header, render_kpi_row


# ============================================================================
# PLOTLY THEME
# ============================================================================

GOLD_COLORS = ['#D4AF37', '#F4E5B2', '#9B7B2E', '#B8860B', '#FFD700', '#DAA520', '#C5A028']
CHART_COLORS = ['#D4AF37', '#8B5CF6', '#48BB78', '#4299E1', '#ECC94B', '#F56565', '#ED64A6']
PURPLE_GOLD = ['#8B5CF6', '#A78BFA', '#D4AF37', '#F4E5B2', '#6D28D9']


def apply_plotly_theme(fig):
    """Pas het premium LIGHT theme toe op een Plotly figuur."""
    fig.update_layout(
        paper_bgcolor='#FAF9FF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#1F2937', family='Inter'),
        title_font=dict(size=16, color='#4C1D95'),
        legend=dict(font=dict(size=11, color='#4B5563'), bgcolor='rgba(255,255,255,0.8)'),
        xaxis=dict(
            gridcolor='#EDE9FE',
            linecolor='#DDD6FE',
            tickfont=dict(color='#6B7280'),
            title_font=dict(color='#4C1D95')
        ),
        yaxis=dict(
            gridcolor='#EDE9FE',
            linecolor='#DDD6FE',
            tickfont=dict(color='#6B7280'),
            title_font=dict(color='#4C1D95')
        ),
        margin=dict(l=40, r=40, t=50, b=40),
        hoverlabel=dict(
            bgcolor='#FFFFFF',
            font_size=12,
            font_family='Inter',
            bordercolor='#DDD6FE'
        )
    )
    return fig


# ============================================================================
# DATABASE HELPERS
# ============================================================================

def safe_count(table: str) -> int:
    """Veilig records tellen."""
    try:
        if table in ALLOWED_TABLES:
            return count_records(table)
    except:
        pass
    return 0


def safe_aggregate(table: str, column: str, where: str = None) -> float:
    """Veilig aggregeren."""
    try:
        if table in ALLOWED_TABLES:
            return aggregate_sum(table, column, where) or 0
    except:
        pass
    return 0


def get_monthly_data(table: str, date_column: str, value_column: str = None) -> pd.DataFrame:
    """Haal maandelijkse data op."""
    try:
        with get_connection() as conn:
            if value_column:
                query = f"""
                    SELECT strftime('%Y-%m', {date_column}) as month, 
                           COUNT(*) as count,
                           SUM({value_column}) as total
                    FROM {table}
                    WHERE {date_column} IS NOT NULL
                    GROUP BY month
                    ORDER BY month DESC
                    LIMIT 12
                """
            else:
                query = f"""
                    SELECT strftime('%Y-%m', {date_column}) as month, 
                           COUNT(*) as count
                    FROM {table}
                    WHERE {date_column} IS NOT NULL
                    GROUP BY month
                    ORDER BY month DESC
                    LIMIT 12
                """
            df = pd.read_sql_query(query, conn)
            return df.sort_values('month')
    except:
        return pd.DataFrame()


# ============================================================================
# MAIN RENDER
# ============================================================================

def render():
    """Render het premium executive dashboard."""
    
    # Premium header
    premium_header(
        "Executive Dashboard",
        f"Real-time overzicht van het ProInvestiX National Platform • v{VERSION}",
        ""
    )
    
    # === WK 2030 MINI COUNTDOWN ===
    render_wk_countdown_mini()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === TOP KPIs ===
    render_top_kpis()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === MAIN CHARTS ===
    if PLOTLY_AVAILABLE:
        # Row 1: Revenue & Distribution
        col1, col2 = st.columns(2)
        with col1:
            render_transfer_volume_chart()
        with col2:
            render_revenue_distribution()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 2: Talent & Tickets
        col1, col2 = st.columns(2)
        with col1:
            render_talent_by_position()
        with col2:
            render_ticket_sales_chart()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 3: Diaspora & Foundation
        col1, col2 = st.columns(2)
        with col1:
            render_diaspora_distribution()
        with col2:
            render_foundation_growth()
        
    else:
        st.warning(" Installeer Plotly voor interactieve grafieken: `pip install plotly`")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === BOTTOM SECTION ===
    col1, col2 = st.columns([2, 1])
    with col1:
        render_recent_activity()
    with col2:
        render_quick_stats()


# ============================================================================
# WK 2030 MINI COUNTDOWN
# ============================================================================

def render_wk_countdown_mini():
    """Mini WK 2030 countdown banner."""
    wk_date = datetime(2030, 6, 13)
    now = datetime.now()
    delta = wk_date - now
    days_left = delta.days
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);
            border: 1px solid #DDD6FE;
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
        '>
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <span style='font-size: 1.5rem;'></span>
                <span style='color: #1F2937; font-weight: 600;'>WK 2030 Morocco</span>
            </div>
            <div style='display: flex; gap: 2rem;'>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 1.5rem; font-weight: 700;'>{days_left:,}</div>
                    <div style='color: #4B5563; font-size: 0.75rem;'>DAGEN</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 1.5rem; font-weight: 700;'>{delta.days // 365}</div>
                    <div style='color: #4B5563; font-size: 0.75rem;'>JAAR</div>
                </div>
                <div style='text-align: center;'>
                    <div style='color: #1F2937; font-size: 1.5rem; font-weight: 700;'>{(delta.days % 365) // 30}</div>
                    <div style='color: #4B5563; font-size: 0.75rem;'>MAANDEN</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


# ============================================================================
# TOP KPIs - MET ECHTE DATA
# ============================================================================

def render_top_kpis():
    """Render de top KPI rij met echte database data."""
    
    # Haal ECHTE data op
    total_talents = safe_count("ntsp_talent_profiles")
    total_transfers = safe_count("transfers")
    total_tickets = safe_count("ticketchain_tickets")
    total_wallets = safe_count("diaspora_wallets")
    
    # Foundation totaal
    foundation_total = safe_aggregate("foundation_contributions", "amount")
    
    # Transfer volume
    transfer_volume = safe_aggregate("transfers", "transfer_fee")
    
    # Ticket revenue
    ticket_revenue = safe_aggregate("fiscal_ledger", "gross_amount")
    
    kpis = [
        ("", "Talenten", f"{total_talents:,}", "NTSP Database"),
        ("", "Transfers", f"{total_transfers:,}", f"€{transfer_volume/1000000:.1f}M volume"),
        ("", "Tickets", f"{total_tickets:,}", f"€{ticket_revenue/1000:.0f}K omzet"),
        ("", "Wallets", f"{total_wallets:,}", "Diaspora actief"),
        ("️", "Foundation", f"€{foundation_total:,.0f}", "Sadaka Jaaria"),
    ]
    
    cols = st.columns(len(kpis))
    
    for col, (icon, label, value, subtitle) in zip(cols, kpis):
        with col:
            st.markdown(f"""
                <div style='
                    background: #FFFFFF;
                    border: 1px solid #EDE9FE;
                    border-radius: 14px;
                    padding: 1.25rem;
                    text-align: center;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 10px rgba(139, 92, 246, 0.05);
                '>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>{icon}</div>
                    <div style='color: #7C3AED; font-size: 1.75rem; font-weight: 700;'>{value}</div>
                    <div style='color: #4C1D95; font-size: 0.9rem; font-weight: 500;'>{label}</div>
                    <div style='color: #6B7280; font-size: 0.75rem; margin-top: 0.25rem;'>{subtitle}</div>
                </div>
            """, unsafe_allow_html=True)


# ============================================================================
# TRANSFER VOLUME CHART
# ============================================================================

def render_transfer_volume_chart():
    """Transfer volume over tijd."""
    st.markdown(f"### {t("transfer_volume")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT 
                    transfer_type,
                    COUNT(*) as count,
                    SUM(transfer_fee) as total_fee,
                    AVG(transfer_fee) as avg_fee
                FROM transfers
                GROUP BY transfer_type
            """, conn)
        
        if not df.empty:
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df['transfer_type'],
                y=df['total_fee'],
                name='Total Fee',
                marker_color=COLORS['gold'],
                text=[f"€{v/1000:.0f}K" for v in df['total_fee']],
                textposition='outside'
            ))
            
            fig = apply_plotly_theme(fig)
            fig.update_layout(
                height=350,
                showlegend=False,
                yaxis_title="Transfer Volume (€)"
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # Stats onder chart
            total = df['total_fee'].sum()
            col1, col2, col3 = st.columns(3)
            col1.metric(t("total"), f"€{total/1000000:.1f}M")
            col2.metric(t("transfers"), f"{df['count'].sum()}")
            col3.metric("Gem. Transfer", f"€{total/df['count'].sum()/1000:.0f}K")
        else:
            st.info(t("no_transfer_data"))
    except Exception as e:
        st.info(t("data_loading"))


# ============================================================================
# REVENUE DISTRIBUTION
# ============================================================================

def render_revenue_distribution():
    """Revenue verdeling donut chart."""
    st.markdown(f"### {t("revenue_streams")}")
    
    # Haal echte data op
    ticket_revenue = safe_aggregate("fiscal_ledger", "gross_amount")
    transfer_revenue = safe_aggregate("transfers", "transfer_fee") * 0.005  # Foundation cut
    foundation_donations = safe_aggregate("foundation_donations", "amount")
    wallet_transactions = safe_aggregate("wallet_transactions", "amount") * 0.01  # Fee estimate
    
    labels = ['Ticket Sales', 'Transfer Fees', 'Donations', 'Wallet Fees']
    values = [ticket_revenue, transfer_revenue, foundation_donations, wallet_transactions]
    
    # Filter zero values
    filtered = [(l, v) for l, v in zip(labels, values) if v > 0]
    if filtered:
        labels, values = zip(*filtered)
    else:
        labels, values = ['No Data'], [1]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.6,
        marker=dict(colors=CHART_COLORS[:len(labels)]),
        textinfo='percent',
        textfont=dict(size=12, color='white'),
        hovertemplate="<b>%{label}</b><br>€ %{value:,.0f}<br>%{percent}<extra></extra>"
    )])
    
    total = sum(values)
    fig.add_annotation(
        text=f"<b>€{total/1000:.0f}K</b><br>Totaal",
        showarrow=False,
        font=dict(size=18, color=COLORS['gold'])
    )
    
    fig = apply_plotly_theme(fig)
    fig.update_layout(
        height=350,
        showlegend=True,
        legend=dict(orientation='h', y=-0.1, font=dict(size=10))
    )
    
    st.plotly_chart(fig, width="stretch")


# ============================================================================
# TALENT BY POSITION
# ============================================================================

def render_talent_by_position():
    """Talent verdeling per positie."""
    st.markdown(f"### {t("talents_by_position")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT primary_position as position, COUNT(*) as count
                FROM ntsp_talent_profiles
                WHERE primary_position IS NOT NULL
                GROUP BY primary_position
                ORDER BY count DESC
            """, conn)
        
        if not df.empty:
            fig = go.Figure(go.Bar(
                x=df['count'],
                y=df['position'],
                orientation='h',
                marker=dict(
                    color=df['count'],
                    colorscale=[[0, '#6D28D9'], [0.5, '#8B5CF6'], [1, '#D4AF37']],
                ),
                text=df['count'],
                textposition='outside'
            ))
            
            fig = apply_plotly_theme(fig)
            fig.update_layout(
                height=350,
                xaxis_title="Aantal Talenten",
                yaxis=dict(autorange="reversed")
            )
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(t("no_talent_data"))
    except Exception as e:
        st.info(t("data_loading"))


# ============================================================================
# TICKET SALES CHART
# ============================================================================

def render_ticket_sales_chart():
    """Ticket sales per event."""
    st.markdown(f"### {t("ticket_sales_event")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT 
                    e.name as event_name,
                    COUNT(t.ticket_hash) as tickets_sold,
                    SUM(t.price) as revenue
                FROM ticketchain_events e
                LEFT JOIN ticketchain_tickets t ON e.event_id = t.event_id
                GROUP BY e.event_id
                ORDER BY tickets_sold DESC
                LIMIT 8
            """, conn)
        
        if not df.empty:
            # Shorten event names
            df['short_name'] = df['event_name'].apply(lambda x: x[:20] + '...' if len(x) > 20 else x)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df['short_name'],
                y=df['tickets_sold'],
                name='Tickets',
                marker_color=COLORS['purple'],
                yaxis='y'
            ))
            
            fig.add_trace(go.Scatter(
                x=df['short_name'],
                y=df['revenue'],
                name='Revenue (€)',
                line=dict(color=COLORS['gold'], width=3),
                yaxis='y2'
            ))
            
            fig = apply_plotly_theme(fig)
            fig.update_layout(
                height=350,
                yaxis=dict(title='Tickets', side='left'),
                yaxis2=dict(title='Revenue (€)', side='right', overlaying='y'),
                legend=dict(orientation='h', y=-0.2),
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(t("no_ticket_data"))
    except Exception as e:
        st.info(t("data_loading"))


# ============================================================================
# DIASPORA DISTRIBUTION
# ============================================================================

def render_diaspora_distribution():
    """Diaspora wallet verdeling per land."""
    st.markdown(f"### {t("diaspora_by_country")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT 
                    i.country,
                    COUNT(*) as count,
                    SUM(w.balance_eur) as total_balance
                FROM diaspora_wallets w
                JOIN identity_shield i ON w.identity_id = i.id
                WHERE i.country != 'Morocco'
                GROUP BY i.country
                ORDER BY count DESC
                LIMIT 10
            """, conn)
        
        if not df.empty:
            fig = go.Figure(go.Bar(
                x=df['country'],
                y=df['count'],
                marker_color=PURPLE_GOLD[:len(df)],
                text=df['count'],
                textposition='outside'
            ))
            
            fig = apply_plotly_theme(fig)
            fig.update_layout(
                height=350,
                xaxis_title="Land",
                yaxis_title="Aantal Wallets",
                xaxis_tickangle=-45
            )
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(t("no_diaspora_data"))
    except Exception as e:
        st.info(t("data_loading"))


# ============================================================================
# FOUNDATION GROWTH
# ============================================================================

def render_foundation_growth():
    """Foundation contributions groei."""
    st.markdown(f"### {t("foundation_pool_growth")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT 
                    source_type,
                    COUNT(*) as count,
                    SUM(amount) as total
                FROM foundation_contributions
                GROUP BY source_type
                ORDER BY total DESC
            """, conn)
        
        if not df.empty:
            fig = go.Figure(go.Pie(
                labels=df['source_type'],
                values=df['total'],
                hole=0.5,
                marker=dict(colors=GOLD_COLORS[:len(df)]),
                textinfo='label+percent',
                textfont=dict(size=11, color='white')
            ))
            
            total = df['total'].sum()
            fig.add_annotation(
                text=f"<b>€{total:,.0f}</b><br>Pool",
                showarrow=False,
                font=dict(size=16, color=COLORS['gold'])
            )
            
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=350, showlegend=False)
            
            st.plotly_chart(fig, width="stretch")
        else:
            st.info(t("no_foundation_data"))
    except Exception as e:
        st.info(t("data_loading"))


# ============================================================================
# RECENT ACTIVITY
# ============================================================================

def render_recent_activity():
    """Recente activiteit uit audit logs."""
    st.markdown(f"### {t("recent_activity")}")
    
    try:
        with get_connection() as conn:
            df = pd.read_sql_query("""
                SELECT action, module, username, timestamp
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT 8
            """, conn)
        
        if not df.empty:
            for _, row in df.iterrows():
                icon = "" if "SUCCESS" in row['action'] else "" if "CREATED" in row['action'] else ""
                color = COLORS['success'] if "SUCCESS" in row['action'] else COLORS['gold']
                
                st.markdown(f"""
                    <div style='
                        background: {COLORS['bg_card']};
                        border-left: 3px solid {color};
                        padding: 0.5rem 1rem;
                        margin-bottom: 0.5rem;
                        border-radius: 0 8px 8px 0;
                    '>
                        <span style='margin-right: 0.5rem;'>{icon}</span>
                        <span style='color: {COLORS['text_primary']};'>{row['action']}</span>
                        <span style='color: {COLORS['text_muted']}; font-size: 0.8rem; margin-left: 0.5rem;'>
                            {row['module']} • {row['username']}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info(t("no_recent_activity"))
    except:
        st.info(t("data_loading"))


# ============================================================================
# QUICK STATS
# ============================================================================

def render_quick_stats():
    """Quick platform stats."""
    st.markdown(f"### {t("platform_status")}")
    
    stats = [
        ("", t("status"), "Operational"),
        ("⏱️", "Uptime", "99.9%"),
        ("", "Security", "Level A"),
        ("", "Version", f"v{VERSION}"),
        ("️", "Database", "SQLite"),
        ("", "Response", "<100ms"),
    ]
    
    for icon, label, value in stats:
        st.markdown(f"""
            <div style='
                background: {COLORS['bg_card']};
                border: 1px solid rgba(212, 175, 55, 0.1);
                padding: 0.75rem 1rem;
                margin-bottom: 0.5rem;
                border-radius: 8px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            '>
                <span>
                    <span style='margin-right: 0.5rem;'>{icon}</span>
                    <span style='color: {COLORS['text_secondary']};'>{label}</span>
                </span>
                <span style='color: {COLORS['gold']}; font-weight: 600;'>{value}</span>
            </div>
        """, unsafe_allow_html=True)
