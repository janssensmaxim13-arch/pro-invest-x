#!/usr/bin/env python3
"""
ProInvestiX Demo Data Generator v5.4.1 - FIXED
===============================================
Genereert realistische demo data voor alle modules.
Roept eerst init_db() aan om tabellen te creëren.

Gebruik:
    python3 demo_data.py load     # Laad demo data
    python3 demo_data.py clear    # Verwijder alle demo data
    python3 demo_data.py reset    # Clear + Load (verse start)
"""

import sqlite3
import random
import sys
from datetime import datetime, timedelta
import hashlib
import os

DB_FILE = "proinvestix_ultimate.db"

# =============================================================================
# REALISTISCHE DATA
# =============================================================================

MOROCCAN_FIRST_NAMES = [
    "Youssef", "Achraf", "Hakim", "Noussair", "Sofyan", "Bilal", "Nayef", 
    "Azzedine", "Munir", "Mehdi", "Ayoub", "Zakaria", "Amine", "Ismail",
    "Walid", "Karim", "Omar", "Hamza", "Rayan", "Adam", "Yassin", "Soufiane"
]

MOROCCAN_LAST_NAMES = [
    "Hakimi", "Ziyech", "Mazraoui", "Amrabat", "El Khannouss", "Aguerd",
    "Bounou", "Saiss", "Ounahi", "Boufal", "Dirar", "El Ahmadi", "Benatia",
    "Feddal", "Belhanda", "Boussoufa", "Chamakh", "Taarabt", "El Arabi"
]

EUROPEAN_FIRST_NAMES = [
    "Mohammed", "Ahmed", "Yassine", "Khalid", "Samir", "Rachid", "Jamal",
    "Farid", "Hassan", "Malik", "Tariq", "Nabil", "Kamal", "Driss"
]

CLUBS = [
    ("Raja Casablanca", "Morocco", "Casablanca"),
    ("Wydad Casablanca", "Morocco", "Casablanca"),
    ("FAR Rabat", "Morocco", "Rabat"),
    ("RS Berkane", "Morocco", "Berkane"),
    ("FUS Rabat", "Morocco", "Rabat"),
    ("Real Madrid", "Spain", "Madrid"),
    ("Barcelona", "Spain", "Barcelona"),
    ("PSG", "France", "Paris"),
    ("Bayern Munich", "Germany", "Munich"),
    ("Manchester United", "England", "Manchester"),
    ("Chelsea", "England", "London"),
    ("Ajax", "Netherlands", "Amsterdam"),
    ("PSV", "Netherlands", "Eindhoven"),
    ("Anderlecht", "Belgium", "Brussels"),
    ("Club Brugge", "Belgium", "Bruges"),
]

POSITIONS = [
    "Goalkeeper", "Right-Back", "Centre-Back", "Left-Back",
    "Defensive Midfield", "Central Midfield", "Attacking Midfield",
    "Right Winger", "Left Winger", "Centre-Forward"
]

DIASPORA_COUNTRIES = [
    "Netherlands", "Belgium", "France", "Germany", "Spain", 
    "Italy", "UK", "USA", "Canada", "UAE"
]

MOROCCAN_CITIES = [
    "Casablanca", "Rabat", "Marrakech", "Fes", "Tangier", 
    "Agadir", "Oujda", "Kenitra", "Tetouan", "Nador"
]

EVENT_NAMES = [
    "WK 2030 - Morocco vs Spain",
    "WK 2030 - Morocco vs France", 
    "WK 2030 - Morocco vs Belgium",
    "WK 2030 Opening Ceremony",
    "WK 2030 Quarter Final",
    "WK 2030 Semi Final",
    "Raja vs Wydad - Derby",
    "Botola Pro - Matchday 15",
    "CAF Champions League Final",
    "Throne Cup Final"
]

STADIUMS = [
    ("Grand Stade de Casablanca", "Casablanca", 115000),
    ("Stade Mohammed V", "Casablanca", 67000),
    ("Complexe Moulay Abdellah", "Rabat", 52000),
    ("Grand Stade de Marrakech", "Marrakech", 45000),
    ("Grand Stade de Tangier", "Tangier", 65000),
    ("Grand Stade d'Agadir", "Agadir", 45000),
]

ACADEMY_NAMES = [
    "Mohammed VI Football Academy",
    "Raja Youth Academy",
    "Wydad Development Center",
    "Atlas Lions Academy",
    "Casablanca Elite Training",
    "Rabat Football School",
    "Marrakech Youth Development",
    "Tangier Talent Center"
]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_id(prefix="ID"):
    """Generate unique ID"""
    return f"{prefix}-{random.randint(100000, 999999)}"

def random_date(start_year=2020, end_year=2025):
    """Generate random date"""
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 12, 31)
    delta = end - start
    random_days = random.randint(0, delta.days)
    return (start + timedelta(days=random_days)).strftime("%Y-%m-%d")

def random_datetime(start_year=2024, end_year=2025):
    """Generate random datetime"""
    return random_date(start_year, end_year) + f" {random.randint(8,20)}:{random.choice(['00','15','30','45'])}:00"

def random_phone():
    """Generate Moroccan phone number"""
    return f"+212 6{random.randint(10000000, 99999999)}"

def random_email(name):
    """Generate email from name"""
    domains = ["gmail.com", "outlook.com", "yahoo.com", "hotmail.com"]
    clean_name = name.lower().replace(" ", ".")
    return f"{clean_name}{random.randint(1,99)}@{random.choice(domains)}"

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DB_FILE)

def init_database():
    """Initialize database with all tables"""
    print("  Initializing database tables...")
    try:
        # Import and run init_db from database setup
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from database.setup import init_db
        init_db()
        print("  ✓ Database tables created")
        return True
    except Exception as e:
        print(f"  ✗ Error initializing database: {e}")
        return False

# =============================================================================
# DATA GENERATORS
# =============================================================================

def generate_talents(cursor, count=50):
    """Generate NTSP talent profiles"""
    print(f"  Generating {count} talents...")
    
    for i in range(count):
        talent_id = generate_id("TAL")
        first_name = random.choice(MOROCCAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        
        club = random.choice(CLUBS)
        position = random.choice(POSITIONS)
        age = random.randint(16, 35)
        dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 364))
        
        potential = random.randint(60, 99)
        market_value = random.randint(50000, 50000000)
        
        is_diaspora = random.choice([0, 0, 0, 1])  # 25% diaspora
        diaspora_country = random.choice(DIASPORA_COUNTRIES) if is_diaspora else None
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ntsp_talent_profiles 
                (talent_id, first_name, last_name, date_of_birth, nationality, 
                 primary_position, current_club, current_club_country, 
                 potential_score, market_value_estimate, talent_status,
                 is_diaspora, diaspora_country, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                talent_id, first_name, last_name, dob.strftime("%Y-%m-%d"), "Moroccan",
                position, club[0], club[1], potential, market_value, "ACTIVE",
                is_diaspora, diaspora_country, datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_transfers(cursor, count=30):
    """Generate transfer records"""
    print(f"  Generating {count} transfers...")
    
    transfer_types = ["Permanent", "Loan", "Free Transfer", "Youth"]
    statuses = ["Completed", "Pending", "Negotiating"]
    
    for i in range(count):
        transfer_id = generate_id("TRF")
        first_name = random.choice(MOROCCAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        player_name = f"{first_name} {last_name}"
        
        from_club = random.choice(CLUBS)
        to_club = random.choice([c for c in CLUBS if c != from_club])
        
        fee = random.randint(100000, 30000000)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO transfers
                (transfer_id, player_name, from_club, to_club, transfer_type,
                 transfer_fee, status, transfer_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transfer_id, player_name, from_club[0], to_club[0],
                random.choice(transfer_types), fee, random.choice(statuses),
                random_date(2024, 2025), datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_events_and_tickets(cursor, event_count=10, ticket_count=100):
    """Generate TicketChain events and tickets"""
    print(f"  Generating {event_count} events and {ticket_count} tickets...")
    
    event_ids = []
    
    # Create events
    for event in EVENT_NAMES[:event_count]:
        event_id = generate_id("EVT")
        event_ids.append((event_id, event))
        stadium = random.choice(STADIUMS)
        event_date = random_date(2025, 2030)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ticketchain_events
                (event_id, name, location, date, capacity, tickets_sold, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event_id, event, stadium[0], event_date,
                stadium[2], random.randint(0, stadium[2]//2),
                datetime.now().isoformat()
            ))
        except Exception as e:
            pass
    
    # Create tickets
    ticket_types = ["Standard", "Premium", "VIP", "Family"]
    statuses = ["VALID", "USED", "VALID"]
    
    for i in range(ticket_count):
        if not event_ids:
            break
            
        event_id, event_name = random.choice(event_ids)
        
        first_name = random.choice(MOROCCAN_FIRST_NAMES + EUROPEAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        owner_id = generate_id("USR")
        
        ticket_type = random.choice(ticket_types)
        prices = {"Standard": 500, "Premium": 1500, "VIP": 5000, "Family": 2000}
        
        # Generate blockchain hash
        hash_input = f"{event_id}{owner_id}{datetime.now()}{i}"
        ticket_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:32].upper()
        
        seat = f"Section {random.choice(['A','B','C','D'])}-Row {random.randint(1,50)}-Seat {random.randint(1,30)}"
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO ticketchain_tickets
                (ticket_hash, event_id, owner_id, seat_info, price, status, minted_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                ticket_hash, event_id, owner_id, seat,
                prices[ticket_type], random.choice(statuses),
                datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_wallets(cursor, count=40):
    """Generate Diaspora Wallets"""
    print(f"  Generating {count} wallets...")
    
    wallet_types = ["PERSONAL", "BUSINESS", "FAMILY"]
    
    for i in range(count):
        wallet_id = generate_id("WAL")
        first_name = random.choice(MOROCCAN_FIRST_NAMES + EUROPEAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        owner_name = f"{first_name} {last_name}"
        
        country = random.choice(DIASPORA_COUNTRIES)
        balance = random.randint(100, 50000)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO diaspora_wallets
                (wallet_id, owner_name, email, phone, country, wallet_type,
                 balance, currency, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wallet_id, owner_name, random_email(owner_name), random_phone(),
                country, random.choice(wallet_types), balance, "EUR", "ACTIVE",
                datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_identities(cursor, count=60):
    """Generate Identity Shield records"""
    print(f"  Generating {count} identities...")
    
    roles = ["User", "Investor", "Player", "Scout", "Agent", "Volunteer"]
    risk_levels = ["LOW", "LOW", "LOW", "MEDIUM", "MEDIUM", "HIGH"]
    
    for i in range(count):
        identity_id = generate_id("IDN")
        first_name = random.choice(MOROCCAN_FIRST_NAMES + EUROPEAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        country = random.choice(DIASPORA_COUNTRIES + ["Morocco"])
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO identity_shield
                (id, name, role, country, risk_level, fraud_score,
                 monitoring_enabled, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                identity_id, full_name, random.choice(roles), country,
                random.choice(risk_levels), random.randint(0, 30),
                1, datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_foundation(cursor, count=50):
    """Generate Foundation Bank contributions"""
    print(f"  Generating {count} foundation contributions...")
    
    source_types = ["TICKET", "TRANSFER", "SUBSCRIPTION", "DONATION"]
    
    for i in range(count):
        contribution_id = generate_id("FND")
        source_id = generate_id("SRC")
        amount = random.choice([5, 10, 25, 50, 100, 250, 500])
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO foundation_contributions
                (contribution_id, source_id, source_type, amount, auto_generated, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                contribution_id, source_id, random.choice(source_types),
                amount, 1, datetime.now().isoformat()
            ))
        except Exception as e:
            pass
    
    # Also generate donations
    for i in range(count // 2):
        donation_id = generate_id("DON")
        first_name = random.choice(MOROCCAN_FIRST_NAMES + EUROPEAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        donor_id = generate_id("USR")
        amount = random.choice([10, 25, 50, 100, 250, 500, 1000])
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO foundation_donations
                (donation_id, donor_identity_id, amount, donation_type, project, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                donation_id, donor_id, amount,
                random.choice(["One-time", "Monthly", "Annual"]),
                random.choice(["Youth Development", "Stadium Project", "Academy Fund", "General"]),
                datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_volunteers(cursor, count=40):
    """Generate FanDorpen volunteers"""
    print(f"  Generating {count} volunteers...")
    
    roles = ["Welkomst Coördinator", "Taalassistent", "Culturele Gids", 
             "Transport Helper", "Informatiebalie", "Veiligheidssteward"]
    languages = ["Arabic", "French", "Dutch", "English", "German", "Spanish"]
    statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "PENDING", "INACTIVE"]
    
    for i in range(count):
        volunteer_id = generate_id("VOL")
        first_name = random.choice(MOROCCAN_FIRST_NAMES + EUROPEAN_FIRST_NAMES)
        last_name = random.choice(MOROCCAN_LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        dual_nationality = random.choice(DIASPORA_COUNTRIES)
        city = random.choice(MOROCCAN_CITIES)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO fandorp_volunteers
                (volunteer_id, full_name, email, phone, dual_nationality,
                 languages, assigned_fandorp, role, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                volunteer_id, full_name, random_email(full_name), random_phone(),
                dual_nationality, ",".join(random.sample(languages, random.randint(2,4))),
                city, random.choice(roles), random.choice(statuses),
                datetime.now().isoformat()
            ))
        except Exception as e:
            pass

def generate_academies(cursor, count=10):
    """Generate Academy records"""
    print(f"  Generating {count} academies...")
    
    for i, name in enumerate(ACADEMY_NAMES[:count]):
        academy_id = generate_id("ACD")
        city = random.choice(MOROCCAN_CITIES)
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO academies
                (academy_id, name, city, region, academy_type, 
                 capacity, players_enrolled, certification_level, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                academy_id, name, city, "Casablanca-Settat",
                random.choice(["Youth Academy", "Professional Academy", "Development Center"]),
                random.randint(50, 200), random.randint(20, 150),
                random.choice(["Bronze", "Silver", "Gold", "Elite"]),
                "ACTIVE", datetime.now().isoformat()
            ))
        except Exception as e:
            pass

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def load_demo_data():
    """Load all demo data"""
    print("\n" + "="*60)
    print("ProInvestiX Demo Data Generator")
    print("="*60)
    print("\nLoading demo data...")
    
    # First initialize the database
    if not init_database():
        print("\n❌ Cannot proceed without database initialization")
        return
    
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        generate_talents(cursor, 50)
        generate_transfers(cursor, 30)
        generate_events_and_tickets(cursor, 10, 100)
        generate_wallets(cursor, 40)
        generate_identities(cursor, 60)
        generate_foundation(cursor, 50)
        generate_volunteers(cursor, 40)
        generate_academies(cursor, 10)
        
        conn.commit()
        
        print("\n" + "="*60)
        print("✅ Demo data loaded successfully!")
        print("="*60)
        print("\nSummary:")
        
        tables = [
            ("ntsp_talent_profiles", "Talents"),
            ("transfers", "Transfers"),
            ("ticketchain_tickets", "Tickets"),
            ("ticketchain_events", "Events"),
            ("diaspora_wallets", "Wallets"),
            ("identity_shield", "Identities"),
            ("foundation_contributions", "Contributions"),
            ("foundation_donations", "Donations"),
            ("fandorp_volunteers", "Volunteers"),
            ("academies", "Academies"),
        ]
        
        for table, name in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {name}: {count} records")
            except:
                print(f"  {name}: table not found")
        
        print("\nStart de app met: streamlit run app.py")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

def clear_demo_data():
    """Clear all demo data from database"""
    print("\n" + "="*60)
    print("Clearing demo data...")
    print("="*60)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    tables = [
        "ntsp_talent_profiles",
        "ntsp_evaluations",
        "transfers",
        "ticketchain_tickets",
        "ticketchain_events",
        "diaspora_wallets",
        "wallet_transactions",
        "identity_shield",
        "fraud_alerts",
        "foundation_contributions",
        "foundation_donations",
        "fandorp_volunteers",
        "fandorp_shifts",
        "fandorp_training",
        "academies",
        "fiscal_ledger",
    ]
    
    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"  Cleared: {table}")
        except Exception as e:
            pass
    
    conn.commit()
    conn.close()
    
    print("\n✅ All demo data cleared!")
    print("   User accounts are preserved.")

def reset_demo_data():
    """Clear and reload demo data"""
    clear_demo_data()
    load_demo_data()

# =============================================================================
# CLI
# =============================================================================

def print_usage():
    print("""
ProInvestiX Demo Data Generator
================================

Usage:
    python3 demo_data.py load     Load demo data
    python3 demo_data.py clear    Clear all demo data  
    python3 demo_data.py reset    Clear + Load (fresh start)
    
Examples:
    python3 demo_data.py load
    python3 demo_data.py clear
    python3 demo_data.py reset
""")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(0)
    
    command = sys.argv[1].lower()
    
    if command == "load":
        load_demo_data()
    elif command == "clear":
        clear_demo_data()
    elif command == "reset":
        reset_demo_data()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)
