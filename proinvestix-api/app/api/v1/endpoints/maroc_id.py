# ============================================================================
# ProInvestiX Enterprise API - Maroc ID Endpoints
# ============================================================================

from datetime import datetime, timedelta
from typing import Any, List, Optional
import uuid
import hashlib
import base64
import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import MarocIdentity, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.identity import (
    MarocIDCreate, MarocIDResponse,
    CertificateCreate, CertificateResponse,
    VerificationRequest, VerificationResponse,
    MarocIDStats,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/maroc-id", tags=["Maroc ID Shield"])


# =============================================================================
# IN-MEMORY STORAGE (voor certificates)
# =============================================================================

certificates_db = []
organizations_db = []


# =============================================================================
# HELPERS
# =============================================================================

def generate_maroc_id() -> str:
    return f"MID-{uuid.uuid4().hex[:8].upper()}"

def generate_certificate_id() -> str:
    return f"CRT-{uuid.uuid4().hex[:8].upper()}"

def generate_wallet_address() -> str:
    return "0x" + hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:40]

def generate_digital_signature(data: str) -> str:
    return hashlib.sha256(f"{data}{datetime.utcnow()}".encode()).hexdigest()[:64]

def generate_qr_code(data: dict) -> str:
    return base64.b64encode(json.dumps(data).encode()).decode()


# =============================================================================
# MAROC ID CRUD
# =============================================================================

@router.get("", response_model=List[MarocIDResponse])
async def list_maroc_ids(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    region: Optional[str] = None,
    kyc_status: Optional[str] = None,
) -> Any:
    """List all Maroc IDs (Admin only)."""
    query = select(MarocIdentity)
    
    if region:
        query = query.where(MarocIdentity.region == region)
    if kyc_status:
        query = query.where(MarocIdentity.kyc_status == kyc_status)
    
    query = query.order_by(MarocIdentity.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    maroc_ids = result.scalars().all()
    
    return [MarocIDResponse.model_validate(m) for m in maroc_ids]


@router.get("/me", response_model=MarocIDResponse)
async def get_my_maroc_id(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's Maroc ID."""
    result = await db.execute(
        select(MarocIdentity).where(MarocIdentity.user_id == current_user.id)
    )
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id="current user")
    
    return MarocIDResponse.model_validate(maroc_id)


@router.get("/{maroc_id_pk}", response_model=MarocIDResponse)
async def get_maroc_id(
    maroc_id_pk: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get Maroc ID by ID."""
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == maroc_id_pk))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=maroc_id_pk)
    
    if maroc_id.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return MarocIDResponse.model_validate(maroc_id)


@router.post("", response_model=MarocIDResponse, status_code=status.HTTP_201_CREATED)
async def create_maroc_id(
    request: MarocIDCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create Maroc ID for current user."""
    # Check if already exists
    result = await db.execute(
        select(MarocIdentity).where(MarocIdentity.user_id == current_user.id)
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Maroc ID already exists for this user")
    
    maroc_id = MarocIdentity(
        maroc_id=generate_maroc_id(),
        user_id=current_user.id,
        **request.model_dump(),
        verification_level=0,
        kyc_status="Pending",
        wallet_address=generate_wallet_address(),
        digital_signature=generate_digital_signature(f"{request.first_name_fr}{request.last_name_fr}"),
        is_active=True,
        created_at=datetime.utcnow(),
    )
    
    db.add(maroc_id)
    await db.commit()
    await db.refresh(maroc_id)
    
    return MarocIDResponse.model_validate(maroc_id)


@router.put("/{maroc_id_pk}", response_model=MarocIDResponse)
async def update_maroc_id(
    maroc_id_pk: int,
    request: MarocIDCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update Maroc ID."""
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == maroc_id_pk))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=maroc_id_pk)
    
    if maroc_id.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maroc_id, field, value)
    
    await db.commit()
    await db.refresh(maroc_id)
    
    return MarocIDResponse.model_validate(maroc_id)


# =============================================================================
# VERIFICATION
# =============================================================================

@router.post("/{maroc_id_pk}/verify", response_model=VerificationResponse)
async def request_verification(
    maroc_id_pk: int,
    request: VerificationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Request Maroc ID verification."""
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == maroc_id_pk))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=maroc_id_pk)
    
    # Simulate verification
    new_level = min(maroc_id.verification_level + 1, 3)
    maroc_id.verification_level = new_level
    
    if new_level >= 2:
        maroc_id.kyc_status = "Verified"
    elif new_level == 1:
        maroc_id.kyc_status = "Basic"
    
    await db.commit()
    
    return VerificationResponse(
        success=True,
        verification_id=f"VRF-{uuid.uuid4().hex[:8].upper()}",
        status=maroc_id.kyc_status,
        level_achieved=new_level,
        message=f"Verification level upgraded to {new_level}",
        next_steps=None if new_level >= 3 else ["Complete additional verification"],
    )


@router.get("/{maroc_id_pk}/level")
async def get_verification_level(
    maroc_id_pk: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get verification level."""
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == maroc_id_pk))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=maroc_id_pk)
    
    return {
        "maroc_id": maroc_id.maroc_id,
        "verification_level": maroc_id.verification_level,
        "kyc_status": maroc_id.kyc_status,
        "max_level": 3,
        "benefits": {
            0: "Basic access",
            1: "Document verification, basic transactions",
            2: "Full KYC, higher limits",
            3: "Premium services, unlimited transactions",
        }
    }


@router.post("/{maroc_id_pk}/upgrade")
async def upgrade_level(
    maroc_id_pk: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Request level upgrade."""
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == maroc_id_pk))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=maroc_id_pk)
    
    if maroc_id.verification_level >= 3:
        return {"success": False, "message": "Already at maximum level"}
    
    return {
        "success": True,
        "message": "Upgrade request submitted",
        "current_level": maroc_id.verification_level,
        "requested_level": maroc_id.verification_level + 1,
        "requirements": ["Submit additional documents", "Complete video verification"],
    }


# =============================================================================
# CERTIFICATES
# =============================================================================

@router.get("/certificates", response_model=List[CertificateResponse])
async def list_certificates(
    current_user: User = Depends(get_current_user),
    maroc_id_pk: Optional[int] = None,
) -> Any:
    """List certificates."""
    result = certificates_db.copy()
    
    if maroc_id_pk:
        result = [c for c in result if c.get("maroc_id") == maroc_id_pk]
    
    return result


@router.post("/certificates", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED)
async def issue_certificate(
    request: CertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Issue certificate."""
    # Verify Maroc ID exists
    result = await db.execute(select(MarocIdentity).where(MarocIdentity.id == request.maroc_id))
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise NotFoundException(resource="Maroc ID", resource_id=request.maroc_id)
    
    issued_at = datetime.utcnow()
    expires_at = issued_at + timedelta(days=request.validity_days)
    
    certificate = {
        "id": len(certificates_db) + 1,
        "certificate_id": generate_certificate_id(),
        "maroc_id": request.maroc_id,
        "certificate_type": request.certificate_type,
        "purpose": request.purpose,
        "issued_at": issued_at,
        "expires_at": expires_at,
        "qr_code": generate_qr_code({
            "cert_id": generate_certificate_id(),
            "type": request.certificate_type,
            "issued": issued_at.isoformat(),
        }),
        "blockchain_hash": generate_digital_signature(f"{request.maroc_id}{request.certificate_type}"),
        "status": "Active",
    }
    
    certificates_db.append(certificate)
    return certificate


@router.put("/certificates/{certificate_id}")
async def update_certificate(
    certificate_id: int,
    status: str,
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update certificate status."""
    for cert in certificates_db:
        if cert["id"] == certificate_id:
            cert["status"] = status
            return cert
    raise NotFoundException(resource="Certificate", resource_id=certificate_id)


# =============================================================================
# DIGITAL SIGNATURE
# =============================================================================

@router.post("/sign")
async def sign_transaction(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Sign a transaction with Maroc ID."""
    result = await db.execute(
        select(MarocIdentity).where(MarocIdentity.user_id == current_user.id)
    )
    maroc_id = result.scalar_one_or_none()
    
    if maroc_id is None:
        raise HTTPException(status_code=400, detail="No Maroc ID found for user")
    
    if maroc_id.verification_level < 2:
        raise HTTPException(status_code=400, detail="Verification level 2+ required for signing")
    
    signature = generate_digital_signature(json.dumps(data))
    
    return {
        "success": True,
        "maroc_id": maroc_id.maroc_id,
        "signature": signature,
        "signed_at": datetime.utcnow().isoformat(),
        "data_hash": hashlib.sha256(json.dumps(data).encode()).hexdigest(),
    }


# =============================================================================
# ORGANIZATIONS
# =============================================================================

@router.get("/organizations")
async def list_organizations(
    current_user: User = Depends(get_current_user),
) -> Any:
    """List registered organizations."""
    return organizations_db


@router.post("/organizations")
async def create_organization(
    name: str,
    org_type: str,
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Register organization."""
    org = {
        "id": len(organizations_db) + 1,
        "org_id": f"ORG-{uuid.uuid4().hex[:8].upper()}",
        "name": name,
        "type": org_type,
        "status": "Active",
        "created_at": datetime.utcnow(),
    }
    organizations_db.append(org)
    return org


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=MarocIDStats)
async def get_maroc_id_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get Maroc ID statistics."""
    # Total
    result = await db.execute(select(func.count(MarocIdentity.id)))
    total = result.scalar() or 0
    
    # Active
    result = await db.execute(
        select(func.count(MarocIdentity.id)).where(MarocIdentity.is_active == True)
    )
    active = result.scalar() or 0
    
    # By region
    result = await db.execute(
        select(MarocIdentity.region, func.count(MarocIdentity.id))
        .group_by(MarocIdentity.region)
    )
    by_region = {row[0] or "Unknown": row[1] for row in result.all()}
    
    # By KYC status
    result = await db.execute(
        select(MarocIdentity.kyc_status, func.count(MarocIdentity.id))
        .group_by(MarocIdentity.kyc_status)
    )
    by_kyc = {row[0] or "Pending": row[1] for row in result.all()}
    
    return MarocIDStats(
        total_maroc_ids=total,
        active_ids=active,
        certificates_issued=len(certificates_db),
        by_region=by_region,
        by_kyc_status=by_kyc,
    )
