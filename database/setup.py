# ============================================================================
# DATABASE SETUP - UITGEBREID VOOR MASTERPLAN
# Inclusief: NTSP™, Transfer Management, Academy, Diaspora Wallet, Mobility
# ============================================================================

import sqlite3
from datetime import datetime
from config import DB_FILE, VAULT_DIR
import os

# Probeer bcrypt te importeren
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    import hashlib


def init_db():
    """Initialiseer de database met alle tabellen en indexes."""
    
    # Maak vault directory als die niet bestaat
    if not os.path.exists(VAULT_DIR):
        os.makedirs(VAULT_DIR)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # =========================================================================
    # BESTAANDE TABELLEN (CORE SYSTEM)
    # =========================================================================
    
    # --- AUTHENTICATIE ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_registry (
            username TEXT PRIMARY KEY, 
            password_hash TEXT NOT NULL, 
            role TEXT NOT NULL, 
            email TEXT,
            active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            last_login TEXT
        )
    ''')
    
    # Default admin account aanmaken
    cursor.execute("SELECT * FROM user_registry WHERE username = 'admin'")
    if not cursor.fetchone():
        if BCRYPT_AVAILABLE:
            admin_hash = bcrypt.hashpw(
                "admin123".encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
        else:
            admin_hash = hashlib.sha256("admin123".encode()).hexdigest()
        
        cursor.execute(
            "INSERT INTO user_registry VALUES (?, ?, ?, ?, ?, ?, ?)", 
            ("admin", admin_hash, "SuperAdmin", "admin@proinvestix.ma", 
             1, datetime.now().isoformat(), None)
        )
    
    # --- IDENTITY SHIELD ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS identity_shield (
            id TEXT PRIMARY KEY, 
            name TEXT NOT NULL, 
            role TEXT NOT NULL, 
            country TEXT, 
            risk_level TEXT DEFAULT 'LOW',
            fraud_score INTEGER DEFAULT 0,
            monitoring_enabled INTEGER DEFAULT 1,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # --- CONSULAAT ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consular_registry (
            id TEXT PRIMARY KEY, 
            doc_type TEXT, 
            filename TEXT, 
            status TEXT, 
            timestamp TEXT
        )
    ''')
    
    # --- FINANCIEEL ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financial_records (
            id TEXT PRIMARY KEY, 
            entity_id TEXT, 
            amount REAL, 
            type TEXT, 
            sector TEXT, 
            status TEXT, 
            timestamp TEXT
        )
    ''')
    
    # --- FOUNDATION CONTRIBUTIONS (MASTERPLAN 0.5%) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foundation_contributions (
            contribution_id TEXT PRIMARY KEY,
            source_id TEXT NOT NULL,
            source_type TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            auto_generated INTEGER DEFAULT 1,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # --- SPORT RECORDS (BASIS) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sport_records (
            id TEXT PRIMARY KEY, 
            identity_id TEXT, 
            discipline TEXT, 
            club TEXT, 
            status TEXT, 
            contract_end TEXT, 
            timestamp TEXT
        )
    ''')
    
    # --- MOBILITEIT ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mobility_records (
            id TEXT PRIMARY KEY, 
            asset_name TEXT, 
            type TEXT, 
            region TEXT, 
            status TEXT, 
            last_maint TEXT, 
            timestamp TEXT
        )
    ''')
    
    # --- GEZONDHEID ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_records (
            id TEXT PRIMARY KEY, 
            identity_id TEXT, 
            checkup_type TEXT, 
            medical_status TEXT, 
            expiry_date TEXT, 
            timestamp TEXT
        )
    ''')
    
    # --- TICKETCHAIN EVENTS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticketchain_events (
            event_id TEXT PRIMARY KEY, 
            name TEXT NOT NULL, 
            location TEXT NOT NULL, 
            date TEXT NOT NULL, 
            capacity INTEGER NOT NULL, 
            tickets_sold INTEGER DEFAULT 0,
            mobility_enabled INTEGER DEFAULT 0,
            mobility_options TEXT,
            diaspora_package_enabled INTEGER DEFAULT 0,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # --- TICKETCHAIN TICKETS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticketchain_tickets (
            ticket_hash TEXT PRIMARY KEY, 
            event_id TEXT NOT NULL, 
            owner_id TEXT NOT NULL, 
            seat_info TEXT NOT NULL, 
            price REAL NOT NULL, 
            status TEXT NOT NULL DEFAULT 'VALID', 
            minted_at TEXT NOT NULL,
            used_at TEXT,
            qr_generated INTEGER DEFAULT 1,
            mobility_booking_id TEXT,
            diaspora_package_id TEXT,
            UNIQUE(event_id, seat_info)
        )
    ''')
    
    # --- FISCAL LEDGER ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiscal_ledger (
            fiscal_id TEXT PRIMARY KEY, 
            ticket_hash TEXT, 
            gross_amount REAL, 
            tax_amount REAL,
            foundation_amount REAL,
            net_amount REAL, 
            timestamp TEXT
        )
    ''')
    
    # --- SCHOLARSHIPS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scholarship_applications (
            application_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            scholarship_type TEXT NOT NULL,
            university TEXT,
            field_of_study TEXT,
            status TEXT DEFAULT 'PENDING',
            amount_requested REAL,
            amount_approved REAL,
            submitted_at TEXT NOT NULL,
            reviewed_at TEXT,
            reviewer TEXT
        )
    ''')
    
    # --- CONSULAIRE ASSISTENTIE ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consular_assistance (
            ticket_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            assistance_type TEXT NOT NULL,
            description TEXT,
            urgency TEXT DEFAULT 'MEDIUM',
            status TEXT DEFAULT 'OPEN',
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            assigned_to TEXT
        )
    ''')
    
    # --- LOYALTY POINTS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS loyalty_points (
            points_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            points_balance INTEGER DEFAULT 0,
            tier TEXT DEFAULT 'BRONZE',
            tickets_purchased INTEGER DEFAULT 0,
            last_activity TEXT
        )
    ''')
    
    # --- MOBILITY BOOKINGS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mobility_bookings (
            booking_id TEXT PRIMARY KEY,
            ticket_hash TEXT,
            identity_id TEXT NOT NULL,
            transport_type TEXT NOT NULL,
            departure_location TEXT,
            arrival_location TEXT,
            departure_time TEXT,
            route TEXT,
            price REAL DEFAULT 0,
            booking_status TEXT DEFAULT 'CONFIRMED',
            created_at TEXT NOT NULL
        )
    ''')
    
    # --- FOUNDATION DONATIES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS foundation_donations (
            donation_id TEXT PRIMARY KEY,
            donor_identity_id TEXT,
            amount REAL NOT NULL,
            donation_type TEXT,
            project TEXT,
            anonymous INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            receipt_sent INTEGER DEFAULT 0
        )
    ''')
    
    # --- FRAUD ALERTS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fraud_alerts (
            alert_id TEXT PRIMARY KEY,
            identity_id TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'MEDIUM',
            description TEXT,
            auto_detected INTEGER DEFAULT 1,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            resolved_at TEXT
        )
    ''')
    
    # --- AUDIT LOGS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            action TEXT NOT NULL,
            module TEXT,
            ip_address TEXT,
            success INTEGER DEFAULT 1,
            details TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # --- API ACCESS LOG ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_access_log (
            log_id TEXT PRIMARY KEY,
            api_key TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            method TEXT,
            status_code INTEGER,
            response_time_ms INTEGER,
            timestamp TEXT NOT NULL
        )
    ''')
    
    # =========================================================================
    # NTSP™ - NATIONAAL TALENT SCOUTING PLATFORM (DOSSIER 1)
    # =========================================================================
    
    # --- TALENT PROFIELEN (Kern van NTSP™) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_talent_profiles (
            talent_id TEXT PRIMARY KEY,
            
            -- Persoonlijke gegevens
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT NOT NULL,
            place_of_birth TEXT,
            nationality TEXT NOT NULL,
            dual_nationality TEXT,
            passport_number TEXT,
            
            -- Diaspora gegevens
            is_diaspora INTEGER DEFAULT 0,
            diaspora_country TEXT,
            diaspora_city TEXT,
            years_abroad INTEGER,
            speaks_arabic INTEGER DEFAULT 0,
            speaks_french INTEGER DEFAULT 0,
            speaks_other_languages TEXT,
            
            -- Contact
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            
            -- Familie contact (voor jeugd)
            parent_name TEXT,
            parent_phone TEXT,
            parent_email TEXT,
            family_contact_preference TEXT,
            
            -- Voetbal gegevens
            primary_position TEXT NOT NULL,
            secondary_position TEXT,
            preferred_foot TEXT DEFAULT 'RIGHT',
            height_cm INTEGER,
            weight_kg INTEGER,
            
            -- Huidige club/situatie
            current_club TEXT,
            current_club_country TEXT,
            current_league TEXT,
            contract_start TEXT,
            contract_end TEXT,
            jersey_number INTEGER,
            
            -- Status en scores
            talent_status TEXT DEFAULT 'PROSPECT',
            overall_score REAL DEFAULT 0,
            potential_score REAL DEFAULT 0,
            market_value_estimate REAL DEFAULT 0,
            
            -- Scouts en evaluaties
            discovered_by TEXT,
            discovery_date TEXT,
            last_evaluation_date TEXT,
            evaluation_count INTEGER DEFAULT 0,
            
            -- Flags en notities
            priority_level TEXT DEFAULT 'NORMAL',
            national_team_eligible INTEGER DEFAULT 1,
            interest_in_morocco INTEGER DEFAULT 0,
            notes TEXT,
            
            -- Media
            photo_url TEXT,
            video_highlights_url TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            created_by TEXT
        )
    ''')
    
    # --- TALENT EVALUATIES (Scout Reports) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_evaluations (
            evaluation_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Scout info
            scout_id TEXT NOT NULL,
            scout_name TEXT,
            evaluation_date TEXT NOT NULL,
            match_observed TEXT,
            match_date TEXT,
            
            -- Technische scores (1-100)
            score_ball_control INTEGER,
            score_passing INTEGER,
            score_dribbling INTEGER,
            score_shooting INTEGER,
            score_heading INTEGER,
            score_first_touch INTEGER,
            
            -- Fysieke scores (1-100)
            score_speed INTEGER,
            score_acceleration INTEGER,
            score_stamina INTEGER,
            score_strength INTEGER,
            score_jumping INTEGER,
            score_agility INTEGER,
            
            -- Mentale scores (1-100)
            score_positioning INTEGER,
            score_vision INTEGER,
            score_composure INTEGER,
            score_leadership INTEGER,
            score_work_rate INTEGER,
            score_decision_making INTEGER,
            
            -- Keeper specifiek (alleen voor keepers)
            score_reflexes INTEGER,
            score_handling INTEGER,
            score_kicking INTEGER,
            score_positioning_gk INTEGER,
            
            -- Totaal scores
            overall_technical REAL,
            overall_physical REAL,
            overall_mental REAL,
            overall_score REAL,
            potential_score REAL,
            
            -- Aanbeveling
            recommendation TEXT,
            follow_up_required INTEGER DEFAULT 0,
            recommended_for_academy INTEGER DEFAULT 0,
            recommended_for_national_team INTEGER DEFAULT 0,
            
            -- Notities
            strengths TEXT,
            weaknesses TEXT,
            development_areas TEXT,
            general_notes TEXT,
            
            -- Video referenties
            video_clips TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- TALENT MEDISCHE GEGEVENS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_medical_records (
            medical_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Basis medisch
            blood_type TEXT,
            allergies TEXT,
            chronic_conditions TEXT,
            current_medications TEXT,
            
            -- Fysieke metingen
            height_cm INTEGER,
            weight_kg INTEGER,
            body_fat_percentage REAL,
            muscle_mass_kg REAL,
            bmi REAL,
            
            -- Fitness tests
            vo2_max REAL,
            sprint_10m_seconds REAL,
            sprint_30m_seconds REAL,
            vertical_jump_cm INTEGER,
            agility_test_seconds REAL,
            beep_test_level REAL,
            
            -- Blessure geschiedenis
            injury_history TEXT,
            surgery_history TEXT,
            current_injuries TEXT,
            injury_risk_assessment TEXT,
            
            -- Medische keuring
            last_medical_checkup TEXT,
            medical_clearance_status TEXT DEFAULT 'PENDING',
            medical_clearance_expiry TEXT,
            doctor_name TEXT,
            doctor_notes TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- TALENT MENTALE EVALUATIES (Cruciaal voor Hayat) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_mental_evaluations (
            mental_eval_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Evaluatie info
            psychologist_id TEXT,
            psychologist_name TEXT,
            evaluation_date TEXT NOT NULL,
            evaluation_type TEXT,
            
            -- Mentale gezondheid scores (1-10)
            score_stress_management INTEGER,
            score_pressure_handling INTEGER,
            score_confidence INTEGER,
            score_motivation INTEGER,
            score_focus INTEGER,
            score_resilience INTEGER,
            score_team_dynamics INTEGER,
            score_communication INTEGER,
            
            -- Persoonlijkheid
            personality_type TEXT,
            learning_style TEXT,
            communication_style TEXT,
            
            -- Risico factoren
            burnout_risk TEXT DEFAULT 'LOW',
            homesickness_risk TEXT DEFAULT 'LOW',
            adaptation_concerns TEXT,
            
            -- Identiteit (specifiek voor diaspora)
            cultural_identity_score INTEGER,
            connection_to_morocco TEXT,
            language_barrier_assessment TEXT,
            integration_support_needed INTEGER DEFAULT 0,
            
            -- Aanbevelingen
            recommendations TEXT,
            follow_up_sessions_needed INTEGER DEFAULT 0,
            referral_needed INTEGER DEFAULT 0,
            referral_type TEXT,
            
            -- Notities
            session_notes TEXT,
            confidential_notes TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- TALENT CARRIÈRE GESCHIEDENIS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_career_history (
            history_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Club info
            club_name TEXT NOT NULL,
            club_country TEXT,
            league TEXT,
            team_level TEXT,
            
            -- Periode
            start_date TEXT NOT NULL,
            end_date TEXT,
            is_current INTEGER DEFAULT 0,
            
            -- Type
            transfer_type TEXT,
            loan INTEGER DEFAULT 0,
            
            -- Statistieken
            appearances INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            clean_sheets INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            minutes_played INTEGER DEFAULT 0,
            
            -- Notities
            performance_notes TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- WATCHLIST (Scouts kunnen talenten volgen) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_watchlist (
            watchlist_id TEXT PRIMARY KEY,
            scout_id TEXT NOT NULL,
            talent_id TEXT NOT NULL,
            
            priority TEXT DEFAULT 'MEDIUM',
            reason TEXT,
            target_action TEXT,
            follow_up_date TEXT,
            notes TEXT,
            
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id),
            UNIQUE(scout_id, talent_id)
        )
    ''')
    
    # --- SCOUTS REGISTRY ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ntsp_scouts (
            scout_id TEXT PRIMARY KEY,
            user_id TEXT,
            
            -- Persoonlijke info
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            
            -- Werkgebied
            region TEXT,
            country TEXT,
            specialization TEXT,
            
            -- Certificering
            license_level TEXT,
            license_expiry TEXT,
            frmf_certified INTEGER DEFAULT 0,
            
            -- Statistieken
            talents_discovered INTEGER DEFAULT 0,
            evaluations_completed INTEGER DEFAULT 0,
            successful_recommendations INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # =========================================================================
    # TRANSFER MANAGEMENT (DOSSIER 1)
    # =========================================================================
    
    # --- TRANSFERS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfers (
            transfer_id TEXT PRIMARY KEY,
            talent_id TEXT NOT NULL,
            
            -- Clubs
            from_club TEXT NOT NULL,
            from_club_country TEXT,
            to_club TEXT NOT NULL,
            to_club_country TEXT,
            
            -- Transfer details
            transfer_type TEXT NOT NULL,
            transfer_date TEXT NOT NULL,
            contract_start TEXT,
            contract_end TEXT,
            contract_years INTEGER,
            
            -- Financieel
            transfer_fee REAL DEFAULT 0,
            transfer_fee_currency TEXT DEFAULT 'EUR',
            
            -- Vergoedingen (MASTERPLAN specifiek)
            training_compensation REAL DEFAULT 0,
            solidarity_contribution REAL DEFAULT 0,
            sell_on_percentage REAL DEFAULT 0,
            
            -- Agent
            agent_name TEXT,
            agent_fee REAL DEFAULT 0,
            agent_fee_percentage REAL DEFAULT 0,
            
            -- Foundation bijdrage (MASTERPLAN)
            foundation_contribution REAL DEFAULT 0,
            foundation_percentage REAL DEFAULT 0.5,
            
            -- Bonussen
            signing_bonus REAL DEFAULT 0,
            performance_bonuses TEXT,
            
            -- Salaris (indien bekend)
            base_salary REAL,
            salary_currency TEXT DEFAULT 'EUR',
            
            -- Smart Contract (blockchain)
            smart_contract_hash TEXT,
            smart_contract_status TEXT DEFAULT 'PENDING',
            
            -- Status
            transfer_status TEXT DEFAULT 'NEGOTIATING',
            fifa_tms_reference TEXT,
            
            -- Documenten
            documents TEXT,
            
            -- Notities
            notes TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            created_by TEXT,
            
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- TRANSFER VERGOEDINGEN LOG ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfer_compensations (
            compensation_id TEXT PRIMARY KEY,
            transfer_id TEXT NOT NULL,
            
            -- Type vergoeding
            compensation_type TEXT NOT NULL,
            
            -- Ontvanger
            recipient_club TEXT NOT NULL,
            recipient_country TEXT,
            
            -- Bedrag
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            
            -- Berekening
            calculation_basis TEXT,
            percentage_used REAL,
            years_training INTEGER,
            
            -- Status
            payment_status TEXT DEFAULT 'PENDING',
            payment_date TEXT,
            payment_reference TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (transfer_id) REFERENCES transfers(transfer_id)
        )
    ''')
    
    # --- CONTRACT TEMPLATES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contract_templates (
            template_id TEXT PRIMARY KEY,
            
            name TEXT NOT NULL,
            contract_type TEXT NOT NULL,
            description TEXT,
            
            -- Template content
            template_content TEXT,
            clauses TEXT,
            
            -- Standaard waardes
            default_foundation_percentage REAL DEFAULT 0.5,
            default_solidarity_percentage REAL DEFAULT 5.0,
            
            -- Status
            is_active INTEGER DEFAULT 1,
            version TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # =========================================================================
    # NARRATIVE INTEGRITY LAYER - NIL™ (DOSSIER 28)
    # Social Media Manipulatie Detectie & Response
    # =========================================================================
    
    # --- NIL SIGNALS (Gedetecteerde content) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_signals (
            signal_id TEXT PRIMARY KEY,
            
            -- Content identificatie
            platform TEXT NOT NULL,
            content_url TEXT,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            
            -- Classificatie
            manipulation_type TEXT NOT NULL,
            risk_level TEXT NOT NULL DEFAULT 'LOW',
            confidence_score INTEGER DEFAULT 50,
            
            -- Engagement metrics
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            engagement_velocity REAL DEFAULT 0,
            
            -- Source info
            source_account TEXT,
            source_id TEXT,
            source_followers INTEGER DEFAULT 0,
            
            -- Status & workflow
            status TEXT DEFAULT 'DETECTED',
            assigned_to TEXT,
            priority TEXT DEFAULT 'STANDARD',
            
            -- Timestamps
            content_posted_at TEXT,
            detected_at TEXT NOT NULL,
            triaged_at TEXT,
            resolved_at TEXT,
            
            -- Response
            fact_card_id TEXT,
            response_notes TEXT,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (source_id) REFERENCES nil_sources(source_id),
            FOREIGN KEY (fact_card_id) REFERENCES nil_fact_cards(fact_card_id)
        )
    ''')
    
    # --- NIL SOURCES (Bronnenregister) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_sources (
            source_id TEXT PRIMARY KEY,
            
            -- Identificatie
            platform TEXT NOT NULL,
            account_name TEXT NOT NULL,
            account_handle TEXT,
            account_url TEXT,
            
            -- Metrics
            followers INTEGER DEFAULT 0,
            following INTEGER DEFAULT 0,
            total_posts INTEGER DEFAULT 0,
            
            -- Risk assessment
            credibility_score INTEGER DEFAULT 50,
            fake_content_count INTEGER DEFAULT 0,
            verified_content_count INTEGER DEFAULT 0,
            risk_category TEXT DEFAULT 'NEUTRAL',
            
            -- Flags
            is_verified INTEGER DEFAULT 0,
            is_official INTEGER DEFAULT 0,
            is_media INTEGER DEFAULT 0,
            is_bot_suspected INTEGER DEFAULT 0,
            is_blacklisted INTEGER DEFAULT 0,
            
            -- History
            first_seen_at TEXT,
            last_activity_at TEXT,
            incidents_count INTEGER DEFAULT 0,
            
            -- Notes
            notes TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # --- NIL EVIDENCE VAULT (Bewijsarchief) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_evidence (
            evidence_id TEXT PRIMARY KEY,
            
            -- Relaties
            signal_id TEXT,
            
            -- Content
            content_hash TEXT NOT NULL UNIQUE,
            original_url TEXT NOT NULL,
            archived_url TEXT,
            
            -- Capture details
            screenshot_path TEXT,
            video_path TEXT,
            raw_content TEXT,
            metadata_json TEXT,
            
            -- Verification
            archive_status TEXT DEFAULT 'PENDING',
            hash_algorithm TEXT DEFAULT 'SHA256',
            blockchain_tx TEXT,
            
            -- Analysis
            manipulation_confirmed INTEGER DEFAULT 0,
            manipulation_type TEXT,
            manipulation_details TEXT,
            ai_analysis_score REAL,
            ai_analysis_details TEXT,
            
            -- Legal
            legal_value TEXT DEFAULT 'LOW',
            legal_notes TEXT,
            used_in_proceedings INTEGER DEFAULT 0,
            
            -- Timestamps
            captured_at TEXT NOT NULL,
            verified_at TEXT,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (signal_id) REFERENCES nil_signals(signal_id)
        )
    ''')
    
    # --- NIL FACT CARDS (Officiële responses) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_fact_cards (
            fact_card_id TEXT PRIMARY KEY,
            
            -- Relaties
            signal_id TEXT,
            
            -- Content
            incident_title TEXT NOT NULL,
            verified_facts TEXT NOT NULL,
            false_claims TEXT NOT NULL,
            official_source_url TEXT,
            additional_context TEXT,
            
            -- Classification
            response_level TEXT DEFAULT 'STANDARD',
            category TEXT,
            language TEXT DEFAULT 'en',
            
            -- Distribution
            published INTEGER DEFAULT 0,
            published_at TEXT,
            published_channels TEXT,
            
            -- Engagement
            views INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            
            -- Approval
            approved_by TEXT,
            approved_at TEXT,
            legal_reviewed INTEGER DEFAULT 0,
            legal_reviewed_by TEXT,
            
            -- Effectiveness
            virality_reduced INTEGER DEFAULT 0,
            correction_rate REAL,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (signal_id) REFERENCES nil_signals(signal_id)
        )
    ''')
    
    # --- NIL CRISIS INCIDENTS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_crisis_incidents (
            incident_id TEXT PRIMARY KEY,
            
            -- Identificatie
            incident_name TEXT NOT NULL,
            description TEXT,
            
            -- Classification
            crisis_level TEXT NOT NULL DEFAULT 'LOW',
            category TEXT,
            
            -- Status
            status TEXT DEFAULT 'OPEN',
            
            -- Team
            incident_lead TEXT,
            team_members TEXT,
            
            -- Timeline
            detected_at TEXT NOT NULL,
            escalated_at TEXT,
            contained_at TEXT,
            resolved_at TEXT,
            
            -- Response times (in minuten)
            time_to_triage INTEGER,
            time_to_response INTEGER,
            time_to_containment INTEGER,
            time_to_resolution INTEGER,
            
            -- Impact
            estimated_reach INTEGER DEFAULT 0,
            actual_reach INTEGER DEFAULT 0,
            reputation_impact TEXT,
            financial_impact REAL DEFAULT 0,
            
            -- Actions taken
            actions_log TEXT,
            lessons_learned TEXT,
            
            -- Related
            related_signals TEXT,
            related_fact_cards TEXT,
            
            -- Stakeholders notified
            sponsors_notified INTEGER DEFAULT 0,
            legal_notified INTEGER DEFAULT 0,
            security_notified INTEGER DEFAULT 0,
            press_notified INTEGER DEFAULT 0,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # --- NIL FORENSICS ANALYSES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_forensics (
            forensic_id TEXT PRIMARY KEY,
            
            -- Relaties
            signal_id TEXT,
            evidence_id TEXT,
            
            -- Content analyzed
            content_url TEXT NOT NULL,
            content_type TEXT NOT NULL,
            
            -- Analysis results
            manipulation_probability REAL DEFAULT 0,
            
            -- Image/Video analysis
            ai_generated_score REAL,
            deepfake_score REAL,
            edit_detection_score REAL,
            metadata_tampering INTEGER DEFAULT 0,
            
            -- Text analysis
            sentiment_score REAL,
            clickbait_score REAL,
            fake_quote_probability REAL,
            
            -- Source analysis
            original_source_found INTEGER DEFAULT 0,
            original_source_url TEXT,
            source_date_mismatch INTEGER DEFAULT 0,
            
            -- Bot detection
            bot_activity_score REAL,
            coordinated_activity INTEGER DEFAULT 0,
            
            -- Conclusions
            verdict TEXT,
            analyst_notes TEXT,
            
            -- Metadata
            analyzed_by TEXT,
            analyzed_at TEXT NOT NULL,
            analysis_duration_seconds INTEGER,
            
            FOREIGN KEY (signal_id) REFERENCES nil_signals(signal_id),
            FOREIGN KEY (evidence_id) REFERENCES nil_evidence(evidence_id)
        )
    ''')
    
    # --- NIL KPI METRICS (Daily tracking) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_kpi_metrics (
            metric_id TEXT PRIMARY KEY,
            
            -- Period
            date TEXT NOT NULL,
            
            -- Volume metrics
            signals_detected INTEGER DEFAULT 0,
            signals_triaged INTEGER DEFAULT 0,
            signals_resolved INTEGER DEFAULT 0,
            
            -- Response times (averages in minutes)
            avg_time_to_triage REAL,
            avg_time_to_fact_card REAL,
            avg_time_to_resolution REAL,
            
            -- Quality metrics
            false_positives INTEGER DEFAULT 0,
            true_positives INTEGER DEFAULT 0,
            accuracy_rate REAL,
            
            -- Impact metrics
            total_reach_prevented INTEGER DEFAULT 0,
            virality_containment_rate REAL,
            
            -- Crisis metrics
            crisis_incidents INTEGER DEFAULT 0,
            crisis_avg_resolution_time REAL,
            
            -- Source metrics
            sources_blacklisted INTEGER DEFAULT 0,
            sources_verified INTEGER DEFAULT 0,
            
            -- Content metrics
            fact_cards_issued INTEGER DEFAULT 0,
            evidence_archived INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # --- NIL PLAYBOOK TEMPLATES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nil_playbook_templates (
            template_id TEXT PRIMARY KEY,
            
            -- Identificatie
            template_name TEXT NOT NULL,
            description TEXT,
            
            -- Classification
            crisis_level TEXT NOT NULL,
            category TEXT,
            
            -- Response protocol
            response_time_target INTEGER NOT NULL,
            escalation_threshold INTEGER,
            
            -- Actions (JSON array)
            immediate_actions TEXT NOT NULL,
            secondary_actions TEXT,
            communication_actions TEXT,
            
            -- Stakeholders
            notify_legal INTEGER DEFAULT 0,
            notify_security INTEGER DEFAULT 0,
            notify_sponsors INTEGER DEFAULT 0,
            notify_press INTEGER DEFAULT 0,
            
            -- Templates
            fact_card_template TEXT,
            press_statement_template TEXT,
            internal_memo_template TEXT,
            
            -- Status
            is_active INTEGER DEFAULT 1,
            
            -- Metadata
            created_by TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # Create indexes for NIL tables
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_signals_status ON nil_signals(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_signals_risk ON nil_signals(risk_level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_signals_platform ON nil_signals(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_sources_risk ON nil_sources(risk_category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_evidence_hash ON nil_evidence(content_hash)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_crisis_status ON nil_crisis_incidents(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nil_kpi_date ON nil_kpi_metrics(date)')
    
    # =========================================================================
    # ACADEMY SYSTEM (DOSSIER 1)
    # =========================================================================
    
    # --- ACADEMIES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academies (
            academy_id TEXT PRIMARY KEY,
            
            -- Basis info
            name TEXT NOT NULL,
            short_name TEXT,
            
            -- Locatie
            region TEXT NOT NULL,
            city TEXT NOT NULL,
            address TEXT,
            country TEXT DEFAULT 'Morocco',
            
            -- Type en niveau
            academy_type TEXT NOT NULL,
            certification_level TEXT DEFAULT 'PENDING',
            frmf_license TEXT,
            frmf_license_expiry TEXT,
            
            -- Affiliatie
            parent_club TEXT,
            partnership_clubs TEXT,
            
            -- Capaciteit
            total_capacity INTEGER,
            current_enrollment INTEGER DEFAULT 0,
            residential_capacity INTEGER DEFAULT 0,
            
            -- Faciliteiten
            num_pitches INTEGER DEFAULT 0,
            has_indoor_facility INTEGER DEFAULT 0,
            has_gym INTEGER DEFAULT 0,
            has_medical_center INTEGER DEFAULT 0,
            has_accommodation INTEGER DEFAULT 0,
            has_school INTEGER DEFAULT 0,
            facilities_rating TEXT,
            
            -- Staff
            director_name TEXT,
            director_contact TEXT,
            num_coaches INTEGER DEFAULT 0,
            num_staff INTEGER DEFAULT 0,
            
            -- Financieel
            annual_budget REAL,
            tuition_fee REAL DEFAULT 0,
            scholarship_available INTEGER DEFAULT 1,
            
            -- Performance
            talents_produced INTEGER DEFAULT 0,
            professional_players_produced INTEGER DEFAULT 0,
            national_team_players_produced INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Contact
            email TEXT,
            phone TEXT,
            website TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    # --- ACADEMY TEAMS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academy_teams (
            team_id TEXT PRIMARY KEY,
            academy_id TEXT NOT NULL,
            
            -- Team info
            team_name TEXT NOT NULL,
            age_group TEXT NOT NULL,
            category TEXT,
            
            -- Seizoen
            season TEXT,
            
            -- Staff
            head_coach TEXT,
            assistant_coach TEXT,
            
            -- Capaciteit
            max_players INTEGER DEFAULT 25,
            current_players INTEGER DEFAULT 0,
            
            -- Competitie
            league TEXT,
            league_position INTEGER,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (academy_id) REFERENCES academies(academy_id)
        )
    ''')
    
    # --- ACADEMY ENROLLMENT (Talent inschrijvingen) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academy_enrollments (
            enrollment_id TEXT PRIMARY KEY,
            academy_id TEXT NOT NULL,
            team_id TEXT,
            talent_id TEXT NOT NULL,
            
            -- Periode
            enrollment_date TEXT NOT NULL,
            expected_end_date TEXT,
            actual_end_date TEXT,
            
            -- Type
            enrollment_type TEXT DEFAULT 'REGULAR',
            is_residential INTEGER DEFAULT 0,
            scholarship_type TEXT,
            scholarship_amount REAL DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            exit_reason TEXT,
            
            -- Prestaties
            progress_reports TEXT,
            final_evaluation TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (academy_id) REFERENCES academies(academy_id),
            FOREIGN KEY (talent_id) REFERENCES ntsp_talent_profiles(talent_id)
        )
    ''')
    
    # --- ACADEMY STAFF ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS academy_staff (
            staff_id TEXT PRIMARY KEY,
            academy_id TEXT NOT NULL,
            
            -- Persoonlijke info
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            
            -- Rol
            role TEXT NOT NULL,
            department TEXT,
            is_head_of_department INTEGER DEFAULT 0,
            
            -- Kwalificaties
            coaching_license TEXT,
            license_expiry TEXT,
            qualifications TEXT,
            specializations TEXT,
            
            -- Contract
            contract_start TEXT,
            contract_end TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (academy_id) REFERENCES academies(academy_id)
        )
    ''')
    
    # =========================================================================
    # DIASPORA WALLET™ (DOSSIER 9)
    # =========================================================================
    
    # --- DIASPORA WALLETS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diaspora_wallets (
            wallet_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            
            -- Wallet details
            wallet_address TEXT UNIQUE,
            wallet_type TEXT DEFAULT 'STANDARD',
            
            -- Balans
            balance_mad REAL DEFAULT 0,
            balance_eur REAL DEFAULT 0,
            
            -- Loyalty
            loyalty_points INTEGER DEFAULT 0,
            loyalty_tier TEXT DEFAULT 'BRONZE',
            
            -- Limieten
            daily_limit REAL DEFAULT 10000,
            monthly_limit REAL DEFAULT 50000,
            
            -- KYC Status
            kyc_status TEXT DEFAULT 'PENDING',
            kyc_verified_at TEXT,
            kyc_documents TEXT,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            is_frozen INTEGER DEFAULT 0,
            freeze_reason TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (identity_id) REFERENCES identity_shield(id)
        )
    ''')
    
    # --- WALLET TRANSACTIES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wallet_transactions (
            transaction_id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            
            -- Transactie type
            transaction_type TEXT NOT NULL,
            
            -- Bedrag
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'MAD',
            exchange_rate REAL,
            amount_in_mad REAL,
            
            -- Fee (0 voor diaspora onderling!)
            fee REAL DEFAULT 0,
            fee_waived INTEGER DEFAULT 0,
            fee_waiver_reason TEXT,
            
            -- Foundation bijdrage
            foundation_contribution REAL DEFAULT 0,
            
            -- Tegenpartij
            counterparty_wallet_id TEXT,
            counterparty_name TEXT,
            counterparty_type TEXT,
            
            -- Referentie
            reference TEXT,
            description TEXT,
            
            -- Status
            status TEXT DEFAULT 'COMPLETED',
            
            -- Blockchain
            blockchain_hash TEXT,
            block_number INTEGER,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (wallet_id) REFERENCES diaspora_wallets(wallet_id)
        )
    ''')
    
    # --- DIASPORA INVESTMENTS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diaspora_investments (
            investment_id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            identity_id TEXT NOT NULL,
            
            -- Project info
            project_id TEXT,
            project_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            project_sector TEXT,
            project_region TEXT,
            
            -- Investering
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'MAD',
            investment_date TEXT NOT NULL,
            
            -- Verwacht rendement
            expected_return_percentage REAL,
            expected_return_date TEXT,
            
            -- Actueel rendement
            actual_return REAL DEFAULT 0,
            dividends_received REAL DEFAULT 0,
            
            -- Status
            investment_status TEXT DEFAULT 'ACTIVE',
            
            -- Risico
            risk_level TEXT DEFAULT 'MEDIUM',
            
            -- Documenten
            contract_reference TEXT,
            documents TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            updated_at TEXT,
            
            FOREIGN KEY (wallet_id) REFERENCES diaspora_wallets(wallet_id)
        )
    ''')
    
    # --- DIASPORA CARDS (Loyalty Cards) ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diaspora_cards (
            card_id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            identity_id TEXT NOT NULL,
            
            -- Card info
            card_number TEXT UNIQUE,
            card_type TEXT DEFAULT 'STANDARD',
            
            -- Geldigheid
            issue_date TEXT NOT NULL,
            expiry_date TEXT NOT NULL,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            is_blocked INTEGER DEFAULT 0,
            block_reason TEXT,
            
            -- Gebruik
            total_transactions INTEGER DEFAULT 0,
            total_spent REAL DEFAULT 0,
            
            -- Benefits
            discount_percentage REAL DEFAULT 0,
            free_mobility INTEGER DEFAULT 0,
            priority_access INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (wallet_id) REFERENCES diaspora_wallets(wallet_id)
        )
    ''')
    
    # =========================================================================
    # MOBILITY INTEGRATION (DOSSIER 3/13)
    # =========================================================================
    
    # --- TRANSPORT PROVIDERS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transport_providers (
            provider_id TEXT PRIMARY KEY,
            
            -- Provider info
            name TEXT NOT NULL,
            provider_type TEXT NOT NULL,
            
            -- Contact
            contact_email TEXT,
            contact_phone TEXT,
            website TEXT,
            
            -- Service area
            service_regions TEXT,
            service_countries TEXT,
            
            -- Partnership
            partnership_status TEXT DEFAULT 'ACTIVE',
            contract_start TEXT,
            contract_end TEXT,
            
            -- Pricing
            base_discount_percentage REAL DEFAULT 0,
            diaspora_discount_percentage REAL DEFAULT 0,
            
            -- Integration
            api_enabled INTEGER DEFAULT 0,
            api_endpoint TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL
        )
    ''')
    
    # --- DIASPORA TRAVEL PACKAGES ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diaspora_travel_packages (
            package_id TEXT PRIMARY KEY,
            
            -- Package info
            name TEXT NOT NULL,
            description TEXT,
            package_type TEXT NOT NULL,
            
            -- Event koppeling
            event_id TEXT,
            
            -- Componenten
            includes_flight INTEGER DEFAULT 0,
            includes_hotel INTEGER DEFAULT 0,
            includes_ticket INTEGER DEFAULT 0,
            includes_transport INTEGER DEFAULT 0,
            includes_tour INTEGER DEFAULT 0,
            
            -- Prijzen
            base_price REAL NOT NULL,
            diaspora_price REAL,
            discount_percentage REAL DEFAULT 0,
            
            -- Beschikbaarheid
            available_from TEXT,
            available_until TEXT,
            max_bookings INTEGER,
            current_bookings INTEGER DEFAULT 0,
            
            -- Status
            status TEXT DEFAULT 'ACTIVE',
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (event_id) REFERENCES ticketchain_events(event_id)
        )
    ''')
    
    # --- PACKAGE BOOKINGS ---
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS package_bookings (
            booking_id TEXT PRIMARY KEY,
            package_id TEXT NOT NULL,
            identity_id TEXT NOT NULL,
            wallet_id TEXT,
            
            -- Boeking details
            booking_date TEXT NOT NULL,
            travel_date TEXT,
            return_date TEXT,
            num_travelers INTEGER DEFAULT 1,
            
            -- Prijzen
            total_price REAL NOT NULL,
            discount_applied REAL DEFAULT 0,
            final_price REAL NOT NULL,
            
            -- Betaling
            payment_status TEXT DEFAULT 'PENDING',
            payment_method TEXT,
            payment_reference TEXT,
            
            -- Status
            booking_status TEXT DEFAULT 'CONFIRMED',
            
            -- Tickets & confirmaties
            flight_confirmation TEXT,
            hotel_confirmation TEXT,
            ticket_hash TEXT,
            transport_booking_id TEXT,
            
            -- Metadata
            created_at TEXT NOT NULL,
            
            FOREIGN KEY (package_id) REFERENCES diaspora_travel_packages(package_id)
        )
    ''')
    
    # =========================================================================
    # PERFORMANCE INDEXES
    # =========================================================================
    
    indexes = [
        # Bestaande indexes
        "CREATE INDEX IF NOT EXISTS idx_tickets_event ON ticketchain_tickets(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_tickets_owner ON ticketchain_tickets(owner_id)",
        "CREATE INDEX IF NOT EXISTS idx_tickets_status ON ticketchain_tickets(status)",
        "CREATE INDEX IF NOT EXISTS idx_events_date ON ticketchain_events(date)",
        "CREATE INDEX IF NOT EXISTS idx_financial_entity ON financial_records(entity_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_username ON audit_logs(username)",
        "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_fraud_identity ON fraud_alerts(identity_id)",
        "CREATE INDEX IF NOT EXISTS idx_foundation_source ON foundation_contributions(source_id)",
        
        # NTSP indexes
        "CREATE INDEX IF NOT EXISTS idx_talent_nationality ON ntsp_talent_profiles(nationality)",
        "CREATE INDEX IF NOT EXISTS idx_talent_diaspora ON ntsp_talent_profiles(is_diaspora, diaspora_country)",
        "CREATE INDEX IF NOT EXISTS idx_talent_position ON ntsp_talent_profiles(primary_position)",
        "CREATE INDEX IF NOT EXISTS idx_talent_status ON ntsp_talent_profiles(talent_status)",
        "CREATE INDEX IF NOT EXISTS idx_talent_club ON ntsp_talent_profiles(current_club)",
        "CREATE INDEX IF NOT EXISTS idx_talent_score ON ntsp_talent_profiles(overall_score)",
        "CREATE INDEX IF NOT EXISTS idx_evaluation_talent ON ntsp_evaluations(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_evaluation_scout ON ntsp_evaluations(scout_id)",
        "CREATE INDEX IF NOT EXISTS idx_evaluation_date ON ntsp_evaluations(evaluation_date)",
        "CREATE INDEX IF NOT EXISTS idx_medical_talent ON ntsp_medical_records(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_mental_talent ON ntsp_mental_evaluations(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_career_talent ON ntsp_career_history(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_watchlist_scout ON ntsp_watchlist(scout_id)",
        "CREATE INDEX IF NOT EXISTS idx_watchlist_talent ON ntsp_watchlist(talent_id)",
        
        # Transfer indexes
        "CREATE INDEX IF NOT EXISTS idx_transfer_talent ON transfers(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_transfer_status ON transfers(transfer_status)",
        "CREATE INDEX IF NOT EXISTS idx_transfer_date ON transfers(transfer_date)",
        "CREATE INDEX IF NOT EXISTS idx_compensation_transfer ON transfer_compensations(transfer_id)",
        
        # Academy indexes
        "CREATE INDEX IF NOT EXISTS idx_academy_region ON academies(region)",
        "CREATE INDEX IF NOT EXISTS idx_academy_status ON academies(status)",
        "CREATE INDEX IF NOT EXISTS idx_team_academy ON academy_teams(academy_id)",
        "CREATE INDEX IF NOT EXISTS idx_enrollment_academy ON academy_enrollments(academy_id)",
        "CREATE INDEX IF NOT EXISTS idx_enrollment_talent ON academy_enrollments(talent_id)",
        "CREATE INDEX IF NOT EXISTS idx_staff_academy ON academy_staff(academy_id)",
        
        # Wallet indexes
        "CREATE INDEX IF NOT EXISTS idx_wallet_identity ON diaspora_wallets(identity_id)",
        "CREATE INDEX IF NOT EXISTS idx_wallet_status ON diaspora_wallets(status)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_wallet ON wallet_transactions(wallet_id)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_type ON wallet_transactions(transaction_type)",
        "CREATE INDEX IF NOT EXISTS idx_transaction_date ON wallet_transactions(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_investment_wallet ON diaspora_investments(wallet_id)",
        "CREATE INDEX IF NOT EXISTS idx_card_wallet ON diaspora_cards(wallet_id)",
        
        # Mobility indexes
        "CREATE INDEX IF NOT EXISTS idx_package_event ON diaspora_travel_packages(event_id)",
        "CREATE INDEX IF NOT EXISTS idx_package_booking ON package_bookings(package_id)",
        "CREATE INDEX IF NOT EXISTS idx_booking_identity ON package_bookings(identity_id)",
    ]
    
    for index_sql in indexes:
        try:
            cursor.execute(index_sql)
        except:
            pass  # Index bestaat mogelijk al
    
    # =========================================================================
    # FANDORPEN SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorpen (
            fandorp_id TEXT PRIMARY KEY,
            country_name TEXT NOT NULL,
            country_code TEXT,
            country_flag TEXT,
            location TEXT,
            name TEXT,
            city TEXT,
            region TEXT,
            languages TEXT,
            capacity INTEGER DEFAULT 0,
            coordinator_id TEXT,
            coordinator_name TEXT,
            volunteer_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_volunteers (
            volunteer_id TEXT PRIMARY KEY,
            fandorp_id TEXT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            nationality_1 TEXT DEFAULT 'Moroccan',
            nationality_2 TEXT,
            languages TEXT,
            role TEXT,
            skills TEXT,
            availability TEXT,
            clearance_level TEXT DEFAULT 'BASIC',
            verified INTEGER DEFAULT 0,
            background_check INTEGER DEFAULT 0,
            training_completed INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            registered_at TEXT,
            joined_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (fandorp_id) REFERENCES fandorpen(fandorp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_shifts (
            shift_id TEXT PRIMARY KEY,
            fandorp_id TEXT,
            volunteer_id TEXT,
            shift_date TEXT NOT NULL,
            shift_type TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            role TEXT,
            location TEXT,
            notes TEXT,
            status TEXT DEFAULT 'SCHEDULED',
            created_at TEXT NOT NULL,
            FOREIGN KEY (fandorp_id) REFERENCES fandorpen(fandorp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_incidents (
            incident_id TEXT PRIMARY KEY,
            fandorp_id TEXT,
            reporter_id TEXT,
            incident_type TEXT NOT NULL,
            description TEXT,
            supporter_nationality TEXT,
            severity TEXT DEFAULT 'LOW',
            status TEXT DEFAULT 'OPEN',
            reported_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (fandorp_id) REFERENCES fandorpen(fandorp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_services (
            service_id TEXT PRIMARY KEY,
            fandorp_id TEXT NOT NULL,
            service_type TEXT NOT NULL,
            description TEXT,
            price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (fandorp_id) REFERENCES fandorpen(fandorp_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_training (
            training_id TEXT PRIMARY KEY,
            fandorp_id TEXT,
            volunteer_id TEXT,
            module_name TEXT,
            module_type TEXT DEFAULT 'ONLINE',
            training_type TEXT,
            training_name TEXT,
            score INTEGER DEFAULT 0,
            passed INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            completed_at TEXT,
            certificate_id TEXT,
            created_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fandorp_messages (
            message_id TEXT PRIMARY KEY,
            fandorp_id TEXT,
            sender_id TEXT,
            sender_name TEXT,
            recipient_id TEXT,
            subject TEXT,
            content TEXT NOT NULL,
            message_type TEXT DEFAULT 'GENERAL',
            priority TEXT DEFAULT 'NORMAL',
            is_read INTEGER DEFAULT 0,
            sent_at TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # =========================================================================
    # ANTI-HATE SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_incidents (
            incident_id TEXT PRIMARY KEY,
            victim_id TEXT,
            victim_name TEXT,
            incident_type TEXT NOT NULL,
            platform TEXT,
            description TEXT,
            evidence_url TEXT,
            severity TEXT DEFAULT 'MEDIUM',
            status TEXT DEFAULT 'REPORTED',
            reported_by TEXT,
            reported_at TEXT NOT NULL,
            resolved_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_legal_cases (
            case_id TEXT PRIMARY KEY,
            incident_id TEXT,
            case_type TEXT NOT NULL,
            jurisdiction TEXT,
            lawyer_assigned TEXT,
            status TEXT DEFAULT 'OPEN',
            filed_at TEXT,
            outcome TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES antihate_incidents(incident_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_monitored (
            monitor_id TEXT PRIMARY KEY,
            target_type TEXT NOT NULL,
            target_id TEXT,
            target_name TEXT,
            platform TEXT,
            account_url TEXT,
            risk_level TEXT DEFAULT 'LOW',
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_wellness_checks (
            check_id TEXT PRIMARY KEY,
            incident_id TEXT,
            victim_id TEXT,
            check_type TEXT,
            notes TEXT,
            wellbeing_score INTEGER,
            follow_up_needed INTEGER DEFAULT 0,
            checked_by TEXT,
            checked_at TEXT NOT NULL,
            FOREIGN KEY (incident_id) REFERENCES antihate_incidents(incident_id)
        )
    ''')
    
    # =========================================================================
    # HAYAT HEALTH SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_crisis_alerts (
            alert_id TEXT PRIMARY KEY,
            talent_id TEXT,
            athlete_id TEXT,
            athlete_name TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'MEDIUM',
            is_anonymous INTEGER DEFAULT 0,
            anonymous_code TEXT,
            description TEXT,
            current_feelings TEXT,
            location TEXT,
            status TEXT DEFAULT 'OPEN',
            responder_id TEXT,
            responder_name TEXT,
            response_time TEXT,
            response_notes TEXT,
            resolved_at TEXT,
            resolution_notes TEXT,
            follow_up_required INTEGER DEFAULT 0,
            follow_up_date TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_wellbeing_logs (
            log_id TEXT PRIMARY KEY,
            talent_id TEXT,
            athlete_id TEXT,
            log_date TEXT NOT NULL,
            mood_score INTEGER,
            energy_score INTEGER,
            sleep_quality INTEGER,
            sleep_hours REAL,
            stress_level INTEGER,
            motivation_score INTEGER,
            pain_level INTEGER,
            pain_location TEXT,
            notes TEXT,
            needs_attention INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_sessions (
            session_id TEXT PRIMARY KEY,
            talent_id TEXT,
            athlete_id TEXT,
            psychologist_id TEXT,
            psychologist_name TEXT,
            provider_id TEXT,
            provider_name TEXT,
            session_date TEXT,
            session_type TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 60,
            location TEXT,
            is_remote INTEGER DEFAULT 0,
            session_notes_hash TEXT,
            mood_score INTEGER,
            anxiety_score INTEGER,
            progress_score INTEGER,
            next_session_date TEXT,
            homework_assigned TEXT,
            scheduled_at TEXT,
            status TEXT DEFAULT 'SCHEDULED',
            no_show INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_rehabilitation (
            rehab_id TEXT PRIMARY KEY,
            talent_id TEXT,
            athlete_id TEXT,
            injury_type TEXT NOT NULL,
            injury_date TEXT,
            start_date TEXT,
            expected_recovery_date TEXT,
            expected_end_date TEXT,
            actual_end_date TEXT,
            rehab_phase TEXT,
            progress_percentage INTEGER DEFAULT 0,
            physiotherapist TEXT,
            psychologist TEXT,
            mental_readiness_score INTEGER,
            fear_of_reinjury_score INTEGER,
            confidence_score INTEGER,
            mental_notes TEXT,
            status TEXT DEFAULT 'ACTIVE',
            notes TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # =========================================================================
    # INCLUSION SYSTEM (WOMEN & PARALYMPICS)
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS women_hubs (
            hub_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            region TEXT,
            city TEXT,
            coordinator_id TEXT,
            member_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS women_players (
            player_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT,
            is_diaspora INTEGER DEFAULT 0,
            diaspora_country TEXT,
            position TEXT,
            preferred_foot TEXT,
            hub_id TEXT,
            current_club TEXT,
            level TEXT,
            national_team INTEGER DEFAULT 0,
            national_team_caps INTEGER DEFAULT 0,
            scholarship INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            FOREIGN KEY (hub_id) REFERENCES women_hubs(hub_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paralympic_athletes (
            athlete_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT,
            is_diaspora INTEGER DEFAULT 0,
            diaspora_country TEXT,
            discipline TEXT,
            disability_class TEXT,
            classification_code TEXT,
            current_club TEXT,
            training_center TEXT,
            national_team INTEGER DEFAULT 0,
            coach_name TEXT,
            scholarship INTEGER DEFAULT 0,
            sport TEXT,
            classification TEXT,
            disability_type TEXT,
            achievements TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_programs (
            program_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            program_type TEXT NOT NULL,
            target_group TEXT,
            description TEXT,
            duration_months INTEGER,
            max_participants INTEGER,
            budget REAL DEFAULT 0,
            scholarship_amount REAL DEFAULT 0,
            start_date TEXT,
            end_date TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_events (
            event_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            target_group TEXT,
            location TEXT,
            event_date TEXT,
            max_participants INTEGER,
            description TEXT,
            capacity INTEGER,
            registered_count INTEGER DEFAULT 0,
            status TEXT DEFAULT 'UPCOMING',
            created_at TEXT NOT NULL
        )
    ''')
    
    # =========================================================================
    # MAROC ID SHIELD SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_identities (
            identity_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            place_of_birth TEXT,
            nationality TEXT DEFAULT 'Moroccan',
            nationality_primary TEXT,
            nationality_secondary TEXT,
            residence_country TEXT,
            cin_number TEXT,
            passport_number TEXT,
            document_type TEXT,
            document_number TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            verification_level INTEGER DEFAULT 0,
            is_verified INTEGER DEFAULT 0,
            is_diaspora INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_organizations (
            org_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            org_type TEXT NOT NULL,
            registration_number TEXT,
            registration_country TEXT,
            address TEXT,
            city TEXT,
            country TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            beneficial_owner_name TEXT,
            bank_account_iban TEXT,
            licenses TEXT,
            is_verified INTEGER DEFAULT 0,
            verification_level INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL,
            updated_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_verification_requests (
            request_id TEXT PRIMARY KEY,
            identity_id TEXT,
            org_id TEXT,
            request_type TEXT NOT NULL,
            target_level INTEGER,
            verification_level INTEGER,
            status TEXT DEFAULT 'PENDING',
            submitted_at TEXT,
            requested_at TEXT NOT NULL,
            processed_at TEXT,
            processed_by TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_consents (
            consent_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            consent_type TEXT NOT NULL,
            purpose TEXT,
            granted_to TEXT,
            is_active INTEGER DEFAULT 1,
            status TEXT DEFAULT 'ACTIVE',
            granted_at TEXT NOT NULL,
            expires_at TEXT,
            revoked_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_transaction_signatures (
            sig_id TEXT PRIMARY KEY,
            signature_id TEXT,
            identity_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_id TEXT,
            transaction_data TEXT,
            signature_hash TEXT NOT NULL,
            biometric_confirmed INTEGER DEFAULT 0,
            requires_second_approval INTEGER DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            signed_at TEXT NOT NULL,
            is_valid INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_pma_queue (
            pma_id TEXT PRIMARY KEY,
            queue_id TEXT,
            identity_id TEXT,
            entity_type TEXT,
            entity_id TEXT,
            transaction_type TEXT,
            request_type TEXT,
            amount REAL,
            source TEXT,
            destination TEXT,
            description TEXT,
            risk_score INTEGER DEFAULT 0,
            auto_approved INTEGER DEFAULT 0,
            priority TEXT DEFAULT 'NORMAL',
            status TEXT DEFAULT 'QUEUED',
            data_json TEXT,
            created_at TEXT NOT NULL,
            processed_at TEXT
        )
    ''')
    
    # =========================================================================
    # SUBSCRIPTION SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_plans (
            plan_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            plan_type TEXT NOT NULL,
            price_monthly REAL NOT NULL,
            price_yearly REAL,
            benefits TEXT,
            features TEXT,
            ticket_discount_pct INTEGER DEFAULT 0,
            active INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            subscription_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            user_name TEXT,
            user_email TEXT,
            plan_id TEXT NOT NULL,
            plan_name TEXT,
            plan_type TEXT,
            billing_cycle TEXT,
            price_paid REAL,
            club_name TEXT,
            player_ids TEXT,
            member_emails TEXT,
            member_count INTEGER DEFAULT 1,
            status TEXT DEFAULT 'ACTIVE',
            start_date TEXT NOT NULL,
            end_date TEXT,
            payment_method TEXT,
            payment_reference TEXT,
            foundation_contribution REAL DEFAULT 0,
            auto_renew INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            FOREIGN KEY (plan_id) REFERENCES subscription_plans(plan_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscription_payments (
            payment_id TEXT PRIMARY KEY,
            subscription_id TEXT NOT NULL,
            amount REAL NOT NULL,
            tax_amount REAL DEFAULT 0,
            foundation_amount REAL DEFAULT 0,
            net_amount REAL,
            payment_method TEXT,
            payment_reference TEXT,
            status TEXT DEFAULT 'COMPLETED',
            payment_date TEXT,
            paid_at TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gift_subscriptions (
            gift_id TEXT PRIMARY KEY,
            giver_id TEXT,
            giver_name TEXT,
            giver_email TEXT,
            recipient_name TEXT,
            recipient_email TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            duration_months INTEGER DEFAULT 12,
            gift_message TEXT,
            message TEXT,
            redemption_code TEXT,
            amount_paid REAL DEFAULT 0,
            status TEXT DEFAULT 'PENDING',
            redeemed INTEGER DEFAULT 0,
            redeemed_at TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    # =========================================================================
    # TRANSFER MARKET SYSTEM
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_players (
            player_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TEXT,
            nationality TEXT,
            position TEXT,
            current_club TEXT,
            current_league TEXT,
            market_value REAL DEFAULT 0,
            contract_until TEXT,
            agent TEXT,
            foot TEXT,
            height_cm INTEGER,
            weight_kg INTEGER,
            national_team TEXT,
            is_moroccan INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_transfers (
            transfer_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            date TEXT NOT NULL,
            from_club TEXT,
            to_club TEXT,
            fee REAL DEFAULT 0,
            type TEXT DEFAULT 'TRANSFER',
            FOREIGN KEY (player_id) REFERENCES tm_players(player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_rumours (
            rumour_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            source TEXT,
            interested_club TEXT,
            rumoured_fee REAL,
            probability INTEGER DEFAULT 50,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL,
            FOREIGN KEY (player_id) REFERENCES tm_players(player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_statistics (
            stat_id TEXT PRIMARY KEY,
            player_id TEXT NOT NULL,
            season TEXT,
            competition TEXT,
            appearances INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            minutes INTEGER DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES tm_players(player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tm_value_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_id TEXT NOT NULL,
            date TEXT NOT NULL,
            value REAL NOT NULL,
            FOREIGN KEY (player_id) REFERENCES tm_players(player_id)
        )
    ''')
    
    # =========================================================================
    # ONTBREKENDE TABELLEN
    # =========================================================================
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            login_at TEXT NOT NULL,
            logout_at TEXT,
            ip_address TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transfer_market_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            player_id TEXT NOT NULL,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, player_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            plan_id TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            start_date TEXT NOT NULL,
            end_date TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification_requests (
            request_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            request_type TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING',
            requested_at TEXT NOT NULL,
            processed_at TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hayat_alerts (
            alert_id TEXT PRIMARY KEY,
            talent_id TEXT,
            athlete_id TEXT,
            alert_type TEXT NOT NULL,
            severity TEXT DEFAULT 'MEDIUM',
            description TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS antihate_cases (
            case_id TEXT PRIMARY KEY,
            incident_id TEXT,
            case_type TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inclusion_athletes (
            athlete_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            sport TEXT,
            category TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mobility_packages (
            package_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consular_services (
            service_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            price REAL DEFAULT 0,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consular_appointments (
            appointment_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            service_id TEXT,
            appointment_date TEXT NOT NULL,
            status TEXT DEFAULT 'SCHEDULED',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consular_documents (
            document_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            document_type TEXT NOT NULL,
            document_name TEXT,
            file_path TEXT,
            status TEXT DEFAULT 'PENDING',
            uploaded_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS esports_players (
            player_id TEXT PRIMARY KEY,
            gamer_tag TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            game TEXT,
            team_id TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS esports_teams (
            team_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            game TEXT,
            region TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS esports_tournaments (
            tournament_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            game TEXT,
            start_date TEXT,
            end_date TEXT,
            prize_pool REAL DEFAULT 0,
            status TEXT DEFAULT 'UPCOMING',
            created_at TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS maroc_role_certificates (
            certificate_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            role TEXT NOT NULL,
            organization_id TEXT,
            issued_at TEXT NOT NULL,
            expires_at TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Commit en sluit database
    conn.commit()
    conn.close()


def migrate_db():
    """
    Voer database migraties uit voor bestaande databases.
    Voegt nieuwe kolommen toe zonder data te verliezen.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check en voeg kolommen toe aan bestaande tabellen
    migrations = [
        # Voeg mobility_options toe aan events
        ("ticketchain_events", "mobility_options", "TEXT"),
        ("ticketchain_events", "diaspora_package_enabled", "INTEGER DEFAULT 0"),
        
        # Voeg mobility en diaspora aan tickets
        ("ticketchain_tickets", "mobility_booking_id", "TEXT"),
        ("ticketchain_tickets", "diaspora_package_id", "TEXT"),
        
        # Voeg extra velden toe aan scholarships
        ("scholarship_applications", "amount_approved", "REAL"),
        
        # Voeg extra velden toe aan mobility_bookings
        ("mobility_bookings", "arrival_location", "TEXT"),
        ("mobility_bookings", "departure_time", "TEXT"),
        ("mobility_bookings", "price", "REAL DEFAULT 0"),
    ]
    
    for table, column, col_type in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")
        except:
            pass  # Kolom bestaat al
    
    conn.commit()
    conn.close()
