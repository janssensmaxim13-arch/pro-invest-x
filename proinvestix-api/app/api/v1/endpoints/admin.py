# ============================================================================
# ProInvestiX Enterprise API - Admin Endpoints
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.db.database import get_db
from app.db.models import User, Session, AuditLog
from app.core.dependencies import get_current_user, require_roles
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundException, AlreadyExistsException
from pydantic import BaseModel, EmailStr, Field

router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# SCHEMAS
# =============================================================================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(default="User")
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    id: int
    user_id: int
    token: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool
    created_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class SystemHealth(BaseModel):
    status: str
    database: str
    uptime: str
    version: str
    environment: str


# =============================================================================
# USERS MANAGEMENT
# =============================================================================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
) -> Any:
    """List all users."""
    query = select(User)
    
    if role:
        query = query.where(User.role == role)
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    if search:
        query = query.where(
            User.username.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%")
        )
    
    query = query.order_by(User.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    return [UserResponse.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise NotFoundException(resource="User", resource_id=user_id)
    
    return UserResponse.model_validate(user)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> Any:
    """Create user (SuperAdmin only)."""
    # Check existing
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise AlreadyExistsException(resource="User", field="email", value=request.email)
    
    result = await db.execute(select(User).where(User.username == request.username))
    if result.scalar_one_or_none():
        raise AlreadyExistsException(resource="User", field="username", value=request.username)
    
    user = User(
        username=request.username,
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=request.role,
        first_name=request.first_name,
        last_name=request.last_name,
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update user."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise NotFoundException(resource="User", resource_id=user_id)
    
    # Only SuperAdmin can change roles
    if request.role and current_user.role != "SuperAdmin":
        raise HTTPException(status_code=403, detail="Only SuperAdmin can change roles")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> None:
    """Delete user (deactivate)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise NotFoundException(resource="User", resource_id=user_id)
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    user.is_active = False
    await db.commit()


# =============================================================================
# SESSIONS
# =============================================================================

@router.get("/sessions", response_model=List[SessionResponse])
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    user_id: Optional[int] = None,
    is_active: bool = True,
) -> Any:
    """List active sessions."""
    query = select(Session).where(Session.is_active == is_active)
    
    if user_id:
        query = query.where(Session.user_id == user_id)
    
    query = query.order_by(Session.created_at.desc()).limit(100)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return [SessionResponse.model_validate(s) for s in sessions]


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def terminate_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> None:
    """Terminate session."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    session = result.scalar_one_or_none()
    
    if session is None:
        raise NotFoundException(resource="Session", resource_id=session_id)
    
    session.is_active = False
    await db.commit()


# =============================================================================
# AUDIT LOGS
# =============================================================================

@router.get("/audit", response_model=List[AuditLogResponse])
async def get_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
) -> Any:
    """Get audit logs."""
    query = select(AuditLog)
    
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
    
    query = query.order_by(AuditLog.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    logs = result.scalars().all()
    
    return [AuditLogResponse.model_validate(l) for l in logs]


# =============================================================================
# SYSTEM
# =============================================================================

@router.get("/health", response_model=SystemHealth)
async def system_health(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get system health."""
    # Check database
    try:
        await db.execute(select(func.count(User.id)))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    from app.config import settings
    
    return SystemHealth(
        status="running",
        database=db_status,
        uptime="N/A",
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )


@router.get("/settings")
async def get_settings(
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> Any:
    """Get system settings."""
    from app.config import settings
    
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
        "cors_origins": settings.CORS_ORIGINS,
    }


@router.get("/stats")
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get admin statistics."""
    # Users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = result.scalar() or 0
    
    # By role
    result = await db.execute(
        select(User.role, func.count(User.id))
        .group_by(User.role)
    )
    by_role = {row[0]: row[1] for row in result.all()}
    
    # Sessions
    result = await db.execute(
        select(func.count(Session.id)).where(Session.is_active == True)
    )
    active_sessions = result.scalar() or 0
    
    # Audit logs today
    from datetime import date
    result = await db.execute(
        select(func.count(AuditLog.id))
        .where(func.date(AuditLog.created_at) == date.today())
    )
    logs_today = result.scalar() or 0
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": by_role,
        },
        "sessions": {
            "active": active_sessions,
        },
        "audit": {
            "logs_today": logs_today,
        }
    }
