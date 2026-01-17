# ============================================================================
# ANALYTICS DASHBOARD MODULE - DAY 3 UPGRADE
# Strategische intelligence en rapportage met interactieve Plotly charts
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from config import ALLOWED_TABLES
from database.connection import get_data, get_connection
from ui.styles import COLORS, premium_header
from ui.components import metric_row, page_header

# Chart colors
CHART_COLORS = ['#D4AF37', '#8B5CF6', '#48BB78', '#4299E1', '#ECC94B', '#F56565', '#ED64A6', '#38B2AC']
GOLD_GRADIENT = ['#D4AF37', '#F4E5B2', '#9B7B2E', '#B8860B', '#FFD700']


def apply_plotly_theme(fig):
    """Apply premium theme."""
    fig.update_layout(
        paper_bgcolor='#FAF9FF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#1F2937', family='Inter'),
        title_font=dict(size=16, color='#D4AF37'),
        legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor='rgba(212, 175, 55, 0.1)', linecolor='rgba(212, 175, 55, 0.3)', tickfont=dict(color='#6B7280')),
        yaxis=dict(gridcolor='rgba(212, 175, 55, 0.1)', linecolor='rgba(212, 175, 55, 0.3)', tickfont=dict(color='#6B7280')),
        margin=dict(l=40, r=40, t=50, b=40),
        hoverlabel=dict(bgcolor='#FFFFFF', font_size=12)
    )
    return fig


def render():
    """Render de Analytics Dashboard module."""
    
    premium_header(
        "Analytics Center",
        "Strategic Intelligence • Real-time Analytics • Performance Metrics",
        ""
    )
    
    tab1, tab2, tab3, tab4 = st.tabs([
        " TicketChain", 
        " Financial", 
        " Talent",
        "️ Security"
    ])
    
    with tab1:
        render_ticketchain_analytics()
    
    with tab2:
        render_financial_analytics()
    
    with tab3:
        render_talent_analytics()
    
    with tab4:
        render_security_analytics()


# ============================================================================
# TICKETCHAIN ANALYTICS
# ============================================================================

def render_ticketchain_analytics():
    """Render TicketChain analytics met Plotly."""
    
    st.markdown("###  TicketChain Performance")
    
    df_events = get_data("ticketchain_events")
    df_tickets = get_data("ticketchain_tickets")
    df_fiscal = get_data("fiscal_ledger")
    
    if df_tickets.empty:
        st.info("Geen ticket data beschikbaar.")
        return
    
    # KPIs
    total_tickets = len(df_tickets)
    total_revenue = df_fiscal['gross_amount'].sum() if not df_fiscal.empty else 0
    total_tax = df_fiscal['tax_amount'].sum() if not df_fiscal.empty else 0
    total_foundation = df_fiscal['foundation_amount'].sum() if not df_fiscal.empty and 'foundation_amount' in df_fiscal.columns else 0
    avg_ticket = df_tickets['price'].mean() if 'price' in df_tickets.columns else 0
    
    cols = st.columns(5)
    kpis = [
        ("️", "Tickets", f"{total_tickets:,}"),
        ("", "Revenue", f"€{total_revenue:,.0f}"),
        ("️", "Tax", f"€{total_tax:,.0f}"),
        ("", "Foundation", f"€{total_foundation:,.0f}"),
        ("", "Avg Price", f"€{avg_ticket:,.0f}"),
    ]
    for col, (icon, label, value) in zip(cols, kpis):
        with col:
            st.markdown(f"""
                <div style='background:{COLORS["bg_card"]}; border:1px solid rgba(212,175,55,0.2); border-radius:10px; padding:1rem; text-align:center;'>
                    <div style='font-size:1.5rem;'>{icon}</div>
                    <div style='color:{COLORS["gold"]}; font-size:1.25rem; font-weight:700;'>{value}</div>
                    <div style='color:{COLORS["text_muted"]}; font-size:0.8rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if PLOTLY_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Sales by Event")
            if not df_events.empty:
                fig = go.Figure(go.Bar(
                    x=df_events['name'].str[:25],
                    y=df_events['tickets_sold'],
                    marker_color=CHART_COLORS[:len(df_events)],
                    text=df_events['tickets_sold'],
                    textposition='outside'
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("####  Revenue Distribution")
            if not df_fiscal.empty:
                labels = ['Net Revenue', 'Tax (15%)', 'Foundation (0.5%)']
                net = df_fiscal['net_amount'].sum() if 'net_amount' in df_fiscal.columns else total_revenue * 0.845
                values = [net, total_tax, total_foundation]
                
                fig = go.Figure(go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.5,
                    marker=dict(colors=['#48BB78', '#ECC94B', '#D4AF37']),
                    textinfo='percent',
                    textfont=dict(color='white')
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350)
                st.plotly_chart(fig, width="stretch")
        
        # Event fill rate
        st.markdown("#### ️ Stadium Fill Rate")
        if not df_events.empty:
            df_events['fill_rate'] = (df_events['tickets_sold'] / df_events['capacity'] * 100).round(1)
            
            fig = go.Figure(go.Bar(
                x=df_events['name'].str[:20],
                y=df_events['fill_rate'],
                marker=dict(
                    color=df_events['fill_rate'],
                    colorscale=[[0, '#F56565'], [0.5, '#ECC94B'], [1, '#48BB78']],
                    showscale=True,
                    colorbar=dict(title='%')
                ),
                text=[f"{v}%" for v in df_events['fill_rate']],
                textposition='outside'
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=300, yaxis_title="Fill Rate (%)", xaxis_tickangle=-45)
            st.plotly_chart(fig, width="stretch")


# ============================================================================
# FINANCIAL ANALYTICS
# ============================================================================

def render_financial_analytics():
    """Render financial analytics met Plotly."""
    
    st.markdown("###  Financial Performance")
    
    df_financial = get_data("financial_records")
    df_donations = get_data("foundation_donations")
    df_contributions = get_data("foundation_contributions")
    df_wallets = get_data("diaspora_wallets")
    df_transactions = get_data("wallet_transactions")
    
    # Calculate totals
    total_transactions = df_financial['amount'].sum() if not df_financial.empty else 0
    total_donations = df_donations['amount'].sum() if not df_donations.empty else 0
    total_auto = df_contributions['amount'].sum() if not df_contributions.empty else 0
    total_wallet_balance = df_wallets['balance_eur'].sum() if not df_wallets.empty and 'balance_eur' in df_wallets.columns else 0
    
    cols = st.columns(4)
    kpis = [
        ("", "Financial Flow", f"€{total_transactions:,.0f}"),
        ("️", "Donations", f"€{total_donations:,.0f}"),
        ("", "Auto 0.5%", f"€{total_auto:,.0f}"),
        ("", "Wallet Balance", f"€{total_wallet_balance:,.0f}"),
    ]
    for col, (icon, label, value) in zip(cols, kpis):
        with col:
            st.markdown(f"""
                <div style='background:{COLORS["bg_card"]}; border:1px solid rgba(212,175,55,0.2); border-radius:10px; padding:1rem; text-align:center;'>
                    <div style='font-size:1.5rem;'>{icon}</div>
                    <div style='color:{COLORS["gold"]}; font-size:1.25rem; font-weight:700;'>{value}</div>
                    <div style='color:{COLORS["text_muted"]}; font-size:0.8rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if PLOTLY_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Capital by Sector")
            if not df_financial.empty:
                sector_data = df_financial.groupby("sector")["amount"].sum().reset_index()
                fig = go.Figure(go.Bar(
                    x=sector_data['sector'],
                    y=sector_data['amount'],
                    marker_color=CHART_COLORS[:len(sector_data)],
                    text=[f"€{v/1000:.0f}K" for v in sector_data['amount']],
                    textposition='outside'
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("####  Foundation Sources")
            if not df_contributions.empty:
                source_data = df_contributions.groupby("source_type")["amount"].sum().reset_index()
                fig = go.Figure(go.Pie(
                    labels=source_data['source_type'],
                    values=source_data['amount'],
                    hole=0.5,
                    marker=dict(colors=GOLD_GRADIENT[:len(source_data)]),
                    textinfo='label+percent'
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, width="stretch")
        
        # Wallet transactions
        st.markdown("####  Wallet Transaction Volume")
        if not df_transactions.empty:
            tx_data = df_transactions.groupby("transaction_type")["amount"].agg(['sum', 'count']).reset_index()
            tx_data.columns = ['type', 'total', 'count']
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(go.Bar(name='Volume (€)', x=tx_data['type'], y=tx_data['total'], marker_color=COLORS['gold']), secondary_y=False)
            fig.add_trace(go.Scatter(name='Count', x=tx_data['type'], y=tx_data['count'], mode='lines+markers', line=dict(color=COLORS['purple'], width=3)), secondary_y=True)
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=300, legend=dict(orientation='h', y=-0.2))
            fig.update_yaxes(title_text="Volume (€)", secondary_y=False)
            fig.update_yaxes(title_text="Count", secondary_y=True)
            st.plotly_chart(fig, width="stretch")


# ============================================================================
# TALENT ANALYTICS
# ============================================================================

def render_talent_analytics():
    """Render talent analytics."""
    
    st.markdown("###  Talent Intelligence")
    
    df_talents = get_data("ntsp_talent_profiles")
    df_evaluations = get_data("ntsp_evaluations")
    df_transfers = get_data("transfers")
    
    if df_talents.empty:
        st.info("Geen talent data beschikbaar.")
        return
    
    # KPIs
    total_talents = len(df_talents)
    diaspora = len(df_talents[df_talents['is_diaspora'] == 1]) if 'is_diaspora' in df_talents.columns else 0
    avg_score = df_talents['overall_score'].mean() if 'overall_score' in df_talents.columns else 0
    avg_potential = df_talents['potential_score'].mean() if 'potential_score' in df_talents.columns else 0
    total_market = df_talents['market_value_estimate'].sum() if 'market_value_estimate' in df_talents.columns else 0
    
    cols = st.columns(5)
    kpis = [
        ("", "Talenten", f"{total_talents:,}"),
        ("", "Diaspora", f"{diaspora:,}"),
        ("⭐", "Avg Score", f"{avg_score:.1f}"),
        ("", "Avg Potential", f"{avg_potential:.1f}"),
        ("", "Market Value", f"€{total_market/1000000:.1f}M"),
    ]
    for col, (icon, label, value) in zip(cols, kpis):
        with col:
            st.markdown(f"""
                <div style='background:{COLORS["bg_card"]}; border:1px solid rgba(212,175,55,0.2); border-radius:10px; padding:1rem; text-align:center;'>
                    <div style='font-size:1.5rem;'>{icon}</div>
                    <div style='color:{COLORS["gold"]}; font-size:1.25rem; font-weight:700;'>{value}</div>
                    <div style='color:{COLORS["text_muted"]}; font-size:0.8rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if PLOTLY_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Score Distribution")
            if 'overall_score' in df_talents.columns:
                fig = go.Figure(go.Histogram(
                    x=df_talents['overall_score'],
                    nbinsx=20,
                    marker_color=COLORS['gold'],
                    opacity=0.8
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=300, xaxis_title="Score", yaxis_title="Count")
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("####  Status Breakdown")
            if 'talent_status' in df_talents.columns:
                status_data = df_talents['talent_status'].value_counts().reset_index()
                status_data.columns = ['status', 'count']
                
                fig = go.Figure(go.Pie(
                    labels=status_data['status'],
                    values=status_data['count'],
                    hole=0.5,
                    marker=dict(colors=CHART_COLORS[:len(status_data)]),
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=300)
                st.plotly_chart(fig, width="stretch")
        
        # Position analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  By Position")
            if 'primary_position' in df_talents.columns:
                pos_data = df_talents['primary_position'].value_counts().reset_index()
                pos_data.columns = ['position', 'count']
                
                fig = go.Figure(go.Bar(
                    y=pos_data['position'],
                    x=pos_data['count'],
                    orientation='h',
                    marker_color=CHART_COLORS[:len(pos_data)],
                    text=pos_data['count'],
                    textposition='outside'
                ))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, yaxis=dict(autorange="reversed"))
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("####  Local vs Diaspora")
            if 'is_diaspora' in df_talents.columns:
                local = len(df_talents[df_talents['is_diaspora'] == 0])
                diaspora_count = len(df_talents[df_talents['is_diaspora'] == 1])
                
                fig = go.Figure(go.Pie(
                    labels=['Local', 'Diaspora'],
                    values=[local, diaspora_count],
                    hole=0.6,
                    marker=dict(colors=[COLORS['purple'], COLORS['gold']]),
                    textinfo='label+percent'
                ))
                fig.add_annotation(text=f"<b>{total_talents}</b><br>Total", showarrow=False, font=dict(size=16, color=COLORS['gold']))
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, showlegend=False)
                st.plotly_chart(fig, width="stretch")


# ============================================================================
# SECURITY ANALYTICS
# ============================================================================

def render_security_analytics():
    """Render security analytics."""
    
    st.markdown("### ️ Security & Compliance")
    
    df_audit = get_data("audit_logs")
    df_identity = get_data("identity_shield")
    
    if df_audit.empty:
        st.info("Geen audit data beschikbaar.")
        return
    
    # KPIs
    total_actions = len(df_audit)
    success = len(df_audit[df_audit['success'] == 1]) if 'success' in df_audit.columns else 0
    failed = total_actions - success
    success_rate = (success / total_actions * 100) if total_actions > 0 else 0
    
    # Identity stats
    total_ids = len(df_identity) if not df_identity.empty else 0
    high_risk = len(df_identity[df_identity['risk_level'] == 'HIGH']) if not df_identity.empty and 'risk_level' in df_identity.columns else 0
    
    cols = st.columns(5)
    kpis = [
        ("", "Total Actions", f"{total_actions:,}"),
        ("", "Successful", f"{success:,}"),
        ("", "Failed", f"{failed:,}"),
        ("", "Success Rate", f"{success_rate:.1f}%"),
        ("", "High Risk IDs", f"{high_risk}"),
    ]
    for col, (icon, label, value) in zip(cols, kpis):
        with col:
            st.markdown(f"""
                <div style='background:{COLORS["bg_card"]}; border:1px solid rgba(212,175,55,0.2); border-radius:10px; padding:1rem; text-align:center;'>
                    <div style='font-size:1.5rem;'>{icon}</div>
                    <div style='color:{COLORS["gold"]}; font-size:1.25rem; font-weight:700;'>{value}</div>
                    <div style='color:{COLORS["text_muted"]}; font-size:0.8rem;'>{label}</div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if PLOTLY_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Activity by User")
            user_data = df_audit['username'].value_counts().head(10).reset_index()
            user_data.columns = ['user', 'actions']
            
            fig = go.Figure(go.Bar(
                x=user_data['user'],
                y=user_data['actions'],
                marker_color=CHART_COLORS[:len(user_data)],
                text=user_data['actions'],
                textposition='outside'
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            st.markdown("####  Activity by Module")
            module_data = df_audit['module'].value_counts().reset_index()
            module_data.columns = ['module', 'count']
            
            fig = go.Figure(go.Pie(
                labels=module_data['module'],
                values=module_data['count'],
                hole=0.5,
                marker=dict(colors=CHART_COLORS[:len(module_data)]),
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=300)
            st.plotly_chart(fig, width="stretch")
        
        # Risk distribution
        if not df_identity.empty and 'risk_level' in df_identity.columns:
            st.markdown("####  Identity Risk Distribution")
            risk_data = df_identity['risk_level'].value_counts().reset_index()
            risk_data.columns = ['risk', 'count']
            
            color_map = {'LOW': '#48BB78', 'MEDIUM': '#ECC94B', 'HIGH': '#F56565'}
            colors = [color_map.get(r, '#A0AEC0') for r in risk_data['risk']]
            
            fig = go.Figure(go.Bar(
                x=risk_data['risk'],
                y=risk_data['count'],
                marker_color=colors,
                text=risk_data['count'],
                textposition='outside'
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=250, xaxis_title="Risk Level", yaxis_title="Count")
            st.plotly_chart(fig, width="stretch")
