# ============================================================================
# ProInvestiX Enterprise API - Additional Module Schemas
# Hayat, Anti-Hate, NIL, Consulate
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# HAYAT HEALTH SCHEMAS
# =============================================================================

class HayatSessionCreate(BaseModel):
    """Create Hayat session."""
    session_type: str = Field(..., description="Counseling, CheckIn, Crisis, Rehabilitation")
    provider_type: Optional[str] = Field(None, description="Psychologist, Counselor, Coach")
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_anonymous: bool = False


class HayatSessionResponse(BaseModel):
    """Hayat session response."""
    id: int
    session_id: str
    user_id: Optional[int] = None
    anonymous_code: Optional[str] = None
    
    session_type: str
    provider_type: Optional[str] = None
    provider_name: Optional[str] = None
    
    status: str
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    
    notes_encrypted: Optional[str] = None
    wellbeing_score_before: Optional[int] = None
    wellbeing_score_after: Optional[int] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


class CrisisAlertCreate(BaseModel):
    """Create crisis alert."""
    severity: str = Field(..., description="Low, Medium, High, Critical")
    description: str
    location: Optional[str] = None
    contact_requested: bool = False


class CrisisAlertResponse(BaseModel):
    """Crisis alert response."""
    id: int
    alert_id: str
    user_id: Optional[int] = None
    anonymous_code: Optional[str] = None
    
    severity: str
    description: str
    location: Optional[str] = None
    
    status: str
    responder_id: Optional[int] = None
    response_time_minutes: Optional[int] = None
    
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# =============================================================================
# ANTI-HATE SCHEMAS
# =============================================================================

class AntiHateIncidentCreate(BaseModel):
    """Report anti-hate incident."""
    incident_type: str = Field(..., description="Racism, Discrimination, Harassment, Threats")
    platform: Optional[str] = Field(None, description="Twitter, Instagram, Stadium, Other")
    severity: str = Field(default="Medium")
    description: str
    victim_name: Optional[str] = None
    perpetrator_info: Optional[str] = None
    evidence_url: Optional[str] = None
    is_anonymous: bool = False


class AntiHateIncidentResponse(BaseModel):
    """Anti-hate incident response."""
    id: int
    incident_id: str
    
    incident_type: str
    platform: Optional[str] = None
    severity: str
    description: str
    
    victim_name: Optional[str] = None
    perpetrator_info: Optional[str] = None
    evidence_url: Optional[str] = None
    
    status: str
    reported_by: Optional[str] = None
    reported_at: datetime
    
    legal_action_taken: bool
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LegalCaseCreate(BaseModel):
    """Create legal case."""
    incident_id: int
    case_type: str = Field(..., description="Civil, Criminal, Administrative")
    jurisdiction: Optional[str] = None
    lawyer_name: Optional[str] = None
    description: str


class LegalCaseResponse(BaseModel):
    """Legal case response."""
    id: int
    case_id: str
    incident_id: int
    
    case_type: str
    case_number: Optional[str] = None
    jurisdiction: Optional[str] = None
    
    status: str
    lawyer_name: Optional[str] = None
    
    filed_at: Optional[datetime] = None
    hearing_date: Optional[datetime] = None
    verdict: Optional[str] = None
    verdict_date: Optional[datetime] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# NIL SCHEMAS (News Intelligence Lab)
# =============================================================================

class NILSignalCreate(BaseModel):
    """Create NIL signal."""
    signal_type: str = Field(..., description="Misinformation, FakeNews, Rumor, Manipulation")
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    headline: str
    content_summary: str
    target_entity: Optional[str] = None
    severity: str = Field(default="Medium")


class NILSignalResponse(BaseModel):
    """NIL signal response."""
    id: int
    signal_id: str
    
    signal_type: str
    source_url: Optional[str] = None
    source_name: Optional[str] = None
    headline: str
    content_summary: str
    
    target_entity: Optional[str] = None
    severity: str
    
    status: str
    verification_status: Optional[str] = None
    fact_check_result: Optional[str] = None
    
    created_at: datetime
    verified_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FactCardCreate(BaseModel):
    """Create fact card."""
    signal_id: Optional[int] = None
    title: str
    claim: str
    verdict: str = Field(..., description="True, False, Misleading, Unverified")
    explanation: str
    sources: Optional[str] = None


class FactCardResponse(BaseModel):
    """Fact card response."""
    id: int
    card_id: str
    signal_id: Optional[int] = None
    
    title: str
    claim: str
    verdict: str
    explanation: str
    sources: Optional[str] = None
    
    views: int
    shares: int
    
    created_at: datetime
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# =============================================================================
# CONSULATE SCHEMAS
# =============================================================================

class ConsularDocumentCreate(BaseModel):
    """Create consular document request."""
    document_type: str = Field(..., description="Passport, CNIE, BirthCert, Attestation")
    purpose: Optional[str] = None
    urgency: str = Field(default="Normal", description="Normal, Urgent, Express")
    notes: Optional[str] = None


class ConsularDocumentResponse(BaseModel):
    """Consular document response."""
    id: int
    document_id: str
    user_id: int
    
    document_type: str
    purpose: Optional[str] = None
    urgency: str
    
    status: str
    submitted_at: datetime
    processed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    pickup_location: Optional[str] = None
    tracking_number: Optional[str] = None
    
    class Config:
        from_attributes = True


class AppointmentCreate(BaseModel):
    """Create appointment."""
    service_type: str = Field(..., description="Document, Notary, Visa, Other")
    consulate_id: Optional[str] = None
    preferred_date: date
    preferred_time: Optional[str] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Appointment response."""
    id: int
    appointment_id: str
    user_id: int
    
    service_type: str
    consulate_id: Optional[str] = None
    consulate_name: Optional[str] = None
    
    scheduled_date: date
    scheduled_time: Optional[str] = None
    
    status: str
    confirmation_code: Optional[str] = None
    
    created_at: datetime
    
    class Config:
        from_attributes = True
