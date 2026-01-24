# ============================================================================
# ProInvestiX Enterprise API - Talents Endpoints
# NTSP - National Talent Scouting Platform
# ============================================================================

from datetime import datetime, date
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from app.db.database import get_db
from app.db.models import Talent, TalentEvaluation, Scout, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.talent import (
    TalentCreate,
    TalentUpdate,
    TalentResponse,
    TalentListResponse,
    TalentDetailResponse,
    EvaluationCreate,
    EvaluationResponse,
    TalentStats,
)
from app.core.exceptions import NotFoundException, AlreadyExistsException

router = APIRouter(prefix="/talents", tags=["NTSP - Talents"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_talent_id() -> str:
    """Generate unique talent ID."""
    return f"NTSP-{uuid.uuid4().hex[:8].upper()}"


def generate_evaluation_id() -> str:
    """Generate unique evaluation ID."""
    return f"EVAL-{uuid.uuid4().hex[:8].upper()}"


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))


def calculate_overall_scores(evaluation: dict) -> dict:
    """Calculate overall scores from individual scores."""
    technical_scores = [
        evaluation.get('score_ball_control'),
        evaluation.get('score_passing'),
        evaluation.get('score_dribbling'),
        evaluation.get('score_shooting'),
        evaluation.get('score_heading'),
        evaluation.get('score_first_touch'),
    ]
    physical_scores = [
        evaluation.get('score_speed'),
        evaluation.get('score_acceleration'),
        evaluation.get('score_stamina'),
        evaluation.get('score_strength'),
        evaluation.get('score_jumping'),
        evaluation.get('score_agility'),
    ]
    mental_scores = [
        evaluation.get('score_positioning'),
        evaluation.get('score_vision'),
        evaluation.get('score_composure'),
        evaluation.get('score_leadership'),
        evaluation.get('score_work_rate'),
        evaluation.get('score_decision_making'),
    ]
    
    def avg(scores):
        valid = [s for s in scores if s is not None]
        return sum(valid) / len(valid) if valid else None
    
    overall_technical = avg(technical_scores)
    overall_physical = avg(physical_scores)
    overall_mental = avg(mental_scores)
    
    all_scores = [overall_technical, overall_physical, overall_mental]
    valid_overall = [s for s in all_scores if s is not None]
    overall_score = sum(valid_overall) / len(valid_overall) if valid_overall else None
    
    return {
        'overall_technical': overall_technical,
        'overall_physical': overall_physical,
        'overall_mental': overall_mental,
        'overall_score': overall_score,
    }


# =============================================================================
# LIST TALENTS
# =============================================================================

@router.get("", response_model=TalentListResponse)
async def list_talents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # Pagination
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    # Filters
    search: Optional[str] = None,
    nationality: Optional[str] = None,
    position: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    is_diaspora: Optional[bool] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    # Sorting
    sort_by: str = Query("created_at", regex="^(created_at|last_name|overall_score|potential_score)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
) -> Any:
    """
    List all talents with filtering and pagination.
    
    - **search**: Search in name, club
    - **nationality**: Filter by nationality
    - **position**: Filter by position (GK, CB, LB, RB, CDM, CM, CAM, LW, RW, ST)
    - **status**: Filter by status (Prospect, Monitored, Priority, Signed, Inactive)
    - **is_diaspora**: Filter diaspora talents
    """
    # Build query
    query = select(Talent)
    
    # Apply filters
    conditions = []
    
    if search:
        search_term = f"%{search}%"
        conditions.append(
            or_(
                Talent.first_name.ilike(search_term),
                Talent.last_name.ilike(search_term),
                Talent.current_club.ilike(search_term),
            )
        )
    
    if nationality:
        conditions.append(Talent.nationality == nationality)
    
    if position:
        conditions.append(
            or_(
                Talent.primary_position == position,
                Talent.secondary_position == position,
            )
        )
    
    if status:
        conditions.append(Talent.status == status)
    
    if priority:
        conditions.append(Talent.priority_level == priority)
    
    if is_diaspora is not None:
        conditions.append(Talent.is_diaspora == is_diaspora)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply sorting
    sort_column = getattr(Talent, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    # Execute
    result = await db.execute(query)
    talents = result.scalars().all()
    
    return TalentListResponse(
        success=True,
        data=[TalentResponse.model_validate(t) for t in talents],
        meta={
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )


# =============================================================================
# GET TALENT
# =============================================================================

@router.get("/{talent_id}", response_model=TalentDetailResponse)
async def get_talent(
    talent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get talent by ID.
    """
    result = await db.execute(
        select(Talent).where(Talent.id == talent_id)
    )
    talent = result.scalar_one_or_none()
    
    if talent is None:
        raise NotFoundException(resource="Talent", resource_id=talent_id)
    
    return TalentDetailResponse(
        success=True,
        data=TalentResponse.model_validate(talent),
    )


# =============================================================================
# CREATE TALENT
# =============================================================================

@router.post("", response_model=TalentDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_talent(
    request: TalentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new talent.
    
    Required roles: Scout, Admin, SuperAdmin
    """
    # Create talent
    talent = Talent(
        talent_id=generate_talent_id(),
        **request.model_dump(),
        status="Prospect",
        overall_score=0,
        potential_score=0,
        market_value=0,
        evaluation_count=0,
        created_at=datetime.utcnow(),
        created_by=current_user.username,
    )
    
    db.add(talent)
    await db.commit()
    await db.refresh(talent)
    
    return TalentDetailResponse(
        success=True,
        data=TalentResponse.model_validate(talent),
    )


# =============================================================================
# UPDATE TALENT
# =============================================================================

@router.put("/{talent_id}", response_model=TalentDetailResponse)
async def update_talent(
    talent_id: int,
    request: TalentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update talent by ID.
    """
    result = await db.execute(
        select(Talent).where(Talent.id == talent_id)
    )
    talent = result.scalar_one_or_none()
    
    if talent is None:
        raise NotFoundException(resource="Talent", resource_id=talent_id)
    
    # Update fields
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(talent, field, value)
    
    talent.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(talent)
    
    return TalentDetailResponse(
        success=True,
        data=TalentResponse.model_validate(talent),
    )


# =============================================================================
# DELETE TALENT
# =============================================================================

@router.delete("/{talent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_talent(
    talent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> None:
    """
    Delete talent by ID.
    
    Required roles: Admin, SuperAdmin
    """
    result = await db.execute(
        select(Talent).where(Talent.id == talent_id)
    )
    talent = result.scalar_one_or_none()
    
    if talent is None:
        raise NotFoundException(resource="Talent", resource_id=talent_id)
    
    await db.delete(talent)
    await db.commit()


# =============================================================================
# TALENT EVALUATIONS
# =============================================================================

@router.get("/{talent_id}/evaluations", response_model=List[EvaluationResponse])
async def get_talent_evaluations(
    talent_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get all evaluations for a talent.
    """
    # Check talent exists
    result = await db.execute(
        select(Talent).where(Talent.id == talent_id)
    )
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="Talent", resource_id=talent_id)
    
    # Get evaluations
    result = await db.execute(
        select(TalentEvaluation)
        .where(TalentEvaluation.talent_id == talent_id)
        .order_by(TalentEvaluation.evaluation_date.desc())
    )
    evaluations = result.scalars().all()
    
    return [EvaluationResponse.model_validate(e) for e in evaluations]


@router.post("/{talent_id}/evaluations", response_model=EvaluationResponse, status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    talent_id: int,
    request: EvaluationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create evaluation for a talent.
    """
    # Check talent exists
    result = await db.execute(
        select(Talent).where(Talent.id == talent_id)
    )
    talent = result.scalar_one_or_none()
    if talent is None:
        raise NotFoundException(resource="Talent", resource_id=talent_id)
    
    # Calculate overall scores
    eval_data = request.model_dump()
    scores = calculate_overall_scores(eval_data)
    
    # Create evaluation
    evaluation = TalentEvaluation(
        evaluation_id=generate_evaluation_id(),
        talent_id=talent_id,
        **eval_data,
        **scores,
        created_at=datetime.utcnow(),
    )
    
    db.add(evaluation)
    
    # Update talent scores and count
    talent.evaluation_count += 1
    talent.last_evaluation = datetime.utcnow()
    
    if scores['overall_score']:
        # Update talent overall score (average of all evaluations)
        result = await db.execute(
            select(func.avg(TalentEvaluation.overall_score))
            .where(TalentEvaluation.talent_id == talent_id)
        )
        avg_score = result.scalar()
        if avg_score:
            talent.overall_score = avg_score
    
    await db.commit()
    await db.refresh(evaluation)
    
    return EvaluationResponse.model_validate(evaluation)


# =============================================================================
# TALENT STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=TalentStats)
async def get_talent_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get talent statistics overview.
    """
    # Total talents
    result = await db.execute(select(func.count(Talent.id)))
    total = result.scalar()
    
    # By status
    result = await db.execute(
        select(Talent.status, func.count(Talent.id))
        .group_by(Talent.status)
    )
    by_status = {row[0]: row[1] for row in result.all()}
    
    # By position
    result = await db.execute(
        select(Talent.primary_position, func.count(Talent.id))
        .group_by(Talent.primary_position)
    )
    by_position = {row[0]: row[1] for row in result.all()}
    
    # By nationality (top 10)
    result = await db.execute(
        select(Talent.nationality, func.count(Talent.id))
        .group_by(Talent.nationality)
        .order_by(func.count(Talent.id).desc())
        .limit(10)
    )
    by_nationality = {row[0]: row[1] for row in result.all()}
    
    # Diaspora count
    result = await db.execute(
        select(func.count(Talent.id))
        .where(Talent.is_diaspora == True)
    )
    diaspora_count = result.scalar()
    
    # Average scores
    result = await db.execute(
        select(
            func.avg(Talent.overall_score),
            func.avg(Talent.potential_score),
        )
    )
    avg_scores = result.one()
    
    return TalentStats(
        total_talents=total or 0,
        by_status=by_status,
        by_position=by_position,
        by_nationality=by_nationality,
        diaspora_count=diaspora_count or 0,
        average_score=avg_scores[0] or 0,
        average_potential=avg_scores[1] or 0,
    )


# =============================================================================
# SEARCH & FILTERS
# =============================================================================

@router.get("/filters/options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get available filter options.
    """
    # Nationalities
    result = await db.execute(
        select(Talent.nationality)
        .distinct()
        .where(Talent.nationality != None)
        .order_by(Talent.nationality)
    )
    nationalities = [row[0] for row in result.all()]
    
    # Clubs
    result = await db.execute(
        select(Talent.current_club)
        .distinct()
        .where(Talent.current_club != None)
        .order_by(Talent.current_club)
    )
    clubs = [row[0] for row in result.all()]
    
    return {
        "positions": ["GK", "CB", "LB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"],
        "statuses": ["Prospect", "Monitored", "Priority", "Signed", "Inactive"],
        "priorities": ["Low", "Normal", "High", "Critical"],
        "nationalities": nationalities,
        "clubs": clubs,
        "feet": ["Right", "Left", "Both"],
    }
