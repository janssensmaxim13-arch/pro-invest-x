# ============================================================================
# ProInvestiX Enterprise API - Event & Ticket Schemas
# TicketChain - Blockchain Ticketing
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# EVENT SCHEMAS
# =============================================================================

class EventBase(BaseModel):
    """Base event fields."""
    name: str = Field(..., min_length=1, max_length=200)
    event_type: Optional[str] = Field(None, description="Match, Concert, Festival, Conference")
    
    venue: str = Field(..., max_length=200)
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    
    date: datetime
    doors_open: Optional[datetime] = None
    
    capacity: int = Field(..., ge=1)
    
    price_min: Optional[float] = Field(None, ge=0)
    price_max: Optional[float] = Field(None, ge=0)
    
    mobility_enabled: bool = False
    diaspora_package: bool = False


class EventCreate(EventBase):
    """Create event request."""
    pass


class EventUpdate(BaseModel):
    """Update event request."""
    name: Optional[str] = None
    event_type: Optional[str] = None
    venue: Optional[str] = None
    city: Optional[str] = None
    date: Optional[datetime] = None
    capacity: Optional[int] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    status: Optional[str] = None
    mobility_enabled: Optional[bool] = None
    diaspora_package: Optional[bool] = None


class EventResponse(EventBase):
    """Event response."""
    id: int
    event_id: str
    tickets_sold: int
    tickets_available: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class EventListResponse(BaseModel):
    """Paginated event list."""
    success: bool = True
    data: List[EventResponse]
    meta: dict


class EventDetailResponse(BaseModel):
    """Single event response."""
    success: bool = True
    data: EventResponse


# =============================================================================
# TICKET SCHEMAS
# =============================================================================

class TicketMintRequest(BaseModel):
    """Mint ticket request."""
    owner_name: str = Field(..., min_length=1, max_length=100)
    owner_id: Optional[int] = None
    
    seat_section: Optional[str] = None
    seat_row: Optional[str] = None
    seat_number: Optional[str] = None
    
    category: str = Field(default="Standard", description="VIP, Standard, Economy")
    price: float = Field(..., ge=0)


class TicketTransferRequest(BaseModel):
    """Transfer ticket to new owner."""
    new_owner_name: str = Field(..., min_length=1, max_length=100)
    new_owner_id: Optional[int] = None


class TicketResponse(BaseModel):
    """Ticket response."""
    id: int
    ticket_hash: str
    event_id: int
    
    owner_id: Optional[int] = None
    owner_name: Optional[str] = None
    
    seat_section: Optional[str] = None
    seat_row: Optional[str] = None
    seat_number: Optional[str] = None
    seat_info: Optional[str] = None
    
    category: Optional[str] = None
    price: float
    
    minted_at: datetime
    block_number: Optional[int] = None
    transaction_hash: Optional[str] = None
    
    status: str
    used_at: Optional[datetime] = None
    
    qr_code: Optional[str] = None
    
    class Config:
        from_attributes = True


class TicketVerifyResponse(BaseModel):
    """Ticket verification response."""
    valid: bool
    ticket: Optional[TicketResponse] = None
    event_name: Optional[str] = None
    message: str


class TicketListResponse(BaseModel):
    """Ticket list response."""
    success: bool = True
    data: List[TicketResponse]
    meta: dict


# =============================================================================
# LOYALTY SCHEMAS
# =============================================================================

class LoyaltyResponse(BaseModel):
    """Loyalty points response."""
    user_id: int
    points_balance: int
    total_earned: int
    total_spent: int
    tier: str
    tickets_purchased: int
    last_activity: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoyaltyRedeemRequest(BaseModel):
    """Redeem loyalty points."""
    points: int = Field(..., ge=1)
    reward_type: str = Field(..., description="Discount, Upgrade, Merchandise")


# =============================================================================
# STATS
# =============================================================================

class TicketChainStats(BaseModel):
    """TicketChain statistics."""
    total_events: int
    total_tickets: int
    tickets_used: int
    total_revenue: float
    by_status: dict
    by_category: dict
    upcoming_events: int
