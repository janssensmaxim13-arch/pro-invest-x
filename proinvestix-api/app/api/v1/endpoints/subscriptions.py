# ============================================================================
# ProInvestiX Enterprise API - Subscriptions Endpoints
# ============================================================================

from datetime import datetime, date, timedelta
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import SubscriptionPlan, Subscription, SubscriptionPayment, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.subscription import (
    PlanResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse, SubscriptionListResponse,
    PaymentResponse,
    GiftSubscriptionRequest, GiftCodeResponse,
    SubscriptionStats,
)
from app.core.exceptions import NotFoundException, BusinessLogicException

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_subscription_id() -> str:
    return f"SUB-{uuid.uuid4().hex[:8].upper()}"

def generate_payment_id() -> str:
    return f"PAY-{uuid.uuid4().hex[:8].upper()}"

def generate_gift_code() -> str:
    return f"GIFT-{uuid.uuid4().hex[:12].upper()}"


# =============================================================================
# PLANS
# =============================================================================

@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    db: AsyncSession = Depends(get_db),
    include_inactive: bool = False,
) -> Any:
    """List available subscription plans. Public endpoint."""
    query = select(SubscriptionPlan)
    if not include_inactive:
        query = query.where(SubscriptionPlan.is_active == True)
    
    query = query.order_by(SubscriptionPlan.price_monthly)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return [PlanResponse.model_validate(p) for p in plans]


@router.get("/plans/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: int,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Get plan by ID."""
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id))
    plan = result.scalar_one_or_none()
    
    if plan is None:
        raise NotFoundException(resource="Plan", resource_id=plan_id)
    
    return PlanResponse.model_validate(plan)


# =============================================================================
# USER SUBSCRIPTIONS
# =============================================================================

@router.get("", response_model=SubscriptionListResponse)
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
) -> Any:
    """List all subscriptions (Admin only)."""
    query = select(Subscription)
    
    if status:
        query = query.where(Subscription.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(Subscription.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    subs = result.scalars().all()
    
    return SubscriptionListResponse(
        success=True,
        data=[SubscriptionResponse.model_validate(s) for s in subs],
        meta={"total": total, "page": page, "per_page": per_page}
    )


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's subscription."""
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "Active")
    )
    sub = result.scalar_one_or_none()
    
    if sub is None:
        raise NotFoundException(resource="Subscription", resource_id="current user")
    
    # Get plan name
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == sub.plan_id))
    plan = result.scalar_one_or_none()
    
    response = SubscriptionResponse.model_validate(sub)
    response.plan_name = plan.name if plan else None
    
    return response


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get subscription by ID."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    sub = result.scalar_one_or_none()
    
    if sub is None:
        raise NotFoundException(resource="Subscription", resource_id=subscription_id)
    
    # Check access
    if sub.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return SubscriptionResponse.model_validate(sub)


@router.post("", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    request: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Subscribe to a plan."""
    # Check for existing active subscription
    result = await db.execute(
        select(Subscription)
        .where(Subscription.user_id == current_user.id)
        .where(Subscription.status == "Active")
    )
    if result.scalar_one_or_none():
        raise BusinessLogicException(
            detail="User already has an active subscription",
            error_code="SUBSCRIPTION_EXISTS"
        )
    
    # Get plan
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == request.plan_id))
    plan = result.scalar_one_or_none()
    
    if plan is None or not plan.is_active:
        raise NotFoundException(resource="Plan", resource_id=request.plan_id)
    
    # Calculate period
    today = date.today()
    if request.billing_cycle == "Yearly":
        period_end = today + timedelta(days=365)
        amount = plan.price_yearly
    else:
        period_end = today + timedelta(days=30)
        amount = plan.price_monthly
    
    subscription = Subscription(
        subscription_id=generate_subscription_id(),
        user_id=current_user.id,
        plan_id=plan.id,
        status="Active",
        billing_cycle=request.billing_cycle,
        auto_renew=request.auto_renew,
        current_period_start=today,
        current_period_end=period_end,
        amount=amount,
        currency=plan.currency,
        created_at=datetime.utcnow(),
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # Create initial payment record
    payment = SubscriptionPayment(
        payment_id=generate_payment_id(),
        subscription_id=subscription.id,
        amount=amount,
        currency=plan.currency,
        status="Completed",
        paid_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
    )
    db.add(payment)
    await db.commit()
    
    response = SubscriptionResponse.model_validate(subscription)
    response.plan_name = plan.name
    
    return response


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    request: SubscriptionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update subscription."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    sub = result.scalar_one_or_none()
    
    if sub is None:
        raise NotFoundException(resource="Subscription", resource_id=subscription_id)
    
    if sub.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(sub, field, value)
    
    await db.commit()
    await db.refresh(sub)
    
    return SubscriptionResponse.model_validate(sub)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_subscription(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Cancel subscription."""
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    sub = result.scalar_one_or_none()
    
    if sub is None:
        raise NotFoundException(resource="Subscription", resource_id=subscription_id)
    
    if sub.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sub.status = "Cancelled"
    sub.cancelled_at = datetime.utcnow()
    sub.auto_renew = False
    
    await db.commit()


# =============================================================================
# PAYMENTS
# =============================================================================

@router.get("/{subscription_id}/payments", response_model=List[PaymentResponse])
async def get_payments(
    subscription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get subscription payments."""
    # Verify access
    result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
    sub = result.scalar_one_or_none()
    
    if sub is None:
        raise NotFoundException(resource="Subscription", resource_id=subscription_id)
    
    if sub.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    result = await db.execute(
        select(SubscriptionPayment)
        .where(SubscriptionPayment.subscription_id == subscription_id)
        .order_by(SubscriptionPayment.created_at.desc())
    )
    payments = result.scalars().all()
    
    return [PaymentResponse.model_validate(p) for p in payments]


# =============================================================================
# GIFT SUBSCRIPTIONS
# =============================================================================

@router.post("/gift", response_model=GiftCodeResponse)
async def create_gift_subscription(
    request: GiftSubscriptionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create gift subscription code."""
    # Get plan
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == request.plan_id))
    plan = result.scalar_one_or_none()
    
    if plan is None:
        raise NotFoundException(resource="Plan", resource_id=request.plan_id)
    
    code = generate_gift_code()
    expires_at = datetime.utcnow() + timedelta(days=90)  # Gift codes expire in 90 days
    
    # In a real implementation, we'd store this in a gift_codes table
    # For now, return the generated code
    
    return GiftCodeResponse(
        code=code,
        plan_name=plan.name,
        months=request.months,
        expires_at=expires_at,
    )


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=SubscriptionStats)
async def get_subscription_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get subscription statistics."""
    # Total active
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.status == "Active")
    )
    total_active = result.scalar() or 0
    
    # Total revenue
    result = await db.execute(
        select(func.sum(SubscriptionPayment.amount))
        .where(SubscriptionPayment.status == "Completed")
    )
    total_revenue = result.scalar() or 0
    
    # By plan
    result = await db.execute(
        select(Subscription.plan_id, func.count(Subscription.id))
        .where(Subscription.status == "Active")
        .group_by(Subscription.plan_id)
    )
    by_plan = {f"Plan {row[0]}": row[1] for row in result.all()}
    
    # By cycle
    result = await db.execute(
        select(Subscription.billing_cycle, func.count(Subscription.id))
        .where(Subscription.status == "Active")
        .group_by(Subscription.billing_cycle)
    )
    by_cycle = {row[0]: row[1] for row in result.all()}
    
    # MRR (Monthly Recurring Revenue)
    result = await db.execute(
        select(func.sum(Subscription.amount))
        .where(Subscription.status == "Active")
        .where(Subscription.billing_cycle == "Monthly")
    )
    monthly = result.scalar() or 0
    
    result = await db.execute(
        select(func.sum(Subscription.amount))
        .where(Subscription.status == "Active")
        .where(Subscription.billing_cycle == "Yearly")
    )
    yearly = result.scalar() or 0
    
    mrr = monthly + (yearly / 12)
    
    return SubscriptionStats(
        total_active=total_active,
        total_revenue=total_revenue,
        by_plan=by_plan,
        by_cycle=by_cycle,
        churn_rate=0,  # Would calculate from historical data
        mrr=round(mrr, 2),
    )
