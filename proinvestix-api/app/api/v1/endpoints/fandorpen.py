# ============================================================================
# ProInvestiX Enterprise API - FanDorpen Endpoints
# WK 2030 Fan Villages
# ============================================================================

from datetime import datetime, date, time
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import FanDorp, FanDorpVolunteer, FanDorpShift, FanDorpIncident, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.fandorp import (
    FanDorpCreate, FanDorpUpdate, FanDorpResponse, FanDorpListResponse,
    VolunteerCreate, VolunteerResponse,
    ShiftCreate, ShiftResponse, ShiftCheckIn,
    IncidentCreate, IncidentUpdate, IncidentResponse,
    FanDorpStats,
)
from app.core.exceptions import NotFoundException, BusinessLogicException

router = APIRouter(prefix="/fandorpen", tags=["FanDorpen - WK 2030"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_fandorp_id() -> str:
    return f"FDR-{uuid.uuid4().hex[:8].upper()}"

def generate_volunteer_id() -> str:
    return f"VOL-{uuid.uuid4().hex[:8].upper()}"

def generate_shift_id() -> str:
    return f"SHF-{uuid.uuid4().hex[:8].upper()}"

def generate_incident_id() -> str:
    return f"INC-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# FANDORPEN CRUD
# =============================================================================

@router.get("", response_model=FanDorpListResponse)
async def list_fandorpen(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    city: Optional[str] = None,
    status: Optional[str] = None,
) -> Any:
    """List all FanDorpen."""
    query = select(FanDorp)
    
    if city:
        query = query.where(FanDorp.city.ilike(f"%{city}%"))
    if status:
        query = query.where(FanDorp.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(FanDorp.name)
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    fandorpen = result.scalars().all()
    
    return FanDorpListResponse(
        success=True,
        data=[FanDorpResponse.model_validate(f) for f in fandorpen],
        meta={"total": total, "page": page, "per_page": per_page}
    )


@router.get("/{fandorp_id}", response_model=FanDorpResponse)
async def get_fandorp(
    fandorp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get FanDorp by ID."""
    result = await db.execute(select(FanDorp).where(FanDorp.id == fandorp_id))
    fandorp = result.scalar_one_or_none()
    
    if fandorp is None:
        raise NotFoundException(resource="FanDorp", resource_id=fandorp_id)
    
    return FanDorpResponse.model_validate(fandorp)


@router.post("", response_model=FanDorpResponse, status_code=status.HTTP_201_CREATED)
async def create_fandorp(
    request: FanDorpCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create FanDorp."""
    fandorp = FanDorp(
        fandorp_id=generate_fandorp_id(),
        **request.model_dump(),
        status="Planning",
        total_volunteers=0,
        total_visitors=0,
        created_at=datetime.utcnow(),
    )
    
    db.add(fandorp)
    await db.commit()
    await db.refresh(fandorp)
    
    return FanDorpResponse.model_validate(fandorp)


@router.put("/{fandorp_id}", response_model=FanDorpResponse)
async def update_fandorp(
    fandorp_id: int,
    request: FanDorpUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update FanDorp."""
    result = await db.execute(select(FanDorp).where(FanDorp.id == fandorp_id))
    fandorp = result.scalar_one_or_none()
    
    if fandorp is None:
        raise NotFoundException(resource="FanDorp", resource_id=fandorp_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fandorp, field, value)
    
    await db.commit()
    await db.refresh(fandorp)
    
    return FanDorpResponse.model_validate(fandorp)


# =============================================================================
# VOLUNTEERS
# =============================================================================

@router.get("/{fandorp_id}/volunteers", response_model=List[VolunteerResponse])
async def get_volunteers(
    fandorp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
) -> Any:
    """Get FanDorp volunteers."""
    query = select(FanDorpVolunteer).where(FanDorpVolunteer.fandorp_id == fandorp_id)
    
    if status:
        query = query.where(FanDorpVolunteer.status == status)
    
    query = query.order_by(FanDorpVolunteer.last_name)
    
    result = await db.execute(query)
    volunteers = result.scalars().all()
    
    return [VolunteerResponse.model_validate(v) for v in volunteers]


@router.post("/{fandorp_id}/volunteers", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
async def register_volunteer(
    fandorp_id: int,
    request: VolunteerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Register as volunteer."""
    # Verify FanDorp
    result = await db.execute(select(FanDorp).where(FanDorp.id == fandorp_id))
    fandorp = result.scalar_one_or_none()
    
    if fandorp is None:
        raise NotFoundException(resource="FanDorp", resource_id=fandorp_id)
    
    volunteer = FanDorpVolunteer(
        volunteer_id=generate_volunteer_id(),
        fandorp_id=fandorp_id,
        user_id=current_user.id,
        **request.model_dump(),
        status="Pending",
        training_completed=False,
        badge_issued=False,
        total_hours=0,
        total_shifts=0,
        created_at=datetime.utcnow(),
    )
    
    db.add(volunteer)
    fandorp.total_volunteers += 1
    
    await db.commit()
    await db.refresh(volunteer)
    
    return VolunteerResponse.model_validate(volunteer)


# =============================================================================
# SHIFTS
# =============================================================================

@router.get("/{fandorp_id}/shifts", response_model=List[ShiftResponse])
async def get_shifts(
    fandorp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> Any:
    """Get FanDorp shifts."""
    query = select(FanDorpShift).where(FanDorpShift.fandorp_id == fandorp_id)
    
    if date_from:
        query = query.where(FanDorpShift.date >= date_from)
    if date_to:
        query = query.where(FanDorpShift.date <= date_to)
    
    query = query.order_by(FanDorpShift.date, FanDorpShift.start_time)
    
    result = await db.execute(query)
    shifts = result.scalars().all()
    
    return [ShiftResponse.model_validate(s) for s in shifts]


@router.post("/{fandorp_id}/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    fandorp_id: int,
    request: ShiftCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create shift."""
    result = await db.execute(select(FanDorp).where(FanDorp.id == fandorp_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="FanDorp", resource_id=fandorp_id)
    
    shift = FanDorpShift(
        shift_id=generate_shift_id(),
        fandorp_id=fandorp_id,
        **request.model_dump(),
        current_volunteers=0,
        status="Open",
        created_at=datetime.utcnow(),
    )
    
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    
    return ShiftResponse.model_validate(shift)


@router.post("/{fandorp_id}/shifts/{shift_id}/checkin")
async def checkin_shift(
    fandorp_id: int,
    shift_id: int,
    request: ShiftCheckIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Check in to shift."""
    result = await db.execute(
        select(FanDorpShift)
        .where(FanDorpShift.id == shift_id)
        .where(FanDorpShift.fandorp_id == fandorp_id)
    )
    shift = result.scalar_one_or_none()
    
    if shift is None:
        raise NotFoundException(resource="Shift", resource_id=shift_id)
    
    if shift.current_volunteers >= shift.max_volunteers:
        raise BusinessLogicException(detail="Shift is full", error_code="SHIFT_FULL")
    
    # Update volunteer
    result = await db.execute(
        select(FanDorpVolunteer).where(FanDorpVolunteer.id == request.volunteer_id)
    )
    volunteer = result.scalar_one_or_none()
    
    if volunteer:
        volunteer.total_shifts += 1
        # Calculate hours
        start = datetime.combine(shift.date, shift.start_time)
        end = datetime.combine(shift.date, shift.end_time)
        hours = (end - start).seconds / 3600
        volunteer.total_hours += hours
    
    shift.current_volunteers += 1
    
    await db.commit()
    
    return {"success": True, "message": "Checked in successfully"}


@router.post("/{fandorp_id}/shifts/{shift_id}/checkout")
async def checkout_shift(
    fandorp_id: int,
    shift_id: int,
    request: ShiftCheckIn,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Check out from shift."""
    return {"success": True, "message": "Checked out successfully"}


# =============================================================================
# INCIDENTS
# =============================================================================

@router.get("/{fandorp_id}/incidents", response_model=List[IncidentResponse])
async def get_incidents(
    fandorp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
    severity: Optional[str] = None,
) -> Any:
    """Get FanDorp incidents."""
    query = select(FanDorpIncident).where(FanDorpIncident.fandorp_id == fandorp_id)
    
    if status:
        query = query.where(FanDorpIncident.status == status)
    if severity:
        query = query.where(FanDorpIncident.severity == severity)
    
    query = query.order_by(FanDorpIncident.reported_at.desc())
    
    result = await db.execute(query)
    incidents = result.scalars().all()
    
    return [IncidentResponse.model_validate(i) for i in incidents]


@router.post("/{fandorp_id}/incidents", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def report_incident(
    fandorp_id: int,
    request: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Report incident."""
    result = await db.execute(select(FanDorp).where(FanDorp.id == fandorp_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="FanDorp", resource_id=fandorp_id)
    
    incident = FanDorpIncident(
        incident_id=generate_incident_id(),
        fandorp_id=fandorp_id,
        **request.model_dump(),
        status="Open",
        reported_by=current_user.username,
        reported_at=datetime.utcnow(),
    )
    
    db.add(incident)
    await db.commit()
    await db.refresh(incident)
    
    return IncidentResponse.model_validate(incident)


@router.put("/{fandorp_id}/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    fandorp_id: int,
    incident_id: int,
    request: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update incident."""
    result = await db.execute(
        select(FanDorpIncident)
        .where(FanDorpIncident.id == incident_id)
        .where(FanDorpIncident.fandorp_id == fandorp_id)
    )
    incident = result.scalar_one_or_none()
    
    if incident is None:
        raise NotFoundException(resource="Incident", resource_id=incident_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(incident, field, value)
    
    if request.status == "Resolved" and request.resolution:
        incident.resolved_at = datetime.utcnow()
        incident.resolved_by = current_user.username
    
    await db.commit()
    await db.refresh(incident)
    
    return IncidentResponse.model_validate(incident)


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=FanDorpStats)
async def get_fandorp_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get FanDorp statistics."""
    # Total FanDorpen
    result = await db.execute(select(func.count(FanDorp.id)))
    total = result.scalar() or 0
    
    # Total capacity
    result = await db.execute(select(func.sum(FanDorp.capacity)))
    capacity = result.scalar() or 0
    
    # Total volunteers
    result = await db.execute(select(func.count(FanDorpVolunteer.id)))
    volunteers = result.scalar() or 0
    
    # Total visitors
    result = await db.execute(select(func.sum(FanDorp.total_visitors)))
    visitors = result.scalar() or 0
    
    # Total incidents
    result = await db.execute(select(func.count(FanDorpIncident.id)))
    incidents = result.scalar() or 0
    
    # By city
    result = await db.execute(
        select(FanDorp.city, func.count(FanDorp.id))
        .group_by(FanDorp.city)
    )
    by_city = {row[0]: row[1] for row in result.all()}
    
    # By status
    result = await db.execute(
        select(FanDorp.status, func.count(FanDorp.id))
        .group_by(FanDorp.status)
    )
    by_status = {row[0]: row[1] for row in result.all()}
    
    # Volunteer hours
    result = await db.execute(select(func.sum(FanDorpVolunteer.total_hours)))
    hours = result.scalar() or 0
    
    return FanDorpStats(
        total_fandorpen=total,
        total_capacity=capacity,
        total_volunteers=volunteers,
        total_visitors=visitors,
        total_incidents=incidents,
        by_city=by_city,
        by_status=by_status,
        volunteer_hours=hours,
    )
