# ============================================================================
# MAROC ID SHIELD™ - NATIONALE MOBILE IDENTITY & VERIFICATION
# 
# Marokkaanse digitale staatsinfrastructuur (itsme®-achtig)
# 
# Implementeert:
# - 4 Verificatieniveaus (Level of Assurance)
# - Device Binding & Biometrie
# - Document Verificatie & Liveness Detection
# - Organisatie Verificatie (KYB)
# - Rol Certificaten & Bevoegdheden
# - Transaction Signing (Digitale Handtekening)
# - Risk Scoring & Fraud Detection
# - PMA (Pre-Manifest Advance) Dashboard
# - Consent Management
# - Tamper-proof Audit Logs
# ============================================================================

import streamlit as st
import hashlib
import hmac
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
import random
import json

from translations import get_text, get_current_language

def t(key):
    return get_text(key, get_current_language())

from config import DB_FILE, Options, FOUNDATION_RATE
from database.connection import get_data, run_query, run_transaction, count_records, aggregate_sum
from utils.helpers import generate_uuid
from auth.security import log_audit, check_permission
from ui.styles import COLORS, premium_header, render_kpi_row


# ============================================================================
# CONSTANTEN
# ============================================================================

# Verificatieniveaus (Level of Assurance)
VERIFICATION_LEVELS = {
    0: {
        "name": "Guest",
        "name_ar": "ضيف",
        "icon": "",
        "color": "#94A3B8",
        "description": "Toeristen & Bezoekers",
        "access": ["Info", "FanDorp bezoek"],
        "restrictions": ["Geen financiële transacties", "Geen contracten"],
        "requirements": ["Geen verificatie nodig"]
    },
    1: {
        "name": "Basic Verified",
        "name_ar": "تحقق أساسي",
        "icon": "",
        "color": "#4299E1",
        "description": "Basis Geverifieerd",
        "access": ["Tickets kopen", "Events bijwonen", "Basis info"],
        "restrictions": ["Max €500 transacties", "Geen officiële rollen"],
        "requirements": ["Telefoon verificatie", "Email verificatie", "Device binding"]
    },
    2: {
        "name": "Strong Verified",
        "name_ar": "تحقق قوي",
        "icon": "",
        "color": "#48BB78",
        "description": "Sterk Geverifieerd (Standaard)",
        "access": ["Contracten tekenen", "Vrijwilligersrollen", "Beperkte betalingen", "Diaspora Wallet"],
        "restrictions": ["Max €10.000 transacties", "Geen kritieke rollen"],
        "requirements": ["ID-document scan", "Selfie liveness check", "Adres verificatie", "Bank/partner validatie"]
    },
    3: {
        "name": "Government Grade",
        "name_ar": "درجة حكومية",
        "icon": "",
        "color": "#D4AF37",
        "description": "Overheidsgraad (Hoogste)",
        "access": ["Officials", "Foundation beheer", "Grote transacties", "Kritieke rollen", "Audit toegang"],
        "restrictions": ["2-man rule voor uitzonderingen"],
        "requirements": ["Face match + document", "Extra attestation", "Background check", "Overheidsvalidatie"]
    }
}

# Rol Types
ROLE_TYPES = [
    ("VOLUNTEER", "Vrijwilliger", "", 2),
    ("STEWARD", "Steward", "", 2),
    ("OFFICIAL", "Official", "", 3),
    ("DONOR", "Donor/Sponsor", "", 2),
    ("AGENT", "Makelaar/Agent", "", 3),
    ("CLUB_MANAGER", "Club Manager", "", 3),
    ("CONSULATE_STAFF", "Consulaat Medewerker", "️", 3),
    ("MEDICAL_STAFF", "Medisch Personeel", "", 2),
    ("SCOUT", "Scout", "", 2),
    ("ACADEMY_STAFF", "Academy Staff", "", 2),
    ("SECURITY", "Beveiliging", "️", 3),
    ("AUDITOR", "Auditor", "", 3),
]

# Organisatie Types
ORG_TYPES = [
    ("CLUB", "Voetbalclub", ""),
    ("FEDERATION", "Federatie", ""),
    ("ACADEMY", "Academy", ""),
    ("SPONSOR", "Sponsor", ""),
    ("SUPPLIER", "Leverancier", ""),
    ("CONSULATE", "Consulaat", "️"),
    ("FOUNDATION", "Stichting", ""),
    ("AGENCY", "Agency/Bureau", ""),
    ("MEDIA", "Media Partner", ""),
    ("GOVERNMENT", "Overheidsinstantie", "️"),
]

# Document Types voor verificatie
DOCUMENT_TYPES = [
    ("CNIE", "Carte Nationale d'Identité (Marokko)", ""),
    ("PASSPORT_MA", "Paspoort Marokko", ""),
    ("PASSPORT_EU", "Paspoort EU", ""),
    ("PASSPORT_OTHER", "Paspoort Overig", ""),
    ("RESIDENCE_PERMIT", "Verblijfsvergunning", ""),
    ("DRIVING_LICENSE", "Rijbewijs", ""),
]

# Transaction Types die signing vereisen
SIGNING_REQUIRED_TRANSACTIONS = [
    "CONTRACT_SIGN",
    "TRANSFER_APPROVE",
    "FOUNDATION_DONATION_LARGE",
    "WALLET_WITHDRAWAL_LARGE",
    "ROLE_ASSIGNMENT",
    "ORGANIZATION_CHANGE",
    "AUDIT_ACCESS",
]

# Risk Indicators
RISK_INDICATORS = [
    ("MULTIPLE_DEVICES", "Meerdere devices", 15),
    ("LOCATION_MISMATCH", "Locatie mismatch", 20),
    ("RAPID_TRANSACTIONS", "Snelle transacties", 25),
    ("FAILED_VERIFICATIONS", "Mislukte verificaties", 30),
    ("WATCHLIST_MATCH", "Watchlist match", 50),
    ("DOCUMENT_EXPIRED", "Verlopen document", 10),
    ("UNUSUAL_PATTERN", "Ongebruikelijk patroon", 20),
]

# PMA Status Types
PMA_STATUSES = [
    ("PENDING_REVIEW", "⏳ Wacht op Review", COLORS['warning']),
    ("APPROVED", " Goedgekeurd", COLORS['success']),
    ("FLAGGED", " Gemarkeerd", COLORS['error']),
    ("BLOCKED", " Geblokkeerd", '#FF0000'),
    ("MANUAL_REVIEW", "️ Handmatige Review", COLORS['info']),
]


# ============================================================================
# DATABASE SETUP
# ============================================================================

def ensure_maroc_id_tables():
    """Maak MAROC ID SHIELD tabellen aan."""
    queries = [
        # Identiteiten tabel (uitgebreid)
        """
        CREATE TABLE IF NOT EXISTS maroc_identities (
            identity_id TEXT PRIMARY KEY,
            user_id TEXT,
            verification_level INTEGER DEFAULT 0,
            
            -- Persoonlijke gegevens
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT,
            nationality_primary TEXT,
            nationality_secondary TEXT,
            residence_country TEXT,
            
            -- Contact & Device
            phone TEXT,
            phone_verified INTEGER DEFAULT 0,
            email TEXT,
            email_verified INTEGER DEFAULT 0,
            device_id TEXT,
            device_bound_at TEXT,
            
            -- Document verificatie
            document_type TEXT,
            document_number TEXT,
            document_country TEXT,
            document_expiry TEXT,
            document_verified INTEGER DEFAULT 0,
            document_verified_at TEXT,
            
            -- Biometrie
            liveness_check_passed INTEGER DEFAULT 0,
            liveness_checked_at TEXT,
            face_match_score REAL,
            biometric_hash TEXT,
            
            -- Status & Risk
            status TEXT DEFAULT 'PENDING',
            risk_score INTEGER DEFAULT 0,
            last_risk_assessment TEXT,
            watchlist_checked INTEGER DEFAULT 0,
            
            -- Metadata
            created_at TEXT,
            updated_at TEXT,
            verified_by TEXT,
            notes TEXT
        )
        """,
        
        # Organisaties tabel (KYB)
        """
        CREATE TABLE IF NOT EXISTS maroc_organizations (
            org_id TEXT PRIMARY KEY,
            org_type TEXT NOT NULL,
            name TEXT NOT NULL,
            registration_number TEXT,
            registration_country TEXT,
            
            -- Beneficial Owner
            beneficial_owner_id TEXT,
            beneficial_owner_name TEXT,
            beneficial_owner_verified INTEGER DEFAULT 0,
            
            -- Bank & Licenties
            bank_account_iban TEXT,
            bank_verified INTEGER DEFAULT 0,
            licenses TEXT,
            
            -- Verificatie
            verification_level INTEGER DEFAULT 1,
            verified INTEGER DEFAULT 0,
            verified_at TEXT,
            verified_by TEXT,
            
            -- Status
            status TEXT DEFAULT 'PENDING',
            risk_score INTEGER DEFAULT 0,
            
            created_at TEXT,
            updated_at TEXT
        )
        """,
        
        # Rol Certificaten
        """
        CREATE TABLE IF NOT EXISTS maroc_role_certificates (
            cert_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            org_id TEXT,
            role_type TEXT NOT NULL,
            role_name TEXT,
            
            -- Bevoegdheden
            permissions TEXT,
            restrictions TEXT,
            max_transaction_amount REAL,
            
            -- Geldigheid
            issued_at TEXT,
            valid_from TEXT,
            valid_until TEXT,
            status TEXT DEFAULT 'ACTIVE',
            
            -- Verificatie
            required_level INTEGER,
            issued_by TEXT,
            revoked_at TEXT,
            revoked_by TEXT,
            revocation_reason TEXT
        )
        """,
        
        # Device Registry
        """
        CREATE TABLE IF NOT EXISTS maroc_devices (
            device_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            device_fingerprint TEXT,
            device_type TEXT,
            device_name TEXT,
            os_version TEXT,
            app_version TEXT,
            
            -- Binding
            bound_at TEXT,
            last_used TEXT,
            is_primary INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE',
            
            -- Security
            failed_attempts INTEGER DEFAULT 0,
            locked_until TEXT
        )
        """,
        
        # Transaction Signing
        """
        CREATE TABLE IF NOT EXISTS maroc_transaction_signatures (
            sig_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_id TEXT,
            transaction_data TEXT,
            
            -- Signing
            signature_hash TEXT,
            signed_at TEXT,
            device_id TEXT,
            biometric_confirmed INTEGER DEFAULT 0,
            
            -- Approval
            status TEXT DEFAULT 'PENDING',
            approved_at TEXT,
            rejected_at TEXT,
            rejection_reason TEXT,
            
            -- Two-man rule
            requires_second_approval INTEGER DEFAULT 0,
            second_approver_id TEXT,
            second_approved_at TEXT
        )
        """,
        
        # Consent Management
        """
        CREATE TABLE IF NOT EXISTS maroc_consents (
            consent_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            consent_type TEXT NOT NULL,
            purpose TEXT,
            
            -- Scope
            data_categories TEXT,
            third_parties TEXT,
            
            -- Validity
            granted_at TEXT,
            valid_until TEXT,
            revoked_at TEXT,
            
            status TEXT DEFAULT 'ACTIVE'
        )
        """,
        
        # PMA (Pre-Manifest Advance) Queue
        """
        CREATE TABLE IF NOT EXISTS maroc_pma_queue (
            pma_id TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            transaction_type TEXT,
            
            -- Details
            amount REAL,
            currency TEXT DEFAULT 'EUR',
            source TEXT,
            destination TEXT,
            description TEXT,
            
            -- Risk Assessment
            risk_score INTEGER DEFAULT 0,
            risk_factors TEXT,
            auto_approved INTEGER DEFAULT 0,
            
            -- Review
            status TEXT DEFAULT 'PENDING_REVIEW',
            reviewed_by TEXT,
            reviewed_at TEXT,
            review_notes TEXT,
            
            -- Timestamps
            created_at TEXT,
            processed_at TEXT
        )
        """,
        
        # Verification Requests
        """
        CREATE TABLE IF NOT EXISTS maroc_verification_requests (
            request_id TEXT PRIMARY KEY,
            identity_id TEXT NOT NULL,
            request_type TEXT NOT NULL,
            target_level INTEGER,
            
            -- Documents
            documents_submitted TEXT,
            
            -- Status
            status TEXT DEFAULT 'PENDING',
            rejection_reason TEXT,
            
            -- Processing
            submitted_at TEXT,
            processed_at TEXT,
            processed_by TEXT
        )
        """
    ]
    
    for query in queries:
        try:
            run_query(query)
        except:
            pass


def get_maroc_id_stats() -> Dict:
    """Haal MAROC ID statistieken op."""
    try:
        identities = count_records('maroc_identities')
        organizations = count_records('maroc_organizations')
        certificates = count_records('maroc_role_certificates')
        signatures = count_records('maroc_transaction_signatures')
        pma_pending = len(get_data("maroc_pma_queue", "status = 'PENDING_REVIEW'"))
        
        # Level breakdown
        level_counts = {}
        for level in range(4):
            df = get_data("maroc_identities", f"verification_level = {level}")
            level_counts[level] = len(df)
        
        return {
            'identities': identities,
            'organizations': organizations,
            'certificates': certificates,
            'signatures': signatures,
            'pma_pending': pma_pending,
            'level_counts': level_counts
        }
    except:
        return {
            'identities': 0,
            'organizations': 0,
            'certificates': 0,
            'signatures': 0,
            'pma_pending': 0,
            'level_counts': {0: 0, 1: 0, 2: 0, 3: 0}
        }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_signature_hash(data: str, identity_id: str) -> str:
    """Genereer een cryptografische handtekening hash."""
    secret = f"MAROC_ID_SHIELD_{identity_id}"
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


def calculate_risk_score(identity_id: str) -> int:
    """Bereken risk score voor een identiteit."""
    score = 0
    
    # Check various risk factors
    df = get_data("maroc_identities", f"identity_id = '{identity_id}'")
    if df.empty:
        return 50  # Unknown = medium risk
    
    identity = df.iloc[0]
    
    # Document expired
    if identity.get('document_expiry'):
        try:
            expiry = datetime.fromisoformat(identity['document_expiry'])
            if expiry < datetime.now():
                score += 10
        except:
            pass
    
    # Not verified
    if not identity.get('document_verified', 0):
        score += 15
    
    if not identity.get('liveness_check_passed', 0):
        score += 20
    
    # Check PMA flags
    pma_df = get_data("maroc_pma_queue", f"entity_id = '{identity_id}' AND status = 'FLAGGED'")
    score += len(pma_df) * 15
    
    return min(score, 100)


def check_pma_auto_approve(amount: float, identity_id: str, transaction_type: str) -> tuple:
    """Check of PMA automatisch goedgekeurd kan worden."""
    # Get identity
    df = get_data("maroc_identities", f"identity_id = '{identity_id}'")
    if df.empty:
        return False, "Identity not found", 50
    
    identity = df.iloc[0]
    level = identity.get('verification_level', 0)
    risk = identity.get('risk_score', 50)
    
    # Auto-approve rules
    if level >= 2 and risk < 20:
        if level == 2 and amount <= 1000:
            return True, "Auto-approved (Level 2, low risk, low amount)", risk
        elif level == 3 and amount <= 10000:
            return True, "Auto-approved (Level 3, low risk)", risk
    
    if risk >= 50:
        return False, "Manual review required (high risk)", risk
    
    if amount > 5000 and level < 3:
        return False, "Manual review required (high amount, insufficient level)", risk
    
    return False, "Manual review required", risk


# ============================================================================
# MAIN RENDER FUNCTION
# ============================================================================

def render(username: str):
    """Render MAROC ID SHIELD module."""
    
    # Ensure tables exist
    ensure_maroc_id_tables()
    
    # Header
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #C41E3A 0%, #006233 50%, #C41E3A 100%);
                    padding: 2rem; border-radius: 12px; margin-bottom: 1.5rem; text-align: center;'>
            <h1 style='color: white; margin: 0; font-family: Rajdhani, sans-serif;'>
                ️ MAROC ID SHIELD
            </h1>
            <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0; font-size: 1.1rem;'>
                النظام الوطني للهوية الرقمية | Nationale Mobile Identity & Verification
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get stats
    stats = get_maroc_id_stats()
    
    # KPI Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🆔 Identiteiten", stats['identities'])
    col2.metric(" Organisaties", stats['organizations'])
    col3.metric(" Certificaten", stats['certificates'])
    col4.metric("️ Handtekeningen", stats['signatures'])
    col5.metric("⏳ PMA Pending", stats['pma_pending'])
    
    # Tabs
    tabs = st.tabs([
        "🆔 Verificatie",
        " Levels Overview",
        " Organisaties",
        " Rol Certificaten",
        "️ Transaction Signing",
        " PMA Dashboard",
        "️ Beheer"
    ])
    
    with tabs[0]:
        render_verification(username)
    
    with tabs[1]:
        render_levels_overview(username)
    
    with tabs[2]:
        render_organizations(username)
    
    with tabs[3]:
        render_role_certificates(username)
    
    with tabs[4]:
        render_transaction_signing(username)
    
    with tabs[5]:
        render_pma_dashboard(username)
    
    with tabs[6]:
        render_admin(username)


# ============================================================================
# VERIFICATIE TAB
# ============================================================================

def render_verification(username: str):
    """Identity verificatie en onboarding."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(212, 175, 55, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(212, 175, 55, 0.3);'>
            <h3 style='color: {COLORS["gold"]}; margin: 0;'>🆔 Identiteit Verificatie</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Verifieer je identiteit om toegang te krijgen tot meer diensten
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([" Nieuwe Verificatie", " Mijn Status", " Upgrade Level"])
    
    with tab1:
        st.markdown("###  Start Verificatie Proces")
        
        with st.form("new_verification"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("Voornaam *")
                last_name = st.text_input("Achternaam *")
                dob = st.date_input("Geboortedatum *", min_value=date(1920, 1, 1), max_value=date.today())
                nationality_primary = st.selectbox("Primaire Nationaliteit *", Options.NATIONALITIES)
                nationality_secondary = st.selectbox("Secundaire Nationaliteit", ["Geen"] + Options.NATIONALITIES)
            
            with col2:
                phone = st.text_input("Telefoonnummer *", placeholder="+212 6XX XXX XXX")
                email = st.text_input("Email *")
                residence_country = st.selectbox("Woonland *", Options.DIASPORA_COUNTRIES + ["Morocco", "Other"])
                document_type = st.selectbox("Document Type *", [d[1] for d in DOCUMENT_TYPES])
                document_number = st.text_input("Document Nummer *")
            
            st.markdown("---")
            
            col_a, col_b = st.columns(2)
            with col_a:
                target_level = st.selectbox(
                    "Gewenst Verificatie Niveau",
                    options=[1, 2, 3],
                    format_func=lambda x: f"Level {x}: {VERIFICATION_LEVELS[x]['name']}"
                )
            
            with col_b:
                st.markdown(f"""
                    **Vereisten voor Level {target_level}:**
                """)
                for req in VERIFICATION_LEVELS[target_level]['requirements']:
                    st.write(f"• {req}")
            
            consent = st.checkbox("Ik ga akkoord met de verwerking van mijn gegevens voor verificatiedoeleinden")
            
            if st.form_submit_button(" Start Verificatie", width="stretch", type="primary"):
                if not all([first_name, last_name, phone, email, document_number]):
                    st.error("Vul alle verplichte velden in")
                elif not consent:
                    st.error("Accepteer de voorwaarden om door te gaan")
                else:
                    identity_id = generate_uuid("MID")
                    
                    # Create identity record
                    success = run_query("""
                        INSERT INTO maroc_identities 
                        (identity_id, first_name, last_name, date_of_birth, nationality_primary,
                         nationality_secondary, residence_country, phone, email, document_type,
                         document_number, verification_level, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 'PENDING', ?, ?)
                    """, (identity_id, first_name, last_name, str(dob), nationality_primary,
                          nationality_secondary if nationality_secondary != "Geen" else None,
                          residence_country, phone, email, document_type, document_number,
                          datetime.now().isoformat(), datetime.now().isoformat()))
                    
                    if success:
                        # Create verification request
                        request_id = generate_uuid("VRQ")
                        run_query("""
                            INSERT INTO maroc_verification_requests
                            (request_id, identity_id, request_type, target_level, status, submitted_at)
                            VALUES (?, ?, 'INITIAL', ?, 'PENDING', ?)
                        """, (request_id, identity_id, target_level, datetime.now().isoformat()))
                        
                        # Create consent record
                        consent_id = generate_uuid("CNS")
                        run_query("""
                            INSERT INTO maroc_consents
                            (consent_id, identity_id, consent_type, purpose, granted_at, status)
                            VALUES (?, ?, 'DATA_PROCESSING', 'Identity Verification', ?, 'ACTIVE')
                        """, (consent_id, identity_id, datetime.now().isoformat()))
                        
                        log_audit(username, "MAROC_ID_VERIFICATION_STARTED", identity_id)
                        
                        st.success(f"""
                             **Verificatie aanvraag ingediend!**
                            
                            **Identity ID:** `{identity_id}`
                            **Request ID:** `{request_id}`
                            
                            Volgende stappen:
                            1.  Bevestig je telefoonnummer (SMS code)
                            2.  Bevestig je email
                            3.  Upload je identiteitsdocument
                            4.  Voltooi liveness check
                        """)
                    else:
                        st.error("Er is een fout opgetreden. Probeer opnieuw.")
    
    with tab2:
        st.markdown("###  Mijn Verificatie Status")
        
        # For demo, show any identities
        df = get_data("maroc_identities")
        
        if not df.empty:
            identity = df.iloc[0]  # Show first for demo
            level = identity.get('verification_level', 0)
            level_info = VERIFICATION_LEVELS[level]
            
            # Status card
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {level_info['color']}22 0%, {level_info['color']}11 100%);
                            padding: 1.5rem; border-radius: 12px; border: 2px solid {level_info['color']};'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div>
                            <span style='font-size: 2rem;'>{level_info['icon']}</span>
                            <h2 style='color: {level_info['color']}; margin: 0.5rem 0;'>
                                Level {level}: {level_info['name']}
                            </h2>
                            <p style='color: {COLORS['text_secondary']}; margin: 0;'>
                                {level_info['name_ar']} | {level_info['description']}
                            </p>
                        </div>
                        <div style='text-align: right;'>
                            <div style='color: {COLORS['text_muted']}; font-size: 0.9rem;'>Risk Score</div>
                            <div style='font-size: 1.5rem; font-weight: 700; color: {COLORS['success'] if identity.get('risk_score', 0) < 30 else COLORS['warning'] if identity.get('risk_score', 0) < 60 else COLORS['error']};'>
                                {identity.get('risk_score', 0)}
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Details
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("####  Persoonlijke Gegevens")
                st.write(f"**Naam:** {identity.get('first_name', '')} {identity.get('last_name', '')}")
                st.write(f"**Nationaliteit:** {identity.get('nationality_primary', 'N/A')}")
                if identity.get('nationality_secondary'):
                    st.write(f"**Tweede Nationaliteit:** {identity['nationality_secondary']}")
                st.write(f"**Woonland:** {identity.get('residence_country', 'N/A')}")
            
            with col2:
                st.markdown("####  Verificatie Status")
                
                checks = [
                    (" Telefoon", identity.get('phone_verified', 0)),
                    (" Email", identity.get('email_verified', 0)),
                    (" Document", identity.get('document_verified', 0)),
                    (" Liveness", identity.get('liveness_check_passed', 0)),
                    (" Watchlist", identity.get('watchlist_checked', 0)),
                ]
                
                for check_name, is_verified in checks:
                    if is_verified:
                        st.success(f" {check_name} geverifieerd")
                    else:
                        st.warning(f"⏳ {check_name} niet geverifieerd")
            
            # Access rights
            st.markdown("---")
            st.markdown("####  Toegangsrechten")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("** Toegang tot:**")
                for access in level_info['access']:
                    st.write(f"• {access}")
            
            with col_b:
                st.markdown("** Beperkingen:**")
                for restriction in level_info['restrictions']:
                    st.write(f"• {restriction}")
        else:
            st.info("Nog geen verificatie gestart. Gebruik het formulier hierboven om te beginnen.")
    
    with tab3:
        st.markdown("###  Upgrade Verificatie Level")
        
        df = get_data("maroc_identities")
        if not df.empty:
            identity = df.iloc[0]
            current_level = identity.get('verification_level', 0)
            
            if current_level < 3:
                next_level = current_level + 1
                next_info = VERIFICATION_LEVELS[next_level]
                
                st.markdown(f"""
                    <div style='background: {COLORS['bg_card']}; padding: 1rem; border-radius: 8px;
                                border: 1px solid {next_info['color']};'>
                        <h4 style='color: {next_info['color']}; margin: 0;'>
                            Upgrade naar Level {next_level}: {next_info['name']}
                        </h4>
                        <p style='color: {COLORS['text_muted']}; margin: 0.5rem 0 0 0;'>
                            {next_info['description']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Vereisten:**")
                for req in next_info['requirements']:
                    st.write(f"• {req}")
                
                st.markdown("**Je krijgt toegang tot:**")
                for access in next_info['access']:
                    st.write(f"• {access}")
                
                if st.button(" Start Upgrade Proces", type="primary"):
                    request_id = generate_uuid("VRQ")
                    run_query("""
                        INSERT INTO maroc_verification_requests
                        (request_id, identity_id, request_type, target_level, status, submitted_at)
                        VALUES (?, ?, 'UPGRADE', ?, 'PENDING', ?)
                    """, (request_id, identity['identity_id'], next_level, datetime.now().isoformat()))
                    
                    st.success(f" Upgrade aanvraag ingediend! Request ID: `{request_id}`")
            else:
                st.success(" Je hebt al het hoogste verificatieniveau (Government Grade)!")
        else:
            st.warning("Start eerst een basis verificatie.")


# ============================================================================
# LEVELS OVERVIEW
# ============================================================================

def render_levels_overview(username: str):
    """Overzicht van alle verificatieniveaus."""
    
    st.markdown("###  Verificatieniveaus Overview")
    
    # Stats
    stats = get_maroc_id_stats()
    
    for level, info in VERIFICATION_LEVELS.items():
        count = stats['level_counts'].get(level, 0)
        
        with st.expander(f"{info['icon']} Level {level}: {info['name']} ({count} gebruikers)", expanded=(level == 2)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"""
                    <div style='padding: 1rem;'>
                        <h4 style='color: {info['color']}; margin: 0;'>{info['name']}</h4>
                        <p style='color: {COLORS['text_muted']};'>{info['name_ar']} | {info['description']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("**Vereisten:**")
                for req in info['requirements']:
                    st.write(f"• {req}")
                
                st.markdown("**Toegang:**")
                for access in info['access']:
                    st.write(f" {access}")
                
                st.markdown("**Beperkingen:**")
                for restriction in info['restrictions']:
                    st.write(f" {restriction}")
            
            with col2:
                # Visual indicator
                st.markdown(f"""
                    <div style='background: {info['color']}; padding: 2rem; border-radius: 12px;
                                text-align: center; color: white;'>
                        <div style='font-size: 3rem;'>{info['icon']}</div>
                        <div style='font-size: 1.5rem; font-weight: 700;'>Level {level}</div>
                        <div style='font-size: 2rem; margin-top: 0.5rem;'>{count}</div>
                        <div style='font-size: 0.9rem;'>gebruikers</div>
                    </div>
                """, unsafe_allow_html=True)


# ============================================================================
# ORGANISATIES (KYB)
# ============================================================================

def render_organizations(username: str):
    """Organisatie verificatie (Know Your Business)."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(72, 187, 120, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(72, 187, 120, 0.3);'>
            <h3 style='color: {COLORS["success"]}; margin: 0;'> Organisatie Verificatie (KYB)</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Verifieer bedrijven, clubs, leveranciers en partners
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs([t("overview"), " Nieuwe Organisatie"])
    
    with tab1:
        df = get_data("maroc_organizations")
        
        if not df.empty:
            for _, org in df.iterrows():
                verified_badge = "" if org.get('verified', 0) else "⏳"
                
                with st.expander(f"{verified_badge} {org['name']} ({org['org_type']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {org['org_type']}")
                        st.write(f"**Registratienummer:** {org.get('registration_number', 'N/A')}")
                        st.write(f"**Land:** {org.get('registration_country', 'N/A')}")
                        st.write(f"**IBAN:** {org.get('bank_account_iban', 'N/A')[:10]}..." if org.get('bank_account_iban') else "**IBAN:** N/A")
                    
                    with col2:
                        st.write(f"**Beneficial Owner:** {org.get('beneficial_owner_name', 'N/A')}")
                        st.write(f"**Verificatie Level:** {org.get('verification_level', 1)}")
                        st.write(f"**Risk Score:** {org.get('risk_score', 0)}")
                        st.write(f"**Status:** {org.get('status', 'PENDING')}")
        else:
            st.info("Nog geen organisaties geregistreerd.")
    
    with tab2:
        st.markdown("###  Registreer Organisatie")
        
        with st.form("new_org"):
            col1, col2 = st.columns(2)
            
            with col1:
                org_type = st.selectbox("Type Organisatie *", [o[1] for o in ORG_TYPES])
                name = st.text_input("Organisatienaam *")
                registration_number = st.text_input("Registratienummer (KvK/RC)")
                registration_country = st.selectbox("Registratieland", ["Morocco"] + Options.DIASPORA_COUNTRIES)
            
            with col2:
                beneficial_owner_name = st.text_input("Uiteindelijke Begunstigde (UBO) *")
                bank_iban = st.text_input("Bank IBAN")
                licenses = st.text_area("Licenties (één per regel)")
            
            if st.form_submit_button(" Registreren", width="stretch"):
                if not name or not beneficial_owner_name:
                    st.error("Vul alle verplichte velden in")
                else:
                    org_id = generate_uuid("ORG")
                    
                    # Find org_type code
                    org_type_code = next((o[0] for o in ORG_TYPES if o[1] == org_type), "OTHER")
                    
                    success = run_query("""
                        INSERT INTO maroc_organizations
                        (org_id, org_type, name, registration_number, registration_country,
                         beneficial_owner_name, bank_account_iban, licenses, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?, ?)
                    """, (org_id, org_type_code, name, registration_number, registration_country,
                          beneficial_owner_name, bank_iban, licenses,
                          datetime.now().isoformat(), datetime.now().isoformat()))
                    
                    if success:
                        log_audit(username, "ORGANIZATION_REGISTERED", org_id)
                        st.success(f" Organisatie geregistreerd! ID: `{org_id}`")
                    else:
                        st.error("Registratie mislukt")


# ============================================================================
# ROL CERTIFICATEN
# ============================================================================

def render_role_certificates(username: str):
    """Beheer rol certificaten en bevoegdheden."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(236, 201, 75, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(236, 201, 75, 0.3);'>
            <h3 style='color: {COLORS["warning"]}; margin: 0;'> Rol Certificaten</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Officiële rolcertificaten met traceerbare bevoegdheden
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Display available roles
    st.markdown("###  Beschikbare Rollen")
    
    cols = st.columns(3)
    for idx, (role_code, role_name, icon, required_level) in enumerate(ROLE_TYPES):
        col_idx = idx % 3
        with cols[col_idx]:
            level_info = VERIFICATION_LEVELS[required_level]
            st.markdown(f"""
                <div style='background: {COLORS["bg_card"]}; padding: 1rem; border-radius: 8px;
                            margin-bottom: 0.5rem; border-left: 3px solid {level_info["color"]};'>
                    <span style='font-size: 1.5rem;'>{icon}</span>
                    <span style='color: {COLORS["text_primary"]}; font-weight: 600;'>{role_name}</span>
                    <br>
                    <span style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>
                        Vereist: Level {required_level}
                    </span>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Existing certificates
    st.markdown("###  Uitgegeven Certificaten")
    
    df = get_data("maroc_role_certificates")
    if not df.empty:
        for _, cert in df.iterrows():
            status_color = COLORS['success'] if cert.get('status') == 'ACTIVE' else COLORS['error']
            
            with st.expander(f" {cert.get('role_name', cert['role_type'])} - {cert.get('status', 'ACTIVE')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Certificaat ID:** `{cert['cert_id']}`")
                    st.write(f"**Rol:** {cert['role_type']}")
                    st.write(f"**Uitgegeven:** {cert.get('issued_at', 'N/A')[:10] if cert.get('issued_at') else 'N/A'}")
                
                with col2:
                    st.write(f"**Geldig tot:** {cert.get('valid_until', 'N/A')[:10] if cert.get('valid_until') else 'Onbeperkt'}")
                    st.markdown(f"**Status:** <span style='color: {status_color};'>{cert.get('status', 'ACTIVE')}</span>", unsafe_allow_html=True)
                    
                if cert.get('status') == 'ACTIVE' and check_permission(["SuperAdmin", "Official"], silent=True):
                    if st.button(" Intrekken", key=f"revoke_{cert['cert_id']}"):
                        run_query("""
                            UPDATE maroc_role_certificates 
                            SET status = 'REVOKED', revoked_at = ?, revoked_by = ?
                            WHERE cert_id = ?
                        """, (datetime.now().isoformat(), username, cert['cert_id']))
                        log_audit(username, "CERTIFICATE_REVOKED", cert['cert_id'])
                        st.rerun()
    else:
        st.info("Nog geen certificaten uitgegeven.")


# ============================================================================
# TRANSACTION SIGNING
# ============================================================================

def render_transaction_signing(username: str):
    """Digitale handtekening voor transacties."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(139, 92, 246, 0.1) 0%, rgba(212, 175, 55, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(139, 92, 246, 0.3);'>
            <h3 style='color: {COLORS["purple"]}; margin: 0;'>️ Transaction Signing</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Digitale handtekening met biometrische bevestiging
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["️ Teken Transactie", " Handtekening Historie"])
    
    with tab1:
        st.markdown("### ️ Nieuwe Transactie Ondertekenen")
        
        with st.form("sign_transaction"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_type = st.selectbox("Transactie Type", SIGNING_REQUIRED_TRANSACTIONS)
                transaction_id = st.text_input("Transactie ID", value=generate_uuid("TXN"))
                amount = st.number_input("Bedrag (€)", min_value=0.0, max_value=1000000.0, value=1000.0)
            
            with col2:
                description = st.text_area("Beschrijving")
                requires_second = st.checkbox("Vereist tweede goedkeuring (2-man rule)")
            
            st.markdown("---")
            
            # Biometric confirmation simulation
            biometric = st.checkbox(" Ik bevestig deze transactie met mijn biometrische gegevens")
            pin = st.text_input("PIN Code", type="password", max_chars=6)
            
            if st.form_submit_button("️ Ondertekenen", width="stretch", type="primary"):
                if not biometric or not pin:
                    st.error("Bevestig met biometrie en PIN")
                elif len(pin) < 4:
                    st.error("PIN moet minimaal 4 cijfers zijn")
                else:
                    sig_id = generate_uuid("SIG")
                    
                    # Generate signature hash
                    sig_data = f"{transaction_type}:{transaction_id}:{amount}:{datetime.now().isoformat()}"
                    sig_hash = generate_signature_hash(sig_data, username)
                    
                    success = run_query("""
                        INSERT INTO maroc_transaction_signatures
                        (sig_id, identity_id, transaction_type, transaction_id, transaction_data,
                         signature_hash, signed_at, biometric_confirmed, requires_second_approval, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, 1, ?, 'SIGNED')
                    """, (sig_id, username, transaction_type, transaction_id,
                          json.dumps({"amount": amount, "description": description}),
                          sig_hash, datetime.now().isoformat(), 1 if requires_second else 0))
                    
                    if success:
                        log_audit(username, "TRANSACTION_SIGNED", sig_id)
                        st.success(f"""
                             **Transactie ondertekend!**
                            
                            **Signature ID:** `{sig_id}`
                            **Hash:** `{sig_hash[:32]}...`
                        """)
                    else:
                        st.error("Ondertekening mislukt")
    
    with tab2:
        df = get_data("maroc_transaction_signatures")
        
        if not df.empty:
            for _, sig in df.tail(20).iterrows():
                status_color = COLORS['success'] if sig.get('status') in ['SIGNED', 'APPROVED'] else COLORS['warning']
                
                st.markdown(f"""
                    <div style='background: {COLORS["bg_card"]}; padding: 1rem; border-radius: 8px;
                                margin-bottom: 0.5rem; border-left: 3px solid {status_color};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='color: {COLORS["gold"]}; font-weight: 600;'>
                                ️ {sig.get('transaction_type', 'N/A')}
                            </span>
                            <span style='color: {COLORS["text_muted"]}; font-size: 0.8rem;'>
                                {sig.get('signed_at', '')[:16] if sig.get('signed_at') else ''}
                            </span>
                        </div>
                        <div style='color: {COLORS["text_secondary"]}; font-size: 0.9rem; margin-top: 0.5rem;'>
                            ID: {sig.get('transaction_id', 'N/A')} | Hash: {sig.get('signature_hash', 'N/A')[:24]}...
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Nog geen transacties ondertekend.")


# ============================================================================
# PMA DASHBOARD
# ============================================================================

def render_pma_dashboard(username: str):
    """Pre-Manifest Advance Dashboard - Douane-grade controle."""
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, #C41E3A 0%, #006233 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;'>
            <h3 style='color: white; margin: 0;'> PMA - Pre-Manifest Advance Dashboard</h3>
            <p style='color: rgba(255,255,255,0.8); margin: 0.5rem 0 0 0;'>
                Douane-grade controle voor geld, contracten, transfers en mensen
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # PMA Stats
    df = get_data("maroc_pma_queue")
    
    pending = len(df[df['status'] == 'PENDING_REVIEW']) if not df.empty else 0
    approved = len(df[df['status'] == 'APPROVED']) if not df.empty else 0
    flagged = len(df[df['status'] == 'FLAGGED']) if not df.empty else 0
    blocked = len(df[df['status'] == 'BLOCKED']) if not df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("⏳ Pending", pending)
    col2.metric(" Approved", approved)
    col3.metric(" Flagged", flagged)
    col4.metric(" Blocked", blocked)
    
    st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs([" Review Queue", " Nieuwe PMA", " Analytics"])
    
    with tab1:
        if not df.empty:
            # Filter
            status_filter = st.selectbox("Filter Status", ["Alle", "PENDING_REVIEW", "FLAGGED", "MANUAL_REVIEW"])
            
            filtered_df = df if status_filter == "Alle" else df[df['status'] == status_filter]
            
            for _, pma in filtered_df.iterrows():
                status_info = next((s for s in PMA_STATUSES if s[0] == pma.get('status')), PMA_STATUSES[0])
                
                with st.expander(f"{status_info[1]} | {pma.get('entity_type', 'N/A')} - €{pma.get('amount', 0):,.2f}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**PMA ID:** `{pma['pma_id']}`")
                        st.write(f"**Type:** {pma.get('transaction_type', 'N/A')}")
                        st.write(f"**Bedrag:** €{pma.get('amount', 0):,.2f}")
                        st.write(f"**Van:** {pma.get('source', 'N/A')}")
                        st.write(f"**Naar:** {pma.get('destination', 'N/A')}")
                    
                    with col2:
                        risk_score = pma.get('risk_score', 0)
                        risk_color = COLORS['success'] if risk_score < 30 else COLORS['warning'] if risk_score < 60 else COLORS['error']
                        
                        st.markdown(f"**Risk Score:** <span style='color: {risk_color}; font-weight: 700;'>{risk_score}</span>", unsafe_allow_html=True)
                        st.write(f"**Risk Factors:** {pma.get('risk_factors', 'None')}")
                        st.write(f"**Aangemaakt:** {pma.get('created_at', 'N/A')[:16] if pma.get('created_at') else 'N/A'}")
                    
                    # Review actions
                    if pma.get('status') in ['PENDING_REVIEW', 'MANUAL_REVIEW', 'FLAGGED']:
                        st.markdown("---")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            if st.button(" Approve", key=f"approve_{pma['pma_id']}"):
                                run_query("""
                                    UPDATE maroc_pma_queue 
                                    SET status = 'APPROVED', reviewed_by = ?, reviewed_at = ?
                                    WHERE pma_id = ?
                                """, (username, datetime.now().isoformat(), pma['pma_id']))
                                log_audit(username, "PMA_APPROVED", pma['pma_id'])
                                st.rerun()
                        
                        with col_b:
                            if st.button(" Flag", key=f"flag_{pma['pma_id']}"):
                                run_query("""
                                    UPDATE maroc_pma_queue 
                                    SET status = 'FLAGGED', reviewed_by = ?, reviewed_at = ?
                                    WHERE pma_id = ?
                                """, (username, datetime.now().isoformat(), pma['pma_id']))
                                log_audit(username, "PMA_FLAGGED", pma['pma_id'])
                                st.rerun()
                        
                        with col_c:
                            if st.button(" Block", key=f"block_{pma['pma_id']}"):
                                run_query("""
                                    UPDATE maroc_pma_queue 
                                    SET status = 'BLOCKED', reviewed_by = ?, reviewed_at = ?
                                    WHERE pma_id = ?
                                """, (username, datetime.now().isoformat(), pma['pma_id']))
                                log_audit(username, "PMA_BLOCKED", pma['pma_id'])
                                st.rerun()
        else:
            st.success(" Geen items in de review queue!")
    
    with tab2:
        st.markdown("###  Nieuwe PMA Entry")
        
        with st.form("new_pma"):
            col1, col2 = st.columns(2)
            
            with col1:
                entity_type = st.selectbox("Entity Type", ["PERSON", "ORGANIZATION", "TRANSACTION", "CONTRACT"])
                entity_id = st.text_input("Entity ID")
                transaction_type = st.selectbox("Transaction Type", 
                    ["TRANSFER", "PAYMENT", "CONTRACT", "DONATION", "INVESTMENT", "WITHDRAWAL"])
                amount = st.number_input("Bedrag (€)", min_value=0.0, value=1000.0)
            
            with col2:
                source = st.text_input("Bron")
                destination = st.text_input("Bestemming")
                description = st.text_area("Beschrijving")
            
            if st.form_submit_button(" Submit voor Review", width="stretch"):
                pma_id = generate_uuid("PMA")
                
                # Auto risk assessment
                risk_score = random.randint(10, 70)  # Simulated
                auto_approved, reason, _ = check_pma_auto_approve(amount, entity_id or "UNKNOWN", transaction_type)
                
                status = "APPROVED" if auto_approved else "PENDING_REVIEW"
                
                success = run_query("""
                    INSERT INTO maroc_pma_queue
                    (pma_id, entity_type, entity_id, transaction_type, amount, source, destination,
                     description, risk_score, auto_approved, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (pma_id, entity_type, entity_id, transaction_type, amount, source, destination,
                      description, risk_score, 1 if auto_approved else 0, status, datetime.now().isoformat()))
                
                if success:
                    log_audit(username, "PMA_SUBMITTED", pma_id)
                    if auto_approved:
                        st.success(f" PMA auto-approved! ID: `{pma_id}`")
                    else:
                        st.info(f"⏳ PMA submitted for review. ID: `{pma_id}` | Reason: {reason}")
    
    with tab3:
        st.markdown("###  PMA Analytics")
        
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Per Status")
                status_counts = df['status'].value_counts()
                st.bar_chart(status_counts)
            
            with col2:
                st.markdown("#### Per Entity Type")
                entity_counts = df['entity_type'].value_counts()
                st.bar_chart(entity_counts)
            
            # Volume
            total_amount = df['amount'].sum()
            avg_risk = df['risk_score'].mean()
            
            st.markdown("---")
            col_a, col_b = st.columns(2)
            col_a.metric(" Totaal Volume", f"€{total_amount:,.0f}")
            col_b.metric("️ Gem. Risk Score", f"{avg_risk:.1f}")
        else:
            st.info("Nog geen PMA data beschikbaar.")


# ============================================================================
# ADMIN
# ============================================================================

def render_admin(username: str):
    """Admin functies voor MAROC ID SHIELD."""
    
    if not check_permission(["SuperAdmin", "Official", "Security Staff"], silent=True):
        st.warning("️ Alleen admins hebben toegang tot deze sectie.")
        return
    
    st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(245, 101, 101, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
                    padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem;
                    border: 1px solid rgba(245, 101, 101, 0.3);'>
            <h3 style='color: {COLORS["error"]}; margin: 0;'>️ Admin Beheer</h3>
            <p style='color: {COLORS["text_muted"]}; margin: 0.5rem 0 0 0;'>
                Systeem configuratie en audit
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([" Verificatie Requests", " Audit Log", "️ Configuratie"])
    
    with tab1:
        st.markdown("###  Openstaande Verificatie Requests")
        
        df = get_data("maroc_verification_requests", "status = 'PENDING'")
        
        if not df.empty:
            for _, req in df.iterrows():
                with st.expander(f" {req['request_type']} - Level {req.get('target_level', 'N/A')}"):
                    st.write(f"**Request ID:** `{req['request_id']}`")
                    st.write(f"**Identity ID:** `{req['identity_id']}`")
                    st.write(f"**Type:** {req['request_type']}")
                    st.write(f"**Target Level:** {req.get('target_level', 'N/A')}")
                    st.write(f"**Submitted:** {req.get('submitted_at', 'N/A')[:16] if req.get('submitted_at') else 'N/A'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(" Approve", key=f"appr_req_{req['request_id']}"):
                            # Update request
                            run_query("""
                                UPDATE maroc_verification_requests 
                                SET status = 'APPROVED', processed_at = ?, processed_by = ?
                                WHERE request_id = ?
                            """, (datetime.now().isoformat(), username, req['request_id']))
                            
                            # Update identity level
                            run_query("""
                                UPDATE maroc_identities 
                                SET verification_level = ?, status = 'VERIFIED', updated_at = ?
                                WHERE identity_id = ?
                            """, (req.get('target_level', 1), datetime.now().isoformat(), req['identity_id']))
                            
                            log_audit(username, "VERIFICATION_APPROVED", req['request_id'])
                            st.success(" Goedgekeurd!")
                            st.rerun()
                    
                    with col2:
                        if st.button(" Reject", key=f"rej_req_{req['request_id']}"):
                            run_query("""
                                UPDATE maroc_verification_requests 
                                SET status = 'REJECTED', processed_at = ?, processed_by = ?
                                WHERE request_id = ?
                            """, (datetime.now().isoformat(), username, req['request_id']))
                            
                            log_audit(username, "VERIFICATION_REJECTED", req['request_id'])
                            st.error(" Afgewezen")
                            st.rerun()
        else:
            st.success(" Geen openstaande requests!")
    
    with tab2:
        st.markdown("###  Recent Audit Log")
        
        audit_df = get_data("audit_logs")
        if not audit_df.empty:
            maroc_audits = audit_df[audit_df['action'].str.contains('MAROC|PMA|VERIFICATION|CERTIFICATE|TRANSACTION_SIGNED', na=False)]
            
            if not maroc_audits.empty:
                for _, log in maroc_audits.tail(50).iterrows():
                    st.markdown(f"""
                        <div style='background: {COLORS["bg_card"]}; padding: 0.5rem 1rem; border-radius: 4px;
                                    margin-bottom: 0.25rem; font-size: 0.9rem;'>
                            <span style='color: {COLORS["text_muted"]};'>{log.get('timestamp', '')[:19]}</span>
                            <span style='color: {COLORS["gold"]}; margin-left: 1rem;'>{log.get('action', '')}</span>
                            <span style='color: {COLORS["text_secondary"]}; margin-left: 1rem;'>{log.get('details', '')}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Geen MAROC ID gerelateerde audit logs.")
        else:
            st.info("Geen audit logs beschikbaar.")
    
    with tab3:
        st.markdown("### ️ Systeem Configuratie")
        
        st.markdown("#### Verificatie Limieten")
        
        col1, col2 = st.columns(2)
        with col1:
            st.number_input("Level 1 Max Transactie (€)", value=500, disabled=True)
            st.number_input("Level 2 Max Transactie (€)", value=10000, disabled=True)
        
        with col2:
            st.number_input("Level 3 Max Transactie (€)", value=1000000, disabled=True)
            st.number_input("Auto-approve Risk Threshold", value=20, disabled=True)
        
        st.markdown("#### PMA Configuratie")
        st.checkbox("Auto-approve enabled", value=True, disabled=True)
        st.checkbox("Two-man rule voor Level 3", value=True, disabled=True)
        
        st.info(" Configuratie wijzigingen vereisen system admin toegang.")
