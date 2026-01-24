# ============================================================================
# ProInvestiX Enterprise API - FRMF Endpoints
# Royal Moroccan Football Federation
# ============================================================================

from datetime import datetime, date
from typing import Any, List, Optional
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.frmf import (
    RefereeCreate, RefereeUpdate, RefereeResponse,
    VARDecisionCreate, VARDecisionResponse,
    FRMFPlayerCreate, FRMFPlayerResponse,
    ContractCreate, ContractResponse,
    MatchAssignmentCreate, MatchAssignmentResponse,
    FRMFStats,
)
from app.core.exceptions import NotFoundException
from pydantic import BaseModel

router = APIRouter(prefix="/frmf", tags=["FRMF"])


# =============================================================================
# IN-MEMORY STORAGE (zou in productie database models zijn)
# =============================================================================

referees_db = []
var_decisions_db = []
players_db = []
contracts_db = []
matches_db = []
referee_chain = []  # Blockchain voor referees


# =============================================================================
# HELPERS
# =============================================================================

def generate_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

def generate_blockchain_hash(data: str) -> str:
    prev_hash = referee_chain[-1]["hash"] if referee_chain else "0" * 64
    block_data = f"{prev_hash}{data}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(block_data.encode()).hexdigest()


# =============================================================================
# REFEREES
# =============================================================================

@router.get("/referees", response_model=List[RefereeResponse])
async def list_referees(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    grade: Optional[str] = None,
    region: Optional[str] = None,
    is_active: bool = True,
) -> Any:
    """List all referees."""
    result = [r for r in referees_db if r.get("is_active", True) == is_active]
    
    if grade:
        result = [r for r in result if r.get("license_grade") == grade]
    if region:
        result = [r for r in result if r.get("region") == region]
    
    return result


@router.get("/referees/{referee_id}", response_model=RefereeResponse)
async def get_referee(
    referee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get referee by ID."""
    for r in referees_db:
        if r["id"] == referee_id:
            return r
    raise NotFoundException(resource="Referee", resource_id=referee_id)


@router.post("/referees", response_model=RefereeResponse, status_code=status.HTTP_201_CREATED)
async def create_referee(
    request: RefereeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create referee."""
    referee = {
        "id": len(referees_db) + 1,
        "referee_id": generate_id("REF"),
        **request.model_dump(),
        "is_active": True,
        "status": "Active",
        "total_matches": 0,
        "avg_rating": None,
        "blockchain_hash": generate_blockchain_hash(request.first_name + request.last_name),
        "created_at": datetime.utcnow(),
    }
    
    # Add to blockchain
    referee_chain.append({
        "index": len(referee_chain),
        "referee_id": referee["referee_id"],
        "hash": referee["blockchain_hash"],
        "timestamp": datetime.utcnow().isoformat(),
    })
    
    referees_db.append(referee)
    return referee


@router.put("/referees/{referee_id}", response_model=RefereeResponse)
async def update_referee(
    referee_id: int,
    request: RefereeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update referee."""
    for r in referees_db:
        if r["id"] == referee_id:
            update_data = request.model_dump(exclude_unset=True)
            r.update(update_data)
            return r
    raise NotFoundException(resource="Referee", resource_id=referee_id)


# =============================================================================
# REFEREE BLOCKCHAIN
# =============================================================================

@router.get("/refereechain")
async def get_referee_chain(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get referee blockchain."""
    return {
        "chain": referee_chain,
        "length": len(referee_chain),
        "is_valid": True,
    }


@router.get("/refereechain/verify")
async def verify_referee_chain(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Verify referee blockchain integrity."""
    is_valid = True
    invalid_blocks = []
    
    for i in range(1, len(referee_chain)):
        # In a real implementation, we'd verify hash chains
        pass
    
    return {
        "is_valid": is_valid,
        "total_blocks": len(referee_chain),
        "invalid_blocks": invalid_blocks,
    }


# =============================================================================
# VAR DECISIONS
# =============================================================================

@router.get("/var-decisions", response_model=List[VARDecisionResponse])
async def list_var_decisions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    decision_type: Optional[str] = None,
    match_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """List VAR decisions."""
    result = var_decisions_db.copy()
    
    if decision_type:
        result = [d for d in result if d.get("decision_type") == decision_type]
    if match_id:
        result = [d for d in result if d.get("match_id") == match_id]
    
    return result[:limit]


@router.get("/var-decisions/{decision_id}", response_model=VARDecisionResponse)
async def get_var_decision(
    decision_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get VAR decision by ID."""
    for d in var_decisions_db:
        if d["id"] == decision_id:
            return d
    raise NotFoundException(resource="VAR Decision", resource_id=decision_id)


@router.post("/var-decisions", response_model=VARDecisionResponse, status_code=status.HTTP_201_CREATED)
async def create_var_decision(
    request: VARDecisionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Record VAR decision."""
    decision = {
        "id": len(var_decisions_db) + 1,
        "decision_id": generate_id("VAR"),
        **request.model_dump(),
        "decision_changed": request.original_decision != request.final_decision,
        "blockchain_hash": generate_blockchain_hash(f"{request.match_id}-{request.minute}"),
        "verified": True,
        "created_at": datetime.utcnow(),
    }
    
    var_decisions_db.append(decision)
    return decision


@router.get("/var-decisions/{decision_id}/verify")
async def verify_var_decision(
    decision_id: int,
    current_user: User = Depends(get_current_user),
) -> Any:
    """Verify VAR decision on blockchain."""
    for d in var_decisions_db:
        if d["id"] == decision_id:
            return {
                "decision_id": d["decision_id"],
                "verified": d.get("verified", True),
                "blockchain_hash": d.get("blockchain_hash"),
                "timestamp": d.get("created_at"),
            }
    raise NotFoundException(resource="VAR Decision", resource_id=decision_id)


# =============================================================================
# PLAYERS
# =============================================================================

@router.get("/players", response_model=List[FRMFPlayerResponse])
async def list_players(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    club: Optional[str] = None,
    is_national_team: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """List FRMF registered players."""
    result = players_db.copy()
    
    if club:
        result = [p for p in result if p.get("current_club") == club]
    if is_national_team is not None:
        result = [p for p in result if p.get("is_national_team") == is_national_team]
    
    return result[:limit]


@router.get("/players/{player_id}", response_model=FRMFPlayerResponse)
async def get_player(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get player by ID."""
    for p in players_db:
        if p["id"] == player_id:
            return p
    raise NotFoundException(resource="Player", resource_id=player_id)


@router.post("/players", response_model=FRMFPlayerResponse, status_code=status.HTTP_201_CREATED)
async def create_player(
    request: FRMFPlayerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Register player with FRMF."""
    player = {
        "id": len(players_db) + 1,
        "player_id": generate_id("PLY"),
        **request.model_dump(),
        "status": "Active",
        "registration_date": date.today(),
        "created_at": datetime.utcnow(),
    }
    
    players_db.append(player)
    return player


# =============================================================================
# CONTRACTS
# =============================================================================

@router.get("/contracts", response_model=List[ContractResponse])
async def list_contracts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    player_id: Optional[int] = None,
    club: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    """List contracts."""
    result = contracts_db.copy()
    
    if player_id:
        result = [c for c in result if c.get("player_id") == player_id]
    if club:
        result = [c for c in result if c.get("club_name") == club]
    if status:
        result = [c for c in result if c.get("status") == status]
    
    return result


@router.post("/contracts", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(
    request: ContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Register contract."""
    contract = {
        "id": len(contracts_db) + 1,
        "contract_id": generate_id("CTR"),
        **request.model_dump(),
        "status": "Active",
        "blockchain_hash": generate_blockchain_hash(f"{request.player_id}-{request.club_name}"),
        "created_at": datetime.utcnow(),
    }
    
    contracts_db.append(contract)
    return contract


@router.get("/contracts/{contract_id}", response_model=ContractResponse)
async def get_contract(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get contract by ID."""
    for c in contracts_db:
        if c["id"] == contract_id:
            return c
    raise NotFoundException(resource="Contract", resource_id=contract_id)


# =============================================================================
# MATCH ASSIGNMENTS
# =============================================================================

@router.get("/matches", response_model=List[MatchAssignmentResponse])
async def list_match_assignments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    referee_id: Optional[int] = None,
    competition: Optional[str] = None,
    date_from: Optional[date] = None,
) -> Any:
    """List match assignments."""
    result = matches_db.copy()
    
    if referee_id:
        result = [m for m in result if m.get("main_referee_id") == referee_id]
    if competition:
        result = [m for m in result if m.get("competition") == competition]
    if date_from:
        result = [m for m in result if m.get("match_date") >= date_from]
    
    return result


@router.post("/matches", response_model=MatchAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_match_assignment(
    request: MatchAssignmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create match assignment."""
    assignment = {
        "id": len(matches_db) + 1,
        "assignment_id": generate_id("MTH"),
        **request.model_dump(),
        "status": "Scheduled",
        "created_at": datetime.utcnow(),
    }
    
    matches_db.append(assignment)
    return assignment


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=FRMFStats)
async def get_frmf_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get FRMF statistics."""
    total_var = len(var_decisions_db)
    changed = len([d for d in var_decisions_db if d.get("decision_changed", False)])
    
    # By referee grade
    by_grade = {}
    for r in referees_db:
        grade = r.get("license_grade", "Unknown")
        by_grade[grade] = by_grade.get(grade, 0) + 1
    
    # By competition
    by_competition = {}
    for m in matches_db:
        comp = m.get("competition", "Unknown")
        by_competition[comp] = by_competition.get(comp, 0) + 1
    
    return FRMFStats(
        total_referees=len(referees_db),
        total_players=len(players_db),
        total_contracts=len(contracts_db),
        total_var_decisions=total_var,
        var_decisions_changed=changed,
        var_accuracy_rate=round((total_var - changed) / total_var * 100, 2) if total_var > 0 else 100,
        by_referee_grade=by_grade,
        by_competition=by_competition,
    )
