# ============================================================================
# ProInvestiX Enterprise API - Transfer Schemas
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class TransferBase(BaseModel):
    """Base transfer fields."""
    player_name: str = Field(..., min_length=1, max_length=100)
    
    from_club: str = Field(..., max_length=100)
    from_country: Optional[str] = Field(None, max_length=50)
    to_club: str = Field(..., max_length=100)
    to_country: Optional[str] = Field(None, max_length=50)
    
    transfer_type: str = Field(..., description="Permanent, Loan, Free, Youth")
    transfer_date: date
    
    # Financial
    transfer_fee: float = Field(default=0, ge=0)
    add_ons: float = Field(default=0, ge=0)
    sell_on_pct: float = Field(default=0, ge=0, le=100)
    agent_fee: float = Field(default=0, ge=0)
    
    # Contract
    contract_length_years: Optional[int] = Field(None, ge=1, le=10)
    salary_annual: Optional[float] = Field(None, ge=0)
    release_clause: Optional[float] = Field(None, ge=0)
    
    notes: Optional[str] = None


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class TransferCreate(TransferBase):
    """Create transfer request."""
    talent_id: Optional[int] = None


class TransferUpdate(BaseModel):
    """Update transfer request."""
    player_name: Optional[str] = None
    from_club: Optional[str] = None
    to_club: Optional[str] = None
    transfer_type: Optional[str] = None
    transfer_date: Optional[date] = None
    transfer_fee: Optional[float] = None
    add_ons: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class CompensationCalculateRequest(BaseModel):
    """Request for compensation calculation."""
    transfer_fee: float = Field(..., ge=0)
    player_age: int = Field(..., ge=12, le=45)
    training_clubs: List[dict] = Field(
        ...,
        description="List of clubs with years: [{club, country, age_from, age_to}]"
    )


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class TransferResponse(TransferBase):
    """Transfer response."""
    id: int
    transfer_id: str
    talent_id: Optional[int] = None
    
    # Calculated fees
    training_compensation: float
    solidarity_contribution: float
    foundation_contribution: float
    
    # Blockchain
    smart_contract_hash: Optional[str] = None
    blockchain_verified: bool
    
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransferListResponse(BaseModel):
    """Paginated transfer list."""
    success: bool = True
    data: List[TransferResponse]
    meta: dict


class TransferDetailResponse(BaseModel):
    """Single transfer response."""
    success: bool = True
    data: TransferResponse


class CompensationResponse(BaseModel):
    """Compensation calculation response."""
    transfer_fee: float
    training_compensation: float
    solidarity_contribution: float
    foundation_contribution: float
    total_cost: float
    breakdown: List[dict]


class TransferStats(BaseModel):
    """Transfer statistics."""
    total_transfers: int
    total_value: float
    average_fee: float
    by_type: dict
    by_status: dict
    foundation_total: float
    top_clubs_spending: List[dict]
    top_clubs_receiving: List[dict]
