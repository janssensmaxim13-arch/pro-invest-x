# ============================================================================
# ProInvestiX Enterprise API - Academy Schemas
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# ACADEMY SCHEMAS
# =============================================================================

class AcademyBase(BaseModel):
    """Base academy fields."""
    name: str = Field(..., min_length=1, max_length=100)
    short_name: Optional[str] = Field(None, max_length=20)
    
    city: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    country: str = Field(default="Morocco", max_length=50)
    address: Optional[str] = None
    
    license_number: Optional[str] = None
    license_level: Optional[str] = Field(None, description="Elite, A, B, C")
    frmf_affiliated: bool = True
    
    founded_year: Optional[int] = None
    capacity: Optional[int] = Field(None, ge=0)
    
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    website: Optional[str] = None


class AcademyCreate(AcademyBase):
    """Create academy request."""
    pass


class AcademyUpdate(BaseModel):
    """Update academy request."""
    name: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    license_level: Optional[str] = None
    capacity: Optional[int] = None
    is_active: Optional[bool] = None


class AcademyResponse(AcademyBase):
    """Academy response."""
    id: int
    academy_id: str
    is_active: bool
    total_talents: int
    total_staff: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AcademyListResponse(BaseModel):
    """Academy list response."""
    success: bool = True
    data: List[AcademyResponse]
    meta: dict


# =============================================================================
# TEAM SCHEMAS
# =============================================================================

class TeamBase(BaseModel):
    """Base team fields."""
    name: str = Field(..., min_length=1, max_length=100)
    age_group: str = Field(..., description="U13, U15, U17, U19, U21")
    category: Optional[str] = Field(None, description="Elite, Development, Foundation")
    coach_name: Optional[str] = None
    max_players: int = Field(default=25, ge=1)


class TeamCreate(TeamBase):
    """Create team request."""
    pass


class TeamResponse(TeamBase):
    """Team response."""
    id: int
    team_id: str
    academy_id: int
    current_players: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# STAFF SCHEMAS
# =============================================================================

class StaffBase(BaseModel):
    """Base staff fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    role: str = Field(..., description="Coach, Assistant, Physio, Scout, Director")
    email: Optional[str] = None
    phone: Optional[str] = None
    license_type: Optional[str] = None
    license_number: Optional[str] = None


class StaffCreate(StaffBase):
    """Create staff request."""
    pass


class StaffResponse(StaffBase):
    """Staff response."""
    id: int
    staff_id: str
    academy_id: int
    is_active: bool
    joined_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# ENROLLMENT SCHEMAS
# =============================================================================

class EnrollmentCreate(BaseModel):
    """Enroll talent request."""
    talent_id: int
    team_id: Optional[int] = None
    position: Optional[str] = None
    scholarship: bool = False
    scholarship_amount: Optional[float] = None
    notes: Optional[str] = None


class EnrollmentResponse(BaseModel):
    """Enrollment response."""
    id: int
    enrollment_id: str
    academy_id: int
    talent_id: int
    team_id: Optional[int] = None
    status: str
    enrolled_date: date
    position: Optional[str] = None
    scholarship: bool
    scholarship_amount: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# STATS
# =============================================================================

class AcademyStats(BaseModel):
    """Academy statistics."""
    total_academies: int
    total_talents: int
    total_staff: int
    by_region: dict
    by_license_level: dict
    top_academies: List[dict]
