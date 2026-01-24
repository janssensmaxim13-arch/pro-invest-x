# ============================================================================
# ProInvestiX Enterprise API - Talent Schemas
# NTSP - National Talent Scouting Platform
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# BASE SCHEMAS
# =============================================================================

class TalentBase(BaseModel):
    """Base talent fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    nationality: str = Field(..., max_length=50)
    dual_nationality: Optional[str] = Field(None, max_length=50)
    
    # Diaspora
    is_diaspora: bool = False
    diaspora_country: Optional[str] = None
    diaspora_city: Optional[str] = None
    years_abroad: Optional[int] = None
    speaks_arabic: bool = False
    speaks_french: bool = False
    other_languages: Optional[str] = None
    
    # Contact
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    
    # Family
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    parent_email: Optional[EmailStr] = None
    
    # Football
    primary_position: str = Field(..., max_length=10)
    secondary_position: Optional[str] = Field(None, max_length=10)
    preferred_foot: str = Field(default="Right", max_length=10)
    height_cm: Optional[int] = Field(None, ge=100, le=250)
    weight_kg: Optional[int] = Field(None, ge=30, le=150)
    
    # Current club
    current_club: Optional[str] = None
    current_club_country: Optional[str] = None
    current_league: Optional[str] = None
    contract_start: Optional[date] = None
    contract_end: Optional[date] = None
    jersey_number: Optional[int] = Field(None, ge=1, le=99)
    
    # Flags
    priority_level: str = Field(default="Normal")
    national_team_eligible: bool = True
    interest_in_morocco: bool = False
    notes: Optional[str] = None
    
    # Media
    photo_url: Optional[str] = None
    video_url: Optional[str] = None


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class TalentCreate(TalentBase):
    """Create talent request."""
    pass


class TalentUpdate(BaseModel):
    """Update talent request - all fields optional."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    date_of_birth: Optional[date] = None
    nationality: Optional[str] = Field(None, max_length=50)
    dual_nationality: Optional[str] = None
    
    is_diaspora: Optional[bool] = None
    diaspora_country: Optional[str] = None
    diaspora_city: Optional[str] = None
    
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    primary_position: Optional[str] = None
    secondary_position: Optional[str] = None
    preferred_foot: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    
    current_club: Optional[str] = None
    current_club_country: Optional[str] = None
    contract_end: Optional[date] = None
    
    status: Optional[str] = None
    priority_level: Optional[str] = None
    notes: Optional[str] = None


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class TalentResponse(TalentBase):
    """Talent response."""
    id: int
    talent_id: str
    status: str
    overall_score: float
    potential_score: float
    market_value: float
    discovered_by: Optional[str] = None
    discovery_date: Optional[date] = None
    evaluation_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TalentListResponse(BaseModel):
    """Paginated talent list response."""
    success: bool = True
    data: List[TalentResponse]
    meta: dict


class TalentDetailResponse(BaseModel):
    """Single talent response."""
    success: bool = True
    data: TalentResponse


# =============================================================================
# EVALUATION SCHEMAS
# =============================================================================

class EvaluationBase(BaseModel):
    """Base evaluation fields."""
    evaluation_date: date
    match_observed: Optional[str] = None
    match_date: Optional[date] = None
    
    # Technical scores (1-100)
    score_ball_control: Optional[int] = Field(None, ge=1, le=100)
    score_passing: Optional[int] = Field(None, ge=1, le=100)
    score_dribbling: Optional[int] = Field(None, ge=1, le=100)
    score_shooting: Optional[int] = Field(None, ge=1, le=100)
    score_heading: Optional[int] = Field(None, ge=1, le=100)
    score_first_touch: Optional[int] = Field(None, ge=1, le=100)
    
    # Physical scores (1-100)
    score_speed: Optional[int] = Field(None, ge=1, le=100)
    score_acceleration: Optional[int] = Field(None, ge=1, le=100)
    score_stamina: Optional[int] = Field(None, ge=1, le=100)
    score_strength: Optional[int] = Field(None, ge=1, le=100)
    score_jumping: Optional[int] = Field(None, ge=1, le=100)
    score_agility: Optional[int] = Field(None, ge=1, le=100)
    
    # Mental scores (1-100)
    score_positioning: Optional[int] = Field(None, ge=1, le=100)
    score_vision: Optional[int] = Field(None, ge=1, le=100)
    score_composure: Optional[int] = Field(None, ge=1, le=100)
    score_leadership: Optional[int] = Field(None, ge=1, le=100)
    score_work_rate: Optional[int] = Field(None, ge=1, le=100)
    score_decision_making: Optional[int] = Field(None, ge=1, le=100)
    
    # Goalkeeper specific
    score_reflexes: Optional[int] = Field(None, ge=1, le=100)
    score_handling: Optional[int] = Field(None, ge=1, le=100)
    score_kicking: Optional[int] = Field(None, ge=1, le=100)
    score_positioning_gk: Optional[int] = Field(None, ge=1, le=100)
    
    # Recommendation
    recommendation: Optional[str] = None
    follow_up_required: bool = False
    recommended_for_academy: bool = False
    recommended_for_national: bool = False
    
    # Notes
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None
    development_areas: Optional[str] = None
    notes: Optional[str] = None


class EvaluationCreate(EvaluationBase):
    """Create evaluation request."""
    scout_id: Optional[int] = None
    scout_name: Optional[str] = None


class EvaluationResponse(EvaluationBase):
    """Evaluation response."""
    id: int
    evaluation_id: str
    talent_id: int
    scout_id: Optional[int] = None
    scout_name: Optional[str] = None
    
    overall_technical: Optional[float] = None
    overall_physical: Optional[float] = None
    overall_mental: Optional[float] = None
    overall_score: Optional[float] = None
    potential_score: Optional[float] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# SCOUT SCHEMAS
# =============================================================================

class ScoutBase(BaseModel):
    """Base scout fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    countries: Optional[str] = None
    specialization: Optional[str] = None
    license_level: Optional[str] = None
    experience_years: Optional[int] = None


class ScoutCreate(ScoutBase):
    """Create scout request."""
    user_id: Optional[int] = None


class ScoutUpdate(BaseModel):
    """Update scout request."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    region: Optional[str] = None
    countries: Optional[str] = None
    specialization: Optional[str] = None
    is_active: Optional[bool] = None


class ScoutResponse(ScoutBase):
    """Scout response."""
    id: int
    scout_id: str
    user_id: Optional[int] = None
    is_active: bool
    total_evaluations: int
    total_signings: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# FILTER & SEARCH SCHEMAS
# =============================================================================

class TalentFilters(BaseModel):
    """Talent search filters."""
    search: Optional[str] = None
    nationality: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    is_diaspora: Optional[bool] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    min_score: Optional[float] = None
    club: Optional[str] = None


class TalentStats(BaseModel):
    """Talent statistics."""
    total_talents: int
    by_status: dict
    by_position: dict
    by_nationality: dict
    diaspora_count: int
    average_score: float
    average_potential: float
