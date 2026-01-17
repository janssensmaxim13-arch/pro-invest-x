# ============================================================================
# PROINVESTIX DEMO DATA GENERATOR v2
# ============================================================================

import sqlite3
import random
import uuid
import hashlib
import hmac
from datetime import datetime, timedelta

DB_FILE = "proinvestix_ultimate.db"
BLOCKCHAIN_SECRET = "DEMO_SECRET_KEY_2025"

# === NAME DATA ===
MOROCCAN_FIRST_NAMES_M = ["Mohammed", "Ahmed", "Youssef", "Amine", "Omar", "Hamza", "Adam", "Ayoub", "Zakaria", "Bilal", "Ismail", "Rachid", "Karim", "Mehdi", "Saad", "Othmane", "Walid", "Nabil", "Adil", "Khalid", "Soufiane", "Reda", "Younes", "Anass"]
MOROCCAN_FIRST_NAMES_F = ["Fatima", "Khadija", "Asmae", "Sanaa", "Nadia", "Laila", "Meryem", "Zineb", "Hajar", "Salma", "Imane", "Houda", "Sara", "Amina", "Yasmine", "Douae"]
MOROCCAN_LAST_NAMES = ["El Amrani", "Benali", "Tazi", "Alaoui", "El Idrissi", "Chaoui", "Bennani", "El Fassi", "Berrada", "Tahiri", "El Khatib", "Naciri", "Squalli", "Belhaj", "El Mansouri", "Chraibi", "Benkirane", "Lahlou", "El Ouafi", "Bouzid", "Ziani", "Hakimi", "Boufous", "Regragui", "Mazraoui", "Ziyech", "Amrabat", "Bounou", "Aguerd", "Ounahi"]

CLUBS_MOROCCO = [("Raja Casablanca", "Casablanca-Settat"), ("Wydad Casablanca", "Casablanca-Settat"), ("FAR Rabat", "Rabat-Salé-Kénitra"), ("AS FAR", "Rabat-Salé-Kénitra"), ("RS Berkane", "Oriental"), ("Hassania Agadir", "Souss-Massa"), ("Maghreb Fès", "Fès-Meknès"), ("FUS Rabat", "Rabat-Salé-Kénitra")]
CLUBS_EUROPE = [("Ajax Amsterdam", "Netherlands"), ("PSV Eindhoven", "Netherlands"), ("Feyenoord", "Netherlands"), ("Paris Saint-Germain", "France"), ("Olympique Lyon", "France"), ("Real Madrid", "Spain"), ("FC Barcelona", "Spain"), ("Chelsea FC", "England"), ("Bayern München", "Germany")]
POSITIONS = ["Goalkeeper", "Right Back", "Center Back", "Left Back", "Defensive Midfielder", "Central Midfielder", "Attacking Midfielder", "Right Winger", "Left Winger", "Striker"]
REGIONS = ["Casablanca-Settat", "Rabat-Salé-Kénitra", "Marrakech-Safi", "Fès-Meknès", "Tanger-Tétouan-Al Hoceïma", "Oriental", "Souss-Massa"]
DIASPORA_COUNTRIES = ["Netherlands", "Belgium", "France", "Spain", "Italy", "Germany"]

def gen_id(prefix): return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
def rand_date(y1, y2): return (datetime(y1,1,1) + timedelta(days=random.randint(0, (datetime(y2,12,31)-datetime(y1,1,1)).days))).strftime("%Y-%m-%d")
def rand_datetime(days=365): return (datetime.now() - timedelta(days=random.randint(0, days))).isoformat()
def gen_hash(data): return hmac.new(BLOCKCHAIN_SECRET.encode(), data.encode(), hashlib.sha256).hexdigest()

def run():
    print("\n" + "="*60)
    print(" PROINVESTIX DEMO DATA GENERATOR v2")
    print("="*60 + "\n")
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 1. TALENTS (500)
    print("Generating 500 talents...")
    talent_ids = []
    for i in range(500):
        tid = gen_id("NTSP")
        talent_ids.append(tid)
        is_diaspora = random.random() < 0.4
        is_female = random.random() < 0.15
        fn = random.choice(MOROCCAN_FIRST_NAMES_F if is_female else MOROCCAN_FIRST_NAMES_M)
        ln = random.choice(MOROCCAN_LAST_NAMES)
        birth_year = random.randint(1995, 2010)
        dob = rand_date(birth_year, birth_year)
        
        if is_diaspora:
            country = random.choice(DIASPORA_COUNTRIES)
            club, _ = random.choice(CLUBS_EUROPE)
            club_country = country
        else:
            country = "Morocco"
            club, region = random.choice(CLUBS_MOROCCO)
            club_country = "Morocco"
        
        score = random.randint(50, 90)
        potential = min(99, score + random.randint(5, 20))
        market = random.randint(10000, 5000000) if score > 70 else random.randint(5000, 200000)
        
        c.execute("""INSERT OR IGNORE INTO ntsp_talent_profiles 
            (talent_id, first_name, last_name, date_of_birth, place_of_birth, nationality, passport_number,
             is_diaspora, diaspora_country, speaks_arabic, speaks_french, email, phone, city, country,
             primary_position, secondary_position, preferred_foot, height_cm, weight_kg,
             current_club, current_club_country, current_league, contract_start, contract_end, jersey_number,
             talent_status, overall_score, potential_score, market_value_estimate,
             discovered_by, discovery_date, evaluation_count, priority_level,
             national_team_eligible, interest_in_morocco, created_at, created_by)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (tid, fn, ln, dob, random.choice(REGIONS), "Moroccan", f"MA{random.randint(10000000,99999999)}",
             1 if is_diaspora else 0, country if is_diaspora else None, 1, random.choice([0,1]),
             f"{fn.lower()}.{ln.lower().replace(' ','')}@email.com", f"+212 6{random.randint(10000000,99999999)}",
             random.choice(REGIONS).split("-")[0], country,
             random.choice(POSITIONS), random.choice(POSITIONS), random.choice(["RIGHT","LEFT","BOTH"]),
             random.randint(165,195), random.randint(60,90),
             club, club_country, "League", rand_date(2022,2024), rand_date(2025,2028),
             random.randint(1,99), random.choice(["PROSPECT","UNDER_EVALUATION","ACADEMY_READY","PROFESSIONAL"]),
             score, potential, market, gen_id("SCT"), rand_date(2020,2024), random.randint(1,10),
             random.choice(["LOW","NORMAL","HIGH"]), 1, 1 if is_diaspora else random.choice([0,1]),
             datetime.now().isoformat(), "system"))
    conn.commit()
    print(f"   {len(talent_ids)} talents created")
    
    # 2. ACADEMIES (25)
    print("Generating 25 academies...")
    academy_names = ["Raja Academy", "Wydad Academy", "FAR Academy", "Atlas Academy", "Phosphate Academy", 
                     "Royal Academy", "Future Stars", "Golden Boot", "Lions Academy", "Desert Eagles",
                     "Ocean Academy", "Mountain Stars", "Casablanca Elite", "Rabat Rising", "Marrakech Talents",
                     "Fes Future", "Tangier Tigers", "Agadir Aces", "Oujda Olympics", "Meknes Masters",
                     "Tetouan Titans", "Kenitra Kings", "Safi Stars", "Beni Mellal Best", "Laayoune Lions"]
    academy_ids = []
    for i, name in enumerate(academy_names):
        aid = gen_id("ACA")
        academy_ids.append(aid)
        region = REGIONS[i % len(REGIONS)]
        c.execute("""INSERT OR IGNORE INTO academies 
            (academy_id, name, short_name, region, city, country, academy_type, certification_level,
             parent_club, total_capacity, current_enrollment, num_pitches, has_gym,
             director_name, num_coaches, annual_budget, talents_produced, status, email, phone, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (aid, name, name[:3].upper(), region, region.split("-")[0], "Morocco",
             random.choice(["ELITE","REGIONAL","COMMUNITY"]), random.choice(["LEVEL_1","LEVEL_2","FIFA_CERTIFIED"]),
             random.choice([c[0] for c in CLUBS_MOROCCO]), random.randint(50,200), random.randint(20,150),
             random.randint(2,8), random.choice([0,1]), f"Dir. {random.choice(MOROCCAN_LAST_NAMES)}",
             random.randint(5,15), random.randint(100000,500000), random.randint(50,300), "ACTIVE",
             f"info@{name.lower().replace(' ','')}@ma", f"+212 5{random.randint(10000000,99999999)}",
             datetime.now().isoformat()))
    conn.commit()
    print(f"   {len(academy_ids)} academies created")
    
    # 3. TRANSFERS (50)
    print("Generating 50 transfers...")
    transfer_ids = []
    for tid in random.sample(talent_ids, 50):
        trf_id = gen_id("TRF")
        transfer_ids.append(trf_id)
        from_club = random.choice(CLUBS_MOROCCO + CLUBS_EUROPE)
        to_club = random.choice(CLUBS_MOROCCO + CLUBS_EUROPE)
        fee = random.choice([0, 50000, 100000, 500000, 1000000, 2500000])
        foundation = fee * 0.005
        c.execute("""INSERT OR IGNORE INTO transfers 
            (transfer_id, talent_id, from_club, from_club_country, to_club, to_club_country,
             transfer_type, transfer_date, contract_years, transfer_fee, training_compensation,
             solidarity_contribution, sell_on_percentage, agent_name, agent_fee,
             foundation_contribution, foundation_percentage, smart_contract_hash, transfer_status, created_at, created_by)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (trf_id, tid, from_club[0], from_club[1] if len(from_club)>1 else "Morocco",
             to_club[0], to_club[1] if len(to_club)>1 else "Morocco",
             random.choice(["PERMANENT","LOAN","FREE_TRANSFER"]), rand_date(2023,2025), random.randint(1,5),
             fee, random.randint(5000,50000), fee*0.05, random.randint(10,25),
             f"Agent {random.choice(MOROCCAN_LAST_NAMES)}", fee*0.05 if fee>0 else 0,
             foundation, 0.5, gen_hash(f"{tid}|{fee}"), "COMPLETED",
             datetime.now().isoformat(), "system"))
    conn.commit()
    print(f"   {len(transfer_ids)} transfers created")
    
    # 4. EVENTS & TICKETS
    print("Generating events and tickets...")
    events = [
        ("Raja vs Wydad - Derby", "Stade Mohammed V", 67000, 250),
        ("Morocco vs Egypt", "Stade Mohammed V", 67000, 300),
        ("WK 2030 Opening", "Grand Stade Casablanca", 93000, 500),
        ("FAR vs AS FAR", "Complexe Moulay Abdellah", 52000, 180),
        ("Cup Final 2025", "Stade Adrar", 45000, 200),
        ("Morocco vs Spain", "Ibn Batouta Tangier", 45000, 350),
        ("Raja vs Al Ahly CAF", "Stade Mohammed V", 67000, 220),
        ("Youth Cup Final", "Centre OCP", 20000, 50),
        ("Women's League Final", "Stade El Harti", 18000, 40),
        ("E-Sports Championship", "CGEM Center", 2000, 100),
    ]
    
    event_ids = []
    ticket_count = 0
    for name, location, capacity, price in events:
        eid = gen_id("EVT")
        event_ids.append(eid)
        sold = random.randint(int(capacity*0.4), int(capacity*0.9))
        c.execute("""INSERT OR IGNORE INTO ticketchain_events 
            (event_id, name, location, date, capacity, tickets_sold, mobility_enabled, timestamp)
            VALUES (?,?,?,?,?,?,?,?)""",
            (eid, name, location, rand_date(2025,2030), capacity, sold, random.choice([0,1]), datetime.now().isoformat()))
        
        for j in range(min(sold, 150)):
            thash = gen_hash(f"{eid}|{j}|{datetime.now().isoformat()}")
            seat = f"Section-{random.choice(['A','B','C','VIP'])}-R{random.randint(1,40)}-S{random.randint(1,25)}"
            tprice = price * (2 if 'VIP' in seat else 1)
            tax = tprice * 0.15
            foundation = tprice * 0.005
            c.execute("""INSERT OR IGNORE INTO ticketchain_tickets 
                (ticket_hash, event_id, owner_id, seat_info, price, status, minted_at, qr_generated)
                VALUES (?,?,?,?,?,?,?,?)""",
                (thash, eid, gen_id("FAN"), seat, tprice, random.choice(["VALID","VALID","USED"]), rand_datetime(180), 1))
            c.execute("""INSERT OR IGNORE INTO fiscal_ledger 
                (fiscal_id, ticket_hash, gross_amount, tax_amount, foundation_amount, net_amount, timestamp)
                VALUES (?,?,?,?,?,?,?)""",
                (gen_id("FSC"), thash, tprice, tax, foundation, tprice-tax-foundation, rand_datetime(180)))
            ticket_count += 1
    conn.commit()
    print(f"   {len(event_ids)} events, {ticket_count} tickets created")
    
    # 5. IDENTITIES (300)
    print("Generating 300 identities...")
    identity_ids = []
    for i in range(300):
        iid = gen_id("ID")
        identity_ids.append(iid)
        fn = random.choice(MOROCCAN_FIRST_NAMES_M + MOROCCAN_FIRST_NAMES_F)
        ln = random.choice(MOROCCAN_LAST_NAMES)
        c.execute("""INSERT OR IGNORE INTO identity_shield 
            (id, name, role, country, risk_level, fraud_score, monitoring_enabled, timestamp)
            VALUES (?,?,?,?,?,?,?,?)""",
            (iid, f"{fn} {ln}", random.choice(["Fan","Investor","Partner","Diaspora"]),
             random.choice(["Morocco"]*5 + DIASPORA_COUNTRIES),
             random.choices(["LOW","MEDIUM","HIGH"], weights=[70,25,5])[0],
             random.randint(0,50), 1, datetime.now().isoformat()))
    conn.commit()
    print(f"   {len(identity_ids)} identities created")
    
    # 6. DIASPORA WALLETS (200)
    print("Generating 200 wallets...")
    wallet_ids = []
    for iid in random.sample(identity_ids, 200):
        wid = gen_id("WLT")
        wallet_ids.append(wid)
        c.execute("""INSERT OR IGNORE INTO diaspora_wallets 
            (wallet_id, identity_id, wallet_address, wallet_type, balance_mad, balance_eur,
             loyalty_points, loyalty_tier, kyc_status, status, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (wid, iid, f"PIX-{uuid.uuid4().hex[:12].upper()}", "STANDARD",
             random.randint(100,50000), random.randint(10,5000),
             random.randint(0,500), random.choice(["BRONZE","SILVER","GOLD","DIAMOND"]),
             "VERIFIED", "ACTIVE", datetime.now().isoformat()))
        for _ in range(random.randint(3,10)):
            c.execute("""INSERT OR IGNORE INTO wallet_transactions 
                (transaction_id, wallet_id, transaction_type, amount, currency, status, reference, created_at)
                VALUES (?,?,?,?,?,?,?,?)""",
                (gen_id("TX"), wid, random.choice(["DEPOSIT","WITHDRAWAL","INVESTMENT"]),
                 random.randint(50,3000), "EUR", "COMPLETED", f"REF-{uuid.uuid4().hex[:8]}", rand_datetime(365)))
    conn.commit()
    print(f"   {len(wallet_ids)} wallets created")
    
    # 7. FINANCIAL + FOUNDATION + DONATIONS
    print("Generating financial data...")
    for i in range(200):
        c.execute("""INSERT OR IGNORE INTO financial_records 
            (id, entity_id, amount, type, sector, status, timestamp)
            VALUES (?,?,?,?,?,?,?)""",
            (gen_id("FIN"), random.choice(identity_ids), random.randint(1000,500000),
             random.choice(["Investment Inbound","Dividend Payout","Grant"]),
             random.choice(["Energy","Tech","Sports","Tourism"]), "Approved", rand_datetime(365)))
    for i in range(500):
        c.execute("""INSERT OR IGNORE INTO foundation_contributions 
            (contribution_id, source_id, source_type, amount, auto_generated, timestamp)
            VALUES (?,?,?,?,?,?)""",
            (gen_id("FND"), gen_id("SRC"), random.choice(["TRANSFER","TICKET","SUBSCRIPTION"]),
             random.randint(5,5000), 1, rand_datetime(365)))
    for i in range(100):
        c.execute("""INSERT OR IGNORE INTO foundation_donations 
            (donation_id, donor_identity_id, amount, donation_type, anonymous, created_at, receipt_sent)
            VALUES (?,?,?,?,?,?,?)""",
            (gen_id("DON"), random.choice(identity_ids) if random.random()<0.7 else None,
             random.randint(10,10000), random.choice(["General Fund","Youth Sports","Education"]),
             random.choice([0,1]), rand_datetime(365), 1))
    conn.commit()
    print("   Financial data created")
    
    # 8. AUDIT LOGS (1000)
    print("Generating 1000 audit logs...")
    for i in range(1000):
        c.execute("""INSERT OR IGNORE INTO audit_logs 
            (log_id, username, action, module, ip_address, success, timestamp)
            VALUES (?,?,?,?,?,?,?)""",
            (gen_id("LOG"), random.choice(["admin","scout_01","manager_01"]),
             random.choice(["LOGIN_SUCCESS","TALENT_CREATED","TICKET_MINTED"]),
             random.choice(["Authentication","NTSP","TicketChain"]), "127.0.0.1",
             1 if random.random()<0.95 else 0, rand_datetime(90)))
    conn.commit()
    print("   1000 audit logs created")
    
    # 9. EVALUATIONS (300)
    print("Generating 300 evaluations...")
    for tid in random.sample(talent_ids, 300):
        scores = {k: random.randint(45,95) for k in ['bc','pa','dr','sh','he','ft','sp','ac','st','sr','ju','ag','po','vi','co','le','wr','dm']}
        tech = sum([scores['bc'],scores['pa'],scores['dr'],scores['sh'],scores['he'],scores['ft']])/6
        phys = sum([scores['sp'],scores['ac'],scores['st'],scores['sr'],scores['ju'],scores['ag']])/6
        ment = sum([scores['po'],scores['vi'],scores['co'],scores['le'],scores['wr'],scores['dm']])/6
        overall = tech*0.4 + phys*0.3 + ment*0.3
        c.execute("""INSERT OR IGNORE INTO ntsp_evaluations 
            (evaluation_id, talent_id, scout_id, scout_name, evaluation_date, match_observed,
             score_ball_control, score_passing, score_dribbling, score_shooting, score_heading, score_first_touch,
             score_speed, score_acceleration, score_stamina, score_strength, score_jumping, score_agility,
             score_positioning, score_vision, score_composure, score_leadership, score_work_rate, score_decision_making,
             overall_technical, overall_physical, overall_mental, overall_score, potential_score,
             recommendation, strengths, weaknesses, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (gen_id("EVL"), tid, gen_id("SCT"), f"Scout {random.choice(MOROCCAN_LAST_NAMES)}",
             rand_date(2024,2025), f"Match vs {random.choice([c[0] for c in CLUBS_MOROCCO])}",
             scores['bc'],scores['pa'],scores['dr'],scores['sh'],scores['he'],scores['ft'],
             scores['sp'],scores['ac'],scores['st'],scores['sr'],scores['ju'],scores['ag'],
             scores['po'],scores['vi'],scores['co'],scores['le'],scores['wr'],scores['dm'],
             round(tech,1), round(phys,1), round(ment,1), round(overall,1), round(overall+random.randint(5,15),1),
             random.choice(["MONITOR","FOLLOW_UP","SIGN","ACADEMY"]), "Good technical skills", "Needs development",
             datetime.now().isoformat()))
    conn.commit()
    print("   300 evaluations created")
    
    # === FANDORPEN (WK2030 Supporter Governance) ===
    print("\n️ Generating FanDorpen data...")
    
    # FanDorpen tabellen aanmaken
    c.execute("""CREATE TABLE IF NOT EXISTS fandorpen (
        fandorp_id TEXT PRIMARY KEY, country_name TEXT NOT NULL, country_code TEXT NOT NULL,
        country_flag TEXT, location TEXT NOT NULL, languages TEXT, capacity INTEGER DEFAULT 500,
        coordinator_id TEXT, consulate_id TEXT, status TEXT DEFAULT 'ACTIVE',
        created_at TEXT, updated_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_volunteers (
        volunteer_id TEXT PRIMARY KEY, identity_id TEXT, first_name TEXT NOT NULL, last_name TEXT NOT NULL,
        email TEXT, phone TEXT, nationality_1 TEXT DEFAULT 'Moroccan', nationality_2 TEXT,
        languages TEXT, role TEXT, fandorp_id TEXT, clearance_level TEXT DEFAULT 'BASIC',
        verified INTEGER DEFAULT 0, background_check INTEGER DEFAULT 0, training_completed INTEGER DEFAULT 0,
        training_score INTEGER DEFAULT 0, badges TEXT, qr_code TEXT,
        status TEXT DEFAULT 'PENDING', registered_at TEXT, updated_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_shifts (
        shift_id TEXT PRIMARY KEY, volunteer_id TEXT NOT NULL, fandorp_id TEXT NOT NULL,
        shift_date TEXT NOT NULL, shift_type TEXT NOT NULL, start_time TEXT, end_time TEXT,
        status TEXT DEFAULT 'SCHEDULED', check_in TEXT, check_out TEXT, notes TEXT, created_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_incidents (
        incident_id TEXT PRIMARY KEY, fandorp_id TEXT NOT NULL, volunteer_id TEXT,
        incident_type TEXT NOT NULL, description TEXT, supporter_nationality TEXT,
        severity TEXT DEFAULT 'LOW', status TEXT DEFAULT 'OPEN', resolution TEXT,
        escalated_to TEXT, reported_at TEXT, resolved_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_services (
        service_id TEXT PRIMARY KEY, fandorp_id TEXT NOT NULL, volunteer_id TEXT,
        service_type TEXT NOT NULL, supporter_nationality TEXT, language_used TEXT,
        description TEXT, satisfaction_score INTEGER, served_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_training (
        training_id TEXT PRIMARY KEY, volunteer_id TEXT NOT NULL, module_name TEXT NOT NULL,
        module_type TEXT, score INTEGER, passed INTEGER DEFAULT 0, completed_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS fandorp_messages (
        message_id TEXT PRIMARY KEY, fandorp_id TEXT NOT NULL, sender_id TEXT NOT NULL,
        sender_name TEXT, message_type TEXT DEFAULT 'CHAT', content TEXT,
        priority TEXT DEFAULT 'NORMAL', read_by TEXT, created_at TEXT
    )""")
    
    # WK2030 Pilot landen
    PILOT_COUNTRIES = [
        ("België", "BE", "🇧🇪", "Casablanca", "Nederlands, Frans, Arabisch, Darija"),
        ("Nederland", "NL", "🇳🇱", "Rabat", "Nederlands, Arabisch, Darija"),
        ("Frankrijk", "FR", "🇫🇷", "Marrakech", "Frans, Arabisch, Darija"),
        ("Duitsland", "DE", "🇩🇪", "Tangier", "Duits, Arabisch, Darija"),
        ("Spanje", "ES", "🇪🇸", "Fes", "Spaans, Arabisch, Darija"),
        ("Engeland", "UK", "🇬🇧", "Agadir", "Engels, Arabisch, Darija"),
    ]
    
    VOLUNTEER_ROLES = ["Welkomst Coördinator", "Taalassistent", "Culturele Gids", "Transport Helper", 
                       "Informatiebalie", "Medische Liaison", "Veiligheidssteward", "Consulaat Liaison"]
    CLEARANCE_LEVELS = ["BASIC", "VERIFIED", "SENIOR", "COORDINATOR", "LIAISON"]
    TRAINING_MODULES = ["Welkom & Gastvrijheid", "Culturele Sensitiviteit", "Noodprocedures", 
                        "Taalvaardigheden", "Conflict Resolutie", "Medische Basis", "VIP Protocol"]
    BADGES = [" Welkomst Expert", " Cultureel Ambassadeur", " EHBO Certified", 
              "️ Meertalig", "⭐ Top Performer", "️ Veiligheid Pro", " VIP Service"]
    INCIDENT_TYPES = ["Verloren voorwerp", "Medische hulp", "Taalprobleem", "Vervoerprobleem",
                      "Accommodatie issue", "Ticket probleem", "Oplichting poging", "Cultureel misverstand"]
    SERVICE_TYPES = ["Informatie", "Vertaling", "Begeleiding", "Medische hulp", "Transport", "VIP Service"]
    
    # 6 FanDorpen aanmaken
    fandorp_ids = []
    for country_name, country_code, flag, location, languages in PILOT_COUNTRIES:
        fid = gen_id("FDP")
        fandorp_ids.append((fid, country_name, country_code))
        c.execute("""INSERT INTO fandorpen 
            (fandorp_id, country_name, country_code, country_flag, location, languages, capacity, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)""",
            (fid, country_name, country_code, flag, location, languages, random.randint(400, 800),
             datetime.now().isoformat(), datetime.now().isoformat()))
    print(f"   {len(PILOT_COUNTRIES)} FanDorpen created")
    
    # 200 Vrijwilligers genereren
    volunteer_ids = []
    for i in range(200):
        vid = gen_id("VOL")
        volunteer_ids.append(vid)
        fandorp = random.choice(fandorp_ids)
        fid, country_name, country_code = fandorp
        
        is_female = random.random() < 0.45
        fn = random.choice(MOROCCAN_FIRST_NAMES_F if is_female else MOROCCAN_FIRST_NAMES_M)
        ln = random.choice(MOROCCAN_LAST_NAMES)
        
        # Talen gebaseerd op tweede nationaliteit
        base_langs = ["Arabisch", "Darija"]
        if country_code == "BE":
            base_langs += ["Nederlands", "Frans"]
        elif country_code == "NL":
            base_langs += ["Nederlands"]
        elif country_code == "FR":
            base_langs += ["Frans"]
        elif country_code == "DE":
            base_langs += ["Duits"]
        elif country_code == "ES":
            base_langs += ["Spaans"]
        elif country_code == "UK":
            base_langs += ["Engels"]
        
        # Status en verificatie
        status = random.choices(["ACTIVE", "PENDING", "INACTIVE"], weights=[70, 25, 5])[0]
        verified = 1 if status == "ACTIVE" else random.choice([0, 1])
        bg_check = 1 if status == "ACTIVE" else random.choice([0, 1])
        training = 1 if status == "ACTIVE" and random.random() > 0.2 else 0
        training_score = random.randint(70, 100) if training else 0
        
        # Badges (alleen voor actieve getrainde vrijwilligers)
        earned_badges = random.sample(BADGES, random.randint(0, 4)) if training else []
        
        # QR code genereren
        qr_data = f"VOL-{vid}-{datetime.now().strftime('%Y%m%d')}"
        qr_code = gen_hash(qr_data)[:16].upper()
        
        c.execute("""INSERT INTO fandorp_volunteers 
            (volunteer_id, first_name, last_name, email, phone, nationality_1, nationality_2,
             languages, role, fandorp_id, clearance_level, verified, background_check,
             training_completed, training_score, badges, qr_code, status, registered_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'Moroccan', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (vid, fn, ln, f"{fn.lower()}.{ln.lower().replace(' ','')}@email.com", 
             f"+212 6{random.randint(10000000, 99999999)}",
             country_name, ", ".join(base_langs), random.choice(VOLUNTEER_ROLES), fid,
             random.choices(CLEARANCE_LEVELS, weights=[40, 30, 15, 10, 5])[0],
             verified, bg_check, training, training_score, ", ".join(earned_badges), qr_code,
             status, rand_datetime(180), datetime.now().isoformat()))
    print(f"   200 Vrijwilligers created")
    
    # Training records voor actieve vrijwilligers
    training_count = 0
    for vid in volunteer_ids[:150]:  # Eerste 150 vrijwilligers hebben training records
        modules_done = random.sample(TRAINING_MODULES, random.randint(3, 7))
        for mod in modules_done:
            score = random.randint(60, 100)
            c.execute("""INSERT INTO fandorp_training 
                (training_id, volunteer_id, module_name, module_type, score, passed, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (gen_id("TRN"), vid, mod, "ONLINE", score, 1 if score >= 70 else 0, rand_datetime(90)))
            training_count += 1
    print(f"   {training_count} Training records created")
    
    # Shifts genereren (voor komende 30 dagen)
    shift_count = 0
    for day_offset in range(30):
        shift_date = (datetime.now() + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        # 3-5 shifts per dag per FanDorp
        for fid, _, _ in fandorp_ids:
            active_vols = [vid for vid in volunteer_ids[:120]]  # Actieve vrijwilligers
            for _ in range(random.randint(3, 5)):
                vid = random.choice(active_vols)
                shift_type = random.choice(["OCHTEND", "MIDDAG", "AVOND", "WEDSTRIJD"])
                status = "COMPLETED" if day_offset < 0 else random.choice(["SCHEDULED", "CONFIRMED"])
                
                c.execute("""INSERT INTO fandorp_shifts 
                    (shift_id, volunteer_id, fandorp_id, shift_date, shift_type, start_time, end_time, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (gen_id("SHF"), vid, fid, shift_date, shift_type, 
                     "06:00" if shift_type == "OCHTEND" else "14:00" if shift_type == "MIDDAG" else "22:00",
                     "14:00" if shift_type == "OCHTEND" else "22:00" if shift_type == "MIDDAG" else "06:00",
                     status, datetime.now().isoformat()))
                shift_count += 1
    print(f"   {shift_count} Shifts created")
    
    # Incidenten genereren (50 incidenten)
    for _ in range(50):
        fid, country_name, _ = random.choice(fandorp_ids)
        vid = random.choice(volunteer_ids[:100])
        severity = random.choices(["LOW", "MEDIUM", "HIGH", "CRITICAL"], weights=[50, 30, 15, 5])[0]
        status = random.choices(["OPEN", "RESOLVED", "ESCALATED"], weights=[20, 70, 10])[0]
        
        c.execute("""INSERT INTO fandorp_incidents 
            (incident_id, fandorp_id, volunteer_id, incident_type, description, supporter_nationality,
             severity, status, resolution, reported_at, resolved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("INC"), fid, vid, random.choice(INCIDENT_TYPES),
             f"Incident reported at FanDorp {country_name}", country_name, severity, status,
             "Successfully resolved" if status == "RESOLVED" else None,
             rand_datetime(30), rand_datetime(15) if status == "RESOLVED" else None))
    print("   50 Incidents created")
    
    # Services log genereren (500 services)
    for _ in range(500):
        fid, country_name, _ = random.choice(fandorp_ids)
        vid = random.choice(volunteer_ids[:100])
        
        c.execute("""INSERT INTO fandorp_services 
            (service_id, fandorp_id, volunteer_id, service_type, supporter_nationality,
             language_used, description, satisfaction_score, served_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("SVC"), fid, vid, random.choice(SERVICE_TYPES), country_name,
             random.choice(["Nederlands", "Frans", "Duits", "Engels", "Spaans", "Arabisch"]),
             f"Service provided to {country_name} supporter", random.randint(3, 5), rand_datetime(30)))
    print("   500 Service records created")
    
    # Chat berichten genereren (100 berichten)
    for _ in range(100):
        fid, country_name, _ = random.choice(fandorp_ids)
        vid = random.choice(volunteer_ids[:50])
        fn = random.choice(MOROCCAN_FIRST_NAMES_M + MOROCCAN_FIRST_NAMES_F)
        ln = random.choice(MOROCCAN_LAST_NAMES)
        
        messages = [
            f"Shift update: alles onder controle bij ingang A",
            f"Vraag: waar is de dichtstbijzijnde EHBO post?",
            f"Supporter uit {country_name} zoekt vervoer naar stadion",
            f"VIP gasten aangekomen, begeleiding nodig",
            f"Vertaling nodig voor {random.choice(['Nederlands', 'Frans', 'Duits', 'Spaans'])} spreker",
            f"Alles rustig bij zone B, geen incidenten",
        ]
        
        c.execute("""INSERT INTO fandorp_messages 
            (message_id, fandorp_id, sender_id, sender_name, message_type, content, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("MSG"), fid, vid, f"{fn} {ln}", 
             random.choice(["CHAT", "ALERT", "UPDATE"]), random.choice(messages),
             random.choice(["NORMAL", "HIGH", "URGENT"]), rand_datetime(7)))
    print("   100 Chat messages created")
    
    # === MAROC ID SHIELD DATA ===
    print("\n️ Generating MAROC ID SHIELD data...")
    
    # Create MAROC ID tables
    c.execute("""CREATE TABLE IF NOT EXISTS maroc_identities (
        identity_id TEXT PRIMARY KEY, user_id TEXT, verification_level INTEGER DEFAULT 0,
        first_name TEXT, last_name TEXT, date_of_birth TEXT,
        nationality_primary TEXT, nationality_secondary TEXT, residence_country TEXT,
        phone TEXT, phone_verified INTEGER DEFAULT 0, email TEXT, email_verified INTEGER DEFAULT 0,
        device_id TEXT, device_bound_at TEXT,
        document_type TEXT, document_number TEXT, document_country TEXT, document_expiry TEXT,
        document_verified INTEGER DEFAULT 0, document_verified_at TEXT,
        liveness_check_passed INTEGER DEFAULT 0, liveness_checked_at TEXT,
        face_match_score REAL, biometric_hash TEXT,
        status TEXT DEFAULT 'PENDING', risk_score INTEGER DEFAULT 0,
        last_risk_assessment TEXT, watchlist_checked INTEGER DEFAULT 0,
        created_at TEXT, updated_at TEXT, verified_by TEXT, notes TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS maroc_organizations (
        org_id TEXT PRIMARY KEY, org_type TEXT NOT NULL, name TEXT NOT NULL,
        registration_number TEXT, registration_country TEXT,
        beneficial_owner_id TEXT, beneficial_owner_name TEXT, beneficial_owner_verified INTEGER DEFAULT 0,
        bank_account_iban TEXT, bank_verified INTEGER DEFAULT 0, licenses TEXT,
        verification_level INTEGER DEFAULT 1, verified INTEGER DEFAULT 0,
        verified_at TEXT, verified_by TEXT,
        status TEXT DEFAULT 'PENDING', risk_score INTEGER DEFAULT 0,
        created_at TEXT, updated_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS maroc_role_certificates (
        cert_id TEXT PRIMARY KEY, identity_id TEXT NOT NULL, org_id TEXT,
        role_type TEXT NOT NULL, role_name TEXT,
        permissions TEXT, restrictions TEXT, max_transaction_amount REAL,
        issued_at TEXT, valid_from TEXT, valid_until TEXT, status TEXT DEFAULT 'ACTIVE',
        required_level INTEGER, issued_by TEXT,
        revoked_at TEXT, revoked_by TEXT, revocation_reason TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS maroc_pma_queue (
        pma_id TEXT PRIMARY KEY, entity_type TEXT NOT NULL, entity_id TEXT NOT NULL,
        transaction_type TEXT, amount REAL, currency TEXT DEFAULT 'EUR',
        source TEXT, destination TEXT, description TEXT,
        risk_score INTEGER DEFAULT 0, risk_factors TEXT, auto_approved INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING_REVIEW', reviewed_by TEXT, reviewed_at TEXT, review_notes TEXT,
        created_at TEXT, processed_at TEXT
    )""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS maroc_transaction_signatures (
        sig_id TEXT PRIMARY KEY, identity_id TEXT NOT NULL,
        transaction_type TEXT NOT NULL, transaction_id TEXT, transaction_data TEXT,
        signature_hash TEXT, signed_at TEXT, device_id TEXT, biometric_confirmed INTEGER DEFAULT 0,
        status TEXT DEFAULT 'PENDING', approved_at TEXT, rejected_at TEXT, rejection_reason TEXT,
        requires_second_approval INTEGER DEFAULT 0, second_approver_id TEXT, second_approved_at TEXT
    )""")
    
    VERIFICATION_LEVELS = [0, 1, 2, 3]
    DOCUMENT_TYPES = ["CNIE", "PASSPORT_MA", "PASSPORT_EU", "PASSPORT_OTHER"]
    ORG_TYPES = ["CLUB", "FEDERATION", "ACADEMY", "SPONSOR", "SUPPLIER", "CONSULATE", "FOUNDATION"]
    ROLE_TYPES = ["VOLUNTEER", "STEWARD", "OFFICIAL", "DONOR", "AGENT", "CLUB_MANAGER", "SCOUT"]
    PMA_STATUSES = ["PENDING_REVIEW", "APPROVED", "FLAGGED", "BLOCKED", "MANUAL_REVIEW"]
    TX_TYPES = ["TRANSFER", "PAYMENT", "CONTRACT", "DONATION", "INVESTMENT"]
    
    # Generate 500 identities
    identity_ids = []
    for i in range(500):
        mid = gen_id("MID")
        identity_ids.append(mid)
        
        is_female = random.random() < 0.35
        fn = random.choice(MOROCCAN_FIRST_NAMES_F if is_female else MOROCCAN_FIRST_NAMES_M)
        ln = random.choice(MOROCCAN_LAST_NAMES)
        
        level = random.choices([0, 1, 2, 3], weights=[10, 30, 45, 15])[0]
        status = "VERIFIED" if level >= 2 else random.choice(["PENDING", "VERIFIED"])
        risk = random.randint(0, 100) if random.random() < 0.1 else random.randint(0, 40)
        
        # Higher levels have more verifications
        phone_verified = 1 if level >= 1 else random.choice([0, 1])
        email_verified = 1 if level >= 1 else random.choice([0, 1])
        doc_verified = 1 if level >= 2 else random.choice([0, 1])
        liveness = 1 if level >= 2 else 0
        
        c.execute("""INSERT INTO maroc_identities 
            (identity_id, first_name, last_name, date_of_birth, nationality_primary, nationality_secondary,
             residence_country, phone, phone_verified, email, email_verified,
             document_type, document_number, document_verified, liveness_check_passed,
             face_match_score, verification_level, status, risk_score, watchlist_checked,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (mid, fn, ln, rand_date(1970, 2005), "Moroccan",
             random.choice(["Dutch", "Belgian", "French", "Spanish", "German", None]),
             random.choice(DIASPORA_COUNTRIES + ["Morocco"]),
             f"+212 6{random.randint(10000000, 99999999)}", phone_verified,
             f"{fn.lower()}.{ln.lower().replace(' ','')}@email.com", email_verified,
             random.choice(DOCUMENT_TYPES), f"MA{random.randint(100000, 999999)}", doc_verified, liveness,
             round(random.uniform(0.85, 0.99), 2) if liveness else None,
             level, status, risk, 1 if level >= 2 else 0,
             rand_datetime(365), datetime.now().isoformat()))
    print(f"   500 MAROC ID identities created")
    
    # Generate 50 organizations
    org_ids = []
    org_names = ["Raja Casablanca", "Wydad AC", "AS FAR", "RS Berkane", "FUS Rabat",
                 "MAS Agency", "Atlas Logistics", "Sahara Sports", "Maghreb Media", "Rif Foundation",
                 "Tanger Tech", "Casa Finance", "Rabat Events", "Marrakech Tours", "Agadir Sports"]
    
    for i, org_name in enumerate(org_names * 3 + org_names[:5]):
        oid = gen_id("ORG")
        org_ids.append(oid)
        
        verified = random.choice([0, 1, 1, 1])
        
        c.execute("""INSERT INTO maroc_organizations 
            (org_id, org_type, name, registration_number, registration_country,
             beneficial_owner_name, bank_account_iban, verification_level, verified,
             status, risk_score, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (oid, random.choice(ORG_TYPES), f"{org_name} {i+1}" if i >= 15 else org_name,
             f"RC{random.randint(10000, 99999)}", "Morocco",
             f"{random.choice(MOROCCAN_FIRST_NAMES_M)} {random.choice(MOROCCAN_LAST_NAMES)}",
             f"MA{random.randint(10, 99)} {random.randint(1000, 9999)} {random.randint(1000, 9999)} {random.randint(1000, 9999)}",
             random.choice([1, 2, 2, 3]), verified,
             "VERIFIED" if verified else "PENDING", random.randint(0, 30),
             rand_datetime(365), datetime.now().isoformat()))
    print(f"   {len(org_ids)} Organizations created")
    
    # Generate 200 role certificates
    for _ in range(200):
        c.execute("""INSERT INTO maroc_role_certificates 
            (cert_id, identity_id, org_id, role_type, role_name, max_transaction_amount,
             issued_at, valid_from, valid_until, status, required_level, issued_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("CRT"), random.choice(identity_ids), random.choice(org_ids),
             random.choice(ROLE_TYPES), None, random.choice([5000, 10000, 50000, 100000]),
             rand_datetime(180), rand_datetime(180), 
             (datetime.now() + timedelta(days=random.randint(30, 365))).isoformat(),
             random.choices(["ACTIVE", "REVOKED", "EXPIRED"], weights=[85, 10, 5])[0],
             random.choice([2, 2, 3]), "SYSTEM"))
    print("   200 Role certificates created")
    
    # Generate 300 PMA entries
    for _ in range(300):
        auto = random.random() < 0.6
        status = "APPROVED" if auto else random.choice(PMA_STATUSES)
        
        c.execute("""INSERT INTO maroc_pma_queue 
            (pma_id, entity_type, entity_id, transaction_type, amount, source, destination,
             description, risk_score, auto_approved, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("PMA"), random.choice(["PERSON", "ORGANIZATION", "TRANSACTION"]),
             random.choice(identity_ids + org_ids), random.choice(TX_TYPES),
             round(random.uniform(100, 50000), 2),
             random.choice(["Morocco", "Netherlands", "Belgium", "France"]),
             random.choice(["Morocco", "Netherlands", "Belgium", "France"]),
             f"Transaction for {random.choice(['transfer', 'payment', 'contract', 'donation'])}",
             random.randint(5, 80), 1 if auto else 0, status, rand_datetime(60)))
    print("   300 PMA entries created")
    
    # Generate 150 transaction signatures
    for _ in range(150):
        sig_data = f"TX-{random.randint(1000, 9999)}-{datetime.now().strftime('%Y%m%d')}"
        sig_hash = gen_hash(sig_data)
        
        c.execute("""INSERT INTO maroc_transaction_signatures 
            (sig_id, identity_id, transaction_type, transaction_id, transaction_data,
             signature_hash, signed_at, biometric_confirmed, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (gen_id("SIG"), random.choice(identity_ids[:200]),
             random.choice(["CONTRACT_SIGN", "TRANSFER_APPROVE", "FOUNDATION_DONATION_LARGE", "ROLE_ASSIGNMENT"]),
             gen_id("TXN"), f'{{"amount": {random.randint(500, 10000)}}}',
             sig_hash, rand_datetime(90), 1, random.choice(["SIGNED", "APPROVED", "PENDING"])))
    print("   150 Transaction signatures created")
    
    # =========================================================================
    # NIL - NARRATIVE INTEGRITY LAYER (Dossier 28)
    # =========================================================================
    print("\nGenerating NIL data...")
    
    # NIL Sources (20)
    nil_sources = []
    source_names = [
        ("FootballLeaks_MA", "TWITTER", "BLACKLISTED"),
        ("TruthAboutFRMF", "FACEBOOK", "HIGH_RISK"),
        ("VAR_Watch_Official", "INSTAGRAM", "SUSPICIOUS"),
        ("MoroccoSports24", "TWITTER", "NEUTRAL"),
        ("DiasporaNewsMA", "FACEBOOK", "TRUSTED"),
        ("AtlasLionsFan", "TIKTOK", "NEUTRAL"),
        ("BotolaInsider", "TWITTER", "SUSPICIOUS"),
        ("WK2030Updates", "INSTAGRAM", "TRUSTED"),
        ("FRMF_Official", "TWITTER", "TRUSTED"),
        ("SportMaroc", "YOUTUBE", "TRUSTED"),
        ("FakeNewsAlert_MA", "TELEGRAM", "BLACKLISTED"),
        ("MatchFixingProof", "TWITTER", "HIGH_RISK"),
        ("RefereeWatch", "INSTAGRAM", "SUSPICIOUS"),
        ("TransferRumors_MA", "FACEBOOK", "NEUTRAL"),
        ("WK2030Critic", "TWITTER", "SUSPICIOUS"),
        ("MoroccoFootballFans", "FACEBOOK", "TRUSTED"),
        ("BotolaTV", "YOUTUBE", "TRUSTED"),
        ("SportsAnalystMA", "TWITTER", "NEUTRAL"),
        ("FootballTruthMA", "TELEGRAM", "HIGH_RISK"),
        ("OfficialBotola", "INSTAGRAM", "TRUSTED"),
    ]
    for name, platform, risk in source_names:
        sid = gen_id("SRC")
        nil_sources.append(sid)
        credibility = 85 if risk == "TRUSTED" else 50 if risk == "NEUTRAL" else 25 if risk == "SUSPICIOUS" else 10
        c.execute("""INSERT OR IGNORE INTO nil_sources 
            (source_id, platform, account_name, account_handle, account_url, followers, credibility_score,
             risk_category, is_verified, is_official, is_media, is_bot_suspected,
             fake_content_count, verified_content_count, incidents_count,
             first_seen_at, last_activity_at, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sid, platform, name, f"@{name.lower().replace('_','')}", f"https://{platform.lower()}.com/{name}",
             random.randint(5000, 500000), credibility, risk,
             1 if risk == "TRUSTED" else 0, 1 if "Official" in name else 0, 1 if risk == "TRUSTED" else 0,
             1 if risk in ["BLACKLISTED", "HIGH_RISK"] else 0,
             random.randint(0, 50) if risk != "TRUSTED" else 0,
             random.randint(10, 100) if risk == "TRUSTED" else random.randint(0, 20),
             random.randint(0, 30),
             rand_datetime(365), rand_datetime(30), datetime.now().isoformat()))
    print(f"   {len(nil_sources)} NIL sources created")
    
    # NIL Signals (50)
    nil_signals = []
    signal_titles = [
        "Zidane breaks silence on Morocco return - FULL STORY",
        "VAR controversy PROOF - Match was fixed!",
        "BREAKING: FRMF corruption scandal exposed",
        "Referee admits to match manipulation",
        "WK 2030 budget fraud revealed - Documents leaked",
        "Star player threatens to leave national team",
        "Secret meeting between officials leaked on video",
        "Major sponsor withdraws due to controversy",
        "Fake interview goes viral - Player denies everything",
        "Coordinated bot attack targets Moroccan football",
        "Transfer deal collapse - Inside story",
        "Coach resignation rumors spread online",
        "Stadium safety concerns raised by fake report",
        "National team selection controversy",
        "Agent corruption allegations surface",
    ]
    manipulation_types = ["FAKE_QUOTE", "EDITED_CLIP", "DEEPFAKE", "BOT_ATTACK", "IMPERSONATION", 
                          "CONTEXT_MANIPULATION", "COORDINATED_CAMPAIGN", "REFEREE_HARASSMENT", 
                          "FALSE_NEWS", "IMAGE_MANIPULATION", "MISINFORMATION"]
    platforms = ["FACEBOOK", "INSTAGRAM", "TWITTER", "TIKTOK", "YOUTUBE", "WHATSAPP", "TELEGRAM"]
    risk_levels = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    statuses = ["DETECTED", "TRIAGING", "INVESTIGATING", "FACT_CARD_ISSUED", "ESCALATED", "RESOLVED", "MONITORING", "DISMISSED"]
    
    for i in range(50):
        sig_id = gen_id("SIG")
        nil_signals.append(sig_id)
        risk = random.choice(risk_levels)
        status = random.choice(statuses)
        c.execute("""INSERT OR IGNORE INTO nil_signals 
            (signal_id, platform, content_url, content_type, title, description,
             manipulation_type, risk_level, confidence_score,
             views, likes, shares, comments, engagement_velocity,
             source_account, source_id, source_followers,
             status, priority, detected_at, created_by, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (sig_id, random.choice(platforms), f"https://example.com/post/{random.randint(10000,99999)}",
             random.choice(["VIDEO", "IMAGE", "TEXT", "AUDIO"]), random.choice(signal_titles),
             "Suspicious content detected requiring investigation",
             random.choice(manipulation_types), risk, random.randint(40, 95),
             random.randint(1000, 500000), random.randint(100, 50000),
             random.randint(50, 25000), random.randint(10, 5000),
             random.uniform(0.5, 10.0),
             f"@suspicious_account_{random.randint(100,999)}", random.choice(nil_sources),
             random.randint(1000, 100000),
             status, random.choice(["STANDARD", "URGENT", "CRISIS"]),
             rand_datetime(30), "system", datetime.now().isoformat()))
    print(f"   {len(nil_signals)} NIL signals created")
    
    # NIL Evidence (30)
    for i in range(30):
        eid = gen_id("EVD")
        content_hash = gen_hash(f"evidence_{i}_{datetime.now()}")
        blockchain_tx = gen_hash(f"blockchain_{eid}_{content_hash}")
        c.execute("""INSERT OR IGNORE INTO nil_evidence 
            (evidence_id, signal_id, content_hash, original_url, raw_content,
             archive_status, hash_algorithm, blockchain_tx,
             manipulation_confirmed, manipulation_type, legal_value,
             captured_at, created_by, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (eid, random.choice(nil_signals), content_hash,
             f"https://example.com/content/{random.randint(10000,99999)}",
             "Archived content for legal evidence",
             random.choice(["ARCHIVED", "PROCESSING", "VERIFIED"]), "SHA256", blockchain_tx,
             random.choice([0, 1]), random.choice(manipulation_types),
             random.choice(["LOW", "MEDIUM", "HIGH"]),
             rand_datetime(60), "system", datetime.now().isoformat()))
    print("   30 NIL evidence entries created")
    
    # NIL Fact Cards (20)
    for i in range(20):
        fcid = gen_id("FC")
        c.execute("""INSERT OR IGNORE INTO nil_fact_cards 
            (fact_card_id, signal_id, incident_title, verified_facts, false_claims,
             official_source_url, additional_context, response_level, language,
             published, views, shares, created_by, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (fcid, random.choice(nil_signals),
             f"Fact Card: {random.choice(signal_titles)[:40]}",
             "The official statement confirms that the reported incident did not occur as described. All relevant parties have been contacted and verified the information.",
             "The viral post contained manipulated content, including edited timestamps and fabricated quotes that were never made by the alleged source.",
             "https://frmf.ma/official-statement", "This fact card was issued in response to viral misinformation.",
             random.choice(["STANDARD", "URGENT", "CRISIS"]), random.choice(["en", "fr", "ar"]),
             random.choice([0, 1]), random.randint(1000, 50000), random.randint(100, 5000),
             "system", datetime.now().isoformat()))
    print("   20 NIL fact cards created")
    
    # NIL Crisis Incidents (5)
    crisis_names = [
        "VAR Controversy Match 15",
        "Fake Interview Viral Campaign",
        "Sponsor Withdrawal Rumors",
        "Coach Resignation False Report",
        "Stadium Safety Misinformation"
    ]
    for i, name in enumerate(crisis_names):
        cid = gen_id("CRI")
        level = random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        c.execute("""INSERT OR IGNORE INTO nil_crisis_incidents 
            (incident_id, incident_name, description, crisis_level, category,
             status, incident_lead, detected_at, created_by, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (cid, name, f"Crisis incident requiring immediate attention: {name}",
             level, random.choice(["Content Crisis", "Security Threat", "Reputation Risk", "Sponsor Issue"]),
             random.choice(["OPEN", "RESOLVED"]), "admin",
             rand_datetime(30), "system", datetime.now().isoformat()))
    print("   5 NIL crisis incidents created")
    
    conn.commit()
    
    # === SUMMARY ===
    print("\n" + "="*60)
    print(" DEMO DATA GENERATION COMPLETE!")
    print("="*60)
    
    tables = ["ntsp_talent_profiles", "academies", "transfers", "ticketchain_events", 
              "ticketchain_tickets", "identity_shield", "diaspora_wallets", "wallet_transactions",
              "financial_records", "foundation_contributions", "foundation_donations", 
              "audit_logs", "ntsp_evaluations", "fandorpen", "fandorp_volunteers", 
              "fandorp_shifts", "fandorp_incidents", "fandorp_services", "fandorp_training", "fandorp_messages",
              "maroc_identities", "maroc_organizations", "maroc_role_certificates", 
              "maroc_pma_queue", "maroc_transaction_signatures",
              "nil_signals", "nil_sources", "nil_evidence", "nil_fact_cards", "nil_crisis_incidents"]
    
    print("\n FINAL COUNTS:")
    for t in tables:
        try:
            c.execute(f"SELECT COUNT(*) FROM {t}")
            print(f"  {t}: {c.fetchone()[0]:,}")
        except:
            pass
    
    c.execute("SELECT SUM(transfer_fee) FROM transfers")
    print(f"\n Transfer Volume: €{(c.fetchone()[0] or 0):,.0f}")
    c.execute("SELECT SUM(amount) FROM foundation_contributions")
    print(f" Foundation Pool: €{(c.fetchone()[0] or 0):,.0f}")
    c.execute("SELECT SUM(gross_amount) FROM fiscal_ledger")
    print(f" Ticket Revenue: €{(c.fetchone()[0] or 0):,.0f}")
    
    conn.close()
    print("\n Database ready for investor demo!\n")

if __name__ == "__main__":
    run()
