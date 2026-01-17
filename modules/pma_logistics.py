# ============================================================================
# PMA LOGISTICS MODULE
# Platform Marocains Abroad - Logistieke diensten voor WK2030
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import hashlib

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from ui.styles import COLORS
from ui.components import page_header, premium_kpi_row, info_box, warning_box, success_message
from database.connection import get_data, run_query
from utils.helpers import generate_uuid
from auth.security import log_audit

# =============================================================================
# CONSTANTS
# =============================================================================

SHIPMENT_TYPES = [
    ("EQUIPMENT", "Sports Equipment"),
    ("MERCHANDISE", "Fan Merchandise"),
    ("MEDICAL", "Medical Supplies"),
    ("BROADCAST", "Broadcasting Equipment"),
    ("CONSTRUCTION", "Construction Materials"),
    ("FOOD", "Food & Catering"),
    ("SECURITY", "Security Equipment"),
    ("IT", "IT Infrastructure")
]

SHIPMENT_STATUSES = [
    "PENDING", "CUSTOMS_CLEARANCE", "IN_TRANSIT", 
    "ARRIVED", "DELIVERED", "RETURNED"
]

TRANSPORT_MODES = ["Air", "Sea", "Road", "Rail", "Multimodal"]

WAREHOUSES = [
    ("WH-CASA", "Casablanca Hub", "Casablanca"),
    ("WH-TNG", "Tanger Med Hub", "Tanger"),
    ("WH-RBT", "Rabat Central", "Rabat"),
    ("WH-AGD", "Agadir Logistics", "Agadir"),
    ("WH-FES", "Fes Distribution", "Fes"),
    ("WH-MRK", "Marrakech Center", "Marrakech")
]

PRIORITY_LEVELS = ["STANDARD", "EXPRESS", "URGENT", "CRITICAL"]

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_pma_tables():
    """Initialize PMA Logistics tables."""
    import sqlite3
    from config import DB_FILE
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Shipments
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_shipments (
            shipment_id TEXT PRIMARY KEY,
            tracking_number TEXT UNIQUE,
            
            -- Content
            shipment_type TEXT NOT NULL,
            description TEXT,
            weight_kg REAL,
            volume_m3 REAL,
            declared_value REAL,
            
            -- Origin
            origin_country TEXT NOT NULL,
            origin_city TEXT,
            origin_address TEXT,
            sender_name TEXT,
            sender_contact TEXT,
            
            -- Destination
            destination_city TEXT NOT NULL,
            destination_address TEXT,
            destination_warehouse TEXT,
            receiver_name TEXT,
            receiver_contact TEXT,
            
            -- Transport
            transport_mode TEXT,
            carrier TEXT,
            estimated_arrival TEXT,
            actual_arrival TEXT,
            
            -- Status
            status TEXT DEFAULT 'PENDING',
            priority TEXT DEFAULT 'STANDARD',
            customs_cleared INTEGER DEFAULT 0,
            customs_reference TEXT,
            
            -- WK2030 specific
            event_related TEXT,
            stadium_destination TEXT,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # Warehouses
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_warehouses (
            warehouse_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            capacity_m3 REAL DEFAULT 0,
            used_capacity_m3 REAL DEFAULT 0,
            manager_name TEXT,
            manager_contact TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Inventory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_inventory (
            inventory_id TEXT PRIMARY KEY,
            warehouse_id TEXT NOT NULL,
            shipment_id TEXT,
            item_name TEXT NOT NULL,
            item_type TEXT,
            quantity INTEGER DEFAULT 1,
            unit TEXT DEFAULT 'pcs',
            location_code TEXT,
            status TEXT DEFAULT 'IN_STOCK',
            received_at TEXT,
            dispatched_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (warehouse_id) REFERENCES pma_warehouses(warehouse_id)
        )
    ''')
    
    # Fleet/Vehicles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_fleet (
            vehicle_id TEXT PRIMARY KEY,
            vehicle_type TEXT NOT NULL,
            license_plate TEXT,
            capacity_kg REAL,
            capacity_m3 REAL,
            driver_name TEXT,
            driver_contact TEXT,
            current_location TEXT,
            status TEXT DEFAULT 'AVAILABLE',
            last_maintenance TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # Deliveries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_deliveries (
            delivery_id TEXT PRIMARY KEY,
            shipment_id TEXT,
            vehicle_id TEXT,
            driver_name TEXT,
            
            -- Route
            pickup_location TEXT,
            pickup_time TEXT,
            delivery_location TEXT,
            delivery_time TEXT,
            estimated_duration_minutes INTEGER,
            actual_duration_minutes INTEGER,
            
            -- Status
            status TEXT DEFAULT 'SCHEDULED',
            signature_received INTEGER DEFAULT 0,
            proof_of_delivery TEXT,
            
            -- Notes
            special_instructions TEXT,
            delivery_notes TEXT,
            
            created_at TEXT NOT NULL,
            FOREIGN KEY (shipment_id) REFERENCES pma_shipments(shipment_id),
            FOREIGN KEY (vehicle_id) REFERENCES pma_fleet(vehicle_id)
        )
    ''')
    
    # Customs clearance
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pma_customs (
            customs_id TEXT PRIMARY KEY,
            shipment_id TEXT NOT NULL,
            declaration_number TEXT,
            hs_code TEXT,
            duty_amount REAL DEFAULT 0,
            vat_amount REAL DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            submitted_at TEXT,
            cleared_at TEXT,
            agent_name TEXT,
            notes TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (shipment_id) REFERENCES pma_shipments(shipment_id)
        )
    ''')
    
    # Indexes
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipment_status ON pma_shipments(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipment_tracking ON pma_shipments(tracking_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON pma_inventory(warehouse_id)")
    except:
        pass
    
    conn.commit()
    conn.close()

# =============================================================================
# DEMO DATA GENERATORS
# =============================================================================

def generate_demo_shipments():
    """Generate demo shipment data."""
    shipments = []
    
    origins = ["Netherlands", "Belgium", "France", "Germany", "Spain", "Italy", "UK", "USA", "China", "UAE"]
    
    for i in range(20):
        ship_type = random.choice(SHIPMENT_TYPES)
        status = random.choice(SHIPMENT_STATUSES)
        
        shipments.append({
            "shipment_id": f"SHP-{5000+i}",
            "tracking_number": f"PMA{random.randint(100000, 999999)}MA",
            "type": ship_type[1],
            "origin": random.choice(origins),
            "destination": random.choice([w[2] for w in WAREHOUSES]),
            "weight_kg": round(random.uniform(10, 5000), 1),
            "status": status,
            "priority": random.choice(PRIORITY_LEVELS),
            "customs_cleared": 1 if status in ["ARRIVED", "DELIVERED"] else 0,
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        })
    
    return pd.DataFrame(shipments)

def generate_demo_inventory():
    """Generate demo inventory."""
    inventory = []
    
    items = [
        ("Football Kits", "EQUIPMENT"), ("Goal Posts", "EQUIPMENT"),
        ("Medical Kits", "MEDICAL"), ("Broadcasting Cameras", "BROADCAST"),
        ("Fan Scarves", "MERCHANDISE"), ("Stadium Seats", "CONSTRUCTION"),
        ("Security Scanners", "SECURITY"), ("Network Switches", "IT")
    ]
    
    for i, (item, itype) in enumerate(items * 3):
        inventory.append({
            "inventory_id": f"INV-{6000+i}",
            "warehouse": random.choice([w[1] for w in WAREHOUSES]),
            "item_name": item,
            "item_type": itype,
            "quantity": random.randint(10, 500),
            "status": random.choice(["IN_STOCK", "RESERVED", "DISPATCHED"])
        })
    
    return pd.DataFrame(inventory)

# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_shipment_tracking(username: str):
    """Render shipment tracking tab."""
    st.markdown("### Shipment Tracking")
    st.caption("Track all incoming shipments for WK2030")
    
    df = get_data("pma_shipments")
    if df.empty:
        df = generate_demo_shipments()
        info_box("Demo Mode", "Showing demo shipments.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Shipments", len(df))
    with col2:
        in_transit = len(df[df['status'] == 'IN_TRANSIT']) if 'status' in df.columns else 0
        st.metric("In Transit", in_transit)
    with col3:
        delivered = len(df[df['status'] == 'DELIVERED']) if 'status' in df.columns else 0
        st.metric("Delivered", delivered)
    with col4:
        pending_customs = len(df[df['status'] == 'CUSTOMS_CLEARANCE']) if 'status' in df.columns else 0
        st.metric("Pending Customs", pending_customs)
    
    st.divider()
    
    # Track shipment
    col1, col2 = st.columns([2, 1])
    with col1:
        tracking_input = st.text_input("Enter Tracking Number", placeholder="PMA123456MA")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        track_btn = st.button("Track", type="primary", width="stretch")
    
    if track_btn and tracking_input:
        # Search in dataframe
        result = df[df['tracking_number'] == tracking_input] if 'tracking_number' in df.columns else pd.DataFrame()
        
        if not result.empty:
            ship = result.iloc[0]
            st.success(f"Shipment Found!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(t("status"), ship.get('status', 'Unknown'))
                st.metric("Type", ship.get('type', 'N/A'))
            with col2:
                st.metric("Origin", ship.get('origin', 'N/A'))
                st.metric("Destination", ship.get('destination', 'N/A'))
            with col3:
                st.metric("Weight", f"{ship.get('weight_kg', 0)} kg")
                st.metric("Priority", ship.get('priority', 'STANDARD'))
        else:
            st.warning("Shipment not found. Check tracking number.")
    
    st.divider()
    
    # Filter
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(t("status"), ["All"] + SHIPMENT_STATUSES)
    with col2:
        type_filter = st.selectbox("Type", ["All"] + [t[1] for t in SHIPMENT_TYPES])
    with col3:
        priority_filter = st.selectbox("Priority", ["All"] + PRIORITY_LEVELS)
    
    # Apply filters
    filtered_df = df.copy()
    if status_filter != "All" and 'status' in df.columns:
        filtered_df = filtered_df[filtered_df['status'] == status_filter]
    
    st.dataframe(filtered_df, width="stretch", hide_index=True)
    
    # Create shipment
    with st.expander("Create New Shipment", expanded=False):
        with st.form("create_shipment"):
            col1, col2 = st.columns(2)
            with col1:
                ship_type = st.selectbox("Shipment Type *", [t[1] for t in SHIPMENT_TYPES])
                description = st.text_input("Description")
                weight = st.number_input("Weight (kg)", 0.0, 50000.0, 100.0)
                origin_country = st.text_input("Origin Country *")
            with col2:
                destination = st.selectbox("Destination City *", [w[2] for w in WAREHOUSES])
                priority = st.selectbox("Priority", PRIORITY_LEVELS)
                transport_mode = st.selectbox("Transport Mode", TRANSPORT_MODES)
                sender_name = st.text_input("Sender Name")
            
            if st.form_submit_button("Create Shipment", type="primary", width="stretch"):
                if origin_country and destination:
                    shipment_id = generate_uuid("SHP")
                    tracking = f"PMA{random.randint(100000, 999999)}MA"
                    type_code = next((t[0] for t in SHIPMENT_TYPES if t[1] == ship_type), "EQUIPMENT")
                    
                    success = run_query("""
                        INSERT INTO pma_shipments 
                        (shipment_id, tracking_number, shipment_type, description, weight_kg,
                         origin_country, destination_city, transport_mode, priority,
                         sender_name, status, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
                    """, (shipment_id, tracking, type_code, description, weight,
                          origin_country, destination, transport_mode, priority,
                          sender_name, username, datetime.now().isoformat()))
                    
                    if success:
                        success_message("Shipment Created!", f"Tracking: {tracking}")
                        log_audit(username, "SHIPMENT_CREATED", "PMA", tracking)
                        st.rerun()
                else:
                    st.error("Origin country and destination are required")


def render_warehouse_management(username: str):
    """Render warehouse management tab."""
    st.markdown("### Warehouse Management")
    st.caption("Manage WK2030 logistics hubs across Morocco")
    
    # Show warehouses
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for wh_id, wh_name, wh_city in WAREHOUSES:
            capacity = random.randint(5000, 20000)
            used = random.randint(1000, capacity - 500)
            usage_pct = (used / capacity) * 100
            
            color = COLORS['success'] if usage_pct < 60 else (COLORS['warning'] if usage_pct < 85 else COLORS['error'])
            
            st.markdown(f"""
                <div style='background: {COLORS['card']}; padding: 1rem; border-radius: 8px; 
                            margin-bottom: 0.5rem; border-left: 4px solid {color};'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <strong>{wh_name}</strong><br>
                            <small style='color: {COLORS['text_muted']}'>{wh_city} | {wh_id}</small>
                        </div>
                        <div style='text-align: right;'>
                            <span style='color: {color}; font-weight: bold;'>{usage_pct:.0f}%</span><br>
                            <small>{used:,} / {capacity:,} m³</small>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### Quick Stats")
        st.metric("Total Warehouses", len(WAREHOUSES))
        st.metric("Total Capacity", "75,000 m³")
        st.metric("Avg Utilization", "67%")
        
        st.divider()
        
        st.markdown("#### Alerts")
        st.warning("Casablanca Hub at 85% capacity")
        st.info("Tanger Med receiving 5 shipments today")


def render_inventory(username: str):
    """Render inventory tab."""
    st.markdown("### Inventory Management")
    st.caption("Track all items across warehouses")
    
    df = get_data("pma_inventory")
    if df.empty:
        df = generate_demo_inventory()
        info_box("Demo Mode", "Showing demo inventory.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Items", len(df))
    with col2:
        in_stock = len(df[df['status'] == 'IN_STOCK']) if 'status' in df.columns else 0
        st.metric("In Stock", in_stock)
    with col3:
        reserved = len(df[df['status'] == 'RESERVED']) if 'status' in df.columns else 0
        st.metric("Reserved", reserved)
    with col4:
        total_qty = df['quantity'].sum() if 'quantity' in df.columns else 0
        st.metric("Total Quantity", f"{total_qty:,}")
    
    st.divider()
    
    # Filter by warehouse
    warehouse_filter = st.selectbox("Filter by Warehouse", ["All"] + [w[1] for w in WAREHOUSES])
    
    filtered_df = df.copy()
    if warehouse_filter != "All" and 'warehouse' in df.columns:
        filtered_df = filtered_df[filtered_df['warehouse'] == warehouse_filter]
    
    st.dataframe(filtered_df, width="stretch", hide_index=True)
    
    # Add inventory item
    with st.expander("Add Inventory Item", expanded=False):
        with st.form("add_inventory"):
            col1, col2 = st.columns(2)
            with col1:
                warehouse = st.selectbox("Warehouse *", [w[1] for w in WAREHOUSES])
                item_name = st.text_input("Item Name *")
                item_type = st.selectbox("Item Type", [t[1] for t in SHIPMENT_TYPES])
            with col2:
                quantity = st.number_input("Quantity", 1, 10000, 10)
                unit = st.selectbox("Unit", ["pcs", "boxes", "pallets", "containers"])
                location_code = st.text_input("Location Code", placeholder="A-12-3")
            
            if st.form_submit_button("Add to Inventory", type="primary", width="stretch"):
                if item_name and warehouse:
                    inv_id = generate_uuid("INV")
                    wh_id = next((w[0] for w in WAREHOUSES if w[1] == warehouse), None)
                    type_code = next((t[0] for t in SHIPMENT_TYPES if t[1] == item_type), "EQUIPMENT")
                    
                    success = run_query("""
                        INSERT INTO pma_inventory 
                        (inventory_id, warehouse_id, item_name, item_type, quantity, unit,
                         location_code, status, received_at, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 'IN_STOCK', ?, ?)
                    """, (inv_id, wh_id, item_name, type_code, quantity, unit,
                          location_code, datetime.now().isoformat(), datetime.now().isoformat()))
                    
                    if success:
                        success_message("Item Added!", inv_id)
                        log_audit(username, "INVENTORY_ADDED", "PMA", f"{item_name} x {quantity}")
                        st.rerun()
                else:
                    st.error("Item name and warehouse are required")


def render_fleet(username: str):
    """Render fleet management tab."""
    st.markdown("### Fleet Management")
    st.caption("Manage delivery vehicles and drivers")
    
    df = get_data("pma_fleet")
    
    # Demo fleet data
    if df.empty:
        fleet = []
        vehicle_types = ["Van", "Truck", "Semi-Trailer", "Refrigerated Truck", "Flatbed"]
        for i in range(12):
            fleet.append({
                "vehicle_id": f"VEH-{7000+i}",
                "type": random.choice(vehicle_types),
                "license_plate": f"{random.randint(10000, 99999)}-A-{random.randint(10, 99)}",
                "capacity_kg": random.randint(1000, 20000),
                "driver": f"Driver {i+1}",
                "location": random.choice([w[2] for w in WAREHOUSES]),
                "status": random.choice(["AVAILABLE", "IN_USE", "MAINTENANCE"])
            })
        df = pd.DataFrame(fleet)
        info_box("Demo Mode", "Showing demo fleet.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Vehicles", len(df))
    with col2:
        available = len(df[df['status'] == 'AVAILABLE']) if 'status' in df.columns else 0
        st.metric("Available", available)
    with col3:
        in_use = len(df[df['status'] == 'IN_USE']) if 'status' in df.columns else 0
        st.metric("In Use", in_use)
    with col4:
        maintenance = len(df[df['status'] == 'MAINTENANCE']) if 'status' in df.columns else 0
        st.metric("Maintenance", maintenance)
    
    st.divider()
    
    # Vehicle list
    for _, veh in df.iterrows():
        status = veh.get('status', 'UNKNOWN')
        status_color = COLORS['success'] if status == 'AVAILABLE' else (
            COLORS['warning'] if status == 'IN_USE' else COLORS['error'])
        
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1:
            st.markdown(f"**{veh.get('type', 'Vehicle')}** | {veh.get('license_plate', 'N/A')}")
        with col2:
            st.markdown(f"{veh.get('capacity_kg', 0):,} kg")
        with col3:
            st.markdown(f"{veh.get('location', 'N/A')}")
        with col4:
            st.markdown(f"<span style='color: {status_color}'>{status}</span>", unsafe_allow_html=True)
        st.divider()


def render_customs(username: str):
    """Render customs clearance tab."""
    st.markdown("### Customs Clearance")
    st.caption("Manage import declarations and clearances")
    
    df = get_data("pma_customs")
    
    # Demo customs data
    if df.empty:
        customs = []
        for i in range(15):
            status = random.choice(["PENDING", "SUBMITTED", "CLEARED", "HELD"])
            customs.append({
                "customs_id": f"CUS-{8000+i}",
                "shipment_id": f"SHP-{5000+random.randint(0, 19)}",
                "declaration": f"DEC-{random.randint(10000, 99999)}",
                "hs_code": f"{random.randint(1000, 9999)}.{random.randint(10, 99)}",
                "duty": round(random.uniform(100, 5000), 2),
                "status": status,
                "submitted_at": (datetime.now() - timedelta(days=random.randint(1, 10))).strftime("%Y-%m-%d")
            })
        df = pd.DataFrame(customs)
        info_box("Demo Mode", "Showing demo customs data.")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Declarations", len(df))
    with col2:
        cleared = len(df[df['status'] == 'CLEARED']) if 'status' in df.columns else 0
        st.metric("Cleared", cleared)
    with col3:
        pending = len(df[df['status'] == 'PENDING']) if 'status' in df.columns else 0
        st.metric("Pending", pending)
    with col4:
        total_duty = df['duty'].sum() if 'duty' in df.columns else 0
        st.metric("Total Duties", f"MAD {total_duty:,.0f}")
    
    st.divider()
    st.dataframe(df, width="stretch", hide_index=True)
    
    # File customs declaration
    with st.expander("File Customs Declaration", expanded=False):
        with st.form("file_customs"):
            col1, col2 = st.columns(2)
            with col1:
                shipment_id = st.text_input("Shipment ID *")
                hs_code = st.text_input("HS Code *", placeholder="8471.30")
                declared_value = st.number_input("Declared Value (MAD)", 0.0, 10000000.0, 10000.0)
            with col2:
                duty_rate = st.slider("Duty Rate %", 0.0, 40.0, 10.0)
                vat_rate = st.slider("VAT Rate %", 0.0, 20.0, 20.0)
                agent_name = st.text_input("Customs Agent")
            
            duty_amount = declared_value * (duty_rate / 100)
            vat_amount = (declared_value + duty_amount) * (vat_rate / 100)
            
            st.info(f"Estimated Duty: MAD {duty_amount:,.2f} | VAT: MAD {vat_amount:,.2f} | Total: MAD {duty_amount + vat_amount:,.2f}")
            
            if st.form_submit_button("Submit Declaration", type="primary", width="stretch"):
                if shipment_id and hs_code:
                    customs_id = generate_uuid("CUS")
                    declaration = f"DEC-{random.randint(10000, 99999)}"
                    
                    success = run_query("""
                        INSERT INTO pma_customs 
                        (customs_id, shipment_id, declaration_number, hs_code, 
                         duty_amount, vat_amount, status, agent_name, submitted_at, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, 'SUBMITTED', ?, ?, ?)
                    """, (customs_id, shipment_id, declaration, hs_code,
                          duty_amount, vat_amount, agent_name,
                          datetime.now().isoformat(), datetime.now().isoformat()))
                    
                    if success:
                        success_message("Declaration Submitted!", declaration)
                        log_audit(username, "CUSTOMS_FILED", "PMA", declaration)
                        st.rerun()
                else:
                    st.error("Shipment ID and HS Code are required")


# =============================================================================
# MAIN RENDER FUNCTION
# =============================================================================

def render(username: str):
    """Render the PMA Logistics module."""
    
    # Initialize tables
    init_pma_tables()
    
    page_header(
        "PMA Logistics Hub",
        "Platform Marocains Abroad - WK2030 Supply Chain Management",
        icon=""
    )
    
    # KPIs
    df_shipments = get_data("pma_shipments")
    df_inventory = get_data("pma_inventory")
    
    ship_count = len(df_shipments) if not df_shipments.empty else 20
    inv_count = len(df_inventory) if not df_inventory.empty else 24
    
    premium_kpi_row([
        ("", "Active Shipments", str(ship_count), "Tracking"),
        ("", "Warehouses", str(len(WAREHOUSES)), "Across Morocco"),
        ("", "Inventory Items", str(inv_count), "In stock"),
        ("", "Fleet Vehicles", "12", "Available")
    ])
    
    st.divider()
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Shipment Tracking",
        " Warehouses",
        " Inventory",
        " Fleet",
        " Customs"
    ])
    
    with tab1:
        render_shipment_tracking(username)
    
    with tab2:
        render_warehouse_management(username)
    
    with tab3:
        render_inventory(username)
    
    with tab4:
        render_fleet(username)
    
    with tab5:
        render_customs(username)
