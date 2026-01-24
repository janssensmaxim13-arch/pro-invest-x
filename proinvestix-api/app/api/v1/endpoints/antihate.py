# ============================================================================
# ProInvestiX Enterprise API - Anti-Hate Shield Endpoints
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import AntiHateIncident, AntiHateLegalCase, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.additional import (
    AntiHateIncidentCreate, AntiHateIncidentResponse,
    LegalCaseCreate, LegalCaseResponse,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/antihate", tags=["Anti-Hate Shield"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_incident_id() -> str:
    return f"AHI-{uuid.uuid4().hex[:8].upper()}"

def generate_case_id() -> str:
    return f"LGC-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# INCIDENTS
# =============================================================================

@router.get("/incidents", response_model=List[AntiHateIncidentResponse])
async def list_incidents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    incident_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
) -> Any:
    """List anti-hate incidents."""
    query = select(AntiHateIncident)
    
    if incident_type:
        query = query.where(AntiHateIncident.incident_type == incident_type)
    if status_filter:
        query = query.where(AntiHateIncident.status == status_filter)
    if severity:
        query = query.where(AntiHateIncident.severity == severity)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(AntiHateIncident.reported_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [AntiHateIncidentResponse.model_validate(i) for i in incidents]


@router.get("/incidents/{incident_id}", response_model=AntiHateIncidentResponse)
async def get_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get incident by ID."""
    result = await db.execute(select(AntiHateIncident).where(AntiHateIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if incident is None:
        raise NotFoundException(resource="Incident", resource_id=incident_id)
    
    return AntiHateIncidentResponse.model_validate(incident)


@router.post("/incidents", response_model=AntiHateIncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    request: AntiHateIncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Report anti-hate incident."""
    incident = AntiHateIncident(
        incident_id=generate_incident_id(),
        incident_type=request.incident_type,
        platform=request.platform,
        severity=request.severity,
        description=request.description,
        victim_name=request.victim_name,
        perpetrator_info=request.perpetrator_info,
        evidence_url=request.evidence_url,
        status="Open",
        reported_by=None if request.is_anonymous else current_user.username,
        reported_at=datetime.utcnow(),
        legal_action_taken=False,
    )
    
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    
    return AntiHateIncidentResponse.model_validate(incident)


@router.put("/incidents/{incident_id}", response_model=AntiHateIncidentResponse)
async def update_incident(
    incident_id: int,
    new_status: Optional[str] = None,
    resolution: Optional[str] = None,
    legal_action: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update incident."""
    result = await db.execute(select(AntiHateIncident).where(AntiHateIncident.id == incident_id))
    incident = result.scalar_one_or_none()
    
    if incident is None:
        raise NotFoundException(resource="Incident", resource_id=incident_id)
    
    if new_status:
        incident.status = new_status
    if resolution:
        incident.resolution = resolution
        incident.resolved_at = datetime.utcnow()
    if legal_action is not None:
        incident.legal_action_taken = legal_action
    
    await db.commit()
    await db.refresh(incident)
    
    return AntiHateIncidentResponse.model_validate(incident)


# =============================================================================
# LEGAL CASES
# =============================================================================

@router.get("/legal", response_model=List[LegalCaseResponse])
async def list_legal_cases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    status_filter: Optional[str] = None,
) -> Any:
    """List legal cases."""
    query = select(AntiHateLegalCase)
    
    if status_filter:
        query = query.where(AntiHateLegalCase.status == status_filter)
    
    query = query.order_by(AntiHateLegalCase.created_at.desc())
    
    result = await db.execute(query)
    cases = result.scalars().all()
    
    return [LegalCaseResponse.model_validate(c) for c in cases]


@router.get("/legal/{case_id}", response_model=LegalCaseResponse)
async def get_legal_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get legal case by ID."""
    result = await db.execute(select(AntiHateLegalCase).where(AntiHateLegalCase.id == case_id))
    case = result.scalar_one_or_none()
    
    if case is None:
        raise NotFoundException(resource="Legal Case", resource_id=case_id)
    
    return LegalCaseResponse.model_validate(case)


@router.post("/legal", response_model=LegalCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_legal_case(
    request: LegalCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create legal case from incident."""
    result = await db.execute(select(AntiHateIncident).where(AntiHateIncident.id == request.incident_id))
    incident = result.scalar_one_or_none()
    
    if incident is None:
        raise NotFoundException(resource="Incident", resource_id=request.incident_id)
    
    case = AntiHateLegalCase(
        case_id=generate_case_id(),
        incident_id=request.incident_id,
        case_type=request.case_type,
        jurisdiction=request.jurisdiction,
        lawyer_name=request.lawyer_name,
        status="Filed",
        filed_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    
    incident.legal_action_taken = True
    
    db.add(case)
    await db.commit()
    await db.refresh(case)
    
    return LegalCaseResponse.model_validate(case)


@router.put("/legal/{case_id}", response_model=LegalCaseResponse)
async def update_legal_case(
    case_id: int,
    new_status: Optional[str] = None,
    verdict: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update legal case."""
    result = await db.execute(select(AntiHateLegalCase).where(AntiHateLegalCase.id == case_id))
    case = result.scalar_one_or_none()
    
    if case is None:
        raise NotFoundException(resource="Legal Case", resource_id=case_id)
    
    if new_status:
        case.status = new_status
    if verdict:
        case.verdict = verdict
        case.verdict_date = datetime.utcnow()
    
    await db.commit()
    await db.refresh(case)
    
    return LegalCaseResponse.model_validate(case)


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats")
async def get_antihate_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get anti-hate statistics."""
    result = await db.execute(select(func.count(AntiHateIncident.id)))
    total = result.scalar() or 0
    
    result = await db.execute(
        select(AntiHateIncident.incident_type, func.count(AntiHateIncident.id))
        .group_by(AntiHateIncident.incident_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}
    
    result = await db.execute(
        select(AntiHateIncident.platform, func.count(AntiHateIncident.id))
        .group_by(AntiHateIncident.platform)
    )
    by_platform = {row[0] or "Unknown": row[1] for row in result.all()}
    
    result = await db.execute(select(func.count(AntiHateLegalCase.id)))
    total_cases = result.scalar() or 0
    
    return {
        "incidents": {"total": total, "by_type": by_type, "by_platform": by_platform},
        "legal_cases": {"total": total_cases},
    }
