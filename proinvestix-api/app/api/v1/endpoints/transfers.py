# ============================================================================
# ProInvestiX Enterprise API - Transfers Endpoints
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.database import get_db
from app.db.models import Transfer, TransferCompensation, Talent, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.transfer import (
    TransferCreate,
    TransferUpdate,
    TransferResponse,
    TransferListResponse,
    TransferDetailResponse,
    CompensationCalculateRequest,
    CompensationResponse,
    TransferStats,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/transfers", tags=["Transfers"])


# =============================================================================
# CONSTANTS
# =============================================================================

# FIFA Training Compensation rates per category
TRAINING_RATES = {
    1: 90000,   # Category 1 clubs
    2: 60000,   # Category 2 clubs
    3: 30000,   # Category 3 clubs
    4: 10000,   # Category 4 clubs
}

# Solidarity contribution percentage
SOLIDARITY_PCT = 5.0

# Foundation contribution (Masterplan 0.5%)
FOUNDATION_PCT = 0.5


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_transfer_id() -> str:
    """Generate unique transfer ID."""
    return f"TRF-{uuid.uuid4().hex[:8].upper()}"


def generate_smart_contract_hash(transfer_data: dict) -> str:
    """Generate blockchain-style hash for transfer."""
    data_string = f"{transfer_data.get('transfer_id')}-{transfer_data.get('from_club')}-{transfer_data.get('to_club')}-{transfer_data.get('transfer_fee')}-{datetime.utcnow().isoformat()}"
    return "0x" + hashlib.sha256(data_string.encode()).hexdigest()


def calculate_training_compensation(
    transfer_fee: float,
    training_clubs: List[dict],
) -> tuple[float, List[dict]]:
    """
    Calculate FIFA training compensation.
    
    Returns: (total_compensation, breakdown)
    """
    total = 0
    breakdown = []
    
    for club in training_clubs:
        years = club.get('age_to', 0) - club.get('age_from', 0)
        category = club.get('category', 4)
        rate = TRAINING_RATES.get(category, TRAINING_RATES[4])
        
        compensation = years * rate
        total += compensation
        
        breakdown.append({
            'club': club.get('club'),
            'country': club.get('country'),
            'years': years,
            'age_from': club.get('age_from'),
            'age_to': club.get('age_to'),
            'category': category,
            'rate': rate,
            'compensation': compensation,
        })
    
    return total, breakdown


def calculate_solidarity_contribution(transfer_fee: float) -> float:
    """Calculate 5% solidarity contribution."""
    return transfer_fee * (SOLIDARITY_PCT / 100)


def calculate_foundation_contribution(transfer_fee: float) -> float:
    """Calculate 0.5% foundation contribution (Masterplan)."""
    return transfer_fee * (FOUNDATION_PCT / 100)


# =============================================================================
# LIST TRANSFERS
# =============================================================================

@router.get("", response_model=TransferListResponse)
async def list_transfers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # Pagination
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    # Filters
    transfer_type: Optional[str] = None,
    status: Optional[str] = None,
    from_club: Optional[str] = None,
    to_club: Optional[str] = None,
    min_fee: Optional[float] = None,
    max_fee: Optional[float] = None,
    # Sorting
    sort_by: str = Query("transfer_date", regex="^(transfer_date|transfer_fee|created_at)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
) -> Any:
    """
    List all transfers with filtering and pagination.
    """
    query = select(Transfer)
    conditions = []
    
    if transfer_type:
        conditions.append(Transfer.transfer_type == transfer_type)
    if status:
        conditions.append(Transfer.status == status)
    if from_club:
        conditions.append(Transfer.from_club.ilike(f"%{from_club}%"))
    if to_club:
        conditions.append(Transfer.to_club.ilike(f"%{to_club}%"))
    if min_fee is not None:
        conditions.append(Transfer.transfer_fee >= min_fee)
    if max_fee is not None:
        conditions.append(Transfer.transfer_fee <= max_fee)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Sort
    sort_column = getattr(Transfer, sort_by)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Paginate
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    transfers = result.scalars().all()
    
    return TransferListResponse(
        success=True,
        data=[TransferResponse.model_validate(t) for t in transfers],
        meta={
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )


# =============================================================================
# GET TRANSFER
# =============================================================================

@router.get("/{transfer_id}", response_model=TransferDetailResponse)
async def get_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get transfer by ID.
    """
    result = await db.execute(
        select(Transfer).where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()
    
    if transfer is None:
        raise NotFoundException(resource="Transfer", resource_id=transfer_id)
    
    return TransferDetailResponse(
        success=True,
        data=TransferResponse.model_validate(transfer),
    )


# =============================================================================
# CREATE TRANSFER
# =============================================================================

@router.post("", response_model=TransferDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_transfer(
    request: TransferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Create a new transfer.
    """
    # Calculate contributions
    solidarity = calculate_solidarity_contribution(request.transfer_fee)
    foundation = calculate_foundation_contribution(request.transfer_fee)
    
    transfer_id = generate_transfer_id()
    
    transfer = Transfer(
        transfer_id=transfer_id,
        **request.model_dump(),
        training_compensation=0,  # Calculated separately
        solidarity_contribution=solidarity,
        foundation_contribution=foundation,
        status="Pending",
        created_at=datetime.utcnow(),
    )
    
    # Generate smart contract hash
    transfer.smart_contract_hash = generate_smart_contract_hash({
        'transfer_id': transfer_id,
        'from_club': request.from_club,
        'to_club': request.to_club,
        'transfer_fee': request.transfer_fee,
    })
    transfer.blockchain_verified = True
    
    db.add(transfer)
    await db.commit()
    await db.refresh(transfer)
    
    return TransferDetailResponse(
        success=True,
        data=TransferResponse.model_validate(transfer),
    )


# =============================================================================
# UPDATE TRANSFER
# =============================================================================

@router.put("/{transfer_id}", response_model=TransferDetailResponse)
async def update_transfer(
    transfer_id: int,
    request: TransferUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Update transfer by ID.
    """
    result = await db.execute(
        select(Transfer).where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()
    
    if transfer is None:
        raise NotFoundException(resource="Transfer", resource_id=transfer_id)
    
    update_data = request.model_dump(exclude_unset=True)
    
    # Recalculate if fee changed
    if 'transfer_fee' in update_data:
        new_fee = update_data['transfer_fee']
        transfer.solidarity_contribution = calculate_solidarity_contribution(new_fee)
        transfer.foundation_contribution = calculate_foundation_contribution(new_fee)
    
    for field, value in update_data.items():
        setattr(transfer, field, value)
    
    # Mark as completed if status changed
    if update_data.get('status') == 'Completed':
        transfer.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(transfer)
    
    return TransferDetailResponse(
        success=True,
        data=TransferResponse.model_validate(transfer),
    )


# =============================================================================
# DELETE TRANSFER
# =============================================================================

@router.delete("/{transfer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transfer(
    transfer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> None:
    """
    Cancel/delete transfer.
    """
    result = await db.execute(
        select(Transfer).where(Transfer.id == transfer_id)
    )
    transfer = result.scalar_one_or_none()
    
    if transfer is None:
        raise NotFoundException(resource="Transfer", resource_id=transfer_id)
    
    # Soft delete - mark as cancelled
    transfer.status = "Cancelled"
    await db.commit()


# =============================================================================
# COMPENSATION CALCULATOR
# =============================================================================

@router.post("/calculate", response_model=CompensationResponse)
async def calculate_compensation(
    request: CompensationCalculateRequest,
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Calculate training compensation, solidarity, and foundation contributions.
    
    FIFA Training Compensation is calculated based on:
    - Years of training (age 12-21)
    - Club category (1-4)
    """
    # Training compensation
    training, breakdown = calculate_training_compensation(
        request.transfer_fee,
        request.training_clubs,
    )
    
    # Solidarity (5%)
    solidarity = calculate_solidarity_contribution(request.transfer_fee)
    
    # Foundation (0.5%)
    foundation = calculate_foundation_contribution(request.transfer_fee)
    
    # Total
    total = request.transfer_fee + training
    
    return CompensationResponse(
        transfer_fee=request.transfer_fee,
        training_compensation=training,
        solidarity_contribution=solidarity,
        foundation_contribution=foundation,
        total_cost=total,
        breakdown=breakdown,
    )


# =============================================================================
# TRANSFER STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=TransferStats)
async def get_transfer_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get transfer statistics overview.
    """
    # Total transfers
    result = await db.execute(select(func.count(Transfer.id)))
    total = result.scalar() or 0
    
    # Total value
    result = await db.execute(select(func.sum(Transfer.transfer_fee)))
    total_value = result.scalar() or 0
    
    # Average fee
    result = await db.execute(select(func.avg(Transfer.transfer_fee)))
    avg_fee = result.scalar() or 0
    
    # By type
    result = await db.execute(
        select(Transfer.transfer_type, func.count(Transfer.id))
        .group_by(Transfer.transfer_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}
    
    # By status
    result = await db.execute(
        select(Transfer.status, func.count(Transfer.id))
        .group_by(Transfer.status)
    )
    by_status = {row[0]: row[1] for row in result.all()}
    
    # Foundation total
    result = await db.execute(select(func.sum(Transfer.foundation_contribution)))
    foundation_total = result.scalar() or 0
    
    # Top spending clubs
    result = await db.execute(
        select(Transfer.to_club, func.sum(Transfer.transfer_fee))
        .group_by(Transfer.to_club)
        .order_by(func.sum(Transfer.transfer_fee).desc())
        .limit(5)
    )
    top_spending = [{"club": row[0], "total": row[1]} for row in result.all()]
    
    # Top receiving clubs
    result = await db.execute(
        select(Transfer.from_club, func.sum(Transfer.transfer_fee))
        .group_by(Transfer.from_club)
        .order_by(func.sum(Transfer.transfer_fee).desc())
        .limit(5)
    )
    top_receiving = [{"club": row[0], "total": row[1]} for row in result.all()]
    
    return TransferStats(
        total_transfers=total,
        total_value=total_value,
        average_fee=round(avg_fee, 2),
        by_type=by_type,
        by_status=by_status,
        foundation_total=foundation_total,
        top_clubs_spending=top_spending,
        top_clubs_receiving=top_receiving,
    )
