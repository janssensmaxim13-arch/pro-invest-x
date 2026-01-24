# ============================================================================
# ProInvestiX Enterprise API - Academy Endpoints
# ============================================================================

from datetime import datetime, date
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Academy, AcademyTeam, AcademyStaff, AcademyEnrollment, Talent, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.academy import (
    AcademyCreate, AcademyUpdate, AcademyResponse, AcademyListResponse,
    TeamCreate, TeamResponse,
    StaffCreate, StaffResponse,
    EnrollmentCreate, EnrollmentResponse,
    AcademyStats,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/academies", tags=["Academy"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_academy_id() -> str:
    return f"ACD-{uuid.uuid4().hex[:8].upper()}"

def generate_team_id() -> str:
    return f"TM-{uuid.uuid4().hex[:8].upper()}"

def generate_staff_id() -> str:
    return f"STF-{uuid.uuid4().hex[:8].upper()}"

def generate_enrollment_id() -> str:
    return f"ENR-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# ACADEMIES CRUD
# =============================================================================

@router.get("", response_model=AcademyListResponse)
async def list_academies(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    region: Optional[str] = None,
    license_level: Optional[str] = None,
    is_active: bool = True,
) -> Any:
    """List all academies."""
    query = select(Academy).where(Academy.is_active == is_active)
    
    if region:
        query = query.where(Academy.region == region)
    if license_level:
        query = query.where(Academy.license_level == license_level)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(Academy.name)
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    academies = result.scalars().all()
    
    return AcademyListResponse(
        success=True,
        data=[AcademyResponse.model_validate(a) for a in academies],
        meta={"total": total, "page": page, "per_page": per_page}
    )


@router.get("/{academy_id}", response_model=AcademyResponse)
async def get_academy(
    academy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get academy by ID."""
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    
    if academy is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    return AcademyResponse.model_validate(academy)


@router.post("", response_model=AcademyResponse, status_code=status.HTTP_201_CREATED)
async def create_academy(
    request: AcademyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create academy."""
    academy = Academy(
        academy_id=generate_academy_id(),
        **request.model_dump(),
        is_active=True,
        total_talents=0,
        total_staff=0,
        created_at=datetime.utcnow(),
    )
    
    db.add(academy)
    await db.commit()
    await db.refresh(academy)
    
    return AcademyResponse.model_validate(academy)


@router.put("/{academy_id}", response_model=AcademyResponse)
async def update_academy(
    academy_id: int,
    request: AcademyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update academy."""
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    
    if academy is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(academy, field, value)
    
    await db.commit()
    await db.refresh(academy)
    
    return AcademyResponse.model_validate(academy)


@router.delete("/{academy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_academy(
    academy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> None:
    """Delete (deactivate) academy."""
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    
    if academy is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    academy.is_active = False
    await db.commit()


# =============================================================================
# TEAMS
# =============================================================================

@router.get("/{academy_id}/teams", response_model=List[TeamResponse])
async def get_academy_teams(
    academy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get academy teams."""
    result = await db.execute(
        select(AcademyTeam)
        .where(AcademyTeam.academy_id == academy_id)
        .order_by(AcademyTeam.age_group)
    )
    teams = result.scalars().all()
    
    return [TeamResponse.model_validate(t) for t in teams]


@router.post("/{academy_id}/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
async def create_team(
    academy_id: int,
    request: TeamCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create team in academy."""
    # Verify academy exists
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    team = AcademyTeam(
        team_id=generate_team_id(),
        academy_id=academy_id,
        **request.model_dump(),
        current_players=0,
        is_active=True,
        created_at=datetime.utcnow(),
    )
    
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    return TeamResponse.model_validate(team)


# =============================================================================
# STAFF
# =============================================================================

@router.get("/{academy_id}/staff", response_model=List[StaffResponse])
async def get_academy_staff(
    academy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get academy staff."""
    result = await db.execute(
        select(AcademyStaff)
        .where(AcademyStaff.academy_id == academy_id)
        .where(AcademyStaff.is_active == True)
        .order_by(AcademyStaff.role)
    )
    staff = result.scalars().all()
    
    return [StaffResponse.model_validate(s) for s in staff]


@router.post("/{academy_id}/staff", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
async def add_staff(
    academy_id: int,
    request: StaffCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Add staff to academy."""
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    
    if academy is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    staff = AcademyStaff(
        staff_id=generate_staff_id(),
        academy_id=academy_id,
        **request.model_dump(),
        is_active=True,
        joined_date=date.today(),
        created_at=datetime.utcnow(),
    )
    
    db.add(staff)
    academy.total_staff += 1
    
    await db.commit()
    await db.refresh(staff)
    
    return StaffResponse.model_validate(staff)


# =============================================================================
# ENROLLMENTS
# =============================================================================

@router.get("/{academy_id}/enrollments", response_model=List[EnrollmentResponse])
async def get_enrollments(
    academy_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
) -> Any:
    """Get academy enrollments."""
    query = select(AcademyEnrollment).where(AcademyEnrollment.academy_id == academy_id)
    
    if status:
        query = query.where(AcademyEnrollment.status == status)
    
    query = query.order_by(AcademyEnrollment.enrolled_date.desc())
    
    result = await db.execute(query)
    enrollments = result.scalars().all()
    
    return [EnrollmentResponse.model_validate(e) for e in enrollments]


@router.post("/{academy_id}/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_talent(
    academy_id: int,
    request: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Enroll talent in academy."""
    # Verify academy
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    if academy is None:
        raise NotFoundException(resource="Academy", resource_id=academy_id)
    
    # Verify talent
    result = await db.execute(select(Talent).where(Talent.id == request.talent_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="Talent", resource_id=request.talent_id)
    
    enrollment = AcademyEnrollment(
        enrollment_id=generate_enrollment_id(),
        academy_id=academy_id,
        **request.model_dump(),
        status="Active",
        enrolled_date=date.today(),
        created_at=datetime.utcnow(),
    )
    
    db.add(enrollment)
    academy.total_talents += 1
    
    await db.commit()
    await db.refresh(enrollment)
    
    return EnrollmentResponse.model_validate(enrollment)


@router.delete("/{academy_id}/enrollments/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_enrollment(
    academy_id: int,
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> None:
    """Remove enrollment."""
    result = await db.execute(
        select(AcademyEnrollment)
        .where(AcademyEnrollment.id == enrollment_id)
        .where(AcademyEnrollment.academy_id == academy_id)
    )
    enrollment = result.scalar_one_or_none()
    
    if enrollment is None:
        raise NotFoundException(resource="Enrollment", resource_id=enrollment_id)
    
    enrollment.status = "Terminated"
    
    # Update academy count
    result = await db.execute(select(Academy).where(Academy.id == academy_id))
    academy = result.scalar_one_or_none()
    if academy and academy.total_talents > 0:
        academy.total_talents -= 1
    
    await db.commit()


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=AcademyStats)
async def get_academy_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get academy statistics."""
    # Total academies
    result = await db.execute(select(func.count(Academy.id)).where(Academy.is_active == True))
    total_academies = result.scalar() or 0
    
    # Total talents
    result = await db.execute(select(func.sum(Academy.total_talents)))
    total_talents = result.scalar() or 0
    
    # Total staff
    result = await db.execute(select(func.sum(Academy.total_staff)))
    total_staff = result.scalar() or 0
    
    # By region
    result = await db.execute(
        select(Academy.region, func.count(Academy.id))
        .where(Academy.is_active == True)
        .group_by(Academy.region)
    )
    by_region = {row[0] or "Unknown": row[1] for row in result.all()}
    
    # By license level
    result = await db.execute(
        select(Academy.license_level, func.count(Academy.id))
        .where(Academy.is_active == True)
        .group_by(Academy.license_level)
    )
    by_license = {row[0] or "None": row[1] for row in result.all()}
    
    # Top academies
    result = await db.execute(
        select(Academy.name, Academy.total_talents)
        .where(Academy.is_active == True)
        .order_by(Academy.total_talents.desc())
        .limit(10)
    )
    top = [{"name": row[0], "talents": row[1]} for row in result.all()]
    
    return AcademyStats(
        total_academies=total_academies,
        total_talents=total_talents,
        total_staff=total_staff,
        by_region=by_region,
        by_license_level=by_license,
        top_academies=top,
    )
