# ============================================================================
# ProInvestiX Enterprise API - Hayat Health Endpoints
# Mental Health & Wellbeing Platform
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import HayatSession, HayatCrisisAlert, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.additional import (
    HayatSessionCreate, HayatSessionResponse,
    CrisisAlertCreate, CrisisAlertResponse,
)
from app.core.exceptions import NotFoundException
from pydantic import BaseModel

router = APIRouter(prefix="/hayat", tags=["Hayat Health"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_session_id() -> str:
    return f"HSN-{uuid.uuid4().hex[:8].upper()}"

def generate_alert_id() -> str:
    return f"CRS-{uuid.uuid4().hex[:8].upper()}"

def generate_anonymous_code() -> str:
    return f"ANON-{uuid.uuid4().hex[:12].upper()}"


# =============================================================================
# SESSIONS
# =============================================================================

@router.get("/sessions", response_model=List[HayatSessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
) -> Any:
    """List user's sessions."""
    query = select(HayatSession).where(HayatSession.user_id == current_user.id)
    
    if status:
        query = query.where(HayatSession.status == status)
    
    query = query.order_by(HayatSession.created_at.desc())
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return [HayatSessionResponse.model_validate(s) for s in sessions]


@router.get("/sessions/{session_id}", response_model=HayatSessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get session by ID."""
    result = await db.execute(select(HayatSession).where(HayatSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if session is None:
        raise NotFoundException(resource="Session", resource_id=session_id)
    
    if session.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return HayatSessionResponse.model_validate(session)


@router.post("/sessions", response_model=HayatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: HayatSessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create support session."""
    session = HayatSession(
        session_id=generate_session_id(),
        user_id=None if request.is_anonymous else current_user.id,
        anonymous_code=generate_anonymous_code() if request.is_anonymous else None,
        session_type=request.session_type,
        provider_type=request.provider_type,
        status="Scheduled" if request.scheduled_at else "Requested",
        scheduled_at=request.scheduled_at,
        notes_encrypted=request.notes,
        created_at=datetime.utcnow(),
    )
    
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return HayatSessionResponse.model_validate(session)


@router.put("/sessions/{session_id}", response_model=HayatSessionResponse)
async def update_session(
    session_id: int,
    status: str,
    wellbeing_score: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update session."""
    result = await db.execute(select(HayatSession).where(HayatSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if session is None:
        raise NotFoundException(resource="Session", resource_id=session_id)
    
    session.status = status
    
    if status == "InProgress" and session.started_at is None:
        session.started_at = datetime.utcnow()
    
    if status == "Completed":
        session.ended_at = datetime.utcnow()
        if session.started_at:
            session.duration_minutes = int((session.ended_at - session.started_at).total_seconds() / 60)
        if wellbeing_score:
            session.wellbeing_score_after = wellbeing_score
    
    await db.commit()
    await db.refresh(session)
    
    return HayatSessionResponse.model_validate(session)


# =============================================================================
# WELLBEING
# =============================================================================

@router.get("/wellbeing/{user_id}")
async def get_wellbeing_history(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get wellbeing history."""
    if user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(
        select(HayatSession)
        .where(HayatSession.user_id == user_id)
        .where(HayatSession.wellbeing_score_after != None)
        .order_by(HayatSession.created_at.desc())
        .limit(30)
    )
    sessions = result.scalars().all()
    
    history = [
        {
            "date": s.created_at.date().isoformat(),
            "score_before": s.wellbeing_score_before,
            "score_after": s.wellbeing_score_after,
            "session_type": s.session_type,
        }
        for s in sessions
    ]
    
    return {"user_id": user_id, "history": history}


@router.post("/wellbeing")
async def log_wellbeing(
    score: int,
    notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Log daily wellbeing check."""
    if score < 1 or score > 10:
        raise HTTPException(status_code=400, detail="Score must be between 1 and 10")
    
    session = HayatSession(
        session_id=generate_session_id(),
        user_id=current_user.id,
        session_type="CheckIn",
        status="Completed",
        wellbeing_score_after=score,
        notes_encrypted=notes,
        created_at=datetime.utcnow(),
        ended_at=datetime.utcnow(),
    )
    
    db.add(session)
    await db.commit()
    
    return {"success": True, "score": score, "message": "Wellbeing logged"}


# =============================================================================
# CRISIS ALERTS
# =============================================================================

@router.get("/crisis", response_model=List[CrisisAlertResponse])
async def list_crisis_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    status: Optional[str] = None,
    severity: Optional[str] = None,
) -> Any:
    """List crisis alerts (Admin only)."""
    query = select(HayatCrisisAlert)
    
    if status:
        query = query.where(HayatCrisisAlert.status == status)
    if severity:
        query = query.where(HayatCrisisAlert.severity == severity)
    
    query = query.order_by(HayatCrisisAlert.created_at.desc())
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return [CrisisAlertResponse.model_validate(a) for a in alerts]


@router.post("/crisis", response_model=CrisisAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_crisis_alert(
    request: CrisisAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create crisis alert (immediate help)."""
    alert = HayatCrisisAlert(
        alert_id=generate_alert_id(),
        user_id=current_user.id if request.contact_requested else None,
        anonymous_code=generate_anonymous_code() if not request.contact_requested else None,
        severity=request.severity,
        description=request.description,
        location=request.location,
        status="Open",
        created_at=datetime.utcnow(),
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return CrisisAlertResponse.model_validate(alert)


@router.put("/crisis/{alert_id}", response_model=CrisisAlertResponse)
async def update_crisis_alert(
    alert_id: int,
    status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update crisis alert."""
    result = await db.execute(select(HayatCrisisAlert).where(HayatCrisisAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if alert is None:
        raise NotFoundException(resource="Crisis Alert", resource_id=alert_id)
    
    alert.status = status
    alert.responder_id = current_user.id
    
    if status == "Resolved":
        alert.resolved_at = datetime.utcnow()
        if alert.created_at:
            alert.response_time_minutes = int((alert.resolved_at - alert.created_at).total_seconds() / 60)
    
    await db.commit()
    await db.refresh(alert)
    
    return CrisisAlertResponse.model_validate(alert)


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats")
async def get_hayat_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get Hayat statistics."""
    # Sessions
    result = await db.execute(select(func.count(HayatSession.id)))
    total_sessions = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(HayatSession.id)).where(HayatSession.status == "Completed")
    )
    completed = result.scalar() or 0
    
    # By type
    result = await db.execute(
        select(HayatSession.session_type, func.count(HayatSession.id))
        .group_by(HayatSession.session_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}
    
    # Crisis alerts
    result = await db.execute(select(func.count(HayatCrisisAlert.id)))
    total_crisis = result.scalar() or 0
    
    result = await db.execute(
        select(func.avg(HayatCrisisAlert.response_time_minutes))
        .where(HayatCrisisAlert.response_time_minutes != None)
    )
    avg_response = result.scalar() or 0
    
    return {
        "sessions": {
            "total": total_sessions,
            "completed": completed,
            "by_type": by_type,
        },
        "crisis": {
            "total": total_crisis,
            "avg_response_minutes": round(avg_response, 1),
        }
    }
