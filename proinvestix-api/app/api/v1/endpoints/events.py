# ============================================================================
# ProInvestiX Enterprise API - Events Endpoints
# TicketChain - Blockchain Ticketing
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid
import hashlib
import json
import base64

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.db.database import get_db
from app.db.models import Event, Ticket, LoyaltyPoints, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.event import (
    EventCreate,
    EventUpdate,
    EventResponse,
    EventListResponse,
    EventDetailResponse,
    TicketMintRequest,
    TicketResponse,
    TicketVerifyResponse,
    TicketListResponse,
    TicketTransferRequest,
    LoyaltyResponse,
    TicketChainStats,
)
from app.core.exceptions import NotFoundException, BusinessLogicException

router = APIRouter(prefix="/events", tags=["TicketChain - Events"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_event_id() -> str:
    return f"EVT-{uuid.uuid4().hex[:8].upper()}"


def generate_ticket_hash() -> str:
    """Generate blockchain-style ticket hash."""
    data = f"{uuid.uuid4()}-{datetime.utcnow().isoformat()}"
    return "0x" + hashlib.sha256(data.encode()).hexdigest()


def generate_qr_code(ticket_hash: str, event_id: str) -> str:
    """Generate QR code data (base64 encoded JSON)."""
    qr_data = {
        "ticket": ticket_hash,
        "event": event_id,
        "timestamp": datetime.utcnow().isoformat(),
    }
    return base64.b64encode(json.dumps(qr_data).encode()).decode()


# =============================================================================
# LIST EVENTS
# =============================================================================

@router.get("", response_model=EventListResponse)
async def list_events(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    city: Optional[str] = None,
    upcoming_only: bool = False,
) -> Any:
    """
    List all events with filtering.
    """
    query = select(Event)
    conditions = []
    
    if status:
        conditions.append(Event.status == status)
    if event_type:
        conditions.append(Event.event_type == event_type)
    if city:
        conditions.append(Event.city.ilike(f"%{city}%"))
    if upcoming_only:
        conditions.append(Event.date >= datetime.utcnow())
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Sort & paginate
    query = query.order_by(Event.date.asc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    events = result.scalars().all()
    
    # Add tickets_available
    response_data = []
    for event in events:
        event_dict = EventResponse.model_validate(event).model_dump()
        event_dict['tickets_available'] = event.capacity - event.tickets_sold
        response_data.append(EventResponse(**event_dict))
    
    return EventListResponse(
        success=True,
        data=response_data,
        meta={
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    )


# =============================================================================
# GET EVENT
# =============================================================================

@router.get("/{event_id}", response_model=EventDetailResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if event is None:
        raise NotFoundException(resource="Event", resource_id=event_id)
    
    event_response = EventResponse.model_validate(event)
    event_response.tickets_available = event.capacity - event.tickets_sold
    
    return EventDetailResponse(success=True, data=event_response)


# =============================================================================
# CREATE EVENT
# =============================================================================

@router.post("", response_model=EventDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    request: EventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create a new event."""
    event = Event(
        event_id=generate_event_id(),
        **request.model_dump(),
        tickets_sold=0,
        tickets_available=request.capacity,
        status="Upcoming",
        created_at=datetime.utcnow(),
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return EventDetailResponse(
        success=True,
        data=EventResponse.model_validate(event),
    )


# =============================================================================
# UPDATE EVENT
# =============================================================================

@router.put("/{event_id}", response_model=EventDetailResponse)
async def update_event(
    event_id: int,
    request: EventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update event."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if event is None:
        raise NotFoundException(resource="Event", resource_id=event_id)
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    await db.commit()
    await db.refresh(event)
    
    return EventDetailResponse(success=True, data=EventResponse.model_validate(event))


# =============================================================================
# DELETE EVENT
# =============================================================================

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("SuperAdmin")),
) -> None:
    """Cancel event."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if event is None:
        raise NotFoundException(resource="Event", resource_id=event_id)
    
    event.status = "Cancelled"
    await db.commit()


# =============================================================================
# MINT TICKET
# =============================================================================

@router.post("/{event_id}/tickets/mint", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def mint_ticket(
    event_id: int,
    request: TicketMintRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Mint a new ticket for an event.
    Creates blockchain-verified ticket with QR code.
    """
    # Get event
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    
    if event is None:
        raise NotFoundException(resource="Event", resource_id=event_id)
    
    # Check availability
    if event.tickets_sold >= event.capacity:
        raise BusinessLogicException(
            detail=f"Event '{event.name}' is sold out",
            error_code="EVENT_SOLD_OUT"
        )
    
    # Generate ticket
    ticket_hash = generate_ticket_hash()
    seat_info = f"{request.seat_section or 'GA'}-{request.seat_row or '0'}-{request.seat_number or '0'}"
    
    ticket = Ticket(
        ticket_hash=ticket_hash,
        event_id=event_id,
        owner_id=request.owner_id or current_user.id,
        owner_name=request.owner_name,
        seat_section=request.seat_section,
        seat_row=request.seat_row,
        seat_number=request.seat_number,
        seat_info=seat_info,
        category=request.category,
        price=request.price,
        minted_at=datetime.utcnow(),
        block_number=int(datetime.utcnow().timestamp()),
        transaction_hash="0x" + hashlib.sha256(ticket_hash.encode()).hexdigest()[:64],
        status="Valid",
        qr_code=generate_qr_code(ticket_hash, event.event_id),
    )
    
    # Update event
    event.tickets_sold += 1
    
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    
    # Update loyalty points
    if request.owner_id:
        result = await db.execute(
            select(LoyaltyPoints).where(LoyaltyPoints.user_id == request.owner_id)
        )
        loyalty = result.scalar_one_or_none()
        
        if loyalty is None:
            loyalty = LoyaltyPoints(
                user_id=request.owner_id,
                points_balance=0,
                total_earned=0,
                total_spent=0,
                tier="Bronze",
                tickets_purchased=0,
            )
            db.add(loyalty)
        
        # 1 point per euro spent
        points_earned = int(request.price)
        loyalty.points_balance += points_earned
        loyalty.total_earned += points_earned
        loyalty.tickets_purchased += 1
        loyalty.last_activity = datetime.utcnow()
        
        # Update tier
        if loyalty.total_earned >= 1000:
            loyalty.tier = "Platinum"
        elif loyalty.total_earned >= 500:
            loyalty.tier = "Gold"
        elif loyalty.total_earned >= 100:
            loyalty.tier = "Silver"
        
        await db.commit()
    
    return TicketResponse.model_validate(ticket)


# =============================================================================
# GET EVENT TICKETS
# =============================================================================

@router.get("/{event_id}/tickets", response_model=TicketListResponse)
async def get_event_tickets(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    status: Optional[str] = None,
) -> Any:
    """Get all tickets for an event."""
    # Verify event exists
    result = await db.execute(select(Event).where(Event.id == event_id))
    if result.scalar_one_or_none() is None:
        raise NotFoundException(resource="Event", resource_id=event_id)
    
    query = select(Ticket).where(Ticket.event_id == event_id)
    
    if status:
        query = query.where(Ticket.status == status)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return TicketListResponse(
        success=True,
        data=[TicketResponse.model_validate(t) for t in tickets],
        meta={"total": total, "page": page, "per_page": per_page}
    )


# =============================================================================
# TICKET STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=TicketChainStats)
async def get_ticketchain_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get TicketChain statistics."""
    # Total events
    result = await db.execute(select(func.count(Event.id)))
    total_events = result.scalar() or 0
    
    # Total tickets
    result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = result.scalar() or 0
    
    # Tickets used
    result = await db.execute(
        select(func.count(Ticket.id)).where(Ticket.status == "Used")
    )
    tickets_used = result.scalar() or 0
    
    # Revenue
    result = await db.execute(select(func.sum(Ticket.price)))
    total_revenue = result.scalar() or 0
    
    # By status
    result = await db.execute(
        select(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status)
    )
    by_status = {row[0]: row[1] for row in result.all()}
    
    # By category
    result = await db.execute(
        select(Ticket.category, func.count(Ticket.id)).group_by(Ticket.category)
    )
    by_category = {row[0] or "Standard": row[1] for row in result.all()}
    
    # Upcoming events
    result = await db.execute(
        select(func.count(Event.id)).where(Event.date >= datetime.utcnow())
    )
    upcoming = result.scalar() or 0
    
    return TicketChainStats(
        total_events=total_events,
        total_tickets=total_tickets,
        tickets_used=tickets_used,
        total_revenue=total_revenue,
        by_status=by_status,
        by_category=by_category,
        upcoming_events=upcoming,
    )
