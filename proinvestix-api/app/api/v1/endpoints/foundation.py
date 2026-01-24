# ============================================================================
# ProInvestiX Enterprise API - Foundation Endpoints
# Sadaka Jaaria Foundation Bank
# ============================================================================

from datetime import datetime, timedelta
from typing import Any, Optional
import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import FoundationDonation, FoundationContribution, User
from app.core.dependencies import get_current_user
from app.schemas.foundation import (
    DonationCreate,
    DonationResponse,
    DonationListResponse,
    ContributionResponse,
    FoundationStats,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/foundation", tags=["Foundation Bank"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_donation_id() -> str:
    return f"DON-{uuid.uuid4().hex[:8].upper()}"


def generate_receipt_number() -> str:
    return f"RCP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats", response_model=FoundationStats)
async def get_foundation_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get foundation statistics overview."""
    # Total donations
    result = await db.execute(select(func.sum(FoundationDonation.amount)))
    total_donations = result.scalar() or 0
    
    # Total contributions (auto 0.5%)
    result = await db.execute(select(func.sum(FoundationContribution.amount)))
    total_contributions = result.scalar() or 0
    
    # Counts
    result = await db.execute(select(func.count(FoundationDonation.id)))
    donation_count = result.scalar() or 0
    
    result = await db.execute(select(func.count(FoundationContribution.id)))
    contribution_count = result.scalar() or 0
    
    # By type
    result = await db.execute(
        select(FoundationDonation.donation_type, func.sum(FoundationDonation.amount))
        .group_by(FoundationDonation.donation_type)
    )
    by_type = {row[0] or "OneTime": row[1] for row in result.all()}
    
    # By project
    result = await db.execute(
        select(FoundationDonation.project, func.sum(FoundationDonation.amount))
        .group_by(FoundationDonation.project)
    )
    by_project = {row[0] or "General": row[1] for row in result.all()}
    
    # Monthly growth (last 6 months)
    monthly = []
    for i in range(5, -1, -1):
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=i*30)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        
        result = await db.execute(
            select(func.sum(FoundationDonation.amount))
            .where(FoundationDonation.created_at >= month_start)
            .where(FoundationDonation.created_at < month_end)
        )
        donations = result.scalar() or 0
        
        result = await db.execute(
            select(func.sum(FoundationContribution.amount))
            .where(FoundationContribution.created_at >= month_start)
            .where(FoundationContribution.created_at < month_end)
        )
        contributions = result.scalar() or 0
        
        monthly.append({
            "month": month_start.strftime("%b %Y"),
            "donations": donations,
            "contributions": contributions,
            "total": donations + contributions,
        })
    
    # Top donors (non-anonymous)
    result = await db.execute(
        select(FoundationDonation.donor_name, func.sum(FoundationDonation.amount))
        .where(FoundationDonation.is_anonymous == False)
        .where(FoundationDonation.donor_name != None)
        .group_by(FoundationDonation.donor_name)
        .order_by(func.sum(FoundationDonation.amount).desc())
        .limit(10)
    )
    top_donors = [{"name": row[0], "total": row[1]} for row in result.all()]
    
    return FoundationStats(
        total_donations=total_donations,
        total_contributions=total_contributions,
        total_combined=total_donations + total_contributions,
        donation_count=donation_count,
        contribution_count=contribution_count,
        by_type=by_type,
        by_project=by_project,
        monthly_growth=monthly,
        top_donors=top_donors,
    )


# =============================================================================
# LIST DONATIONS
# =============================================================================

@router.get("/donations", response_model=DonationListResponse)
async def list_donations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    donation_type: Optional[str] = None,
    project: Optional[str] = None,
) -> Any:
    """List all donations."""
    query = select(FoundationDonation)
    
    if donation_type:
        query = query.where(FoundationDonation.donation_type == donation_type)
    if project:
        query = query.where(FoundationDonation.project == project)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(FoundationDonation.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    donations = result.scalars().all()
    
    # Hide donor info for anonymous donations
    response_data = []
    for d in donations:
        donation = DonationResponse.model_validate(d)
        if d.is_anonymous:
            donation.donor_name = "Anonymous"
            donation.donor_email = None
        response_data.append(donation)
    
    return DonationListResponse(
        success=True,
        data=response_data,
        meta={"total": total, "page": page, "per_page": per_page}
    )


# =============================================================================
# CREATE DONATION
# =============================================================================

@router.post("/donations", response_model=DonationResponse, status_code=status.HTTP_201_CREATED)
async def create_donation(
    request: DonationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Make a donation to the foundation."""
    donation = FoundationDonation(
        donation_id=generate_donation_id(),
        donor_id=current_user.id,
        donor_name=request.donor_name or f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username,
        donor_email=request.donor_email or current_user.email,
        amount=request.amount,
        currency=request.currency,
        donation_type=request.donation_type,
        project=request.project,
        is_anonymous=request.is_anonymous,
        is_recurring=request.is_recurring,
        receipt_sent=False,
        status="Completed",
        created_at=datetime.utcnow(),
    )
    
    # Generate receipt
    donation.receipt_number = generate_receipt_number()
    donation.receipt_sent = True
    
    db.add(donation)
    await db.commit()
    await db.refresh(donation)
    
    return DonationResponse.model_validate(donation)


# =============================================================================
# GET DONATION
# =============================================================================

@router.get("/donations/{donation_id}", response_model=DonationResponse)
async def get_donation(
    donation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get donation by ID."""
    result = await db.execute(
        select(FoundationDonation).where(FoundationDonation.id == donation_id)
    )
    donation = result.scalar_one_or_none()
    
    if donation is None:
        raise NotFoundException(resource="Donation", resource_id=donation_id)
    
    return DonationResponse.model_validate(donation)


# =============================================================================
# LIST CONTRIBUTIONS
# =============================================================================

@router.get("/contributions")
async def list_contributions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    source_type: Optional[str] = None,
) -> Any:
    """List auto-generated contributions (0.5% from transfers/tickets)."""
    query = select(FoundationContribution)
    
    if source_type:
        query = query.where(FoundationContribution.source_type == source_type)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(FoundationContribution.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    contributions = result.scalars().all()
    
    return {
        "success": True,
        "data": [ContributionResponse.model_validate(c) for c in contributions],
        "meta": {"total": total, "page": page, "per_page": per_page}
    }


# =============================================================================
# PROJECTS
# =============================================================================

@router.get("/projects")
async def get_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get list of foundation projects."""
    result = await db.execute(
        select(
            FoundationDonation.project,
            func.sum(FoundationDonation.amount),
            func.count(FoundationDonation.id)
        )
        .where(FoundationDonation.project != None)
        .group_by(FoundationDonation.project)
        .order_by(func.sum(FoundationDonation.amount).desc())
    )
    
    projects = [
        {
            "name": row[0],
            "total_raised": row[1],
            "donor_count": row[2],
        }
        for row in result.all()
    ]
    
    return {
        "success": True,
        "data": projects
    }


# =============================================================================
# MY DONATIONS
# =============================================================================

@router.get("/my-donations")
async def get_my_donations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's donations."""
    result = await db.execute(
        select(FoundationDonation)
        .where(FoundationDonation.donor_id == current_user.id)
        .order_by(FoundationDonation.created_at.desc())
    )
    donations = result.scalars().all()
    
    # Total donated
    total = sum(d.amount for d in donations)
    
    return {
        "success": True,
        "data": [DonationResponse.model_validate(d) for d in donations],
        "total_donated": total,
        "donation_count": len(donations)
    }
