# ============================================================================
# ProInvestiX Enterprise API - Auth Schemas
# Pydantic models for authentication
# ============================================================================

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# =============================================================================
# REQUEST SCHEMAS
# =============================================================================

class LoginRequest(BaseModel):
    """Login request body."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password")


class RegisterRequest(BaseModel):
    """Registration request body."""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")


class RefreshTokenRequest(BaseModel):
    """Refresh token request body."""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request body."""
    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation body."""
    token: str = Field(..., description="Reset token from email")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordChange(BaseModel):
    """Password change request body."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class UserResponse(BaseModel):
    """User data in responses."""
    id: int
    username: str
    email: EmailStr
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")
    user: UserResponse = Field(..., description="User information")


class RefreshTokenResponse(BaseModel):
    """Refresh token response."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class MessageResponse(BaseModel):
    """Simple message response."""
    message: str
    success: bool = True
