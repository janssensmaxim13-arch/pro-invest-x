# ============================================================================
# ProInvestiX Enterprise API - Scouts Endpoints
# NTSP - National Talent Scouting Platform
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Scout, TalentEvaluation, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.talent import (
    ScoutCreate,
    ScoutUpdate,
    ScoutResponse,
    EvaluationResponse,
)
from app.core.exceptions import NotFoundException, AlreadyExistsException

router = APIRouter(prefix="/scouts", tags=["NTSP - Scouts"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_scout_id() -> str:
    """Generate unique scout ID."""
    return f"SCT-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# LIST SCOUTS
# =============================================================================

@router.get("", response_model=List[ScoutResponse])
async def list_scouts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    is_active: Optional[bool] = None,
    region: Optional[str] = None,
) -> Any:
    """
    List all scouts.
    """
    query = select(Scout)
    
    if is_active is not None:
        query = query.where(Scout.is_active == is_active)
    
    if region:
        query = query.where(Scout.region == region)
    
    query = query.order_by(Scout.last_name)
    
    result = await db.execute(query)
    scouts = result.scalars().all()
    
    return [ScoutResponse.model_validate(s) for s in scouts]


# =============================================================================
# GET SCOUT
# =============================================================================

@router.get("/{scout_id}", response_model=ScoutResponse)
async def get_scout(
    scout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get scout by ID.
    """
    result = await db.execute(
        select(Scout).where(Scout.id == scout_id)
    )
    scout = result.scalar_one_or_none()
    
    if scout is None:
        raise NotFoundException(resource="Scout", resource_id=scout_id)
    
    return ScoutResponse.model_validate(scout)


# =============================================================================
# CREATE SCOUT
# =============================================================================

@router.post("", response_model=ScoutResponse, status_code=status.HTTP_201_CREATED)
async def create_scout(
    request: ScoutCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """
    Create a new scout.
    
    Required roles: Admin, SuperAdmin
    """
    scout = Scout(
        scout_id=generate_scout_id(),
        **request.model_dump(),
        is_active=True,
        total_evaluations=0,
        total_signings=0,
        created_at=datetime.utcnow(),
    )
    
    db.add(scout)
    await db.commit()
    await db.refresh(scout)
    
    return ScoutResponse.model_validate(scout)


# =============================================================================
# UPDATE SCOUT
# =============================================================================

@router.put("/{scout_id}", response_model=ScoutResponse)
async def update_scout(
    scout_id: int,
    request: ScoutUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """
    Update scout by ID.
    """
    result = await db.execute(
        select(Scout).where(Scout.id == scout_id)
    )
    scout = result.scalar_one_or_none()
    
    if scout is None:
        raise NotFoundException(resource="Scout", resource_id=scout_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scout, field, value)
    
    await db.commit()
    await db.refresh(scout)
    
    return ScoutResponse.model_validate(scout)


# =============================================================================
# DELETE SCOUT
# =============================================================================

@router.delete("/{scout_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scout(
    scout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> None:
    """
    Delete scout by ID.
    
    Required roles: SuperAdmin
    """
    result = await db.execute(
        select(Scout).where(Scout.id == scout_id)
    )
    scout = result.scalar_one_or_none()
    
    if scout is None:
        raise NotFoundException(resource="Scout", resource_id=scout_id)
    
    await db.delete(scout)
    await db.commit()


# =============================================================================
# SCOUT EVALUATIONS
# =============================================================================

@router.get("/{scout_id}/evaluations", response_model=List[EvaluationResponse])
async def get_scout_evaluations(
    scout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
) -> Any:
    """
    Get all evaluations by a scout.
    """
    # Check scout exists
    result = await db.execute(
        select(Scout).where(Scout.id == scout_id)
    )
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="Scout", resource_id=scout_id)
    
    # Get evaluations
    result = await db.execute(
        select(TalentEvaluation)
        .where(TalentEvaluation.scout_id == scout_id)
        .order_by(TalentEvaluation.evaluation_date.desc())
        .limit(limit)
    )
    evaluations = result.scalars().all()
    
    return [EvaluationResponse.model_validate(e) for e in evaluations]


# =============================================================================
# SCOUT STATISTICS
# =============================================================================

@router.get("/{scout_id}/stats")
async def get_scout_stats(
    scout_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get statistics for a scout.
    """
    # Check scout exists
    result = await db.execute(
        select(Scout).where(Scout.id == scout_id)
    )
    scout = result.scalar_one_or_none()
    if scout is None:
        raise NotFoundException(resource="Scout", resource_id=scout_id)
    
    # Count evaluations
    result = await db.execute(
        select(func.count(TalentEvaluation.id))
        .where(TalentEvaluation.scout_id == scout_id)
    )
    total_evaluations = result.scalar()
    
    # Average score given
    result = await db.execute(
        select(func.avg(TalentEvaluation.overall_score))
        .where(TalentEvaluation.scout_id == scout_id)
    )
    avg_score = result.scalar()
    
    # Evaluations by recommendation
    result = await db.execute(
        select(TalentEvaluation.recommendation, func.count(TalentEvaluation.id))
        .where(TalentEvaluation.scout_id == scout_id)
        .group_by(TalentEvaluation.recommendation)
    )
    by_recommendation = {row[0] or "None": row[1] for row in result.all()}
    
    return {
        "scout_id": scout.scout_id,
        "name": f"{scout.first_name} {scout.last_name}",
        "total_evaluations": total_evaluations or 0,
        "total_signings": scout.total_signings,
        "average_score_given": round(avg_score, 2) if avg_score else 0,
        "by_recommendation": by_recommendation,
        "success_rate": round(scout.total_signings / total_evaluations * 100, 2) if total_evaluations else 0,
    }
