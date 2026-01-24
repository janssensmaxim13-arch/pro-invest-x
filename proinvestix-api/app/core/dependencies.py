# ============================================================================
# ProInvestiX Enterprise API - Dependencies
# FastAPI Dependency Injection
# ============================================================================

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.core.security import verify_token, TokenPayload

# =============================================================================
# SECURITY SCHEME
# =============================================================================

security = HTTPBearer()


# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, token_type="access")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == int(payload.sub))
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are active.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current user and verify they are a superuser.
    """
    if current_user.role != "SuperAdmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


# =============================================================================
# ROLE-BASED ACCESS CONTROL
# =============================================================================

def require_roles(*allowed_roles: str):
    """
    Dependency factory for role-based access control.
    
    Usage:
        @app.get("/admin", dependencies=[Depends(require_roles("Admin", "SuperAdmin"))])
        async def admin_endpoint():
            ...
    """
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role}' not authorized. Required: {allowed_roles}",
            )
        return current_user
    
    return role_checker


# =============================================================================
# OPTIONAL AUTHENTICATION
# =============================================================================

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[User]:
    """
    Get the current user if authenticated, otherwise return None.
    Useful for endpoints that work both with and without authentication.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        return None
    
    result = await db.execute(
        select(User).where(User.id == int(payload.sub))
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        return None
    
    return user
