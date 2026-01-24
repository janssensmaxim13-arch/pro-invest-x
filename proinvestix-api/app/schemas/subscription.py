# ============================================================================
# ProInvestiX Enterprise API - Subscription Schemas
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# PLAN SCHEMAS
# =============================================================================

class PlanResponse(BaseModel):
    """Subscription plan response."""
    id: int
    plan_id: str
    name: str
    description: Optional[str] = None
    price_monthly: float
    price_yearly: float
    currency: str
    features: Optional[str] = None
    max_talents: Optional[int] = None
    max_transfers: Optional[int] = None
    max_users: Optional[int] = None
    api_access: bool
    priority_support: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# SUBSCRIPTION SCHEMAS
# =============================================================================

class SubscriptionCreate(BaseModel):
    """Create subscription request."""
    plan_id: int
    billing_cycle: str = Field(default="Monthly", description="Monthly, Yearly")
    auto_renew: bool = True


class SubscriptionUpdate(BaseModel):
    """Update subscription."""
    plan_id: Optional[int] = None
    billing_cycle: Optional[str] = None
    auto_renew: Optional[bool] = None


class SubscriptionResponse(BaseModel):
    """Subscription response."""
    id: int
    subscription_id: str
    user_id: int
    plan_id: int
    plan_name: Optional[str] = None
    
    status: str
    billing_cycle: str
    auto_renew: bool
    
    current_period_start: date
    current_period_end: date
    
    amount: float
    currency: str
    
    created_at: datetime
    cancelled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Subscription list."""
    success: bool = True
    data: List[SubscriptionResponse]
    meta: dict


# =============================================================================
# PAYMENT SCHEMAS
# =============================================================================

class PaymentResponse(BaseModel):
    """Payment response."""
    id: int
    payment_id: str
    subscription_id: int
    amount: float
    currency: str
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    status: str
    paid_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# GIFT SCHEMAS
# =============================================================================

class GiftSubscriptionRequest(BaseModel):
    """Gift subscription request."""
    recipient_email: str
    plan_id: int
    months: int = Field(default=1, ge=1, le=12)
    message: Optional[str] = None


class GiftCodeResponse(BaseModel):
    """Gift code response."""
    code: str
    plan_name: str
    months: int
    expires_at: datetime


# =============================================================================
# STATS
# =============================================================================

class SubscriptionStats(BaseModel):
    """Subscription statistics."""
    total_active: int
    total_revenue: float
    by_plan: dict
    by_cycle: dict
    churn_rate: float
    mrr: float  # Monthly Recurring Revenue
