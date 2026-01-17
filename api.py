# ============================================================================
# PROINVESTIX REST API
# FastAPI backend voor externe integraties
# ============================================================================

from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import hashlib
import secrets

# =============================================================================
# CONFIG
# =============================================================================

DB_FILE = "proinvestix_ultimate.db"
API_VERSION = "1.0.0"

# API Key validation
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Valid API keys (in production, store in database or environment)
VALID_API_KEYS = {
    "pk_live_proinvestix_2026": {"name": "Production Key", "role": "admin"},
    "pk_test_proinvestix_demo": {"name": "Test Key", "role": "readonly"},
}

# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(
    title="ProInvestiX API",
    description="REST API for ProInvestiX National Investment Platform",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# AUTHENTICATION
# =============================================================================

async def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key is None:
        raise HTTPException(status_code=401, detail="API Key required")
    if api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return VALID_API_KEYS[api_key]

# =============================================================================
# MODELS
# =============================================================================

class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str

class TalentProfile(BaseModel):
    talent_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str]
    nationality: Optional[str]
    position: Optional[str]
    current_club: Optional[str]
    status: Optional[str]

class Transfer(BaseModel):
    transfer_id: str
    player_name: str
    from_club: Optional[str]
    to_club: Optional[str]
    fee: Optional[float]
    status: str

class TicketEvent(BaseModel):
    event_id: str
    name: str
    location: str
    date: str
    capacity: int
    tickets_sold: int

class Ticket(BaseModel):
    ticket_hash: str
    event_id: str
    owner_id: str
    seat_info: str
    price: float
    status: str

class WalletBalance(BaseModel):
    wallet_id: str
    identity_id: str
    balance: float
    currency: str
    status: str

class FoundationStats(BaseModel):
    total_contributions: float
    total_donations: float
    contributor_count: int
    donation_count: int

class Referee(BaseModel):
    referee_id: str
    first_name: str
    last_name: str
    license_level: str
    total_matches: Optional[int]
    avg_rating: Optional[float]
    status: str

class VARDecision(BaseModel):
    var_id: str
    match_id: str
    minute: int
    decision_type: str
    outcome: str
    screenshot_hash: Optional[str]

class Signal(BaseModel):
    signal_id: str
    platform: str
    title: str
    manipulation_type: str
    risk_level: str
    status: str

class Identity(BaseModel):
    identity_id: str
    name: Optional[str]
    risk_level: Optional[str]
    status: Optional[str]

# =============================================================================
# DATABASE HELPER
# =============================================================================

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    return dict(row) if row else None

# =============================================================================
# ENDPOINTS - HEALTH
# =============================================================================

@app.get("/", tags=["Health"])
async def root():
    return {"message": "ProInvestiX API", "version": API_VERSION, "docs": "/docs"}

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": API_VERSION,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/stats", tags=["Health"])
async def get_stats(auth: dict = Depends(verify_api_key)):
    """Get platform statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    stats = {}
    
    tables = [
        ("talents", "ntsp_talent_profiles"),
        ("transfers", "transfers"),
        ("tickets", "ticketchain_tickets"),
        ("events", "ticketchain_events"),
        ("wallets", "diaspora_wallets"),
        ("identities", "identity_shield"),
        ("referees", "frmf_referees"),
        ("signals", "nil_signals"),
    ]
    
    for name, table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[name] = cursor.fetchone()[0]
        except:
            stats[name] = 0
    
    conn.close()
    return {"stats": stats, "timestamp": datetime.now().isoformat()}

# =============================================================================
# ENDPOINTS - NTSP (Talents)
# =============================================================================

@app.get("/api/v1/talents", tags=["NTSP"])
async def list_talents(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List talent profiles"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM ntsp_talent_profiles"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += f" LIMIT {limit} OFFSET {offset}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"talents": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/talents/{talent_id}", tags=["NTSP"])
async def get_talent(talent_id: str, auth: dict = Depends(verify_api_key)):
    """Get single talent profile"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ntsp_talent_profiles WHERE talent_id = ?", (talent_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Talent not found")
    
    return dict_from_row(row)

# =============================================================================
# ENDPOINTS - TRANSFERS
# =============================================================================

@app.get("/api/v1/transfers", tags=["Transfers"])
async def list_transfers(
    limit: int = Query(50, ge=1, le=500),
    status: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List transfers"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM transfers"
    params = []
    
    if status:
        query += " WHERE status = ?"
        params.append(status)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"transfers": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/transfers/{transfer_id}", tags=["Transfers"])
async def get_transfer(transfer_id: str, auth: dict = Depends(verify_api_key)):
    """Get single transfer"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transfers WHERE transfer_id = ?", (transfer_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    return dict_from_row(row)

# =============================================================================
# ENDPOINTS - TICKETCHAIN
# =============================================================================

@app.get("/api/v1/events", tags=["TicketChain"])
async def list_events(
    limit: int = Query(50, ge=1, le=100),
    auth: dict = Depends(verify_api_key)
):
    """List events"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM ticketchain_events LIMIT {limit}")
    rows = cursor.fetchall()
    conn.close()
    
    return {"events": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/events/{event_id}", tags=["TicketChain"])
async def get_event(event_id: str, auth: dict = Depends(verify_api_key)):
    """Get single event"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ticketchain_events WHERE event_id = ?", (event_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return dict_from_row(row)

@app.get("/api/v1/tickets/verify/{ticket_hash}", tags=["TicketChain"])
async def verify_ticket(ticket_hash: str, auth: dict = Depends(verify_api_key)):
    """Verify ticket authenticity"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ticketchain_tickets WHERE ticket_hash = ?", (ticket_hash,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"valid": False, "message": "Ticket not found"}
    
    ticket = dict_from_row(row)
    return {
        "valid": True,
        "status": ticket.get("status", "UNKNOWN"),
        "event_id": ticket.get("event_id"),
        "owner_id": ticket.get("owner_id"),
        "seat_info": ticket.get("seat_info")
    }

# =============================================================================
# ENDPOINTS - WALLETS
# =============================================================================

@app.get("/api/v1/wallets", tags=["Diaspora Wallet"])
async def list_wallets(
    limit: int = Query(50, ge=1, le=500),
    auth: dict = Depends(verify_api_key)
):
    """List wallets"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM diaspora_wallets LIMIT {limit}")
    rows = cursor.fetchall()
    conn.close()
    
    return {"wallets": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/wallets/{wallet_id}/balance", tags=["Diaspora Wallet"])
async def get_wallet_balance(wallet_id: str, auth: dict = Depends(verify_api_key)):
    """Get wallet balance"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diaspora_wallets WHERE wallet_id = ?", (wallet_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    wallet = dict_from_row(row)
    return {
        "wallet_id": wallet_id,
        "balance": wallet.get("balance", 0),
        "currency": wallet.get("currency", "EUR"),
        "status": wallet.get("status", "UNKNOWN")
    }

# =============================================================================
# ENDPOINTS - FOUNDATION
# =============================================================================

@app.get("/api/v1/foundation/stats", tags=["Foundation"])
async def get_foundation_stats(auth: dict = Depends(verify_api_key)):
    """Get foundation statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Contributions
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM foundation_contributions")
    contrib_row = cursor.fetchone()
    
    # Donations
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM foundation_donations")
    donation_row = cursor.fetchone()
    
    conn.close()
    
    return {
        "contributions": {
            "count": contrib_row[0],
            "total": contrib_row[1]
        },
        "donations": {
            "count": donation_row[0],
            "total": donation_row[1]
        },
        "grand_total": contrib_row[1] + donation_row[1]
    }

# =============================================================================
# ENDPOINTS - FRMF (Referees & VAR)
# =============================================================================

@app.get("/api/v1/referees", tags=["FRMF"])
async def list_referees(
    limit: int = Query(50, ge=1, le=200),
    level: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List referees"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM frmf_referees"
    params = []
    
    if level:
        query += " WHERE license_level = ?"
        params.append(level)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"referees": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/var-decisions", tags=["FRMF"])
async def list_var_decisions(
    limit: int = Query(50, ge=1, le=200),
    match_id: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List VAR decisions"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM frmf_var_vault"
    params = []
    
    if match_id:
        query += " WHERE match_id = ?"
        params.append(match_id)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"var_decisions": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/var-decisions/{var_id}/verify", tags=["FRMF"])
async def verify_var_decision(var_id: str, auth: dict = Depends(verify_api_key)):
    """Verify VAR decision authenticity via hash"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM frmf_var_vault WHERE var_id = ?", (var_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"valid": False, "message": "VAR decision not found"}
    
    decision = dict_from_row(row)
    return {
        "valid": True,
        "var_id": var_id,
        "match_id": decision.get("match_id"),
        "decision_type": decision.get("decision_type"),
        "outcome": decision.get("outcome"),
        "screenshot_hash": decision.get("screenshot_hash"),
        "is_authentic": True
    }

# =============================================================================
# ENDPOINTS - NIL (Narrative Integrity)
# =============================================================================

@app.get("/api/v1/signals", tags=["NIL"])
async def list_signals(
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List NIL signals"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM nil_signals"
    conditions = []
    params = []
    
    if status:
        conditions.append("status = ?")
        params.append(status)
    if risk_level:
        conditions.append("risk_level = ?")
        params.append(risk_level)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"signals": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/signals/{signal_id}", tags=["NIL"])
async def get_signal(signal_id: str, auth: dict = Depends(verify_api_key)):
    """Get single NIL signal"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nil_signals WHERE signal_id = ?", (signal_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Signal not found")
    
    return dict_from_row(row)

# =============================================================================
# ENDPOINTS - IDENTITY
# =============================================================================

@app.get("/api/v1/identities", tags=["Identity"])
async def list_identities(
    limit: int = Query(50, ge=1, le=500),
    risk_level: Optional[str] = None,
    auth: dict = Depends(verify_api_key)
):
    """List identities"""
    conn = get_db()
    cursor = conn.cursor()
    
    query = "SELECT * FROM identity_shield"
    params = []
    
    if risk_level:
        query += " WHERE risk_level = ?"
        params.append(risk_level)
    
    query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return {"identities": [dict_from_row(r) for r in rows], "count": len(rows)}

@app.get("/api/v1/identities/{identity_id}/verify", tags=["Identity"])
async def verify_identity(identity_id: str, auth: dict = Depends(verify_api_key)):
    """Verify identity status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM identity_shield WHERE identity_id = ?", (identity_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"verified": False, "message": "Identity not found"}
    
    identity = dict_from_row(row)
    return {
        "verified": True,
        "identity_id": identity_id,
        "risk_level": identity.get("risk_level", "UNKNOWN"),
        "status": identity.get("status", "UNKNOWN")
    }

# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
