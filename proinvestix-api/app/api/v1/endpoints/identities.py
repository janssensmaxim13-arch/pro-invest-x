# ============================================================================
# ProInvestiX Enterprise API - Identity Shield Endpoints
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Identity, FraudAlert, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.identity import (
    IdentityCreate, IdentityUpdate, IdentityResponse,
    FraudAlertCreate, FraudAlertUpdate, FraudAlertResponse,
    VerificationRequest, VerificationResponse,
    IdentityStats,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/identities", tags=["Identity Shield"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_identity_id() -> str:
    return f"IDN-{uuid.uuid4().hex[:8].upper()}"

def generate_alert_id() -> str:
    return f"ALR-{uuid.uuid4().hex[:8].upper()}"

def generate_verification_id() -> str:
    return f"VRF-{uuid.uuid4().hex[:8].upper()}"

def generate_blockchain_hash(data: str) -> str:
    return "0x" + hashlib.sha256(f"{data}{datetime.utcnow()}".encode()).hexdigest()


# =============================================================================
# IDENTITIES CRUD
# =============================================================================

@router.get("", response_model=List[IdentityResponse])
async def list_identities(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_verified: Optional[bool] = None,
    verification_level: Optional[int] = None,
) -> Any:
    """List all identities (Admin only)."""
    query = select(Identity)
    
    if is_verified is not None:
        query = query.where(Identity.is_verified == is_verified)
    if verification_level is not None:
        query = query.where(Identity.verification_level == verification_level)
    
    query = query.order_by(Identity.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    identities = result.scalars().all()
    
    return [IdentityResponse.model_validate(i) for i in identities]


@router.get("/me", response_model=IdentityResponse)
async def get_my_identity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's identity."""
    result = await db.execute(
        select(Identity).where(Identity.user_id == current_user.id)
    )
    identity = result.scalar_one_or_none()
    
    if identity is None:
        raise NotFoundException(resource="Identity", resource_id="current user")
    
    return IdentityResponse.model_validate(identity)


@router.get("/{identity_id}", response_model=IdentityResponse)
async def get_identity(
    identity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get identity by ID."""
    result = await db.execute(select(Identity).where(Identity.id == identity_id))
    identity = result.scalar_one_or_none()
    
    if identity is None:
        raise NotFoundException(resource="Identity", resource_id=identity_id)
    
    # Check access
    if identity.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return IdentityResponse.model_validate(identity)


@router.post("", response_model=IdentityResponse, status_code=status.HTTP_201_CREATED)
async def create_identity(
    request: IdentityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create identity for current user."""
    # Check if already exists
    result = await db.execute(
        select(Identity).where(Identity.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Identity already exists for this user")
    
    identity = Identity(
        identity_id=generate_identity_id(),
        user_id=current_user.id,
        **request.model_dump(),
        verification_level=0,
        is_verified=False,
        status="Pending",
        blockchain_hash=generate_blockchain_hash(f"{request.first_name}{request.last_name}"),
        created_at=datetime.utcnow(),
    )
    
    db.add(identity)
    await db.commit()
    await db.refresh(identity)
    
    return IdentityResponse.model_validate(identity)


@router.put("/{identity_id}", response_model=IdentityResponse)
async def update_identity(
    identity_id: int,
    request: IdentityUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update identity."""
    result = await db.execute(select(Identity).where(Identity.id == identity_id))
    identity = result.scalar_one_or_none()
    
    if identity is None:
        raise NotFoundException(resource="Identity", resource_id=identity_id)
    
    if identity.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(identity, field, value)
    
    await db.commit()
    await db.refresh(identity)
    
    return IdentityResponse.model_validate(identity)


# =============================================================================
# VERIFICATION
# =============================================================================

@router.get("/{identity_id}/verify", response_model=VerificationResponse)
async def get_verification_status(
    identity_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get verification status."""
    result = await db.execute(select(Identity).where(Identity.id == identity_id))
    identity = result.scalar_one_or_none()
    
    if identity is None:
        raise NotFoundException(resource="Identity", resource_id=identity_id)
    
    next_steps = []
    if identity.verification_level < 1:
        next_steps.append("Submit document for verification")
    if identity.verification_level < 2:
        next_steps.append("Complete biometric verification")
    if identity.verification_level < 3:
        next_steps.append("Verify address")
    
    return VerificationResponse(
        success=True,
        verification_id=identity.identity_id,
        status=identity.status,
        level_achieved=identity.verification_level,
        message=f"Verification level {identity.verification_level}/3",
        next_steps=next_steps if next_steps else None,
    )


@router.post("/{identity_id}/verify", response_model=VerificationResponse)
async def submit_verification(
    identity_id: int,
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Submit verification request."""
    result = await db.execute(select(Identity).where(Identity.id == identity_id))
    identity = result.scalar_one_or_none()
    
    if identity is None:
        raise NotFoundException(resource="Identity", resource_id=identity_id)
    
    if identity.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Simulate verification process
    new_level = min(identity.verification_level + 1, 3)
    identity.verification_level = new_level
    identity.status = "Verified" if new_level == 3 else "Partially Verified"
    
    if new_level == 3:
        identity.is_verified = True
        identity.verified_at = datetime.utcnow()
    
    await db.commit()
    
    return VerificationResponse(
        success=True,
        verification_id=generate_verification_id(),
        status=identity.status,
        level_achieved=new_level,
        message=f"Verification level upgraded to {new_level}",
        next_steps=["Complete remaining steps"] if new_level < 3 else None,
    )


# =============================================================================
# FRAUD ALERTS
# =============================================================================

@router.get("/fraud/alerts", response_model=List[FraudAlertResponse])
async def list_fraud_alerts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    status: Optional[str] = None,
    severity: Optional[str] = None,
) -> Any:
    """List fraud alerts."""
    query = select(FraudAlert)
    
    if status:
        query = query.where(FraudAlert.status == status)
    if severity:
        query = query.where(FraudAlert.severity == severity)
    
    query = query.order_by(FraudAlert.reported_at.desc())
    
    result = await db.execute(query)
    alerts = result.scalars().all()
    
    return [FraudAlertResponse.model_validate(a) for a in alerts]


@router.post("/fraud/alerts", response_model=FraudAlertResponse, status_code=status.HTTP_201_CREATED)
async def create_fraud_alert(
    request: FraudAlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Report fraud alert."""
    alert = FraudAlert(
        alert_id=generate_alert_id(),
        **request.model_dump(),
        status="Open",
        reported_by=current_user.username,
        reported_at=datetime.utcnow(),
    )
    
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    
    return FraudAlertResponse.model_validate(alert)


@router.put("/fraud/alerts/{alert_id}", response_model=FraudAlertResponse)
async def update_fraud_alert(
    alert_id: int,
    request: FraudAlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update fraud alert."""
    result = await db.execute(select(FraudAlert).where(FraudAlert.id == alert_id))
    alert = result.scalar_one_or_none()
    
    if alert is None:
        raise NotFoundException(resource="Fraud Alert", resource_id=alert_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(alert, field, value)
    
    if request.status == "Resolved":
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user.username
    
    await db.commit()
    await db.refresh(alert)
    
    return FraudAlertResponse.model_validate(alert)


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=IdentityStats)
async def get_identity_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get identity statistics."""
    # Total identities
    result = await db.execute(select(func.count(Identity.id)))
    total = result.scalar() or 0
    
    # Verified
    result = await db.execute(
        select(func.count(Identity.id)).where(Identity.is_verified == True)
    )
    verified = result.scalar() or 0
    
    # Fraud alerts
    result = await db.execute(select(func.count(FraudAlert.id)))
    alerts = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(FraudAlert.id)).where(FraudAlert.status == "Resolved")
    )
    resolved = result.scalar() or 0
    
    # By verification level
    result = await db.execute(
        select(Identity.verification_level, func.count(Identity.id))
        .group_by(Identity.verification_level)
    )
    by_level = {f"Level {row[0]}": row[1] for row in result.all()}
    
    # By nationality
    result = await db.execute(
        select(Identity.nationality, func.count(Identity.id))
        .group_by(Identity.nationality)
    )
    by_nationality = {row[0] or "Unknown": row[1] for row in result.all()}
    
    return IdentityStats(
        total_identities=total,
        verified_identities=verified,
        verification_rate=round(verified / total * 100, 2) if total > 0 else 0,
        fraud_alerts=alerts,
        fraud_resolved=resolved,
        by_verification_level=by_level,
        by_nationality=by_nationality,
    )
