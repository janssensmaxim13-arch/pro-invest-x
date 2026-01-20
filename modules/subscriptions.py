# ============================================================================
# SUBSCRIPTIONS MODULE (DOSSIER 7)
# 
# Implementeert:
# - Club Membership (seizoensabonnementen)
# - Player Pass (volg je favoriete speler)
# - National Team Pass
# - Diaspora Pass (speciale kortingen)
# - Family Plans
# - Corporate Packages
# ============================================================================

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Optional

from config import DB_FILE, Options, Messages, FOUNDATION_RATE, TAX_RATE
from database.connection import get_data, run_query, run_transaction, get_connection, count_records, aggregate_sum
from utils.helpers import generate_uuid
from auth.security import log_audit, check_permission
from ui.components import metric_row, page_header, paginated_dataframe


# ============================================================================
# SUBSCRIPTION PLANS
# ============================================================================

SUBSCRIPTION_PLANS = {
    # Club Memberships
    "CLUB_BRONZE": {
        "name": "Club Bronze",
        "type": "CLUB_MEMBERSHIP",
        "price_monthly": 9.99,
        "price_yearly": 99,
        "benefits": ["Match highlights", "Club news", "5% ticket discount"],
        "max_tickets_discount": 5,
        "ticket_discount_pct": 5
    },
    "CLUB_SILVER": {
        "name": "Club Silver", 
        "type": "CLUB_MEMBERSHIP",
        "price_monthly": 19.99,
        "price_yearly": 199,
        "benefits": ["All Bronze benefits", "Live match radio", "10% ticket discount", "Early access"],
        "max_tickets_discount": 10,
        "ticket_discount_pct": 10
    },
    "CLUB_GOLD": {
        "name": "Club Gold",
        "type": "CLUB_MEMBERSHIP",
        "price_monthly": 39.99,
        "price_yearly": 399,
        "benefits": ["All Silver benefits", "Exclusive content", "20% ticket discount", "Meet & greet lottery"],
        "max_tickets_discount": 20,
        "ticket_discount_pct": 20
    },
    
    # Player Pass
    "PLAYER_PASS": {
        "name": "Player Pass",
        "type": "PLAYER_PASS",
        "price_monthly": 4.99,
        "price_yearly": 49,
        "benefits": ["Player stats", "Match notifications", "Exclusive content", "Digital collectibles"],
        "max_players": 3
    },
    
    # National Team
    "LIONS_PASS": {
        "name": "Atlas Lions Pass",
        "type": "NATIONAL_TEAM",
        "price_monthly": 14.99,
        "price_yearly": 149,
        "benefits": ["All national team matches", "Behind the scenes", "15% ticket discount", "Priority booking"],
        "ticket_discount_pct": 15
    },
    "LIONESSES_PASS": {
        "name": "Lionesses Pass",
        "type": "NATIONAL_TEAM",
        "price_monthly": 9.99,
        "price_yearly": 99,
        "benefits": ["Women's national team content", "Match access", "10% ticket discount"],
        "ticket_discount_pct": 10
    },
    
    # Diaspora Special
    "DIASPORA_PASS": {
        "name": "Diaspora Pass",
        "type": "DIASPORA",
        "price_monthly": 7.99,
        "price_yearly": 79,
        "benefits": ["All leagues streaming", "Diaspora events", "20% ticket discount", "Travel package discounts"],
        "ticket_discount_pct": 20,
        "travel_discount_pct": 15
    },
    
    # Family
    "FAMILY_PACK": {
        "name": "Family Pack",
        "type": "FAMILY",
        "price_monthly": 29.99,
        "price_yearly": 299,
        "benefits": ["Up to 5 members", "All Club Gold benefits", "Family seating priority", "Kids activities"],
        "max_members": 5,
        "ticket_discount_pct": 20
    },
    
    # Corporate
    "CORPORATE_BASIC": {
        "name": "Corporate Basic",
        "type": "CORPORATE",
        "price_yearly": 2999,
        "benefits": ["10 employee passes", "VIP lounge access", "Networking events"],
        "employee_passes": 10
    },
    "CORPORATE_PREMIUM": {
        "name": "Corporate Premium",
        "type": "CORPORATE",
        "price_yearly": 9999,
        "benefits": ["50 employee passes", "Private box", "Brand visibility", "Exclusive events"],
        "employee_passes": 50
    }
}


# ============================================================================
# DATABASE TABELLEN
# ============================================================================

def init_subscription_tables():
    """Initialiseer subscription tabellen."""
    import sqlite3
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Subscription Plans (referentie tabel)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            plan_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            plan_type TEXT NOT NULL,
            price_monthly REAL,
            price_yearly REAL NOT NULL,
            benefits TEXT,
            ticket_discount_pct INTEGER DEFAULT 0,
            max_tickets_discount INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    # User Subscriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id TEXT PRIMARY KEY,
            
            -- User
            user_id TEXT NOT NULL,
            user_name TEXT,
            user_email TEXT,
            
            -- Plan
            plan_id TEXT NOT NULL,
            plan_name TEXT,
            plan_type TEXT,
            
            -- Billing
            billing_cycle TEXT DEFAULT 'YEARLY',
            price_paid REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            
            -- Club/Player specifiek
            club_id TEXT,
            club_name TEXT,
            player_ids TEXT,
            
            -- Family/Corporate
            member_count INTEGER DEFAULT 1,
            member_emails TEXT,
            
            -- Dates
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            
            -- Payment
            payment_method TEXT,
            payment_reference TEXT,
            
            -- Foundation
            foundation_contribution REAL DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            auto_renew INTEGER DEFAULT 1,
            cancelled_at TEXT,
            cancellation_reason TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # Subscription Usage (track benefits gebruikt)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_usage (
            usage_id TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            
            -- Usage type
            usage_type TEXT NOT NULL,
            usage_date TEXT NOT NULL,
            
            -- Details
            description TEXT,
            value_used REAL DEFAULT 0,
            
            -- Ticket discount tracking
            ticket_id TEXT,
            discount_amount REAL DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
        )
    ''')
    
    # Subscription Payments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_payments (
            payment_id TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            
            -- Payment details
            amount REAL NOT NULL,
            tax_amount REAL DEFAULT 0,
            foundation_amount REAL DEFAULT 0,
            net_amount REAL NOT NULL,
            
            currency TEXT DEFAULT 'EUR',
            payment_method TEXT,
            payment_reference TEXT,
            
            -- Status
            status TEXT DEFAULT 'COMPLETED',
            payment_date TEXT NOT NULL,
            
            -- Renewal
            is_renewal INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
        )
    ''')
    
    # Gift Subscriptions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gift_subscriptions (
            gift_id TEXT PRIMARY KEY,
            
            -- Giver
            giver_name TEXT NOT NULL,
            giver_email TEXT,
            
            -- Recipient
            recipient_name TEXT NOT NULL,
            recipient_email TEXT NOT NULL,
            
            -- Gift details
            plan_id TEXT NOT NULL,
            duration_months INTEGER DEFAULT 12,
            
            -- Message
            gift_message TEXT,
            
            -- Code
            redemption_code TEXT UNIQUE,
            redeemed INTEGER DEFAULT 0,
            redeemed_at TEXT,
            subscription_id TEXT,
            
            -- Payment
            amount_paid REAL NOT NULL,
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # Indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_user ON subscriptions(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_status ON subscriptions(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sub_plan ON subscriptions(plan_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_payment_sub ON subscription_payments(subscription_id)")
    
    conn.commit()
    conn.close()
    
    # Seed plans
    seed_subscription_plans()


def seed_subscription_plans():
    """Voeg standaard subscription plans toe."""
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        existing = count_records("subscription_plans", "plan_id = ?", (plan_id,))
        if existing == 0:
            run_query("""
                INSERT INTO subscription_plans (
                    plan_id, name, plan_type, price_monthly, price_yearly,
                    benefits, ticket_discount_pct, active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?)
            """, (
                plan_id, plan_data['name'], plan_data['type'],
                plan_data.get('price_monthly', 0), plan_data['price_yearly'],
                ', '.join(plan_data['benefits']),
                plan_data.get('ticket_discount_pct', 0),
                datetime.now().isoformat()
            ))


def register_subscription_tables():
    """Registreer tabellen in whitelist."""
    from config import ALLOWED_TABLES
    tables = [
        'subscription_plans',
        'subscriptions',
        'subscription_usage',
        'subscription_payments',
        'gift_subscriptions'
    ]
    for table in tables:
        if table not in ALLOWED_TABLES:
            ALLOWED_TABLES.append(table)


# ============================================================================
# HELPER FUNCTIES
# ============================================================================

def calculate_subscription_price(plan_id: str, billing_cycle: str) -> tuple:
    """
    Bereken prijs inclusief tax en Foundation.
    
    Returns:
        Tuple van (bruto, tax, foundation, netto)
    """
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        return (0, 0, 0, 0)
    
    if billing_cycle == "MONTHLY":
        base_price = plan.get('price_monthly', plan['price_yearly'] / 12)
    else:
        base_price = plan['price_yearly']
    
    tax = base_price * TAX_RATE
    foundation = base_price * FOUNDATION_RATE
    net = base_price - tax - foundation
    
    return (base_price, tax, foundation, net)


def get_user_active_subscriptions(user_id: str) -> list:
    """Haal actieve subscriptions op voor een user."""
    df = get_data("subscriptions")
    if df.empty:
        return []
    
    active = df[(df['user_id'] == user_id) & (df['status'] == 'ACTIVE')]
    return active.to_dict('records')


def get_subscription_discount(user_id: str) -> int:
    """Haal hoogste ticket discount op voor user."""
    subs = get_user_active_subscriptions(user_id)
    if not subs:
        return 0
    
    max_discount = 0
    for sub in subs:
        plan = SUBSCRIPTION_PLANS.get(sub['plan_id'], {})
        discount = plan.get('ticket_discount_pct', 0)
        if discount > max_discount:
            max_discount = discount
    
    return max_discount


# ============================================================================
# MAIN RENDER
# ============================================================================

def render(username: str):
    """Render de Subscriptions module."""
    
    # Init
    init_subscription_tables()
    register_subscription_tables()
    
    page_header(
        " Subscriptions & Memberships",
        "Dossier 7 | Club Membership | Player Pass | Diaspora Pass | Family & Corporate"
    )
    
    tabs = st.tabs([
        " Plans",
        " Mijn Subscriptions",
        " Nieuw Abonnement",
        " Gift Cards",
        " Analytics"
    ])
    
    with tabs[0]:
        render_plans()
    
    with tabs[1]:
        render_my_subscriptions(username)
    
    with tabs[2]:
        render_new_subscription(username)
    
    with tabs[3]:
        render_gift_cards(username)
    
    with tabs[4]:
        render_subscription_analytics()


# ============================================================================
# TAB 1: PLANS OVERVIEW
# ============================================================================

def render_plans():
    """Render beschikbare subscription plans."""
    
    st.subheader(" Beschikbare Abonnementen")
    
    # Group by type
    plan_types = {
        "CLUB_MEMBERSHIP": " Club Membership",
        "PLAYER_PASS": " Player Pass",
        "NATIONAL_TEAM": " National Team",
        "DIASPORA": " Diaspora",
        "FAMILY": "‍‍‍ Family",
        "CORPORATE": " Corporate"
    }
    
    for plan_type, type_name in plan_types.items():
        st.markdown(f"### {type_name}")
        
        plans_of_type = {k: v for k, v in SUBSCRIPTION_PLANS.items() if v['type'] == plan_type}
        
        cols = st.columns(len(plans_of_type) if len(plans_of_type) <= 3 else 3)
        
        for i, (plan_id, plan) in enumerate(plans_of_type.items()):
            with cols[i % 3]:
                monthly = plan.get('price_monthly', '-')
                yearly = plan['price_yearly']
                
                st.markdown(f"""
                <div style='
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 10px;
                '>
                    <h4 style='margin: 0; color: white;'>{plan['name']}</h4>
                    <p style='font-size: 24px; margin: 10px 0;'>
                        €{yearly}<span style='font-size: 14px;'>/jaar</span>
                    </p>
                    {f"<p style='font-size: 14px;'>of €{monthly}/maand</p>" if monthly != '-' else ""}
                </div>
                """, unsafe_allow_html=True)
                
                # Benefits
                for benefit in plan['benefits'][:4]:
                    st.write(f" {benefit}")
                
                if plan.get('ticket_discount_pct'):
                    st.write(f" **{plan['ticket_discount_pct']}% ticket korting**")
        
        st.markdown("<br>", unsafe_allow_html=True)


# ============================================================================
# TAB 2: MY SUBSCRIPTIONS
# ============================================================================

def render_my_subscriptions(username: str):
    """Render user's subscriptions."""
    
    st.subheader(" Mijn Abonnementen")
    
    df = get_data("subscriptions")
    
    if not df.empty:
        user_subs = df[df['user_id'] == username]
        
        if not user_subs.empty:
            active = user_subs[user_subs['status'] == 'ACTIVE']
            
            metric_row([
                (" Actieve Abonnementen", len(active)),
                (" Totaal Betaald", f"€ {user_subs['price_paid'].sum():,.2f}"),
                (" Hoogste Korting", f"{get_subscription_discount(username)}%"),
            ])
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            for _, sub in user_subs.iterrows():
                status_emoji = "" if sub['status'] == 'ACTIVE' else "" if sub['status'] == 'PAUSED' else ""
                
                with st.expander(f"{status_emoji} {sub['plan_name']} - {sub['status']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Plan:** {sub['plan_name']}")
                        st.write(f"**Type:** {sub['plan_type']}")
                        st.write(f"**Prijs:** € {sub['price_paid']:.2f}")
                        st.write(f"**Billing:** {sub['billing_cycle']}")
                    
                    with col2:
                        st.write(f"**Start:** {sub['start_date'][:10]}")
                        st.write(f"**Einde:** {sub['end_date'][:10]}")
                        st.write(f"**Auto-renew:** {'Ja' if sub['auto_renew'] else 'Nee'}")
                        
                        if sub['club_name']:
                            st.write(f"**Club:** {sub['club_name']}")
                    
                    # Actions
                    if sub['status'] == 'ACTIVE':
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button(" Pauzeren", key=f"pause_{sub['subscription_id']}"):
                                run_query(
                                    "UPDATE subscriptions SET status = 'PAUSED' WHERE subscription_id = ?",
                                    (sub['subscription_id'],)
                                )
                                st.success("Abonnement gepauzeerd.")
                                st.rerun()
                        
                        with col2:
                            if st.button(" Opzeggen", key=f"cancel_{sub['subscription_id']}"):
                                run_query("""
                                    UPDATE subscriptions 
                                    SET status = 'CANCELLED', cancelled_at = ?, auto_renew = 0
                                    WHERE subscription_id = ?
                                """, (datetime.now().isoformat(), sub['subscription_id']))
                                st.warning("Abonnement opgezegd.")
                                st.rerun()
        else:
            st.info("Je hebt nog geen abonnementen.")
            st.write(" Ga naar **Nieuw Abonnement** om er een af te sluiten!")
    else:
        st.info("Nog geen abonnementen in het systeem.")


# ============================================================================
# TAB 3: NEW SUBSCRIPTION
# ============================================================================

def render_new_subscription(username: str):
    """Render new subscription form."""
    
    st.subheader(" Nieuw Abonnement Afsluiten")
    
    # Step 1: Kies type
    plan_type = st.selectbox(
        "Kies type abonnement",
        list(set(p['type'] for p in SUBSCRIPTION_PLANS.values())),
        format_func=lambda x: {
            "CLUB_MEMBERSHIP": " Club Membership",
            "PLAYER_PASS": " Player Pass",
            "NATIONAL_TEAM": " National Team Pass",
            "DIASPORA": " Diaspora Pass",
            "FAMILY": "‍‍‍ Family Pack",
            "CORPORATE": " Corporate Package"
        }.get(x, x)
    )
    
    # Filter plans
    available_plans = {k: v for k, v in SUBSCRIPTION_PLANS.items() if v['type'] == plan_type}
    
    # Step 2: Kies plan
    plan_id = st.selectbox(
        "Kies abonnement",
        list(available_plans.keys()),
        format_func=lambda x: f"{available_plans[x]['name']} - € {available_plans[x]['price_yearly']}/jaar"
    )
    
    selected_plan = available_plans[plan_id]
    
    # Step 3: Billing cycle
    has_monthly = selected_plan.get('price_monthly') is not None
    
    if has_monthly:
        billing_cycle = st.radio(
            "Billing cycle",
            ["YEARLY", "MONTHLY"],
            format_func=lambda x: f"Jaarlijks (€ {selected_plan['price_yearly']})" if x == "YEARLY" else f"Maandelijks (€ {selected_plan['price_monthly']}/maand)"
        )
    else:
        billing_cycle = "YEARLY"
        st.info("Dit abonnement is alleen jaarlijks beschikbaar.")
    
    # Calculate price
    gross, tax, foundation, net = calculate_subscription_price(plan_id, billing_cycle)
    
    # Show price breakdown
    st.markdown("###  Prijsoverzicht")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Basisprijs:** € {gross:.2f}")
        st.write(f"**BTW ({int(TAX_RATE * 100)}%):** € {tax:.2f}")
        st.write(f"**Foundation ({FOUNDATION_RATE * 100}%):** € {foundation:.2f}")
    
    with col2:
        st.markdown(f"""
        <div style='
            background-color: #e8f5e9;
            padding: 15px;
            border-radius: 10px;
        '>
            <h3 style='margin: 0; color: #2e7d32;'>Totaal: € {gross:.2f}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Extra info based on type
    club_name = None
    player_ids = None
    member_emails = None
    
    if plan_type == "CLUB_MEMBERSHIP":
        club_name = st.text_input("Club naam", placeholder="Bijv: Wydad AC, Raja CA, AS FAR...")
    
    elif plan_type == "PLAYER_PASS":
        player_ids = st.text_area("Speler ID's (max 3)", placeholder="Voer speler IDs in, gescheiden door komma")
    
    elif plan_type == "FAMILY":
        member_emails = st.text_area("Familie emails (max 5)", placeholder="email1@test.com, email2@test.com")
    
    # Payment
    st.markdown("###  Betaling")
    
    payment_method = st.selectbox("Betaalmethode", ["CARD", "WALLET", "BANK_TRANSFER"])
    
    user_email = st.text_input("Email voor bevestiging", value=f"{username}@example.com")
    
    # Submit
    if st.button(" ABONNEMENT AFSLUITEN", width='stretch', type="primary"):
        subscription_id = generate_uuid("SUB")
        payment_ref = generate_uuid("PAY")
        
        start = date.today()
        if billing_cycle == "YEARLY":
            end = start + timedelta(days=365)
        else:
            end = start + timedelta(days=30)
        
        # Atomic transaction
        queries = [
            # Insert subscription
            ("""
                INSERT INTO subscriptions (
                    subscription_id, user_id, user_name, user_email,
                    plan_id, plan_name, plan_type, billing_cycle, price_paid,
                    club_name, player_ids, member_emails, member_count,
                    start_date, end_date, payment_method, payment_reference,
                    foundation_contribution, status, auto_renew, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVE', 1, ?)
            """, (
                subscription_id, username, username, user_email,
                plan_id, selected_plan['name'], plan_type, billing_cycle, gross,
                club_name, player_ids, member_emails, 1,
                str(start), str(end), payment_method, payment_ref,
                foundation, datetime.now().isoformat()
            )),
            # Insert payment
            ("""
                INSERT INTO subscription_payments (
                    payment_id, subscription_id, amount, tax_amount, foundation_amount,
                    net_amount, payment_method, payment_reference, status, payment_date, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED', ?, ?)
            """, (
                payment_ref, subscription_id, gross, tax, foundation, net,
                payment_method, payment_ref, datetime.now().isoformat(), datetime.now().isoformat()
            )),
            # Log Foundation contribution
            ("""
                INSERT INTO foundation_contributions (
                    contribution_id, source_type, source_id, amount, description, timestamp
                ) VALUES (?, 'SUBSCRIPTION', ?, ?, ?, ?)
            """, (
                generate_uuid("FND"), subscription_id, foundation,
                f"Subscription: {selected_plan['name']}", datetime.now().isoformat()
            ))
        ]
        
        success = run_transaction(queries)
        
        if success:
            st.success(f" **Abonnement succesvol afgesloten!**")
            st.balloons()
            
            st.info(f"""
            **Details:**
            - Abonnement ID: `{subscription_id}`
            - Plan: {selected_plan['name']}
            - Geldig tot: {end}
            - Foundation bijdrage: € {foundation:.2f}
            """)
            
            log_audit(username, "SUBSCRIPTION_CREATED", "Subscriptions", 
                     details=f"Plan: {plan_id}, Amount: € {gross}")


# ============================================================================
# TAB 4: GIFT CARDS
# ============================================================================

def render_gift_cards(username: str):
    """Render gift subscription functionality."""
    
    st.subheader(" Gift Subscriptions")
    
    tab1, tab2 = st.tabs([" Geef een Cadeau", " Mijn Giften"])
    
    with tab1:
        st.info("Geef een ProInvestiX abonnement cadeau aan een vriend of familielid!")
        
        with st.form("gift_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("###  Cadeau Details")
                plan_id = st.selectbox(
                    "Kies abonnement",
                    list(SUBSCRIPTION_PLANS.keys()),
                    format_func=lambda x: f"{SUBSCRIPTION_PLANS[x]['name']} - € {SUBSCRIPTION_PLANS[x]['price_yearly']}"
                )
                
                duration = st.selectbox("Duur", [6, 12, 24], format_func=lambda x: f"{x} maanden")
                
                gift_message = st.text_area("Persoonlijk bericht", placeholder="Gefeliciteerd met...")
            
            with col2:
                st.markdown("###  Ontvanger")
                recipient_name = st.text_input("Naam ontvanger *")
                recipient_email = st.text_input("Email ontvanger *")
                
                st.markdown("###  Jouw Gegevens")
                giver_email = st.text_input("Jouw email", value=f"{username}@example.com")
            
            # Price
            plan = SUBSCRIPTION_PLANS[plan_id]
            amount = plan['price_yearly'] * (duration / 12)
            
            st.markdown(f"###  Totaal: € {amount:.2f}")
            
            if st.form_submit_button(" VERSTUUR CADEAU", width='stretch'):
                if not recipient_name or not recipient_email:
                    st.error("Vul ontvanger gegevens in.")
                else:
                    import random
                    import string
                    
                    gift_id = generate_uuid("GFT")
                    redemption_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                    
                    run_query("""
                        INSERT INTO gift_subscriptions (
                            gift_id, giver_name, giver_email, recipient_name, recipient_email,
                            plan_id, duration_months, gift_message, redemption_code, amount_paid, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        gift_id, username, giver_email, recipient_name, recipient_email,
                        plan_id, duration, gift_message, redemption_code, amount,
                        datetime.now().isoformat()
                    ))
                    
                    st.success(" Cadeau verzonden!")
                    st.info(f"**Redemption Code:** `{redemption_code}`\n\nDe ontvanger kan deze code gebruiken om het abonnement te activeren.")
                    
                    log_audit(username, "GIFT_SUBSCRIPTION_CREATED", "Subscriptions")
    
    with tab2:
        df = get_data("gift_subscriptions")
        
        if not df.empty:
            user_gifts = df[df['giver_name'] == username]
            
            if not user_gifts.empty:
                st.dataframe(
                    user_gifts[['recipient_name', 'plan_id', 'redemption_code', 'redeemed', 'created_at']],
                    width='stretch', hide_index=True
                )
            else:
                st.info("Je hebt nog geen cadeaus verstuurd.")
        else:
            st.info("Nog geen gift subscriptions.")


# ============================================================================
# TAB 5: ANALYTICS
# ============================================================================

def render_subscription_analytics():
    """Render subscription analytics."""
    
    st.subheader(" Subscription Analytics")
    
    if not check_permission(["SuperAdmin", "Analytics", "Official"], silent=True):
        st.warning(" Analytics zijn beperkt toegankelijk.")
        return
    
    df = get_data("subscriptions")
    df_payments = get_data("subscription_payments")
    
    if df.empty:
        st.info("Nog geen subscription data.")
        return
    
    # Metrics
    total_subs = len(df)
    active_subs = len(df[df['status'] == 'ACTIVE'])
    total_revenue = df_payments['amount'].sum() if not df_payments.empty else 0
    total_foundation = df_payments['foundation_amount'].sum() if not df_payments.empty else 0
    
    metric_row([
        (" Totaal Subscriptions", total_subs),
        (" Actief", active_subs),
        (" Totale Revenue", f"€ {total_revenue:,.2f}"),
        (" Foundation Bijdrage", f"€ {total_foundation:,.2f}"),
    ])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("####  Subscriptions per Type")
        st.bar_chart(df['plan_type'].value_counts())
    
    with col2:
        st.write("####  Subscriptions per Status")
        st.bar_chart(df['status'].value_counts())
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Revenue by plan
    if not df_payments.empty:
        st.write("####  Revenue per Plan")
        revenue_by_plan = df.groupby('plan_name')['price_paid'].sum().sort_values(ascending=False)
        st.bar_chart(revenue_by_plan)
