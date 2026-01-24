# ============================================================================
# ProInvestiX Enterprise API - FRMF Schemas
# Royal Moroccan Football Federation
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# REFEREE SCHEMAS
# =============================================================================

class RefereeBase(BaseModel):
    """Base referee fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    nationality: str = Field(default="Moroccan", max_length=50)
    
    license_number: Optional[str] = None
    license_grade: Optional[str] = Field(None, description="FIFA, CAF, National, Regional")
    license_expiry: Optional[date] = None
    
    region: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    years_experience: Optional[int] = None
    specialization: Optional[str] = Field(None, description="Main, Assistant, VAR, Fourth")


class RefereeCreate(RefereeBase):
    """Create referee."""
    pass


class RefereeUpdate(BaseModel):
    """Update referee."""
    license_grade: Optional[str] = None
    license_expiry: Optional[date] = None
    region: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None


class RefereeResponse(RefereeBase):
    """Referee response."""
    id: int
    referee_id: str
    is_active: bool
    status: str
    total_matches: int
    avg_rating: Optional[float] = None
    blockchain_hash: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# VAR DECISION SCHEMAS
# =============================================================================

class VARDecisionCreate(BaseModel):
    """Create VAR decision."""
    match_id: str
    match_date: date
    minute: int = Field(..., ge=0, le=120)
    
    decision_type: str = Field(..., description="Goal, Penalty, RedCard, MistakenIdentity")
    original_decision: str
    final_decision: str
    
    var_referee_id: Optional[int] = None
    main_referee_id: Optional[int] = None
    
    review_duration_seconds: Optional[int] = None
    video_url: Optional[str] = None
    notes: Optional[str] = None


class VARDecisionResponse(BaseModel):
    """VAR decision response."""
    id: int
    decision_id: str
    match_id: str
    match_date: date
    minute: int
    
    decision_type: str
    original_decision: str
    final_decision: str
    decision_changed: bool
    
    var_referee_id: Optional[int] = None
    main_referee_id: Optional[int] = None
    
    review_duration_seconds: Optional[int] = None
    blockchain_hash: Optional[str] = None
    verified: bool
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# PLAYER SCHEMAS
# =============================================================================

class FRMFPlayerBase(BaseModel):
    """Base FRMF player fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    nationality: str = Field(default="Moroccan")
    
    frmf_id: Optional[str] = None
    position: Optional[str] = None
    current_club: Optional[str] = None
    
    is_national_team: bool = False
    national_team_caps: int = 0
    national_team_goals: int = 0


class FRMFPlayerCreate(FRMFPlayerBase):
    """Create FRMF player."""
    pass


class FRMFPlayerResponse(FRMFPlayerBase):
    """FRMF player response."""
    id: int
    player_id: str
    status: str
    registration_date: Optional[date] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# CONTRACT SCHEMAS
# =============================================================================

class ContractCreate(BaseModel):
    """Create contract."""
    player_id: int
    club_name: str
    contract_type: str = Field(..., description="Professional, Amateur, Youth")
    start_date: date
    end_date: date
    salary_annual: Optional[float] = None
    release_clause: Optional[float] = None


class ContractResponse(BaseModel):
    """Contract response."""
    id: int
    contract_id: str
    player_id: int
    club_name: str
    contract_type: str
    start_date: date
    end_date: date
    salary_annual: Optional[float] = None
    release_clause: Optional[float] = None
    status: str
    blockchain_hash: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# MATCH ASSIGNMENT SCHEMAS
# =============================================================================

class MatchAssignmentCreate(BaseModel):
    """Create match assignment."""
    match_id: str
    match_date: date
    home_team: str
    away_team: str
    competition: str
    venue: Optional[str] = None
    
    main_referee_id: int
    assistant1_id: Optional[int] = None
    assistant2_id: Optional[int] = None
    fourth_official_id: Optional[int] = None
    var_referee_id: Optional[int] = None


class MatchAssignmentResponse(BaseModel):
    """Match assignment response."""
    id: int
    assignment_id: str
    match_id: str
    match_date: date
    home_team: str
    away_team: str
    competition: str
    venue: Optional[str] = None
    
    main_referee_id: int
    assistant1_id: Optional[int] = None
    assistant2_id: Optional[int] = None
    fourth_official_id: Optional[int] = None
    var_referee_id: Optional[int] = None
    
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# STATS
# =============================================================================

class FRMFStats(BaseModel):
    """FRMF statistics."""
    total_referees: int
    total_players: int
    total_contracts: int
    total_var_decisions: int
    var_decisions_changed: int
    var_accuracy_rate: float
    by_referee_grade: dict
    by_competition: dict
