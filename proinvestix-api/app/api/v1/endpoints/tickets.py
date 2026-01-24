# ============================================================================
# ProInvestiX Enterprise API - Tickets Endpoints
# TicketChain - Blockchain Ticketing
# ============================================================================

from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import Ticket, Event, LoyaltyPoints, User
from app.core.dependencies import get_current_user
from app.schemas.event import (
    TicketResponse,
    TicketVerifyResponse,
    TicketTransferRequest,
    LoyaltyResponse,
    LoyaltyRedeemRequest,
)
from app.core.exceptions import NotFoundException, BusinessLogicException

router = APIRouter(prefix="/tickets", tags=["TicketChain - Tickets"])


# =============================================================================
# GET TICKET BY HASH
# =============================================================================

@router.get("/{ticket_hash}", response_model=TicketResponse)
async def get_ticket(
    ticket_hash: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get ticket by hash."""
    result = await db.execute(
        select(Ticket).where(Ticket.ticket_hash == ticket_hash)
    )
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise NotFoundException(resource="Ticket", resource_id=ticket_hash)
    
    return TicketResponse.model_validate(ticket)


# =============================================================================
# VERIFY TICKET
# =============================================================================

@router.get("/{ticket_hash}/verify", response_model=TicketVerifyResponse)
async def verify_ticket(
    ticket_hash: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    Verify ticket validity.
    Public endpoint for ticket scanners.
    """
    result = await db.execute(
        select(Ticket).where(Ticket.ticket_hash == ticket_hash)
    )
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        return TicketVerifyResponse(
            valid=False,
            ticket=None,
            event_name=None,
            message="Ticket not found"
        )
    
    # Get event
    result = await db.execute(
        select(Event).where(Event.id == ticket.event_id)
    )
    event = result.scalar_one_or_none()
    
    if ticket.status == "Used":
        return TicketVerifyResponse(
            valid=False,
            ticket=TicketResponse.model_validate(ticket),
            event_name=event.name if event else None,
            message=f"Ticket already used at {ticket.used_at}"
        )
    
    if ticket.status == "Cancelled":
        return TicketVerifyResponse(
            valid=False,
            ticket=TicketResponse.model_validate(ticket),
            event_name=event.name if event else None,
            message="Ticket has been cancelled"
        )
    
    if ticket.status == "Expired":
        return TicketVerifyResponse(
            valid=False,
            ticket=TicketResponse.model_validate(ticket),
            event_name=event.name if event else None,
            message="Ticket has expired"
        )
    
    return TicketVerifyResponse(
        valid=True,
        ticket=TicketResponse.model_validate(ticket),
        event_name=event.name if event else None,
        message="Ticket is valid"
    )


# =============================================================================
# USE TICKET
# =============================================================================

@router.post("/{ticket_hash}/use", response_model=TicketResponse)
async def use_ticket(
    ticket_hash: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Mark ticket as used (scan at entrance).
    """
    result = await db.execute(
        select(Ticket).where(Ticket.ticket_hash == ticket_hash)
    )
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise NotFoundException(resource="Ticket", resource_id=ticket_hash)
    
    if ticket.status == "Used":
        raise BusinessLogicException(
            detail=f"Ticket already used at {ticket.used_at}",
            error_code="TICKET_ALREADY_USED"
        )
    
    if ticket.status != "Valid":
        raise BusinessLogicException(
            detail=f"Ticket status is {ticket.status}",
            error_code="TICKET_INVALID"
        )
    
    ticket.status = "Used"
    ticket.used_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse.model_validate(ticket)


# =============================================================================
# TRANSFER TICKET
# =============================================================================

@router.post("/{ticket_hash}/transfer", response_model=TicketResponse)
async def transfer_ticket(
    ticket_hash: str,
    request: TicketTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Transfer ticket to new owner.
    Only ticket owner can transfer.
    """
    result = await db.execute(
        select(Ticket).where(Ticket.ticket_hash == ticket_hash)
    )
    ticket = result.scalar_one_or_none()
    
    if ticket is None:
        raise NotFoundException(resource="Ticket", resource_id=ticket_hash)
    
    # Check ownership
    if ticket.owner_id != current_user.id:
        raise BusinessLogicException(
            detail="You are not the owner of this ticket",
            error_code="NOT_TICKET_OWNER"
        )
    
    if ticket.status != "Valid":
        raise BusinessLogicException(
            detail=f"Cannot transfer ticket with status {ticket.status}",
            error_code="TICKET_NOT_TRANSFERABLE"
        )
    
    # Transfer
    ticket.owner_id = request.new_owner_id
    ticket.owner_name = request.new_owner_name
    ticket.status = "Resold"
    
    await db.commit()
    await db.refresh(ticket)
    
    return TicketResponse.model_validate(ticket)


# =============================================================================
# MY TICKETS
# =============================================================================

@router.get("/my/tickets")
async def get_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
) -> Any:
    """Get current user's tickets."""
    query = select(Ticket).where(Ticket.owner_id == current_user.id)
    
    if status:
        query = query.where(Ticket.status == status)
    
    query = query.order_by(Ticket.minted_at.desc())
    
    result = await db.execute(query)
    tickets = result.scalars().all()
    
    return {
        "success": True,
        "data": [TicketResponse.model_validate(t) for t in tickets],
        "total": len(tickets)
    }


# =============================================================================
# LOYALTY ENDPOINTS
# =============================================================================

@router.get("/loyalty/me", response_model=LoyaltyResponse)
async def get_my_loyalty(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's loyalty points."""
    result = await db.execute(
        select(LoyaltyPoints).where(LoyaltyPoints.user_id == current_user.id)
    )
    loyalty = result.scalar_one_or_none()
    
    if loyalty is None:
        # Create new loyalty account
        loyalty = LoyaltyPoints(
            user_id=current_user.id,
            points_balance=0,
            total_earned=0,
            total_spent=0,
            tier="Bronze",
            tickets_purchased=0,
        )
        db.add(loyalty)
        await db.commit()
        await db.refresh(loyalty)
    
    return LoyaltyResponse.model_validate(loyalty)


@router.post("/loyalty/redeem")
async def redeem_loyalty_points(
    request: LoyaltyRedeemRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Redeem loyalty points for rewards."""
    result = await db.execute(
        select(LoyaltyPoints).where(LoyaltyPoints.user_id == current_user.id)
    )
    loyalty = result.scalar_one_or_none()
    
    if loyalty is None or loyalty.points_balance < request.points:
        raise BusinessLogicException(
            detail=f"Insufficient points. Available: {loyalty.points_balance if loyalty else 0}",
            error_code="INSUFFICIENT_POINTS"
        )
    
    loyalty.points_balance -= request.points
    loyalty.total_spent += request.points
    loyalty.last_activity = datetime.utcnow()
    
    await db.commit()
    
    return {
        "success": True,
        "message": f"Redeemed {request.points} points for {request.reward_type}",
        "remaining_points": loyalty.points_balance
    }
