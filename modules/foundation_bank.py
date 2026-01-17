# ============================================================================
# FOUNDATION BANK MODULE - DAY 4 PREMIUM UPGRADE
# صدقة جارية - Sadaka Jaaria - Continuous Charity
# ============================================================================

import streamlit as st
from datetime import datetime
import pandas as pd

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

from config import Options, FOUNDATION_RATE
from database.connection import get_data, run_query, aggregate_sum, count_records
from utils.helpers import get_identity_names_map, generate_uuid
from auth.security import log_audit
from ui.styles import COLORS, premium_header
from ui.components import (
    metric_row, page_header, data_table_with_empty_state,
    premium_kpi_row, form_section, success_message, info_box
)


def apply_plotly_theme(fig):
    """Apply premium theme to Plotly figure."""
    fig.update_layout(
        paper_bgcolor='#FAF9FF',
        plot_bgcolor='#FFFFFF',
        font=dict(color='#1F2937', family='Inter'),
        title_font=dict(size=16, color='#D4AF37'),
        legend=dict(font=dict(size=11), bgcolor='rgba(0,0,0,0)'),
        xaxis=dict(gridcolor='rgba(212, 175, 55, 0.1)', linecolor='rgba(212, 175, 55, 0.3)'),
        yaxis=dict(gridcolor='rgba(212, 175, 55, 0.1)', linecolor='rgba(212, 175, 55, 0.3)'),
        margin=dict(l=40, r=40, t=50, b=40)
    )
    return fig


def render(username: str):
    """Render de Foundation Bank module."""
    
    # Premium header met Sadaka Jaaria branding
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
            border: 1px solid rgba(212, 175, 55, 0.3);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            text-align: center;
        '>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'></div>
            <h1 style='
                font-family: Rajdhani, sans-serif;
                font-size: 2rem;
                color: {COLORS["gold"]};
                margin: 0;
            '>Foundation Bank</h1>
            <p style='
                color: {COLORS["text_secondary"]};
                font-size: 1rem;
                margin: 0.5rem 0;
            '>Capital Management | Investment Tracking | Portfolio</p>
            <div style='
                background: rgba(212, 175, 55, 0.1);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: 8px;
                padding: 0.75rem 1.5rem;
                display: inline-block;
                margin-top: 1rem;
            '>
                <span style='color: {COLORS["gold"]}; font-size: 1.25rem;'>صدقة جارية</span>
                <span style='color: {COLORS["text_muted"]}; margin-left: 0.5rem;'>Sadaka Jaaria - Continuous Charity</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Render summary KPIs
    render_foundation_summary()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        t("overview"), 
        " Transactions", 
        " Donations", 
        " Analytics"
    ])
    
    with tab1:
        render_overview()
    
    with tab2:
        render_transactions(username)
    
    with tab3:
        render_donations(username)
    
    with tab4:
        render_analytics()


def render_foundation_summary():
    """Render foundation summary KPIs."""
    
    # Get totals from different sources
    contributions = aggregate_sum("foundation_contributions", "amount") or 0
    donations = aggregate_sum("foundation_donations", "amount") or 0
    transactions = aggregate_sum("financial_records", "amount") or 0
    
    total_pool = contributions + donations
    
    kpis = [
        ("", "Foundation Pool", f"€{total_pool:,.0f}", "Auto 0.5% + Donations"),
        ("", "Auto Contributions", f"€{contributions:,.0f}", f"{FOUNDATION_RATE*100}% from transactions"),
        ("", "Donations", f"€{donations:,.0f}", "Direct charitable giving"),
        ("", "Financial Flow", f"€{transactions:,.0f}", "Total platform volume"),
    ]
    
    premium_kpi_row(kpis)


def render_overview():
    """Render overview tab with visualizations."""
    
    st.markdown("###  Foundation Overview")
    
    # Info box about the foundation
    info_box(
        "The ProInvestiX Foundation",
        """The Foundation automatically receives 0.5% of all platform transactions (transfers, tickets, subscriptions). 
        This "Sadaka Jaaria" (continuous charity) model ensures sustainable funding for youth sports, 
        education, and infrastructure projects across Morocco.""",
        ""
    )
    
    if PLOTLY_AVAILABLE:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("####  Contribution Sources")
            df_contrib = get_data("foundation_contributions")
            
            if not df_contrib.empty:
                source_data = df_contrib.groupby("source_type")["amount"].sum().reset_index()
                
                fig = go.Figure(go.Pie(
                    labels=source_data['source_type'],
                    values=source_data['amount'],
                    hole=0.6,
                    marker=dict(colors=['#D4AF37', '#8B5CF6', '#48BB78', '#4299E1', '#ECC94B']),
                    textinfo='percent',
                    textfont=dict(color='white')
                ))
                
                total = source_data['amount'].sum()
                fig.add_annotation(
                    text=f"<b>€{total/1000:.0f}K</b><br>Total",
                    showarrow=False,
                    font=dict(size=16, color=COLORS['gold'])
                )
                
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, showlegend=True, legend=dict(orientation='h', y=-0.1))
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No contribution data yet.")
        
        with col2:
            st.markdown("####  Monthly Growth")
            df_contrib = get_data("foundation_contributions")
            
            if not df_contrib.empty and 'timestamp' in df_contrib.columns:
                df_contrib['month'] = pd.to_datetime(df_contrib['timestamp']).dt.to_period('M').astype(str)
                monthly = df_contrib.groupby('month')['amount'].sum().reset_index()
                monthly = monthly.tail(12)  # Last 12 months
                
                fig = go.Figure(go.Bar(
                    x=monthly['month'],
                    y=monthly['amount'],
                    marker_color=COLORS['gold'],
                    text=[f"€{v/1000:.0f}K" for v in monthly['amount']],
                    textposition='outside'
                ))
                
                fig = apply_plotly_theme(fig)
                fig.update_layout(height=350, xaxis_tickangle=-45)
                st.plotly_chart(fig, width="stretch")
            else:
                st.info("No monthly data available.")
    
    # Recent contributions
    st.markdown("####  Recent Contributions")
    df_recent = get_data("foundation_contributions")
    
    if not df_recent.empty:
        df_recent = df_recent.sort_values('timestamp', ascending=False).head(10)
        display_df = df_recent[['contribution_id', 'source_type', 'amount', 'timestamp']].copy()
        display_df['amount'] = display_df['amount'].apply(lambda x: f"€ {x:,.2f}")
        st.dataframe(display_df, width="stretch", hide_index=True)
    else:
        st.info("No contributions yet.")


def render_transactions(username: str):
    """Render transactions tab."""
    
    form_section("Log New Transaction", "")
    
    id_map = get_identity_names_map()
    
    with st.form("fin_reg"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if id_map:
                entity_id = st.selectbox(
                    "Linked Entity *", 
                    list(id_map.keys()), 
                    format_func=lambda x: id_map.get(x, x)
                )
            else:
                st.warning("No identities registered yet.")
                entity_id = None
            
            amount = st.number_input("Amount (€) *", min_value=0.0, step=1000.0)
        
        with col2:
            sector = st.selectbox("Sector *", Options.SECTORS)
            tx_type = st.selectbox("Type *", Options.TRANSACTION_TYPES)
        
        with col3:
            # Show foundation contribution preview
            foundation_amount = amount * FOUNDATION_RATE
            st.markdown(f"""
                <div style='
                    background: rgba(212, 175, 55, 0.1);
                    border: 1px solid rgba(212, 175, 55, 0.3);
                    border-radius: 8px;
                    padding: 1rem;
                    margin-top: 1.5rem;
                '>
                    <div style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>Foundation (0.5%)</div>
                    <div style='color: {COLORS["gold"]}; font-size: 1.5rem; font-weight: 700;'>€ {foundation_amount:,.2f}</div>
                    <div style='color: {COLORS["text_muted"]}; font-size: 0.75rem;'>صدقة جارية</div>
                </div>
            """, unsafe_allow_html=True)
        
        if st.form_submit_button(" LOG TRANSACTION", width="stretch", type="primary"):
            if not entity_id:
                st.error(" Entity required.")
            elif amount <= 0:
                st.error(" Amount must be positive.")
            else:
                tx_id = generate_uuid("TX")
                
                # Log transaction
                success = run_query(
                    "INSERT INTO financial_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (tx_id, entity_id, amount, tx_type, sector, "Approved", 
                     datetime.now().isoformat())
                )
                
                # Auto-contribute to foundation
                if success:
                    contrib_id = generate_uuid("FND")
                    run_query(
                        "INSERT INTO foundation_contributions VALUES (?, ?, ?, ?, ?, ?)",
                        (contrib_id, tx_id, "FINANCIAL", foundation_amount, 1, datetime.now().isoformat())
                    )
                    
                    success_message(
                        f"Transaction {tx_id} logged: € {amount:,.2f}",
                        f"Foundation contribution: € {foundation_amount:,.2f} (0.5%)"
                    )
                    log_audit(username, "TRANSACTION_LOGGED", "Foundation Bank", details=f"Amount: €{amount}")
                    st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Transaction list
    st.markdown("###  Transaction History")
    
    df = get_data("financial_records")
    
    if not df.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            filter_sector = st.selectbox("Filter by Sector", ["All"] + Options.SECTORS, key="tx_sector")
        with col2:
            filter_type = st.selectbox("Filter by Type", ["All"] + Options.TRANSACTION_TYPES, key="tx_type")
        
        filtered = df.copy()
        if filter_sector != "All":
            filtered = filtered[filtered['sector'] == filter_sector]
        if filter_type != "All":
            filtered = filtered[filtered['type'] == filter_type]
        
        if not filtered.empty:
            display_df = filtered.copy()
            display_df['amount'] = display_df['amount'].apply(lambda x: f"€ {x:,.2f}")
            st.dataframe(display_df, width="stretch", hide_index=True)
            
            # Summary
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Volume", f"€ {filtered['amount'].sum():,.0f}")
            col2.metric("Transactions", len(filtered))
            col3.metric("Avg Transaction", f"€ {filtered['amount'].mean():,.0f}")
    else:
        st.info("No transactions yet.")


def render_donations(username: str):
    """Render donations tab."""
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(245, 101, 101, 0.1) 0%, rgba(212, 175, 55, 0.1) 100%);
            border: 1px solid rgba(245, 101, 101, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            text-align: center;
        '>
            <div style='font-size: 2rem;'></div>
            <h3 style='color: {COLORS["text_primary"]}; margin: 0.5rem 0;'>Donation Portal</h3>
            <p style='color: {COLORS["text_muted"]}; font-size: 0.9rem;'>
                Support Moroccan youth sports, education, and community development
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    id_map = get_identity_names_map()
    
    form_section("Make a Donation", "")
    
    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            donor_options = ["Anonymous"] + list(id_map.keys())
            donor_id = st.selectbox(
                "Donor Identity", 
                donor_options,
                format_func=lambda x: " Anonymous Donor" if x == "Anonymous" else id_map.get(x, x)
            )
            donation_amt = st.number_input("Donation Amount (€) *", min_value=1.0, step=10.0, value=100.0)
        
        with col2:
            donation_type = st.selectbox("Donation Purpose *", Options.DONATION_TYPES)
            project = st.text_input("Specific Project (optional)", placeholder="e.g., Academy Equipment")
        
        anonymous = st.checkbox(" Make this donation anonymous", value=donor_id == "Anonymous")
        
        # Donation tiers
        st.markdown("####  Donation Recognition Tiers")
        cols = st.columns(4)
        tiers = [
            (" Bronze", "€10-99", "Certificate"),
            (" Silver", "€100-499", "+ Name on website"),
            (" Gold", "€500-999", "+ VIP event invite"),
            (" Diamond", "€1000+", "+ All benefits"),
        ]
        for col, (tier, amount, benefit) in zip(cols, tiers):
            with col:
                st.markdown(f"""
                    <div style='
                        background: {COLORS["bg_card"]};
                        border: 1px solid rgba(212, 175, 55, 0.2);
                        border-radius: 8px;
                        padding: 0.75rem;
                        text-align: center;
                        font-size: 0.85rem;
                    '>
                        <div style='font-size: 1.25rem;'>{tier.split()[0]}</div>
                        <div style='color: {COLORS["gold"]}; font-weight: 600;'>{amount}</div>
                        <div style='color: {COLORS["text_muted"]}; font-size: 0.75rem;'>{benefit}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.form_submit_button(" DONATE NOW", width="stretch", type="primary"):
            if donation_amt <= 0:
                st.error(" Amount must be positive.")
            else:
                donation_id = generate_uuid("DON")
                donor_val = None if donor_id == "Anonymous" or anonymous else donor_id
                
                success = run_query(
                    "INSERT INTO foundation_donations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (donation_id, donor_val, donation_amt, donation_type, project, 
                     1 if anonymous else 0, datetime.now().isoformat(), 0)
                )
                
                if success:
                    # Determine tier
                    if donation_amt >= 1000:
                        tier = " Diamond"
                    elif donation_amt >= 500:
                        tier = " Gold"
                    elif donation_amt >= 100:
                        tier = " Silver"
                    else:
                        tier = " Bronze"
                    
                    success_message(
                        f"Thank you for your donation of € {donation_amt:,.2f}!",
                        f"Recognition tier: {tier} • Tax receipt will be sent to registered email"
                    )
                    st.balloons()
                    log_audit(username, "DONATION_RECEIVED", "Foundation Bank")
                    st.rerun()
    
    # Recent donations
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("###  Recent Donations")
    
    df = get_data("foundation_donations")
    
    if not df.empty:
        df_display = df.sort_values('created_at', ascending=False).head(20).copy()
        df_display['donor'] = df_display['donor_identity_id'].apply(
            lambda x: " Anonymous" if pd.isna(x) else id_map.get(x, x[:15] + "...")
        )
        df_display['amount'] = df_display['amount'].apply(lambda x: f"€ {x:,.2f}")
        
        display_cols = ['donation_id', 'donor', 'amount', 'donation_type', 'created_at']
        st.dataframe(df_display[display_cols], width="stretch", hide_index=True)
        
        # Total donated
        total = df['amount'].sum()
        st.markdown(f"""
            <div style='text-align: center; padding: 1rem;'>
                <span style='color: {COLORS["text_muted"]};'>Total Donated:</span>
                <span style='color: {COLORS["gold"]}; font-size: 1.5rem; font-weight: 700; margin-left: 0.5rem;'>
                    € {total:,.2f}
                </span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.info("No donations yet. Be the first to contribute!")


def render_analytics():
    """Render analytics tab."""
    
    st.markdown("###  Foundation Analytics")
    
    if not PLOTLY_AVAILABLE:
        st.warning("Install Plotly for visualizations: `pip install plotly`")
        return
    
    df_contrib = get_data("foundation_contributions")
    df_donations = get_data("foundation_donations")
    df_financial = get_data("financial_records")
    
    # Combined metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_contrib = df_contrib['amount'].sum() if not df_contrib.empty else 0
        st.metric("Auto Contributions", f"€{total_contrib:,.0f}")
    
    with col2:
        total_donations = df_donations['amount'].sum() if not df_donations.empty else 0
        st.metric("Donations", f"€{total_donations:,.0f}")
    
    with col3:
        num_donors = len(df_donations[df_donations['donor_identity_id'].notna()]) if not df_donations.empty else 0
        st.metric("Unique Donors", num_donors)
    
    with col4:
        avg_donation = df_donations['amount'].mean() if not df_donations.empty else 0
        st.metric("Avg Donation", f"€{avg_donation:,.0f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("####  Revenue by Sector")
        if not df_financial.empty:
            sector_data = df_financial.groupby('sector')['amount'].sum().reset_index()
            
            fig = go.Figure(go.Bar(
                x=sector_data['sector'],
                y=sector_data['amount'],
                marker_color=['#D4AF37', '#8B5CF6', '#48BB78', '#4299E1', '#ECC94B', '#F56565'][:len(sector_data)],
                text=[f"€{v/1000:.0f}K" for v in sector_data['amount']],
                textposition='outside'
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=350, xaxis_tickangle=-45)
            st.plotly_chart(fig, width="stretch")
    
    with col2:
        st.markdown("####  Donation Types")
        if not df_donations.empty:
            type_data = df_donations.groupby('donation_type')['amount'].sum().reset_index()
            
            fig = go.Figure(go.Pie(
                labels=type_data['donation_type'],
                values=type_data['amount'],
                hole=0.5,
                marker=dict(colors=['#D4AF37', '#8B5CF6', '#48BB78', '#4299E1']),
            ))
            fig = apply_plotly_theme(fig)
            fig.update_layout(height=350)
            st.plotly_chart(fig, width="stretch")
    
    # Impact statement
    total_foundation = (df_contrib['amount'].sum() if not df_contrib.empty else 0) + \
                       (df_donations['amount'].sum() if not df_donations.empty else 0)
    
    st.markdown(f"""
        <div style='
            background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(72, 187, 120, 0.1) 100%);
            border: 1px solid rgba(212, 175, 55, 0.2);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin-top: 2rem;
        '>
            <div style='font-size: 2.5rem;'></div>
            <h3 style='color: {COLORS["gold"]}; margin: 0.5rem 0;'>Impact Statement</h3>
            <p style='color: {COLORS["text_secondary"]}; font-size: 1.1rem;'>
                The Foundation has raised <span style='color: {COLORS["gold"]}; font-weight: 700;'>€ {total_foundation:,.0f}</span>
                for Moroccan youth development.
            </p>
            <p style='color: {COLORS["text_muted"]}; font-size: 0.9rem; margin-top: 1rem;'>
                Every transaction on ProInvestiX automatically contributes 0.5% to this cause.<br>
                <em>صدقة جارية - Sadaka Jaaria</em>
            </p>
        </div>
    """, unsafe_allow_html=True)
