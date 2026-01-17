# ============================================================================
# DIASPORA WALLET™ MODULE (DOSSIER 9)
# Digitale portemonnee voor diaspora:
# - Fee-loze transacties tussen diaspora
# - Investeringen in Marokko
# - Loyalty cards
# - KYC verificatie
# ============================================================================

import streamlit as st
import hashlib
import hmac
from datetime import datetime, date, timedelta
from typing import Dict

from config import (
    Options, Messages, BLOCKCHAIN_SECRET, FOUNDATION_RATE, LoyaltyTiers
)
from database.connection import get_data, run_query, get_connection
from utils.helpers import generate_uuid, get_identity_names_map
from auth.security import log_audit
from ui.components import metric_row, page_header


def generate_wallet_address(identity_id: str) -> str:
    """Genereer uniek wallet adres."""
    message = f"WALLET|{identity_id}|{datetime.now().isoformat()}"
    return "0x" + hmac.new(BLOCKCHAIN_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()[:40]


def get_wallets_dropdown() -> Dict[str, str]:
    df = get_data("diaspora_wallets")
    if df.empty:
        return {}
    return {row['wallet_id']: f"{row['identity_id']} ({row['wallet_type']})" for _, row in df.iterrows()}


def process_transaction(wallet_id: str, amount: float, tx_type: str, description: str = None, 
                       counterparty_id: str = None, fee_waived: bool = False) -> bool:
    """Verwerk een wallet transactie."""
    tx_id = generate_uuid("WTX")
    
    # Fee berekening (0 voor diaspora onderling!)
    fee = 0 if fee_waived else amount * 0.01  # 1% fee voor niet-diaspora
    foundation = amount * FOUNDATION_RATE  # 0.5% altijd naar Foundation
    
    # Blockchain hash
    blockchain_hash = hmac.new(
        BLOCKCHAIN_SECRET.encode(),
        f"{tx_id}|{wallet_id}|{amount}|{tx_type}".encode(),
        hashlib.sha256
    ).hexdigest()
    
    success = run_query("""
        INSERT INTO wallet_transactions (
            transaction_id, wallet_id, transaction_type, amount, currency,
            fee, fee_waived, fee_waiver_reason, foundation_contribution,
            counterparty_wallet_id, description, status, blockchain_hash, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tx_id, wallet_id, tx_type, amount, "MAD",
        fee, 1 if fee_waived else 0, "Diaspora Transfer" if fee_waived else None, foundation,
        counterparty_id, description, "COMPLETED", blockchain_hash,
        datetime.now().isoformat()
    ))
    
    if success and foundation > 0:
        run_query("""
            INSERT INTO foundation_contributions (contribution_id, source_id, source_type, amount, auto_generated, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (generate_uuid("FND"), tx_id, "WALLET_TX", foundation, 1, datetime.now().isoformat()))
    
    return success


def render(username: str):
    """Render Diaspora Wallet module."""
    
    page_header(
        " Diaspora Wallet™",
        "Dossier 9 | Fee-loze transacties | Investeringen | Loyalty Cards"
    )
    
    tabs = st.tabs([
        " Mijn Wallet",
        " Nieuwe Wallet",
        " Transacties",
        " Investeringen",
        " Diaspora Card",
        " Analytics"
    ])
    
    with tabs[0]:
        render_wallet_overview(username)
    with tabs[1]:
        render_new_wallet(username)
    with tabs[2]:
        render_transactions(username)
    with tabs[3]:
        render_investments(username)
    with tabs[4]:
        render_diaspora_card(username)
    with tabs[5]:
        render_wallet_analytics()


def render_wallet_overview(username: str):
    """Render wallet overzicht."""
    
    st.subheader(" Wallet Overzicht")
    
    df = get_data("diaspora_wallets")
    
    if not df.empty:
        total_balance_mad = df['balance_mad'].sum()
        total_balance_eur = df['balance_eur'].sum()
        total_wallets = len(df)
        verified = len(df[df['kyc_status'] == 'VERIFIED'])
        
        metric_row([
            (" Wallets", total_wallets),
            (" MAD", f"{total_balance_mad:,.0f}"),
            (" EUR", f"{total_balance_eur:,.0f}"),
            (" Geverifieerd", verified),
        ])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        display_cols = ['wallet_id', 'identity_id', 'wallet_type', 'balance_mad', 'balance_eur', 'kyc_status', 'status']
        display_cols = [c for c in display_cols if c in df.columns]
        
        display_df = df[display_cols].copy()
        display_df['balance_mad'] = display_df['balance_mad'].apply(lambda x: f"{x:,.2f} MAD")
        display_df['balance_eur'] = display_df['balance_eur'].apply(lambda x: f"{x:,.2f} EUR")
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Wallet detail
        wallets = get_wallets_dropdown()
        if wallets:
            st.markdown("<br>", unsafe_allow_html=True)
            selected = st.selectbox("Selecteer wallet", list(wallets.keys()), format_func=lambda x: wallets.get(x, x))
            
            if selected:
                wallet = df[df['wallet_id'] == selected].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("####  Wallet Details")
                    st.write(f"**ID:** `{wallet['wallet_id']}`")
                    st.write(f"**Adres:** `{wallet.get('wallet_address', '-')}`")
                    st.write(f"**Type:** {wallet['wallet_type']}")
                    st.write(f"**KYC:** {wallet['kyc_status']}")
                
                with col2:
                    st.markdown("####  Balans")
                    st.metric("MAD", f"{wallet['balance_mad']:,.2f}")
                    st.metric("EUR", f"{wallet['balance_eur']:,.2f}")
                    st.metric("Loyalty Points", wallet.get('loyalty_points', 0))
    else:
        st.info(" Nog geen wallets. Maak een wallet aan.")


def render_new_wallet(username: str):
    """Render form voor nieuwe wallet."""
    
    st.subheader(" Nieuwe Diaspora Wallet")
    
    identities = get_identity_names_map()
    
    if not identities:
        st.warning(" Geen identiteiten. Registreer eerst in Identity Shield.")
        return
    
    # Check bestaande wallets
    df_wallets = get_data("diaspora_wallets")
    existing_ids = df_wallets['identity_id'].tolist() if not df_wallets.empty else []
    
    available_ids = {k: v for k, v in identities.items() if k not in existing_ids}
    
    if not available_ids:
        st.info("Alle geregistreerde identiteiten hebben al een wallet.")
        return
    
    with st.form("wallet_form"):
        identity_id = st.selectbox("Identiteit *", list(available_ids.keys()), format_func=lambda x: available_ids.get(x, x))
        wallet_type = st.selectbox("Wallet Type", Options.WALLET_TYPES)
        
        col1, col2 = st.columns(2)
        with col1:
            daily_limit = st.number_input("Dagelijks Limiet (MAD)", 1000.0, 100000.0, 10000.0, step=1000.0)
        with col2:
            monthly_limit = st.number_input("Maandelijks Limiet (MAD)", 10000.0, 500000.0, 50000.0, step=10000.0)
        
        initial_deposit = st.number_input("Initiële Storting (MAD)", 0.0, 100000.0, 0.0, step=100.0)
        
        st.info("**KYC Verificatie:** Na aanmaken moet je identiteitsdocumenten uploaden voor verificatie.")
        
        if st.form_submit_button(" WALLET AANMAKEN", use_container_width=True):
            wallet_id = generate_uuid("WLT")
            wallet_address = generate_wallet_address(identity_id)
            
            success = run_query("""
                INSERT INTO diaspora_wallets (
                    wallet_id, identity_id, wallet_address, wallet_type,
                    balance_mad, balance_eur, loyalty_points, loyalty_tier,
                    daily_limit, monthly_limit, kyc_status, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wallet_id, identity_id, wallet_address, wallet_type,
                initial_deposit, 0, 0, "BRONZE",
                daily_limit, monthly_limit, "PENDING", "ACTIVE",
                datetime.now().isoformat()
            ))
            
            if success:
                if initial_deposit > 0:
                    process_transaction(wallet_id, initial_deposit, "DEPOSIT", "Initiële storting", fee_waived=True)
                
                st.success(Messages.WALLET_CREATED.format(identity_id))
                st.code(f"Wallet Adres: {wallet_address}", language="text")
                log_audit(username, "WALLET_CREATED", "Diaspora Wallet")
                st.balloons()


def render_transactions(username: str):
    """Render transacties tab."""
    
    st.subheader(" Transacties")
    
    wallets = get_wallets_dropdown()
    
    if not wallets:
        st.warning("Geen wallets beschikbaar.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("###  Nieuwe Transactie")
        
        with st.form("tx_form"):
            from_wallet = st.selectbox("Van Wallet *", list(wallets.keys()), format_func=lambda x: wallets.get(x, x))
            tx_type = st.selectbox("Type", Options.TRANSACTION_TYPES_WALLET)
            amount = st.number_input("Bedrag (MAD) *", min_value=1.0, step=100.0)
            
            # Counterparty voor transfers
            to_wallet = None
            if tx_type in ["TRANSFER_OUT"]:
                to_wallet = st.selectbox("Naar Wallet", ["None"] + [w for w in wallets.keys() if w != from_wallet],
                                        format_func=lambda x: "Selecteer..." if x == "None" else wallets.get(x, x))
            
            description = st.text_input("Omschrijving", placeholder="Beschrijving transactie...")
            fee_waived = st.checkbox("Fee-vrij (diaspora onderling)", value=True)
            
            # Toon fees
            fee = 0 if fee_waived else amount * 0.01
            foundation = amount * FOUNDATION_RATE
            
            st.info(f"Fee: {fee:.2f} MAD | Foundation: {foundation:.2f} MAD")
            
            if st.form_submit_button(" UITVOEREN"):
                success = process_transaction(
                    from_wallet, amount, tx_type, description,
                    to_wallet if to_wallet != "None" else None, fee_waived
                )
                
                if success:
                    # Update balance
                    if tx_type in ["DEPOSIT", "TRANSFER_IN"]:
                        run_query("UPDATE diaspora_wallets SET balance_mad = balance_mad + ? WHERE wallet_id = ?", (amount, from_wallet))
                    elif tx_type in ["WITHDRAWAL", "TRANSFER_OUT", "PAYMENT"]:
                        run_query("UPDATE diaspora_wallets SET balance_mad = balance_mad - ? WHERE wallet_id = ?", (amount + fee, from_wallet))
                        
                        if to_wallet and to_wallet != "None":
                            run_query("UPDATE diaspora_wallets SET balance_mad = balance_mad + ? WHERE wallet_id = ?", (amount, to_wallet))
                    
                    st.success(" Transactie voltooid!")
                    log_audit(username, "WALLET_TX", "Diaspora Wallet", details=f"Amount: {amount} MAD")
    
    with col2:
        st.markdown("###  Transactie Geschiedenis")
        
        df = get_data("wallet_transactions")
        
        if not df.empty:
            display_cols = ['transaction_id', 'wallet_id', 'transaction_type', 'amount', 'fee', 'foundation_contribution', 'status', 'created_at']
            display_cols = [c for c in display_cols if c in df.columns]
            
            display_df = df[display_cols].head(20).copy()
            display_df['amount'] = display_df['amount'].apply(lambda x: f"{x:,.2f} MAD")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("Nog geen transacties.")


def render_investments(username: str):
    """Render investeringen tab."""
    
    st.subheader(" Diaspora Investeringen")
    
    st.info("""
    **Investeer in Marokko:**
    -  Vastgoed
    -  Bedrijven
    -  Landbouw
    -  Sport faciliteiten
    -  Infrastructuur
    """)
    
    wallets = get_wallets_dropdown()
    
    if not wallets:
        st.warning("Wallet nodig om te investeren.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("invest_form"):
            wallet_id = st.selectbox("Wallet *", list(wallets.keys()), format_func=lambda x: wallets.get(x, x))
            project_name = st.text_input("Project Naam *", placeholder="Villa Casablanca")
            project_type = st.selectbox("Type *", Options.INVESTMENT_TYPES)
            project_sector = st.selectbox("Sector", Options.SECTORS)
            project_region = st.selectbox("Regio", Options.REGIONS_MOROCCO)
            
            amount = st.number_input("Investering (MAD) *", min_value=10000.0, step=10000.0)
            expected_return = st.number_input("Verwacht Rendement (%)", 0.0, 30.0, 8.0)
            risk_level = st.selectbox("Risico", Options.RISK_LEVELS)
            
            if st.form_submit_button(" INVESTEREN"):
                if not project_name:
                    st.error("Project naam verplicht.")
                else:
                    inv_id = generate_uuid("INV")
                    
                    # Get identity from wallet
                    df_wallets = get_data("diaspora_wallets")
                    identity_id = df_wallets[df_wallets['wallet_id'] == wallet_id]['identity_id'].iloc[0]
                    
                    success = run_query("""
                        INSERT INTO diaspora_investments (
                            investment_id, wallet_id, identity_id, project_name, project_type,
                            project_sector, project_region, amount, currency, investment_date,
                            expected_return_percentage, investment_status, risk_level, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        inv_id, wallet_id, identity_id, project_name, project_type,
                        project_sector, project_region, amount, "MAD", str(date.today()),
                        expected_return, "ACTIVE", risk_level, datetime.now().isoformat()
                    ))
                    
                    if success:
                        # Deduct from wallet
                        run_query("UPDATE diaspora_wallets SET balance_mad = balance_mad - ? WHERE wallet_id = ?", (amount, wallet_id))
                        process_transaction(wallet_id, amount, "INVESTMENT", f"Investment: {project_name}", fee_waived=True)
                        
                        st.success(f" Investering {inv_id} geregistreerd!")
                        log_audit(username, "INVESTMENT_CREATED", "Diaspora Wallet")
    
    with col2:
        df = get_data("diaspora_investments")
        
        if not df.empty:
            total_invested = df['amount'].sum()
            active = len(df[df['investment_status'] == 'ACTIVE'])
            
            metric_row([
                (" Totaal Geïnvesteerd", f"{total_invested:,.0f} MAD"),
                (" Actief", active),
            ])
            
            st.dataframe(df[['investment_id', 'project_name', 'project_type', 'amount', 'expected_return_percentage', 'investment_status']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Nog geen investeringen.")


def render_diaspora_card(username: str):
    """Render Diaspora Card tab."""
    
    st.subheader(" Diaspora Loyalty Card")
    
    st.info("""
    **Card Benefits:**
    -  **STANDARD** (€29/jaar): Basis korting, fee-vrije transfers
    -  **SILVER** (€49/jaar): 10% korting, prioriteit booking
    -  **GOLD** (€79/jaar): 20% korting, VIP access, gratis transport
    -  **PLATINUM** (€149/jaar): 30% korting, alle benefits, concierge service
    """)
    
    wallets = get_wallets_dropdown()
    
    if not wallets:
        st.warning("Wallet nodig voor card.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.form("card_form"):
            wallet_id = st.selectbox("Wallet *", list(wallets.keys()), format_func=lambda x: wallets.get(x, x))
            card_type = st.selectbox("Card Type *", Options.CARD_TYPES)
            
            # Get price
            prices = {"STANDARD": 29, "SILVER": 49, "GOLD": 79, "PLATINUM": 149}
            price = prices.get(card_type, 29)
            
            st.write(f"**Jaarlijkse kosten:** €{price}")
            
            if st.form_submit_button(" CARD AANVRAGEN"):
                card_id = generate_uuid("CRD")
                card_number = f"DIA-{generate_uuid('')[:12].upper()}"
                
                # Get identity
                df_wallets = get_data("diaspora_wallets")
                identity_id = df_wallets[df_wallets['wallet_id'] == wallet_id]['identity_id'].iloc[0]
                
                # Discount percentage
                discounts = {"STANDARD": 0, "SILVER": 10, "GOLD": 20, "PLATINUM": 30}
                discount = discounts.get(card_type, 0)
                
                success = run_query("""
                    INSERT INTO diaspora_cards (
                        card_id, wallet_id, identity_id, card_number, card_type,
                        issue_date, expiry_date, status, discount_percentage,
                        free_mobility, priority_access, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    card_id, wallet_id, identity_id, card_number, card_type,
                    str(date.today()), str(date.today() + timedelta(days=365)), "ACTIVE",
                    discount, 1 if card_type in ["GOLD", "PLATINUM"] else 0,
                    1 if card_type != "STANDARD" else 0,
                    datetime.now().isoformat()
                ))
                
                if success:
                    st.success(f" Card aangemaakt: {card_number}")
                    log_audit(username, "CARD_CREATED", "Diaspora Wallet")
    
    with col2:
        df = get_data("diaspora_cards")
        
        if not df.empty:
            st.dataframe(df[['card_number', 'card_type', 'discount_percentage', 'expiry_date', 'status']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Nog geen cards uitgegeven.")


def render_wallet_analytics():
    """Render wallet analytics."""
    
    st.subheader(" Wallet Analytics")
    
    df_wallets = get_data("diaspora_wallets")
    df_tx = get_data("wallet_transactions")
    df_inv = get_data("diaspora_investments")
    
    if df_wallets.empty:
        st.info("Geen data.")
        return
    
    total_wallets = len(df_wallets)
    total_balance = df_wallets['balance_mad'].sum()
    total_tx = len(df_tx) if not df_tx.empty else 0
    total_invested = df_inv['amount'].sum() if not df_inv.empty else 0
    
    metric_row([
        (" Wallets", total_wallets),
        (" Totaal Balans", f"{total_balance:,.0f} MAD"),
        (" Transacties", total_tx),
        (" Geïnvesteerd", f"{total_invested:,.0f} MAD"),
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Per Wallet Type")
        st.bar_chart(df_wallets['wallet_type'].value_counts())
    
    with col2:
        st.write("#### Per KYC Status")
        st.bar_chart(df_wallets['kyc_status'].value_counts())
    
    # Foundation contributions
    df_foundation = get_data("foundation_contributions")
    wallet_contributions = df_foundation[df_foundation['source_type'] == 'WALLET_TX'] if not df_foundation.empty else None
    
    if wallet_contributions is not None and not wallet_contributions.empty:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("####  Foundation Bijdragen uit Wallet Transacties")
        st.metric("Totaal", f"{wallet_contributions['amount'].sum():,.2f} MAD")
