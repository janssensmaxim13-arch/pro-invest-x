# ============================================================================
# TICKETCHAIN™ MODULE
# Blockchain ticketing systeem met QR codes en loyalty
# ============================================================================

import streamlit as st
import sqlite3
import hashlib
import hmac
import uuid
from datetime import datetime
from io import BytesIO

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import BLOCKCHAIN_SECRET, TAX_RATE, FOUNDATION_RATE, DB_FILE, LoyaltyTiers
from database.connection import get_data, run_query
from utils.helpers import get_identity_names_map, generate_uuid
from auth.security import log_audit
from ui.components import metric_row, page_header

# QR code support
try:
    import qrcode
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False


def generate_ticket_hash(event_id: str, owner_id: str, seat: str, timestamp: str) -> str:
    """Genereer HMAC-SHA256 ticket hash (blockchain-grade)."""
    message = f"{event_id}|{owner_id}|{seat}|{timestamp}"
    return hmac.new(
        BLOCKCHAIN_SECRET.encode(), 
        message.encode(), 
        hashlib.sha256
    ).hexdigest()


def generate_qr_code(ticket_hash: str) -> bytes | None:
    """Genereer QR code voor ticket."""
    if not QR_AVAILABLE:
        return None
    
    try:
        qr = qrcode.QRCode(
            version=1, 
            error_correction=qrcode.constants.ERROR_CORRECT_H, 
            box_size=10, 
            border=4
        )
        qr.add_data(ticket_hash)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#2e0d43", back_color="white")
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        return buf.getvalue()
    except:
        return None


def check_event_capacity(event_id: str) -> tuple:
    """
    Check event capaciteit.
    
    Returns:
        (capacity, sold, available, is_full)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT capacity FROM ticketchain_events WHERE event_id = ?", 
            (event_id,)
        )
        result = cursor.fetchone()
        
        if not result:
            return (0, 0, 0, True)
        
        capacity = result[0]
        
        cursor.execute(
            "SELECT COUNT(*) FROM ticketchain_tickets WHERE event_id = ? AND status IN ('VALID', 'USED')", 
            (event_id,)
        )
        sold = cursor.fetchone()[0]
        
        return (capacity, sold, capacity - sold, sold >= capacity)
        
    except:
        return (0, 0, 0, True)
    finally:
        conn.close()


def check_seat_availability(event_id: str, seat: str) -> tuple:
    """
    Check of een stoel beschikbaar is.
    
    Returns:
        (is_taken, owner_id)
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT owner_id FROM ticketchain_tickets WHERE event_id=? AND seat_info=? AND status IN ('VALID','USED')", 
            (event_id, seat)
        )
        result = cursor.fetchone()
        
        return (True, result[0]) if result else (False, None)
        
    except:
        return (True, "ERROR")
    finally:
        conn.close()


def update_event_counter(event_id: str):
    """Update tickets_sold counter voor event."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT COUNT(*) FROM ticketchain_tickets WHERE event_id=? AND status IN ('VALID','USED')", 
            (event_id,)
        )
        count = cursor.fetchone()[0]
        
        cursor.execute(
            "UPDATE ticketchain_events SET tickets_sold=? WHERE event_id=?", 
            (count, event_id)
        )
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()


def log_fiscal(ticket_hash: str, amount: float) -> tuple:
    """
    Log fiscale transactie met FOUNDATION BIJDRAGE (MASTERPLAN).
    
    Returns:
        (success, tax, foundation, net)
    """
    tax = amount * TAX_RATE
    foundation = amount * FOUNDATION_RATE  # 0.5% naar Foundation!
    net = amount - tax - foundation
    
    fiscal_id = generate_uuid("TAX")
    
    # Log fiscal record
    run_query(
        "INSERT INTO fiscal_ledger VALUES (?, ?, ?, ?, ?, ?, ?)", 
        (fiscal_id, ticket_hash, amount, tax, foundation, net, datetime.now().isoformat())
    )
    
    # Log Foundation contribution (MASTERPLAN!)
    contribution_id = generate_uuid("FND")
    run_query(
        "INSERT INTO foundation_contributions VALUES (?, ?, ?, ?, ?, ?)",
        (contribution_id, ticket_hash, "TICKET_SALE", foundation, 1, datetime.now().isoformat())
    )
    
    return (True, tax, foundation, net)


def award_loyalty_points(identity_id: str, points: int):
    """Ken loyalty punten toe bij ticket aankoop."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT points_balance, tickets_purchased FROM loyalty_points WHERE identity_id=?", 
            (identity_id,)
        )
        result = cursor.fetchone()
        
        if result:
            new_balance = result[0] + points
            new_tickets = result[1] + 1
            tier = LoyaltyTiers.get_tier(new_balance)
            
            cursor.execute(
                "UPDATE loyalty_points SET points_balance=?, tickets_purchased=?, tier=?, last_activity=? WHERE identity_id=?",
                (new_balance, new_tickets, tier, datetime.now().isoformat(), identity_id)
            )
        else:
            points_id = generate_uuid("LP")
            cursor.execute(
                "INSERT INTO loyalty_points VALUES (?, ?, ?, ?, ?, ?)",
                (points_id, identity_id, points, "BRONZE", 1, datetime.now().isoformat())
            )
        
        conn.commit()
        return True
        
    except:
        conn.rollback()
        return False
    finally:
        conn.close()


def render(username: str):
    """Render de TicketChain module."""
    
    page_header(
        " TicketChain™",
        "Blockchain Ticketing System | Fraud-Proof Smart Ticketing with Loyalty Rewards"
    )
    
    tab1, tab2, tab3, tab4 = st.tabs([
        " Events", 
        " Minting", 
        " Validator", 
        " Loyalty System"
    ])
    
    with tab1:
        render_events(username)
    
    with tab2:
        render_minting(username)
    
    with tab3:
        render_validator(username)
    
    with tab4:
        render_loyalty()


def render_events(username: str):
    """Render event management."""
    
    st.subheader(" Event Management")
    
    with st.form("new_event"):
        col1, col2 = st.columns(2)
        
        with col1:
            event_name = st.text_input("Event Name", placeholder="e.g., Derby Casablanca")
            event_location = st.text_input("Location", placeholder="e.g., Mohamed V Stadium")
        
        with col2:
            event_date = st.date_input("Event Date")
            event_capacity = st.number_input("Capacity", min_value=100, step=100, value=1000)
        
        mobility = st.checkbox("Enable Mobility Integration (bus/train booking)")
        
        if st.form_submit_button(" DEPLOY EVENT CONTRACT", width='stretch'):
            if not event_name or not event_location:
                st.error(" Event name and location required.")
            else:
                event_id = generate_uuid("EVT")
                
                success = run_query(
                    "INSERT INTO ticketchain_events VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (event_id, event_name, event_location, str(event_date), 
                     event_capacity, 0, 1 if mobility else 0, None, 0, datetime.now().isoformat())
                )
                
                if success:
                    st.success(f" Event Contract Deployed: {event_id}")
                    log_audit(username, "EVENT_CREATED", "TicketChain", details=f"Event: {event_name}")
                    st.balloons()
                    st.rerun()
    
    st.divider()
    
    # Event list
    st.write("###  Active Events")
    df_events = get_data("ticketchain_events")
    
    if not df_events.empty:
        for idx, row in df_events.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1.5, 1, 1])
            
            col1.markdown(f"**{row['name']}**")
            col2.write(f" {row['location']}")
            col3.write(f" {row['date']}")
            
            sold = row.get('tickets_sold', 0)
            capacity = row['capacity']
            
            if sold >= capacity:
                col4.markdown(" **SOLD OUT**")
            else:
                col4.markdown(f" {sold}/{capacity}")
            
            st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    else:
        st.info(" No events yet. Create your first event above.")


def render_minting(username: str):
    """Render ticket minting."""
    
    st.subheader(" Mint Smart Tickets")
    
    # Session state voor laatste ticket
    if 'last_minted_ticket' not in st.session_state:
        st.session_state.last_minted_ticket = None
    
    events_df = get_data("ticketchain_events")
    id_map = get_identity_names_map()
    
    if events_df.empty:
        st.warning(" No events available. Create an event first.")
        return
    
    if not id_map:
        st.warning(" No verified identities. Register buyers in Identity Shield first.")
        return
    
    event_options = dict(zip(events_df['event_id'], events_df['name']))
    
    with st.form("mint_ticket"):
        col1, col2 = st.columns(2)
        
        with col1:
            selected_event = st.selectbox(
                "Select Event", 
                list(event_options.keys()), 
                format_func=lambda x: f"{event_options[x]} ({x})"
            )
            selected_owner = st.selectbox(
                "Buyer Identity", 
                list(id_map.keys()), 
                format_func=lambda x: f"{id_map[x]} ({x})"
            )
        
        with col2:
            seat_info = st.text_input("Seat Assignment", placeholder="e.g., VIP Row 5 Seat 12")
            price = st.number_input("Price (MAD)", min_value=0.0, step=10.0, value=100.0)
        
        capacity, sold, available, is_full = check_event_capacity(selected_event)
        st.info(f" Capacity: {sold}/{capacity} sold • {available} remaining")
        
        if st.form_submit_button(" MINT TICKET", width='stretch'):
            if is_full:
                st.error(f" EVENT SOLD OUT! All {capacity} tickets minted.")
            elif not seat_info or not seat_info.strip():
                st.error(" Seat assignment is required.")
            elif price <= 0:
                st.error(" Price must be positive.")
            else:
                seat_taken, owner = check_seat_availability(selected_event, seat_info)
                
                if seat_taken:
                    st.error(f" Seat '{seat_info}' already assigned to {owner}")
                else:
                    timestamp = datetime.now().isoformat()
                    ticket_hash = generate_ticket_hash(selected_event, selected_owner, seat_info, timestamp)
                    
                    try:
                        success = run_query(
                            "INSERT INTO ticketchain_tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (ticket_hash, selected_event, selected_owner, seat_info, 
                             price, "VALID", timestamp, None, 1, None, None)
                        )
                        
                        if success:
                            update_event_counter(selected_event)
                            fiscal_success, tax, foundation, net = log_fiscal(ticket_hash, price)
                            loyalty_points = int(price / 10)
                            award_loyalty_points(selected_owner, loyalty_points)
                            qr_bytes = generate_qr_code(ticket_hash)
                            
                            # Sla op in session state
                            st.session_state.last_minted_ticket = {
                                "hash": ticket_hash,
                                "qr": qr_bytes,
                                "seat": seat_info,
                                "price": price,
                                "event": event_options[selected_event],
                                "owner": id_map[selected_owner],
                                "tax": tax,
                                "foundation": foundation,
                                "net": net,
                                "loyalty_points": loyalty_points,
                                "timestamp": timestamp
                            }
                            
                            st.success(" TICKET SUCCESSFULLY MINTED!")
                            log_audit(username, "TICKET_MINTED", "TicketChain", 
                                     details=f"Event: {selected_event}, Hash: {ticket_hash[:16]}...")
                    
                    except Exception as e:
                        st.error(f" Minting failed: {str(e)}")
    
    # Toon resultaat BUITEN form
    if st.session_state.last_minted_ticket:
        res = st.session_state.last_minted_ticket
        
        st.divider()
        st.balloons()
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("####  Ticket Details")
            st.code(f"""
Event: {res['event']}
Owner: {res['owner']}
Seat: {res['seat']}
Price: {res['price']:.2f} MAD
Status: VALID
Minted: {res['timestamp']}
            """)
        
        with col_b:
            st.markdown("####  Blockchain Hash")
            st.code(res['hash'], language="text")
            
            st.markdown("####  Financial Breakdown")
            st.write(f"Gross: {res['price']:.2f} MAD")
            st.write(f"Tax (15%): {res['tax']:.2f} MAD")
            st.write(f"Foundation (0.5%): {res['foundation']:.2f} MAD")
            st.write(f"Net: {res['net']:.2f} MAD")
            
            st.markdown(f"####  Loyalty Reward")
            st.write(f"+{res['loyalty_points']} points earned!")
        
        # QR Code + Download
        if res['qr']:
            st.markdown("####  QR Code Ticket")
            st.image(res['qr'], caption="Scan at entrance", width=300)
            st.download_button(
                " Download QR", 
                res['qr'], 
                f"ticket_{res['hash'][:8]}.png", 
                "image/png"
            )
        else:
            st.info("QR unavailable. Use hash for validation.")
    
    st.divider()
    
    # Ticket ledger
    st.write("###  Blockchain Ledger")
    df_tickets = get_data("ticketchain_tickets")
    
    if not df_tickets.empty:
        display_df = df_tickets.copy()
        display_df['hash_preview'] = display_df['ticket_hash'].apply(lambda x: f"{x[:16]}...")
        display_df['price'] = display_df['price'].apply(lambda x: f"{x:.2f} MAD")
        
        cols = ['hash_preview', 'event_id', 'owner_id', 'seat_info', 'price', 'status', 'minted_at']
        st.dataframe(display_df[cols], width='stretch', hide_index=True)
    else:
        st.info("No tickets minted yet.")


def render_validator(username: str):
    """Render ticket validator."""
    
    st.subheader(" Ticket Validator")
    
    check_hash = st.text_input(
        " Input Ticket Hash (64 characters)", 
        placeholder="Paste ticket hash..."
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" VERIFY AUTHENTICITY", width='stretch'):
            if not check_hash or len(check_hash.strip()) != 64:
                st.error(" Invalid hash format. Must be 64 characters.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM ticketchain_tickets WHERE ticket_hash = ?", 
                    (check_hash.strip(),)
                )
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    status = result[5]
                    
                    if status == "VALID":
                        st.success(" TICKET IS VALID AND AUTHENTIC")
                        st.json({
                            "Event ID": result[1],
                            "Owner ID": result[2],
                            "Seat": result[3],
                            "Price": f"{result[4]:.2f} MAD",
                            t("status"): result[5],
                            "Minted At": result[6],
                            "Used At": result[7] if result[7] else "Not used yet"
                        })
                    elif status == "USED":
                        st.warning(" TICKET ALREADY USED")
                        st.write(f"Used at: {result[7]}")
                    else:
                        st.info(f"Status: {status}")
                else:
                    st.error(" INVALID - NOT FOUND IN BLOCKCHAIN")
                    st.warning(" POSSIBLE FRAUD DETECTED")
    
    with col2:
        if st.button(" MARK AS USED", width='stretch'):
            if not check_hash or len(check_hash.strip()) != 64:
                st.error(" Invalid hash format.")
            else:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT status FROM ticketchain_tickets WHERE ticket_hash = ?", 
                    (check_hash.strip(),)
                )
                result = cursor.fetchone()
                
                if not result:
                    st.error(" Ticket not found.")
                elif result[0] == "USED":
                    st.warning(" Already marked as used.")
                else:
                    cursor.execute(
                        "UPDATE ticketchain_tickets SET status = 'USED', used_at = ? WHERE ticket_hash = ?",
                        (datetime.now().isoformat(), check_hash.strip())
                    )
                    conn.commit()
                    st.success(" Ticket marked as USED")
                    st.info("Entry granted! Enjoy the event.")
                    log_audit(username, "TICKET_VALIDATED", "TicketChain")
                
                conn.close()
    
    st.divider()
    
    # Statistics
    st.write("###  Validation Statistics")
    df_all = get_data("ticketchain_tickets")
    
    if not df_all.empty:
        total = len(df_all)
        valid = len(df_all[df_all['status'] == 'VALID'])
        used = len(df_all[df_all['status'] == 'USED'])
        
        metric_row([
            ("Total Minted", total),
            ("Valid (Unused)", valid),
            ("Used", used),
        ])


def render_loyalty():
    """Render loyalty program."""
    
    st.subheader(" Fan Loyalty & Rewards Program")
    
    df_loyalty = get_data("loyalty_points")
    
    if not df_loyalty.empty:
        st.write("###  Top Fans Leaderboard")
        leaderboard = df_loyalty.sort_values('points_balance', ascending=False).head(10)
        
        for idx, (index, fan) in enumerate(leaderboard.iterrows(), 1):
            col1, col2, col3, col4 = st.columns([0.5, 2, 1, 1])
            
            medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
            col1.write(medal)
            col2.write(f"**{fan['identity_id']}**")
            col3.write(f" {fan['points_balance']} pts")
            col4.write(f" {fan['tier']}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.write("###  Tier Distribution")
        tier_counts = df_loyalty['tier'].value_counts()
        st.bar_chart(tier_counts)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.info("""
        **Tier Benefits:**
        -  BRONZE (0-99 points): Standard benefits
        -  SILVER (100-499 points): Priority booking, 10% discount
        -  GOLD (500-999 points): VIP access, 20% discount, exclusive events
        -  DIAMOND (1000+ points): All benefits + free mobility, merchandise
        """)
    else:
        st.info("No loyalty data yet. Start minting tickets to earn points!")
