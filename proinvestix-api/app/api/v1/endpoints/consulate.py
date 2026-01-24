# ============================================================================
# ProInvestiX Enterprise API - Consulate Hub Endpoints
# ============================================================================

from datetime import datetime, date
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import ConsularDocument, ConsularAppointment, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.additional import (
    ConsularDocumentCreate, ConsularDocumentResponse,
    AppointmentCreate, AppointmentResponse,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/consulate", tags=["Consulate Hub"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_document_id() -> str:
    return f"DOC-{uuid.uuid4().hex[:8].upper()}"

def generate_appointment_id() -> str:
    return f"APT-{uuid.uuid4().hex[:8].upper()}"

def generate_confirmation_code() -> str:
    return f"CNF-{uuid.uuid4().hex[:6].upper()}"

def generate_tracking_number() -> str:
    return f"TRK-{uuid.uuid4().hex[:10].upper()}"


# =============================================================================
# CONSULATES
# =============================================================================

consulates = [
    {"id": "CON-001", "name": "Consulaat Brussel", "city": "Brussels", "country": "Belgium"},
    {"id": "CON-002", "name": "Consulaat Amsterdam", "city": "Amsterdam", "country": "Netherlands"},
    {"id": "CON-003", "name": "Consulaat Parijs", "city": "Paris", "country": "France"},
    {"id": "CON-004", "name": "Consulaat Barcelona", "city": "Barcelona", "country": "Spain"},
    {"id": "CON-005", "name": "Consulaat Frankfurt", "city": "Frankfurt", "country": "Germany"},
]


@router.get("/list")
async def list_consulates(
    country: Optional[str] = None,
    current_user: User = Depends(get_current_user),
) -> Any:
    """List available consulates."""
    result = consulates.copy()
    
    if country:
        result = [c for c in result if c["country"].lower() == country.lower()]
    
    return {"consulates": result}


# =============================================================================
# DOCUMENTS
# =============================================================================

@router.get("/documents", response_model=List[ConsularDocumentResponse])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = None,
) -> Any:
    """List user's document requests."""
    query = select(ConsularDocument).where(ConsularDocument.user_id == current_user.id)
    
    if status_filter:
        query = query.where(ConsularDocument.status == status_filter)
    
    query = query.order_by(ConsularDocument.submitted_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [ConsularDocumentResponse.model_validate(d) for d in documents]


@router.get("/documents/{document_id}", response_model=ConsularDocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get document request by ID."""
    result = await db.execute(select(ConsularDocument).where(ConsularDocument.id == document_id))
    document = result.scalar_one_or_none()
    
    if document is None:
        raise NotFoundException(resource="Document", resource_id=document_id)
    
    if document.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return ConsularDocumentResponse.model_validate(document)


@router.post("/documents", response_model=ConsularDocumentResponse, status_code=status.HTTP_201_CREATED)
async def request_document(
    request: ConsularDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Request consular document."""
    document = ConsularDocument(
        document_id=generate_document_id(),
        user_id=current_user.id,
        document_type=request.document_type,
        purpose=request.purpose,
        urgency=request.urgency,
        status="Submitted",
        submitted_at=datetime.utcnow(),
        tracking_number=generate_tracking_number(),
    )
    
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return ConsularDocumentResponse.model_validate(document)


@router.put("/documents/{document_id}", response_model=ConsularDocumentResponse)
async def update_document_status(
    document_id: int,
    new_status: str,
    pickup_location: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update document status."""
    result = await db.execute(select(ConsularDocument).where(ConsularDocument.id == document_id))
    document = result.scalar_one_or_none()
    
    if document is None:
        raise NotFoundException(resource="Document", resource_id=document_id)
    
    document.status = new_status
    
    if new_status == "Processing":
        document.processed_at = datetime.utcnow()
    elif new_status == "Ready":
        document.completed_at = datetime.utcnow()
        if pickup_location:
            document.pickup_location = pickup_location
    
    await db.commit()
    await db.refresh(document)
    
    return ConsularDocumentResponse.model_validate(document)


@router.get("/documents/{document_id}/track")
async def track_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Track document status."""
    result = await db.execute(select(ConsularDocument).where(ConsularDocument.id == document_id))
    document = result.scalar_one_or_none()
    
    if document is None:
        raise NotFoundException(resource="Document", resource_id=document_id)
    
    timeline = [
        {"status": "Submitted", "date": document.submitted_at.isoformat(), "completed": True},
    ]
    
    if document.processed_at:
        timeline.append({"status": "Processing", "date": document.processed_at.isoformat(), "completed": True})
    else:
        timeline.append({"status": "Processing", "date": None, "completed": False})
    
    if document.completed_at:
        timeline.append({"status": "Ready", "date": document.completed_at.isoformat(), "completed": True})
    else:
        timeline.append({"status": "Ready", "date": None, "completed": False})
    
    return {
        "tracking_number": document.tracking_number,
        "document_type": document.document_type,
        "current_status": document.status,
        "timeline": timeline,
        "pickup_location": document.pickup_location,
    }


# =============================================================================
# APPOINTMENTS
# =============================================================================

@router.get("/appointments", response_model=List[AppointmentResponse])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    upcoming_only: bool = True,
) -> Any:
    """List user's appointments."""
    query = select(ConsularAppointment).where(ConsularAppointment.user_id == current_user.id)
    
    if upcoming_only:
        query = query.where(ConsularAppointment.scheduled_date >= date.today())
    
    query = query.order_by(ConsularAppointment.scheduled_date.asc())
    
    result = await db.execute(query)
    appointments = result.scalars().all()
    
    return [AppointmentResponse.model_validate(a) for a in appointments]


@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get appointment by ID."""
    result = await db.execute(select(ConsularAppointment).where(ConsularAppointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    
    if appointment is None:
        raise NotFoundException(resource="Appointment", resource_id=appointment_id)
    
    if appointment.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return AppointmentResponse.model_validate(appointment)


@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    request: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Book appointment."""
    # Find consulate name
    consulate_name = None
    if request.consulate_id:
        for c in consulates:
            if c["id"] == request.consulate_id:
                consulate_name = c["name"]
                break
    
    appointment = ConsularAppointment(
        appointment_id=generate_appointment_id(),
        user_id=current_user.id,
        service_type=request.service_type,
        consulate_id=request.consulate_id,
        consulate_name=consulate_name,
        scheduled_date=request.preferred_date,
        scheduled_time=request.preferred_time,
        status="Confirmed",
        confirmation_code=generate_confirmation_code(),
        created_at=datetime.utcnow(),
    )
    
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    
    return AppointmentResponse.model_validate(appointment)


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Cancel appointment."""
    result = await db.execute(select(ConsularAppointment).where(ConsularAppointment.id == appointment_id))
    appointment = result.scalar_one_or_none()
    
    if appointment is None:
        raise NotFoundException(resource="Appointment", resource_id=appointment_id)
    
    if appointment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    appointment.status = "Cancelled"
    await db.commit()


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats")
async def get_consulate_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get consulate statistics."""
    # Documents
    result = await db.execute(select(func.count(ConsularDocument.id)))
    total_docs = result.scalar() or 0
    
    result = await db.execute(
        select(ConsularDocument.document_type, func.count(ConsularDocument.id))
        .group_by(ConsularDocument.document_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}
    
    # Appointments
    result = await db.execute(select(func.count(ConsularAppointment.id)))
    total_appointments = result.scalar() or 0
    
    return {
        "documents": {"total": total_docs, "by_type": by_type},
        "appointments": {"total": total_appointments},
        "consulates": len(consulates),
    }
