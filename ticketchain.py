"""
ProInvestiX - TicketChain Module v3.0
Blockchain-based Event Ticketing System
With improved Event Management and Readable Hash Codes
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import hashlib
import qrcode
from io import BytesIO
import base64
import random
import string

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

EVENT_CATEGORIES = [
    "Football Match",
    "WK 2030 Match",
    "Concert",
    "Festival",
    "Sports Event",
    "Conference",
    "Exhibition",
    "Theater",
    "Other"
]

TICKET_TYPES = [
    {"name": "Standard", "multiplier": 1.0, "benefits": "General admission"},
    {"name": "Premium", "multiplier": 1.5, "benefits": "Better seating, fast entry"},
    {"name": "VIP", "multiplier": 3.0, "benefits": "Best seats, lounge access, meet & greet"},
    {"name": "Family Pack (4)", "multiplier": 3.5, "benefits": "4 tickets, family zone"},
    {"name": "Group (10)", "multiplier": 8.0, "benefits": "10 tickets, group discount"},
    {"name": "Student", "multiplier": 0.7, "benefits": "Valid student ID required"},
    {"name": "Early Bird", "multiplier": 0.8, "benefits": "Limited availability"},
    {"name": "Last Minute", "multiplier": 1.2, "benefits": "Available 24h before event"},
]

VENUES = {
    "Stade Mohammed V": {"city": "Casablanca", "capacity": 67000, "country": "Morocco"},
    "Complexe Moulay Abdellah": {"city": "Rabat", "capacity": 53000, "country": "Morocco"},
    "Stade de Marrakech": {"city": "Marrakech", "capacity": 45240, "country": "Morocco"},
    "Grand Stade de Tanger": {"city": "Tangier", "capacity": 65000, "country": "Morocco"},
    "Stade de Fes": {"city": "Fes", "capacity": 45000, "country": "Morocco"},
    "Stade d'Agadir": {"city": "Agadir", "capacity": 45480, "country": "Morocco"},
    "Stade Adrar": {"city": "Agadir", "capacity": 45480, "country": "Morocco"},
    "Santiago Bernabeu": {"city": "Madrid", "capacity": 81044, "country": "Spain"},
    "Camp Nou": {"city": "Barcelona", "capacity": 99354, "country": "Spain"},
}

# Demo events for WK 2030
WK2030_EVENTS = [
    {
        "name": "WK 2030 Opening Ceremony",
        "category": "WK 2030 Match",
        "venue": "Stade Mohammed V",
        "date": "2030-06-13",
        "time": "20:00",
        "base_price": 500,
        "capacity": 67000,
        "description": "Grand opening ceremony of FIFA World Cup 2030"
    },
    {
        "name": "WK 2030 - Morocco vs Spain",
        "category": "WK 2030 Match",
        "venue": "Stade Mohammed V",
        "date": "2030-06-15",
        "time": "21:00",
        "base_price": 300,
        "capacity": 67000,
        "description": "Group stage match"
    },
    {
        "name": "WK 2030 Quarter Final 1",
        "category": "WK 2030 Match",
        "venue": "Grand Stade de Tanger",
        "date": "2030-07-04",
        "time": "18:00",
        "base_price": 400,
        "capacity": 65000,
        "description": "Quarter final match"
    },
    {
        "name": "WK 2030 Final",
        "category": "WK 2030 Match",
        "venue": "Stade Mohammed V",
        "date": "2030-07-13",
        "time": "18:00",
        "base_price": 1000,
        "capacity": 67000,
        "description": "FIFA World Cup 2030 Final"
    },
]


# ============================================================================
# HASH & BLOCKCHAIN UTILITIES
# ============================================================================

def generate_ticket_hash(ticket_id: str, event_id: str, owner: str) -> str:
    """Generate a readable, copyable ticket hash"""
    # Create deterministic but unique hash
    data = f"{ticket_id}:{event_id}:{owner}:{datetime.now().isoformat()}"
    full_hash = hashlib.sha256(data.encode()).hexdigest()
    
    # Return formatted hash (easier to read and copy)
    # Format: XXXX-XXXX-XXXX-XXXX (16 chars in 4 groups)
    short_hash = full_hash[:16].upper()
    formatted = f"{short_hash[:4]}-{short_hash[4:8]}-{short_hash[8:12]}-{short_hash[12:16]}"
    return formatted


def generate_block_hash(previous_hash: str, ticket_data: dict) -> str:
    """Generate block hash for blockchain"""
    data = f"{previous_hash}:{ticket_data}:{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:32].upper()


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


def display_hash_with_copy(hash_value: str, label: str = "Hash"):
    """Display hash in a copyable format"""
    st.markdown(f"""
    <div style='background: #1a1a2e; padding: 15px; border-radius: 8px; margin: 10px 0;'>
        <p style='color: #888; margin: 0 0 5px 0; font-size: 12px;'>{label}</p>
        <code style='font-family: "Courier New", monospace; font-size: 18px; color: #00ff88; 
                     letter-spacing: 2px; word-break: break-all; display: block;
                     background: #0a0a15; padding: 10px; border-radius: 4px;
                     user-select: all; cursor: text;'>{hash_value}</code>
    </div>
    """, unsafe_allow_html=True)
    
    # Also provide a text input for easy copying
    st.text_input(f"Copy {label}", value=hash_value, key=f"copy_{hash_value}_{label}", 
                  help="Click and Ctrl+A to select all, then Ctrl+C to copy")


# ============================================================================
# EVENT MANAGEMENT
# ============================================================================

def render_event_management():
    """Render event management section"""
    st.subheader("Event Management")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "All Events", 
        "Create Event", 
        "WK 2030 Events",
        "Event Analytics"
    ])
    
    with tab1:
        render_all_events()
    
    with tab2:
        render_create_event()
    
    with tab3:
        render_wk2030_events()
    
    with tab4:
        render_event_analytics()


def render_all_events():
    """Display all events"""
    st.markdown("### Upcoming Events")
    
    # Initialize demo events if not exists
    if 'ticketchain_events' not in st.session_state:
        st.session_state['ticketchain_events'] = WK2030_EVENTS.copy()
    
    events = st.session_state['ticketchain_events']
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox("Category", ["All"] + EVENT_CATEGORIES)
    with col2:
        filter_venue = st.selectbox("Venue", ["All"] + list(VENUES.keys()))
    with col3:
        sort_by = st.selectbox("Sort by", ["Date", "Price", "Name"])
    
    # Display events
    for i, event in enumerate(events):
        # Apply filters
        if filter_category != "All" and event.get('category') != filter_category:
            continue
        if filter_venue != "All" and event.get('venue') != filter_venue:
            continue
        
        venue_info = VENUES.get(event.get('venue', ''), {})
        
        with st.container():
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                        padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 4px solid #FFD700;'>
                <h3 style='color: white; margin: 0;'>{event['name']}</h3>
                <p style='color: #888;'>{event.get('category', 'Event')}</p>
                <div style='display: flex; gap: 30px; margin-top: 10px;'>
                    <div>
                        <span style='color: #FFD700;'>Date:</span>
                        <span style='color: white;'> {event.get('date', 'TBD')} {event.get('time', '')}</span>
                    </div>
                    <div>
                        <span style='color: #FFD700;'>Venue:</span>
                        <span style='color: white;'> {event.get('venue', 'TBD')}</span>
                    </div>
                    <div>
                        <span style='color: #FFD700;'>From:</span>
                        <span style='color: white;'> {event.get('base_price', 0)} MAD</span>
                    </div>
                </div>
                <p style='color: #aaa; margin-top: 10px; font-size: 14px;'>{event.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                if st.button(f"Buy Tickets", key=f"buy_{i}"):
                    st.session_state['selected_event'] = event
                    st.session_state['ticketchain_tab'] = 'mint'
            with col2:
                st.caption(f"Capacity: {event.get('capacity', 'N/A'):,}")


def render_create_event():
    """Create new event form"""
    st.markdown("### Create New Event")
    
    with st.form("create_event_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            event_name = st.text_input("Event Name *")
            event_category = st.selectbox("Category *", EVENT_CATEGORIES)
            event_venue = st.selectbox("Venue *", list(VENUES.keys()))
            event_date = st.date_input("Date *", min_value=date.today())
        
        with col2:
            event_time = st.time_input("Time *")
            base_price = st.number_input("Base Price (MAD) *", min_value=0, value=100)
            capacity = st.number_input("Capacity", min_value=1, value=VENUES.get(event_venue, {}).get('capacity', 1000))
            event_description = st.text_area("Description")
        
        st.markdown("### Ticket Types Available")
        selected_types = st.multiselect(
            "Select ticket types for this event",
            [t['name'] for t in TICKET_TYPES],
            default=["Standard", "Premium", "VIP"]
        )
        
        st.markdown("### Additional Options")
        col1, col2, col3 = st.columns(3)
        with col1:
            early_bird = st.checkbox("Enable Early Bird pricing")
            early_bird_end = st.date_input("Early Bird ends", disabled=not early_bird) if early_bird else None
        with col2:
            resale_allowed = st.checkbox("Allow ticket resale", value=True)
            max_resale_markup = st.slider("Max resale markup %", 0, 100, 20, disabled=not resale_allowed)
        with col3:
            foundation_donation = st.checkbox("Include Foundation donation", value=True)
            donation_percent = st.slider("Donation %", 0, 10, 1, disabled=not foundation_donation)
        
        submitted = st.form_submit_button("Create Event")
        
        if submitted and event_name:
            new_event = {
                "name": event_name,
                "category": event_category,
                "venue": event_venue,
                "date": str(event_date),
                "time": str(event_time),
                "base_price": base_price,
                "capacity": capacity,
                "description": event_description,
                "ticket_types": selected_types,
                "early_bird": early_bird,
                "resale_allowed": resale_allowed,
                "max_resale_markup": max_resale_markup if resale_allowed else 0,
                "foundation_donation": donation_percent if foundation_donation else 0,
                "created_at": datetime.now().isoformat()
            }
            
            if 'ticketchain_events' not in st.session_state:
                st.session_state['ticketchain_events'] = []
            
            st.session_state['ticketchain_events'].append(new_event)
            st.success(f"Event '{event_name}' created successfully!")
            
            # Generate event hash
            event_hash = generate_ticket_hash(event_name, event_category, "SYSTEM")
            display_hash_with_copy(event_hash, "Event ID")


def render_wk2030_events():
    """Display WK 2030 specific events"""
    st.markdown("### FIFA World Cup 2030 - Morocco Events")
    
    # Countdown
    wk_start = datetime(2030, 6, 13)
    days_until = (wk_start - datetime.now()).days
    
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #c8102e 0%, #006233 100%); 
                padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0;'>FIFA World Cup 2030</h2>
        <h1 style='color: #FFD700; margin: 10px 0; font-size: 48px;'>{days_until} Days</h1>
        <p style='color: white;'>Until Opening Ceremony in Casablanca</p>
    </div>
    """, unsafe_allow_html=True)
    
    # WK 2030 Events
    for event in WK2030_EVENTS:
        st.markdown(f"""
        <div style='background: #1a1a2e; padding: 20px; border-radius: 10px; margin: 10px 0;
                    border: 2px solid #FFD700;'>
            <h3 style='color: #FFD700; margin: 0;'>{event['name']}</h3>
            <p style='color: white;'>{event['venue']} | {event['date']} {event['time']}</p>
            <p style='color: #888;'>{event['description']}</p>
            <p style='color: #00ff88; font-size: 20px;'>From {event['base_price']} MAD</p>
        </div>
        """, unsafe_allow_html=True)


def render_event_analytics():
    """Display event analytics"""
    st.markdown("### Event Analytics Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", len(st.session_state.get('ticketchain_events', WK2030_EVENTS)))
    with col2:
        st.metric("Tickets Sold", "12,450")
    with col3:
        st.metric("Revenue", "3.2M MAD")
    with col4:
        st.metric("Fill Rate", "78%")
    
    # Sales by category
    st.markdown("### Sales by Category")
    chart_data = pd.DataFrame({
        'Category': ['WK 2030', 'Football', 'Concert', 'Festival', 'Other'],
        'Tickets': [8500, 2100, 1200, 450, 200]
    })
    st.bar_chart(chart_data.set_index('Category'))


# ============================================================================
# TICKET MINTING
# ============================================================================

def render_ticket_minting():
    """Render ticket minting/purchase section"""
    st.subheader("Mint Ticket (Purchase)")
    
    events = st.session_state.get('ticketchain_events', WK2030_EVENTS)
    
    # Event selection
    event_names = [e['name'] for e in events]
    selected_event_name = st.selectbox("Select Event", event_names)
    selected_event = next((e for e in events if e['name'] == selected_event_name), None)
    
    if selected_event:
        st.markdown(f"""
        <div style='background: #1a1a2e; padding: 15px; border-radius: 8px; margin: 15px 0;'>
            <h4 style='color: #FFD700; margin: 0;'>{selected_event['name']}</h4>
            <p style='color: white;'>{selected_event.get('venue', 'TBD')} | {selected_event.get('date', 'TBD')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            ticket_type = st.selectbox("Ticket Type", [t['name'] for t in TICKET_TYPES])
            quantity = st.number_input("Quantity", min_value=1, max_value=10, value=1)
            buyer_name = st.text_input("Buyer Name *")
            buyer_email = st.text_input("Buyer Email *")
        
        with col2:
            # Calculate price
            type_info = next((t for t in TICKET_TYPES if t['name'] == ticket_type), TICKET_TYPES[0])
            base_price = selected_event.get('base_price', 100)
            unit_price = base_price * type_info['multiplier']
            total_price = unit_price * quantity
            foundation_fee = total_price * 0.005  # 0.5% Foundation
            
            st.markdown("### Order Summary")
            st.markdown(f"""
            | Item | Amount |
            |------|--------|
            | Base Price | {base_price} MAD |
            | Type Multiplier | x{type_info['multiplier']} |
            | Unit Price | {unit_price:.2f} MAD |
            | Quantity | {quantity} |
            | **Subtotal** | **{total_price:.2f} MAD** |
            | Foundation (0.5%) | {foundation_fee:.2f} MAD |
            | **Total** | **{total_price + foundation_fee:.2f} MAD** |
            """)
        
        if st.button("Mint Ticket", type="primary"):
            if buyer_name and buyer_email:
                # Generate ticket
                ticket_id = f"TKT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
                ticket_hash = generate_ticket_hash(ticket_id, selected_event_name, buyer_name)
                block_hash = generate_block_hash("GENESIS", {"ticket": ticket_id})
                
                # Store ticket
                if 'minted_tickets' not in st.session_state:
                    st.session_state['minted_tickets'] = []
                
                ticket = {
                    "ticket_id": ticket_id,
                    "ticket_hash": ticket_hash,
                    "block_hash": block_hash,
                    "event": selected_event_name,
                    "type": ticket_type,
                    "quantity": quantity,
                    "buyer": buyer_name,
                    "email": buyer_email,
                    "total": total_price + foundation_fee,
                    "minted_at": datetime.now().isoformat()
                }
                st.session_state['minted_tickets'].append(ticket)
                
                st.success("Ticket minted successfully!")
                
                # Display ticket with readable hashes
                st.markdown("---")
                st.markdown("### Your Ticket")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                                padding: 25px; border-radius: 15px; border: 2px solid #FFD700;'>
                        <h3 style='color: #FFD700; margin: 0;'>{selected_event_name}</h3>
                        <p style='color: white; font-size: 18px;'>{ticket_type} Ticket x{quantity}</p>
                        <hr style='border-color: #333;'>
                        <p style='color: #888;'>Holder: {buyer_name}</p>
                        <p style='color: #888;'>Date: {selected_event.get('date', 'TBD')}</p>
                        <p style='color: #888;'>Venue: {selected_event.get('venue', 'TBD')}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # READABLE HASH CODES
                    st.markdown("### Ticket Verification Codes")
                    display_hash_with_copy(ticket_hash, "Ticket Hash")
                    display_hash_with_copy(block_hash, "Block Hash")
                    display_hash_with_copy(ticket_id, "Ticket ID")
                
                with col2:
                    # QR Code
                    qr_data = f"PROINVESTIX-TICKET:{ticket_hash}"
                    qr_base64 = generate_qr_code(qr_data)
                    st.markdown(f"""
                    <div style='text-align: center; padding: 10px;'>
                        <img src='data:image/png;base64,{qr_base64}' style='width: 200px;'>
                        <p style='color: #888; margin-top: 10px;'>Scan to verify</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.error("Please fill in all required fields")


# ============================================================================
# MY TICKETS
# ============================================================================

def render_my_tickets():
    """Display user's tickets"""
    st.subheader("My Tickets")
    
    tickets = st.session_state.get('minted_tickets', [])
    
    if not tickets:
        st.info("You haven't purchased any tickets yet.")
        return
    
    for ticket in tickets:
        with st.expander(f"{ticket['event']} - {ticket['type']}", expanded=False):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                **Event:** {ticket['event']}  
                **Type:** {ticket['type']}  
                **Quantity:** {ticket['quantity']}  
                **Total Paid:** {ticket['total']:.2f} MAD  
                **Purchased:** {ticket['minted_at'][:10]}
                """)
                
                # Display hashes in readable format
                st.markdown("---")
                display_hash_with_copy(ticket['ticket_hash'], "Ticket Hash")
                display_hash_with_copy(ticket['block_hash'], "Block Hash")
            
            with col2:
                qr_data = f"PROINVESTIX-TICKET:{ticket['ticket_hash']}"
                qr_base64 = generate_qr_code(qr_data)
                st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{qr_base64}' style='width: 150px;'>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# VERIFY TICKET
# ============================================================================

def render_verify_ticket():
    """Verify ticket authenticity"""
    st.subheader("Verify Ticket")
    
    st.markdown("""
    Enter a ticket hash to verify its authenticity on the blockchain.
    """)
    
    verify_hash = st.text_input("Enter Ticket Hash (e.g., XXXX-XXXX-XXXX-XXXX)")
    
    if st.button("Verify"):
        if verify_hash:
            # Check against stored tickets
            tickets = st.session_state.get('minted_tickets', [])
            found = next((t for t in tickets if t['ticket_hash'] == verify_hash.upper()), None)
            
            if found:
                st.success("VALID TICKET")
                st.markdown(f"""
                **Event:** {found['event']}  
                **Type:** {found['type']}  
                **Holder:** {found['buyer']}  
                **Minted:** {found['minted_at'][:10]}
                """)
                display_hash_with_copy(found['block_hash'], "Block Hash")
            else:
                st.error("TICKET NOT FOUND - This ticket hash is not in our system")
        else:
            st.warning("Please enter a ticket hash")


# ============================================================================
# RESALE MARKETPLACE
# ============================================================================

def render_resale_marketplace():
    """Ticket resale marketplace"""
    st.subheader("Resale Marketplace")
    
    st.info("List your tickets for resale or browse available tickets from other users.")
    
    tab1, tab2 = st.tabs(["Available Tickets", "List My Ticket"])
    
    with tab1:
        st.markdown("### Tickets Available for Resale")
        
        # Demo resale listings
        resale_listings = [
            {"event": "WK 2030 Opening Ceremony", "type": "VIP", "original": 1500, "asking": 1800, "seller": "Ahmed M."},
            {"event": "WK 2030 - Morocco vs Spain", "type": "Premium", "original": 450, "asking": 500, "seller": "Sara K."},
        ]
        
        for listing in resale_listings:
            markup = ((listing['asking'] - listing['original']) / listing['original']) * 100
            st.markdown(f"""
            <div style='background: #1a1a2e; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h4 style='color: white; margin: 0;'>{listing['event']}</h4>
                <p style='color: #888;'>{listing['type']} Ticket</p>
                <p style='color: #FFD700;'>Asking: {listing['asking']} MAD 
                   <span style='color: {"#ff6b6b" if markup > 15 else "#00ff88"};'>
                   (+{markup:.0f}%)</span></p>
                <p style='color: #666;'>Seller: {listing['seller']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Buy from {listing['seller']}", key=f"buy_resale_{listing['event']}"):
                st.info("Contact seller to complete transaction")
    
    with tab2:
        st.markdown("### List Your Ticket")
        
        my_tickets = st.session_state.get('minted_tickets', [])
        
        if my_tickets:
            ticket_options = [f"{t['event']} - {t['type']}" for t in my_tickets]
            selected = st.selectbox("Select ticket to sell", ticket_options)
            asking_price = st.number_input("Asking Price (MAD)", min_value=1)
            
            if st.button("List for Sale"):
                st.success("Ticket listed for sale!")
        else:
            st.info("You don't have any tickets to sell")


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render():
    """Main render function"""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); 
                padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0;'>TicketChain</h1>
        <p style='color: #888; margin: 5px 0 0 0;'>Blockchain-Powered Event Ticketing</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs([
        "Events",
        "Buy Tickets",
        "My Tickets",
        "Verify",
        "Resale Market"
    ])
    
    with tabs[0]:
        render_event_management()
    with tabs[1]:
        render_ticket_minting()
    with tabs[2]:
        render_my_tickets()
    with tabs[3]:
        render_verify_ticket()
    with tabs[4]:
        render_resale_marketplace()
