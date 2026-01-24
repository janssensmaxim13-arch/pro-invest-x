# ============================================================================
# ProInvestiX Enterprise API - Auth Endpoints
# ============================================================================

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.dependencies import get_current_user
from app.config import settings
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    PasswordChange,
    TokenResponse,
    RefreshTokenResponse,
    UserResponse,
    MessageResponse,
)
from app.core.exceptions import (
    InvalidCredentialsException,
    AlreadyExistsException,
    InvalidTokenException,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# LOGIN
# =============================================================================

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User's email address
    - **password**: User's password
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if user is None or not verify_password(request.password, user.password_hash):
        raise InvalidCredentialsException()
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


# =============================================================================
# REGISTER
# =============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Register a new user.
    
    - **username**: Unique username
    - **email**: Unique email address
    - **password**: Password (minimum 8 characters)
    """
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == request.email)
    )
    if result.scalar_one_or_none():
        raise AlreadyExistsException(resource="User", field="email", value=request.email)
    
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    if result.scalar_one_or_none():
        raise AlreadyExistsException(resource="User", field="username", value=request.username)
    
    # Create user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        role="User",
        first_name=request.first_name,
        last_name=request.last_name,
        is_active=True,
        is_verified=False,
        created_at=datetime.utcnow(),
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create tokens
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


# =============================================================================
# REFRESH TOKEN
# =============================================================================

@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Refresh access token using refresh token.
    """
    # Verify refresh token
    payload = verify_token(request.refresh_token, token_type="refresh")
    if payload is None:
        raise InvalidTokenException()
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == int(payload.sub))
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise InvalidTokenException()
    
    # Create new access token
    access_token = create_access_token(subject=user.id, role=user.role)
    
    return RefreshTokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# =============================================================================
# GET CURRENT USER
# =============================================================================

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


# =============================================================================
# CHANGE PASSWORD
# =============================================================================

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Change password for current user.
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    # Update password
    current_user.password_hash = get_password_hash(request.new_password)
    await db.commit()
    
    return MessageResponse(
        message="Password changed successfully",
        success=True,
    )


# =============================================================================
# LOGOUT (Optional - for token blacklisting)
# =============================================================================

@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Logout current user.
    
    Note: In a stateless JWT system, the client simply discards the token.
    For enhanced security, implement token blacklisting with Redis.
    """
    # In a real implementation, you would add the token to a blacklist
    # For now, we just return success
    return MessageResponse(
        message="Successfully logged out",
        success=True,
    )
