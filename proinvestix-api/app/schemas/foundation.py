# ============================================================================
# ProInvestiX Enterprise API - Foundation Schemas
# Sadaka Jaaria Foundation Bank
# ============================================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# DONATION SCHEMAS
# =============================================================================

class DonationCreate(BaseModel):
    """Create donation request."""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="EUR")
    donation_type: str = Field(default="OneTime", description="OneTime, Monthly, Annual, Sadaka")
    project: Optional[str] = None
    is_anonymous: bool = False
    is_recurring: bool = False
    donor_name: Optional[str] = None
    donor_email: Optional[EmailStr] = None


class DonationResponse(BaseModel):
    """Donation response."""
    id: int
    donation_id: str
    donor_id: Optional[int] = None
    donor_name: Optional[str] = None
    donor_email: Optional[str] = None
    amount: float
    currency: str
    donation_type: Optional[str] = None
    project: Optional[str] = None
    is_anonymous: bool
    is_recurring: bool
    payment_method: Optional[str] = None
    payment_reference: Optional[str] = None
    receipt_sent: bool
    receipt_number: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DonationListResponse(BaseModel):
    """Donation list response."""
    success: bool = True
    data: List[DonationResponse]
    meta: dict


# =============================================================================
# CONTRIBUTION SCHEMAS
# =============================================================================

class ContributionResponse(BaseModel):
    """Auto contribution response (0.5% from transfers/tickets)."""
    id: int
    contribution_id: str
    source_type: str
    source_id: str
    amount: float
    percentage: float
    description: Optional[str] = None
    auto_generated: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# STATS
# =============================================================================

class FoundationStats(BaseModel):
    """Foundation statistics."""
    total_donations: float
    total_contributions: float
    total_combined: float
    donation_count: int
    contribution_count: int
    by_type: dict
    by_project: dict
    monthly_growth: List[dict]
    top_donors: List[dict]
