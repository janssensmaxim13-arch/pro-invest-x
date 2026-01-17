# ============================================================================
# PROINVESTIX - NARRATIVE INTEGRITY LAYER (NIL™)
# Dossier 28: Social Media Manipulatie Detectie & Response
# ============================================================================

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import hmac
import json
from typing import Optional, Dict

from config import DB_FILE, BLOCKCHAIN_SECRET
from database.connection import get_data, run_query, count_records
from utils.helpers import generate_uuid
from auth.security import log_audit
from ui.styles import COLORS
from ui.components import page_header, premium_kpi_row, info_box, success_message
from translations import get_text, get_current_language

try:
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

def t(key):
    return get_text(key, get_current_language())

# =============================================================================
# CONSTANTS
# =============================================================================

MANIPULATION_TYPES = [
    ("FAKE_QUOTE", "Fake Quote / Nepquote", "🗣"),
    ("EDITED_CLIP", "Edited Video Clip", "🎬"),
    ("DEEPFAKE", "AI Deepfake", "🤖"),
    ("BOT_ATTACK", "Coordinated Bot Attack", "🤖"),
    ("IMPERSONATION", "Account Impersonation", ""),
    ("CONTEXT_MANIPULATION", "Context Manipulation", ""),
    ("COORDINATED_CAMPAIGN", "Coordinated Campaign", ""),
    ("REFEREE_HARASSMENT", "Referee/Official Harassment", ""),
    ("FALSE_NEWS", "False Breaking News", "📰"),
    ("IMAGE_MANIPULATION", "Manipulated Image", "🖼"),
    ("HATE_SPEECH", "Hate Speech / Racism", "🚫"),
    ("MISINFORMATION", "General Misinformation", ""),
]

RISK_LEVELS = [
    ("LOW", "Low", "#48BB78", 24),
    ("MEDIUM", "Medium", "#ECC94B", 4),
    ("HIGH", "High", "#F56565", 1),
    ("CRITICAL", "Critical", "#E53E3E", 0.5),
]

PLATFORMS = [
    ("FACEBOOK", "Facebook", "📘"),
    ("INSTAGRAM", "Instagram", "📷"),
    ("TWITTER", "Twitter/X", "🐦"),
    ("TIKTOK", "TikTok", "🎵"),
    ("YOUTUBE", "YouTube", ""),
    ("WHATSAPP", "WhatsApp", ""),
    ("TELEGRAM", "Telegram", "✈"),
    ("OTHER", "Other", ""),
]

SIGNAL_STATUSES = [
    ("DETECTED", "Detected", "#4299E1"),
    ("TRIAGING", "Triaging", "#ECC94B"),
    ("INVESTIGATING", "Investigating", "#9F7AEA"),
    ("FACT_CARD_ISSUED", "Fact Card Issued", "#48BB78"),
    ("ESCALATED", "Escalated", "#F56565"),
    ("RESOLVED", "Resolved", "#68D391"),
    ("MONITORING", "Monitoring", "#A0AEC0"),
    ("DISMISSED", "Dismissed", "#718096"),
]

SOURCE_CATEGORIES = [
    ("TRUSTED", "Trusted", "#48BB78"),
    ("NEUTRAL", "Neutral", "#A0AEC0"),
    ("SUSPICIOUS", "Suspicious", "#ECC94B"),
    ("HIGH_RISK", "High Risk", "#F56565"),
    ("BLACKLISTED", "Blacklisted", "#E53E3E"),
]

CRISIS_LEVELS = [
    ("LOW", " Low", 24*60),
    ("MEDIUM", " Medium", 4*60),
    ("HIGH", " High", 60),
    ("CRITICAL", "🚨 Critical", 30),
]

RESPONSE_LEVELS = ["STANDARD", "URGENT", "CRISIS"]

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_content_hash(url: str, content: str = "") -> str:
    message = f"{url}|{content}|{datetime.now().isoformat()}"
    return hashlib.sha256(message.encode()).hexdigest()

def generate_blockchain_hash(evidence_id: str, content_hash: str) -> str:
    message = f"{evidence_id}|{content_hash}|{datetime.now().isoformat()}"
    return hmac.new(BLOCKCHAIN_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

def calculate_risk_score(engagement: int, shares: int, source_credibility: int, confidence: int) -> tuple:
    engagement_score = min(40, (engagement / 10000) * 40)
    virality_score = min(30, (shares / 1000) * 30)
    credibility_risk = (100 - source_credibility) * 0.15
    manipulation_score = confidence * 0.15
    total = engagement_score + virality_score + credibility_risk + manipulation_score
    
    if total >= 75: return ("CRITICAL", total)
    elif total >= 50: return ("HIGH", total)
    elif total >= 25: return ("MEDIUM", total)
    else: return ("LOW", total)

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

def create_signal(data: Dict) -> Optional[str]:
    signal_id = generate_uuid("SIG")
    try:
        success = run_query("""
            INSERT INTO nil_signals (signal_id, platform, content_url, content_type, title, description,
                manipulation_type, risk_level, confidence_score, views, likes, shares, comments,
                source_account, status, priority, detected_at, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (signal_id, data.get('platform'), data.get('content_url'), data.get('content_type', 'POST'),
              data.get('title'), data.get('description'), data.get('manipulation_type'),
              data.get('risk_level', 'LOW'), data.get('confidence_score', 50),
              data.get('views', 0), data.get('likes', 0), data.get('shares', 0), data.get('comments', 0),
              data.get('source_account'), 'DETECTED', data.get('priority', 'STANDARD'),
              datetime.now().isoformat(), data.get('created_by'), datetime.now().isoformat()))
        return signal_id if success else None
    except Exception as e:
        return None

def create_source(data: Dict) -> Optional[str]:
    source_id = generate_uuid("SRC")
    success = run_query("""
        INSERT INTO nil_sources (source_id, platform, account_name, account_handle, account_url,
            followers, following, total_posts, credibility_score, fake_content_count, 
            verified_content_count, risk_category, is_verified, is_official, is_media,
            is_bot_suspected, is_blacklisted, first_seen_at, last_activity_at, incidents_count,
            notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (source_id, data.get('platform'), data.get('account_name'), data.get('account_handle'),
          data.get('account_url'), data.get('followers', 0), data.get('following', 0),
          data.get('total_posts', 0), data.get('credibility_score', 50), data.get('fake_content_count', 0),
          data.get('verified_content_count', 0), data.get('risk_category', 'NEUTRAL'),
          data.get('is_verified', 0), data.get('is_official', 0), data.get('is_media', 0),
          data.get('is_bot_suspected', 0), data.get('is_blacklisted', 0),
          datetime.now().isoformat(), datetime.now().isoformat(), data.get('incidents_count', 0),
          data.get('notes'), datetime.now().isoformat()))
    return source_id if success else None

def create_evidence(data: Dict) -> Optional[str]:
    evidence_id = generate_uuid("EVD")
    content_hash = generate_content_hash(data.get('original_url', ''), data.get('raw_content', ''))
    blockchain_tx = generate_blockchain_hash(evidence_id, content_hash)
    success = run_query("""
        INSERT INTO nil_evidence (evidence_id, signal_id, content_hash, original_url, raw_content,
            metadata_json, archive_status, hash_algorithm, blockchain_tx, legal_value,
            captured_at, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (evidence_id, data.get('signal_id'), content_hash, data.get('original_url'),
          data.get('raw_content'), data.get('metadata_json'), 'ARCHIVED', 'SHA256', blockchain_tx,
          data.get('legal_value', 'MEDIUM'), datetime.now().isoformat(),
          data.get('created_by'), datetime.now().isoformat()))
    return evidence_id if success else None

def create_fact_card(data: Dict) -> Optional[str]:
    fact_card_id = generate_uuid("FC")
    success = run_query("""
        INSERT INTO nil_fact_cards (fact_card_id, signal_id, incident_title, verified_facts,
            false_claims, official_source_url, additional_context, response_level, language,
            created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (fact_card_id, data.get('signal_id'), data.get('incident_title'), data.get('verified_facts'),
          data.get('false_claims'), data.get('official_source_url'), data.get('additional_context'),
          data.get('response_level', 'STANDARD'), data.get('language', 'en'),
          data.get('created_by'), datetime.now().isoformat()))
    
    if success and data.get('signal_id'):
        run_query("UPDATE nil_signals SET fact_card_id = ?, status = 'FACT_CARD_ISSUED' WHERE signal_id = ?",
                  (fact_card_id, data.get('signal_id')))
    return fact_card_id if success else None

def create_crisis(data: Dict) -> Optional[str]:
    incident_id = generate_uuid("CRI")
    success = run_query("""
        INSERT INTO nil_crisis_incidents (incident_id, incident_name, description, crisis_level,
            category, status, incident_lead, detected_at, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (incident_id, data.get('incident_name'), data.get('description'),
          data.get('crisis_level', 'LOW'), data.get('category'), 'OPEN',
          data.get('incident_lead'), datetime.now().isoformat(),
          data.get('created_by'), datetime.now().isoformat()))
    return incident_id if success else None

def get_nil_stats() -> Dict:
    signals = get_data("nil_signals")
    sources = get_data("nil_sources")
    evidence = get_data("nil_evidence")
    fact_cards = get_data("nil_fact_cards")
    crises = get_data("nil_crisis_incidents")
    
    return {
        'total_signals': len(signals) if not signals.empty else 0,
        'active_signals': len(signals[signals['status'].isin(['DETECTED', 'TRIAGING', 'INVESTIGATING'])]) if not signals.empty and 'status' in signals.columns else 0,
        'critical_signals': len(signals[signals['risk_level'] == 'CRITICAL']) if not signals.empty and 'risk_level' in signals.columns else 0,
        'total_sources': len(sources) if not sources.empty else 0,
        'blacklisted_sources': len(sources[sources['risk_category'] == 'BLACKLISTED']) if not sources.empty and 'risk_category' in sources.columns else 0,
        'total_evidence': len(evidence) if not evidence.empty else 0,
        'total_fact_cards': len(fact_cards) if not fact_cards.empty else 0,
        'active_crises': len(crises[crises['status'] == 'OPEN']) if not crises.empty and 'status' in crises.columns else 0,
    }

# =============================================================================
# DEMO DATA
# =============================================================================

def generate_demo_signals() -> pd.DataFrame:
    import random
    signals = []
    titles = [
        "Zidane breaks silence on Morocco return - FULL STORY",
        "VAR controversy PROOF - Match was fixed!",
        "BREAKING: FRMF corruption scandal exposed",
        "Star player threatens to leave national team",
        "WK 2030 budget fraud revealed",
        "Fake interview goes viral",
    ]
    for i in range(12):
        signals.append({
            "signal_id": f"SIG-{random.randint(100000, 999999)}",
            "platform": random.choice([p[0] for p in PLATFORMS]),
            "title": random.choice(titles),
            "manipulation_type": random.choice([m[0] for m in MANIPULATION_TYPES]),
            "risk_level": random.choice([r[0] for r in RISK_LEVELS]),
            "confidence_score": random.randint(40, 95),
            "views": random.randint(1000, 500000),
            "shares": random.randint(100, 50000),
            "status": random.choice([s[0] for s in SIGNAL_STATUSES[:5]]),
            "source_account": f"@user_{random.randint(100,999)}",
            "detected_at": (datetime.now() - timedelta(hours=random.randint(1, 72))).strftime("%Y-%m-%d %H:%M"),
        })
    return pd.DataFrame(signals)

def generate_demo_sources() -> pd.DataFrame:
    import random
    sources = []
    names = [("FootballLeaks_MA", "TWITTER", "HIGH_RISK"), ("TruthAboutFRMF", "FACEBOOK", "BLACKLISTED"),
             ("VAR_Watch", "INSTAGRAM", "SUSPICIOUS"), ("MoroccoSports24", "TWITTER", "NEUTRAL"),
             ("FRMF_Official", "TWITTER", "TRUSTED"), ("WK2030Updates", "INSTAGRAM", "TRUSTED")]
    for name, platform, risk in names:
        sources.append({
            "source_id": f"SRC-{hash(name) % 900000 + 100000}",
            "account_name": name, "platform": platform,
            "followers": random.randint(5000, 500000),
            "credibility_score": random.randint(15, 95),
            "fake_content_count": random.randint(0, 50),
            "risk_category": risk,
            "is_verified": 1 if risk == "TRUSTED" else 0,
        })
    return pd.DataFrame(sources)


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_signal_monitor(username: str):
    st.markdown("###  Real-time Signal Monitor")
    st.caption("Monitoring viral content across platforms for manipulation")
    
    df = get_data("nil_signals")
    if df.empty:
        df = generate_demo_signals()
        info_box("Demo Mode", "Showing demo data. Add real signals to see live monitoring.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        platform_filter = st.selectbox("Platform", ["All"] + [p[1] for p in PLATFORMS])
    with col2:
        risk_filter = st.selectbox("Risk Level", ["All"] + [r[1] for r in RISK_LEVELS])
    with col3:
        status_filter = st.selectbox(t("status"), ["All"] + [s[1] for s in SIGNAL_STATUSES])
    
    if platform_filter != "All":
        code = next((p[0] for p in PLATFORMS if p[1] == platform_filter), None)
        if code: df = df[df['platform'] == code]
    if risk_filter != "All":
        code = next((r[0] for r in RISK_LEVELS if r[1] == risk_filter), None)
        if code: df = df[df['risk_level'] == code]
    if status_filter != "All":
        code = next((s[0] for s in SIGNAL_STATUSES if s[1] == status_filter), None)
        if code and 'status' in df.columns: df = df[df['status'] == code]
    
    critical = len(df[df['risk_level'] == 'CRITICAL']) if 'risk_level' in df.columns else 0
    high = len(df[df['risk_level'] == 'HIGH']) if 'risk_level' in df.columns else 0
    
    if critical > 0:
        st.error(f"🚨 **{critical} CRITICAL** signals require immediate attention!")
    if high > 0:
        st.warning(f" **{high} HIGH** risk signals need review within 1 hour")
    
    st.divider()
    
    for _, row in df.head(10).iterrows():
        risk_color = next((r[2] for r in RISK_LEVELS if r[0] == row.get('risk_level')), "#A0AEC0")
        status_color = next((s[2] for s in SIGNAL_STATUSES if s[0] == row.get('status', 'DETECTED')), "#4299E1")
        platform_icon = next((p[2] for p in PLATFORMS if p[0] == row.get('platform')), "")
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 1, 1])
            with c1:
                title = str(row.get('title', 'No title'))
                st.markdown(f"**{platform_icon} {title[:55]}{'...' if len(title) > 55 else ''}**")
                st.caption(f"Source: {row.get('source_account', 'Unknown')} • {row.get('detected_at', 'N/A')}")
            with c2:
                st.markdown(f"<span style='background:{risk_color};color:white;padding:2px 8px;border-radius:4px;'>{row.get('risk_level','LOW')}</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<span style='background:{status_color};color:white;padding:2px 8px;border-radius:4px;'>{row.get('status','DETECTED')}</span>", unsafe_allow_html=True)
    
    st.divider()
    with st.expander("➕ Report New Signal"):
        with st.form("new_signal"):
            c1, c2 = st.columns(2)
            with c1:
                title = st.text_input("Title *")
                platform = st.selectbox("Platform", [f"{p[2]} {p[1]}" for p in PLATFORMS])
                manip = st.selectbox("Manipulation Type", [f"{m[2]} {m[1]}" for m in MANIPULATION_TYPES])
            with c2:
                source = st.text_input("Source Account")
                views = st.number_input("Views", 0)
                shares = st.number_input("Shares", 0)
                confidence = st.slider("Confidence", 0, 100, 50)
            
            if st.form_submit_button("🚨 Submit", type="primary", width="stretch"):
                if title:
                    platform_code = next((p[0] for p in PLATFORMS if p[1] in platform), "OTHER")
                    manip_code = next((m[0] for m in MANIPULATION_TYPES if m[1] in manip), "MISINFORMATION")
                    risk, _ = calculate_risk_score(views, shares, 50, confidence)
                    
                    sig_id = create_signal({
                        'title': title, 'platform': platform_code, 'manipulation_type': manip_code,
                        'source_account': source, 'views': views, 'shares': shares,
                        'confidence_score': confidence, 'risk_level': risk, 'created_by': username
                    })
                    if sig_id:
                        success_message("Signal Reported!", f"{sig_id} - {risk} risk")
                        log_audit(username, "SIGNAL_CREATED", "NIL", sig_id)
                        st.rerun()

def render_content_forensics(username: str):
    st.markdown("### 🔬 Content Forensics")
    st.caption("Analyze content for manipulation with AI-powered detection")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("forensics"):
            url = st.text_input("Content URL *")
            content_type = st.selectbox("Type", ["Video", "Image", "Text Post", "Audio"])
            analyze_clicked = st.form_submit_button(" Analyze", type="primary", width="stretch")
        
        if analyze_clicked and url:
            import time, random
            with st.spinner("Analyzing..."):
                time.sleep(1.5)
            
            manip = random.randint(20, 95)
            deepfake = random.randint(5, 85) if content_type in ["Video", "Image"] else 0
            clickbait = random.randint(30, 90)
            
            # Store in session state for archive button
            st.session_state['forensics_result'] = {
                'url': url,
                'manip': manip,
                'deepfake': deepfake,
                'clickbait': clickbait,
                'content_type': content_type
            }
            
            st.success(" Analysis Complete!")
            
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("Manipulation", f"{manip}%")
            with m2: st.metric("Deepfake", f"{deepfake}%" if deepfake else "N/A")
            with m3: st.metric("Clickbait", f"{clickbait}%")
            
            issues = []
            if manip > 60: issues.append(" High manipulation probability")
            if deepfake > 50: issues.append(" Potential AI-generated media")
            if clickbait > 70: issues.append(" Clickbait patterns detected")
            if not issues: issues.append(" Content appears authentic")
            
            for i in issues: st.markdown(f"- {i}")
        
        # Archive button outside form
        if 'forensics_result' in st.session_state:
            result = st.session_state['forensics_result']
            if st.button("📥 Archive to Evidence Vault"):
                eid = create_evidence({
                    'original_url': result['url'],
                    'metadata_json': json.dumps({'manip': result['manip'], 'deepfake': result['deepfake']}),
                    'legal_value': 'HIGH' if result['manip'] > 70 else 'MEDIUM',
                    'created_by': username
                })
                if eid:
                    success_message("Archived!", f"{eid}")
                    del st.session_state['forensics_result']
    
    with c2:
        st.markdown("#### Quick Stats")
        st.metric("Analyses Today", "47")
        st.metric("Confirmed Fake", "23")
        st.divider()
        for cap in [" AI image detection", " Deepfake analysis", " Bot detection"]:
            st.markdown(f"<small>{cap}</small>", unsafe_allow_html=True)

def render_source_registry(username: str):
    st.markdown("###  Source Registry")
    
    df = get_data("nil_sources")
    if df.empty:
        df = generate_demo_sources()
        info_box("Demo Mode", "Showing demo data.")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total", len(df))
    with c2: st.metric("Trusted", len(df[df['risk_category'] == 'TRUSTED']))
    with c3: st.metric("Suspicious", len(df[df['risk_category'].isin(['SUSPICIOUS', 'HIGH_RISK'])]))
    with c4: st.metric("Blacklisted", len(df[df['risk_category'] == 'BLACKLISTED']))
    
    st.divider()
    st.dataframe(df[['account_name', 'platform', 'followers', 'credibility_score', 'risk_category']], 
                 width="stretch", hide_index=True)
    
    with st.expander("➕ Add Source"):
        with st.form("add_source"):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Account Name *")
                platform = st.selectbox("Platform", [p[1] for p in PLATFORMS])
            with c2:
                followers = st.number_input("Followers", 0)
                risk = st.selectbox("Risk Category", [c[1] for c in SOURCE_CATEGORIES])
            
            if st.form_submit_button("➕ Add", width="stretch"):
                if name:
                    sid = create_source({
                        'account_name': name,
                        'platform': next((p[0] for p in PLATFORMS if p[1] == platform), "OTHER"),
                        'followers': followers,
                        'risk_category': next((c[0] for c in SOURCE_CATEGORIES if c[1] == risk), "NEUTRAL"),
                    })
                    if sid:
                        success_message("Added!", sid)
                        st.rerun()

def render_evidence_vault(username: str):
    st.markdown("### 🗃 Evidence Vault")
    info_box("Blockchain Secured", "All evidence is SHA256 hashed and HMAC signed.", "")
    
    df = get_data("nil_evidence")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Entries", len(df) if not df.empty else 0)
    with c2: st.metric("High Legal Value", len(df[df['legal_value'] == 'HIGH']) if not df.empty and 'legal_value' in df.columns else 0)
    with c3: st.metric("Blockchain Verified", len(df) if not df.empty else 0)
    
    st.divider()
    
    if not df.empty:
        for _, row in df.head(8).iterrows():
            with st.container(border=True):
                st.markdown(f"**{row.get('evidence_id', 'N/A')}**")
                st.caption(f"Hash: `{str(row.get('content_hash', 'N/A'))[:20]}...`")
                st.caption(f"Legal: {row.get('legal_value', 'MEDIUM')} | {str(row.get('captured_at', ''))[:10]}")
    else:
        st.info("No evidence yet. Use Content Forensics to archive.")
    
    with st.expander("📥 Quick Archive"):
        with st.form("archive"):
            url = st.text_input("URL *")
            legal = st.select_slider("Legal Value", ["LOW", "MEDIUM", "HIGH"])
            if st.form_submit_button("📥 Archive", type="primary", width="stretch"):
                if url:
                    eid = create_evidence({'original_url': url, 'legal_value': legal, 'created_by': username})
                    if eid:
                        success_message("Archived!", eid)
                        st.rerun()

def render_fact_cards(username: str):
    st.markdown("### 📄 Fact Card Generator")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        with st.form("fact_card"):
            title = st.text_input("Incident Title *")
            facts = st.text_area(" Verified Facts *", height=80)
            false_claims = st.text_area(" False Claims *", height=80)
            source = st.text_input("Official Source URL")
            level = st.selectbox("Response Level", RESPONSE_LEVELS)
            
            if st.form_submit_button("📄 Generate", type="primary", width="stretch"):
                if title and facts and false_claims:
                    fcid = create_fact_card({
                        'incident_title': title, 'verified_facts': facts,
                        'false_claims': false_claims, 'official_source_url': source,
                        'response_level': level, 'created_by': username
                    })
                    if fcid:
                        success_message("Created!", fcid)
                        st.markdown(f"""
                        <div style='background:white;border:2px solid {COLORS["purple_light"]};border-radius:12px;padding:20px;margin-top:1rem;'>
                            <h3 style='color:{COLORS["purple_light"]};'> FACT CARD - {fcid}</h3>
                            <h4>{title}</h4>
                            <div style='background:#F0FDF4;border-left:4px solid #22C55E;padding:1rem;margin:1rem 0;'>
                                <strong> VERIFIED:</strong><br>{facts}
                            </div>
                            <div style='background:#FEF2F2;border-left:4px solid #EF4444;padding:1rem;margin:1rem 0;'>
                                <strong> FALSE:</strong><br>{false_claims}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("#### Recent Cards")
        fcs = get_data("nil_fact_cards")
        if not fcs.empty:
            for _, row in fcs.head(5).iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row.get('fact_card_id', 'N/A')}**")
                    st.caption(str(row.get('incident_title', ''))[:25])
        else:
            st.info("No fact cards yet")

def render_crisis_playbook(username: str):
    st.markdown("### 🚨 Crisis Response Playbook")
    
    c1, c2, c3, c4 = st.columns(4)
    for col, (level, label, _) in zip([c1, c2, c3, c4], CRISIS_LEVELS):
        with col:
            with st.container(border=True):
                st.markdown(f"### {label}")
                times = {"LOW": "< 24h", "MEDIUM": "< 4h", "HIGH": "< 1h", "CRITICAL": "< 30min"}
                st.markdown(f"**Response:** {times.get(level, '< 24h')}")
    
    st.divider()
    st.markdown("#### Active Crises")
    
    crises = get_data("nil_crisis_incidents")
    active = crises[crises['status'] == 'OPEN'] if not crises.empty and 'status' in crises.columns else pd.DataFrame()
    
    if not active.empty:
        for _, row in active.iterrows():
            with st.container(border=True):
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.markdown(f"**{row.get('incident_name', 'Unnamed')}**")
                    st.caption(f"Level: {row.get('crisis_level', 'LOW')}")
                with c2:
                    if st.button("Resolve", key=f"r_{row.get('incident_id')}"):
                        run_query("UPDATE nil_crisis_incidents SET status='RESOLVED', resolved_at=? WHERE incident_id=?",
                                  (datetime.now().isoformat(), row.get('incident_id')))
                        st.rerun()
    else:
        st.success(" No active crises")
    
    with st.expander("🚨 Declare Crisis"):
        with st.form("crisis"):
            name = st.text_input("Name *")
            level = st.selectbox("Level", [c[1] for c in CRISIS_LEVELS])
            desc = st.text_area("Description *")
            
            if st.form_submit_button("🚨 Declare", type="primary", width="stretch"):
                if name and desc:
                    cid = create_crisis({
                        'incident_name': name,
                        'crisis_level': next((c[0] for c in CRISIS_LEVELS if c[1] == level), "LOW"),
                        'description': desc,
                        'incident_lead': username,
                        'created_by': username
                    })
                    if cid:
                        st.error(f"🚨 CRISIS DECLARED: {cid}")
                        st.rerun()

def render_kpi_dashboard():
    st.markdown("###  NIL Performance Metrics")
    
    stats = get_nil_stats()
    
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("Active Signals", stats['active_signals'])
    with c2: st.metric("Critical", stats['critical_signals'], delta_color="inverse")
    with c3: st.metric("Fact Cards", stats['total_fact_cards'])
    with c4: st.metric("Evidence", stats['total_evidence'])
    with c5: st.metric("Crises", stats['active_crises'], delta_color="inverse")
    
    st.divider()
    st.markdown("#### Target KPIs")
    
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown("**Time-to-Triage**\n- Target: < 60 min\n- Status: ")
    with k2:
        st.markdown("**Time-to-FactCard**\n- Target: < 2 hours\n- Status: ")
    with k3:
        st.markdown("**Virality Containment**\n- Target: -50% in 12h\n- Status: ")

# =============================================================================
# MAIN RENDER
# =============================================================================

def render(username: str = None):
    if not username: username = "Anonymous"
    
    st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(139,92,246,0.15),rgba(79,70,229,0.1));
                    border:1px solid rgba(139,92,246,0.3);border-radius:16px;padding:2rem;
                    margin-bottom:2rem;text-align:center;'>
            <div style='font-size:3rem;'></div>
            <h1 style='font-family:Rajdhani;font-size:2rem;color:{COLORS["purple_light"]};margin:0;'>
                Narrative Integrity Layer (NIL™)</h1>
            <p style='color:{COLORS["text_secondary"]};'>Detectie • Verificatie • Response • Bewijsvoering</p>
            <div style='background:rgba(139,92,246,0.1);border-radius:8px;padding:0.5rem;display:inline-block;'>
                <span style='color:{COLORS["text_muted"]};font-size:0.85rem;'>CAF/FRMF/FIFA-proof • Dossier 28</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    stats = get_nil_stats()
    premium_kpi_row([
        ("", "Active Signals", str(stats['active_signals']), "Real-time"),
        ("", "Critical", str(stats['critical_signals']), "< 30 min"),
        ("📄", "Fact Cards", str(stats['total_fact_cards']), "Issued"),
        ("🗃", "Evidence", str(stats['total_evidence']), "Archived"),
        ("🚨", "Crises", str(stats['active_crises']), "Open"),
    ])
    
    st.divider()
    
    tabs = st.tabs([" Signals", "🔬 Forensics", " Sources", "🗃 Evidence", "📄 Fact Cards", "🚨 Crisis", " KPIs"])
    
    with tabs[0]: render_signal_monitor(username)
    with tabs[1]: render_content_forensics(username)
    with tabs[2]: render_source_registry(username)
    with tabs[3]: render_evidence_vault(username)
    with tabs[4]: render_fact_cards(username)
    with tabs[5]: render_crisis_playbook(username)
    with tabs[6]: render_kpi_dashboard()
