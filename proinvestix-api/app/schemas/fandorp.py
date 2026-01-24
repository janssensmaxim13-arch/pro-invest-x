# ============================================================================
# ProInvestiX Enterprise API - FanDorp Schemas
# WK 2030 Fan Villages
# ============================================================================

from datetime import date, datetime, time
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# FANDORP SCHEMAS
# =============================================================================

class FanDorpBase(BaseModel):
    """Base FanDorp fields."""
    name: str = Field(..., min_length=1, max_length=100)
    
    city: str = Field(..., max_length=100)
    country: str = Field(default="Morocco", max_length=50)
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    
    capacity: int = Field(..., ge=100)
    
    opening_date: Optional[date] = None
    closing_date: Optional[date] = None
    
    has_screen: bool = True
    has_food: bool = True
    has_merchandise: bool = True
    has_activities: bool = True
    is_family_friendly: bool = True
    accessibility_enabled: bool = True
    
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class FanDorpCreate(FanDorpBase):
    """Create FanDorp request."""
    pass


class FanDorpUpdate(BaseModel):
    """Update FanDorp."""
    name: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None
    opening_date: Optional[date] = None
    closing_date: Optional[date] = None


class FanDorpResponse(FanDorpBase):
    """FanDorp response."""
    id: int
    fandorp_id: str
    status: str
    total_volunteers: int
    total_visitors: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FanDorpListResponse(BaseModel):
    """FanDorp list."""
    success: bool = True
    data: List[FanDorpResponse]
    meta: dict


# =============================================================================
# VOLUNTEER SCHEMAS
# =============================================================================

class VolunteerCreate(BaseModel):
    """Register volunteer."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    
    date_of_birth: date
    nationality: Optional[str] = None
    languages: Optional[str] = None
    
    role_preference: Optional[str] = Field(None, description="Guide, Security, Food, Activities, Medical")
    availability_start: Optional[date] = None
    availability_end: Optional[date] = None
    
    has_experience: bool = False
    experience_details: Optional[str] = None
    emergency_contact: Optional[str] = None


class VolunteerResponse(BaseModel):
    """Volunteer response."""
    id: int
    volunteer_id: str
    fandorp_id: Optional[int] = None
    user_id: Optional[int] = None
    
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    
    role: Optional[str] = None
    status: str
    
    training_completed: bool
    badge_issued: bool
    
    total_hours: float
    total_shifts: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# SHIFT SCHEMAS
# =============================================================================

class ShiftCreate(BaseModel):
    """Create shift."""
    date: date
    start_time: time
    end_time: time
    role: str
    max_volunteers: int = Field(default=5, ge=1)
    description: Optional[str] = None


class ShiftResponse(BaseModel):
    """Shift response."""
    id: int
    shift_id: str
    fandorp_id: int
    
    date: date
    start_time: time
    end_time: time
    
    role: str
    max_volunteers: int
    current_volunteers: int
    
    status: str
    description: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class ShiftCheckIn(BaseModel):
    """Check in to shift."""
    volunteer_id: int


# =============================================================================
# INCIDENT SCHEMAS
# =============================================================================

class IncidentCreate(BaseModel):
    """Report incident."""
    incident_type: str = Field(..., description="Medical, Security, Technical, Other")
    severity: str = Field(default="Low", description="Low, Medium, High, Critical")
    description: str
    location_in_venue: Optional[str] = None


class IncidentUpdate(BaseModel):
    """Update incident."""
    status: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None


class IncidentResponse(BaseModel):
    """Incident response."""
    id: int
    incident_id: str
    fandorp_id: int
    
    incident_type: str
    severity: str
    description: str
    location_in_venue: Optional[str] = None
    
    status: str
    reported_by: Optional[str] = None
    reported_at: datetime
    
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    class Config:
        from_attributes = True


# =============================================================================
# STATS
# =============================================================================

class FanDorpStats(BaseModel):
    """FanDorp statistics."""
    total_fandorpen: int
    total_capacity: int
    total_volunteers: int
    total_visitors: int
    total_incidents: int
    by_city: dict
    by_status: dict
    volunteer_hours: float
