# ============================================================================
# ProInvestiX Enterprise API - Identity Schemas
# Identity Shield & Maroc ID
# ============================================================================

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


# =============================================================================
# IDENTITY SHIELD SCHEMAS
# =============================================================================

class IdentityBase(BaseModel):
    """Base identity fields."""
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: date
    nationality: str = Field(default="Moroccan", max_length=50)
    
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    
    document_type: Optional[str] = Field(None, description="Passport, ID Card, Residence Permit")
    document_number: Optional[str] = None
    document_expiry: Optional[date] = None
    document_country: Optional[str] = None


class IdentityCreate(IdentityBase):
    """Create identity."""
    pass


class IdentityUpdate(BaseModel):
    """Update identity."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    document_type: Optional[str] = None
    document_number: Optional[str] = None
    document_expiry: Optional[date] = None
    verification_level: Optional[int] = None


class IdentityResponse(IdentityBase):
    """Identity response."""
    id: int
    identity_id: str
    user_id: Optional[int] = None
    
    verification_level: int
    is_verified: bool
    verified_at: Optional[datetime] = None
    
    blockchain_hash: Optional[str] = None
    status: str
    
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# FRAUD ALERT SCHEMAS
# =============================================================================

class FraudAlertCreate(BaseModel):
    """Create fraud alert."""
    identity_id: Optional[int] = None
    alert_type: str = Field(..., description="Duplicate, Suspicious, Stolen, Fake")
    severity: str = Field(default="Medium", description="Low, Medium, High, Critical")
    description: str
    evidence: Optional[str] = None


class FraudAlertUpdate(BaseModel):
    """Update fraud alert."""
    status: Optional[str] = None
    resolution: Optional[str] = None
    resolved_by: Optional[str] = None


class FraudAlertResponse(BaseModel):
    """Fraud alert response."""
    id: int
    alert_id: str
    identity_id: Optional[int] = None
    
    alert_type: str
    severity: str
    description: str
    evidence: Optional[str] = None
    
    status: str
    reported_by: Optional[str] = None
    reported_at: datetime
    
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    class Config:
        from_attributes = True


# =============================================================================
# MAROC ID SCHEMAS
# =============================================================================

class MarocIDBase(BaseModel):
    """Base Maroc ID fields."""
    first_name_ar: Optional[str] = None
    last_name_ar: Optional[str] = None
    first_name_fr: str = Field(..., min_length=1, max_length=50)
    last_name_fr: str = Field(..., min_length=1, max_length=50)
    
    date_of_birth: date
    place_of_birth: Optional[str] = None
    gender: str = Field(..., description="M, F")
    
    cin_number: Optional[str] = Field(None, description="Carte d'Identité Nationale")
    passport_number: Optional[str] = None
    
    address: Optional[str] = None
    city: Optional[str] = None
    region: Optional[str] = None
    
    father_name: Optional[str] = None
    mother_name: Optional[str] = None


class MarocIDCreate(MarocIDBase):
    """Create Maroc ID."""
    email: Optional[EmailStr] = None
    phone: Optional[str] = None


class MarocIDResponse(MarocIDBase):
    """Maroc ID response."""
    id: int
    maroc_id: str
    user_id: Optional[int] = None
    
    verification_level: int
    kyc_status: str
    
    wallet_address: Optional[str] = None
    digital_signature: Optional[str] = None
    
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# =============================================================================
# VERIFICATION SCHEMAS
# =============================================================================

class VerificationRequest(BaseModel):
    """Request verification."""
    verification_type: str = Field(..., description="Document, Biometric, Address, Phone")
    document_url: Optional[str] = None
    selfie_url: Optional[str] = None


class VerificationResponse(BaseModel):
    """Verification response."""
    success: bool
    verification_id: str
    status: str
    level_achieved: int
    message: str
    next_steps: Optional[List[str]] = None


# =============================================================================
# CERTIFICATE SCHEMAS
# =============================================================================

class CertificateCreate(BaseModel):
    """Issue certificate."""
    maroc_id: int
    certificate_type: str = Field(..., description="Birth, Marriage, Residence, Employment")
    purpose: Optional[str] = None
    validity_days: int = Field(default=30, ge=1, le=365)


class CertificateResponse(BaseModel):
    """Certificate response."""
    id: int
    certificate_id: str
    maroc_id: int
    
    certificate_type: str
    purpose: Optional[str] = None
    
    issued_at: datetime
    expires_at: datetime
    
    qr_code: Optional[str] = None
    blockchain_hash: Optional[str] = None
    
    status: str
    
    class Config:
        from_attributes = True


# =============================================================================
# STATS
# =============================================================================

class IdentityStats(BaseModel):
    """Identity statistics."""
    total_identities: int
    verified_identities: int
    verification_rate: float
    fraud_alerts: int
    fraud_resolved: int
    by_verification_level: dict
    by_nationality: dict


class MarocIDStats(BaseModel):
    """Maroc ID statistics."""
    total_maroc_ids: int
    active_ids: int
    certificates_issued: int
    by_region: dict
    by_kyc_status: dict
