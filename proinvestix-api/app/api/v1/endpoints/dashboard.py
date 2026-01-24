# ============================================================================
# ProInvestiX Enterprise API - Dashboard Endpoints
# ============================================================================

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import (
    User, Talent, Transfer, Event, Ticket, Wallet, 
    FoundationDonation, FanDorp, Subscription
)
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# =============================================================================
# MAIN STATISTICS
# =============================================================================

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get main dashboard statistics.
    """
    # Users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0
    
    # Talents
    result = await db.execute(select(func.count(Talent.id)))
    total_talents = result.scalar() or 0
    
    # Transfers
    result = await db.execute(select(func.count(Transfer.id)))
    total_transfers = result.scalar() or 0
    
    result = await db.execute(select(func.sum(Transfer.transfer_fee)))
    transfer_volume = result.scalar() or 0
    
    # Events
    result = await db.execute(select(func.count(Event.id)))
    total_events = result.scalar() or 0
    
    # Tickets
    result = await db.execute(select(func.count(Ticket.id)))
    total_tickets = result.scalar() or 0
    
    result = await db.execute(select(func.sum(Ticket.price)))
    ticket_revenue = result.scalar() or 0
    
    # Wallets
    result = await db.execute(select(func.count(Wallet.id)))
    total_wallets = result.scalar() or 0
    
    result = await db.execute(select(func.sum(Wallet.balance)))
    total_wallet_balance = result.scalar() or 0
    
    # Foundation
    result = await db.execute(select(func.sum(FoundationDonation.amount)))
    foundation_total = result.scalar() or 0
    
    result = await db.execute(select(func.sum(Transfer.foundation_contribution)))
    foundation_from_transfers = result.scalar() or 0
    
    # FanDorpen
    result = await db.execute(select(func.count(FanDorp.id)))
    total_fandorpen = result.scalar() or 0
    
    # Subscriptions
    result = await db.execute(
        select(func.count(Subscription.id))
        .where(Subscription.status == "Active")
    )
    active_subscriptions = result.scalar() or 0
    
    return {
        "users": {
            "total": total_users,
        },
        "talents": {
            "total": total_talents,
        },
        "transfers": {
            "total": total_transfers,
            "volume": transfer_volume,
        },
        "ticketchain": {
            "events": total_events,
            "tickets_sold": total_tickets,
            "revenue": ticket_revenue,
        },
        "wallets": {
            "total": total_wallets,
            "total_balance": total_wallet_balance,
        },
        "foundation": {
            "donations": foundation_total,
            "from_transfers": foundation_from_transfers,
            "total": (foundation_total or 0) + (foundation_from_transfers or 0),
        },
        "fandorpen": {
            "total": total_fandorpen,
        },
        "subscriptions": {
            "active": active_subscriptions,
        },
    }


# =============================================================================
# KPI CARDS
# =============================================================================

@router.get("/kpis")
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get KPI card data.
    """
    # Calculate period comparisons (this month vs last month)
    now = datetime.utcnow()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # Transfers this month
    result = await db.execute(
        select(func.sum(Transfer.transfer_fee))
        .where(Transfer.created_at >= this_month_start)
    )
    transfers_this_month = result.scalar() or 0
    
    result = await db.execute(
        select(func.sum(Transfer.transfer_fee))
        .where(Transfer.created_at >= last_month_start)
        .where(Transfer.created_at < this_month_start)
    )
    transfers_last_month = result.scalar() or 0
    
    # Tickets this month
    result = await db.execute(
        select(func.count(Ticket.id))
        .where(Ticket.minted_at >= this_month_start)
    )
    tickets_this_month = result.scalar() or 0
    
    result = await db.execute(
        select(func.count(Ticket.id))
        .where(Ticket.minted_at >= last_month_start)
        .where(Ticket.minted_at < this_month_start)
    )
    tickets_last_month = result.scalar() or 0
    
    # New talents this month
    result = await db.execute(
        select(func.count(Talent.id))
        .where(Talent.created_at >= this_month_start)
    )
    new_talents = result.scalar() or 0
    
    # Foundation this month
    result = await db.execute(
        select(func.sum(FoundationDonation.amount))
        .where(FoundationDonation.created_at >= this_month_start)
    )
    donations_this_month = result.scalar() or 0
    
    def calc_change(current, previous):
        if previous == 0:
            return 100 if current > 0 else 0
        return round((current - previous) / previous * 100, 1)
    
    return {
        "kpis": [
            {
                "title": "Transfer Volume",
                "value": transfers_this_month,
                "change": calc_change(transfers_this_month, transfers_last_month),
                "format": "currency",
            },
            {
                "title": "Tickets Sold",
                "value": tickets_this_month,
                "change": calc_change(tickets_this_month, tickets_last_month),
                "format": "number",
            },
            {
                "title": "New Talents",
                "value": new_talents,
                "change": 0,
                "format": "number",
            },
            {
                "title": "Foundation Donations",
                "value": donations_this_month,
                "change": 0,
                "format": "currency",
            },
        ]
    }


# =============================================================================
# CHARTS DATA
# =============================================================================

@router.get("/charts/{chart_type}")
async def get_chart_data(
    chart_type: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get chart data by type.
    
    Chart types: transfers, tickets, talents, foundation
    """
    if chart_type == "transfers":
        # Monthly transfer volume (last 6 months)
        data = []
        for i in range(5, -1, -1):
            month_start = (datetime.utcnow().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            result = await db.execute(
                select(func.sum(Transfer.transfer_fee))
                .where(Transfer.created_at >= month_start)
                .where(Transfer.created_at < month_end)
            )
            total = result.scalar() or 0
            
            data.append({
                "month": month_start.strftime("%b %Y"),
                "value": total,
            })
        
        return {"type": "transfers", "data": data}
    
    elif chart_type == "talents":
        # Talents by position
        result = await db.execute(
            select(Talent.primary_position, func.count(Talent.id))
            .group_by(Talent.primary_position)
        )
        data = [{"position": row[0], "count": row[1]} for row in result.all()]
        
        return {"type": "talents_by_position", "data": data}
    
    elif chart_type == "tickets":
        # Tickets by status
        result = await db.execute(
            select(Ticket.status, func.count(Ticket.id))
            .group_by(Ticket.status)
        )
        data = [{"status": row[0], "count": row[1]} for row in result.all()]
        
        return {"type": "tickets_by_status", "data": data}
    
    elif chart_type == "foundation":
        # Foundation growth
        data = []
        running_total = 0
        for i in range(5, -1, -1):
            month_start = (datetime.utcnow().replace(day=1) - timedelta(days=i*30)).replace(day=1)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            
            result = await db.execute(
                select(func.sum(FoundationDonation.amount))
                .where(FoundationDonation.created_at >= month_start)
                .where(FoundationDonation.created_at < month_end)
            )
            monthly = result.scalar() or 0
            running_total += monthly
            
            data.append({
                "month": month_start.strftime("%b %Y"),
                "monthly": monthly,
                "cumulative": running_total,
            })
        
        return {"type": "foundation_growth", "data": data}
    
    return {"type": chart_type, "data": [], "error": "Unknown chart type"}


# =============================================================================
# RECENT ACTIVITY
# =============================================================================

@router.get("/activity")
async def get_recent_activity(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
) -> Any:
    """
    Get recent activity feed.
    """
    activities = []
    
    # Recent transfers
    result = await db.execute(
        select(Transfer)
        .order_by(Transfer.created_at.desc())
        .limit(5)
    )
    for transfer in result.scalars().all():
        activities.append({
            "type": "transfer",
            "icon": "arrow-right-left",
            "title": f"New Transfer: {transfer.player_name}",
            "subtitle": f"{transfer.from_club} → {transfer.to_club}",
            "value": transfer.transfer_fee,
            "timestamp": transfer.created_at.isoformat(),
        })
    
    # Recent talents
    result = await db.execute(
        select(Talent)
        .order_by(Talent.created_at.desc())
        .limit(5)
    )
    for talent in result.scalars().all():
        activities.append({
            "type": "talent",
            "icon": "user-plus",
            "title": f"New Talent: {talent.first_name} {talent.last_name}",
            "subtitle": f"{talent.primary_position} - {talent.nationality}",
            "timestamp": talent.created_at.isoformat(),
        })
    
    # Sort by timestamp
    activities.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"activities": activities[:limit]}


# =============================================================================
# WK 2030 COUNTDOWN
# =============================================================================

@router.get("/wk-countdown")
async def get_wk_countdown(
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Get WK 2030 countdown data.
    """
    # WK 2030 opening date (estimated: June 2030)
    wk_date = datetime(2030, 6, 13, 0, 0, 0)
    now = datetime.utcnow()
    
    delta = wk_date - now
    
    years = delta.days // 365
    months = (delta.days % 365) // 30
    days = delta.days % 30
    
    return {
        "event": "FIFA World Cup 2030",
        "date": wk_date.isoformat(),
        "countdown": {
            "years": years,
            "months": months,
            "days": days,
            "total_days": delta.days,
        },
        "host_countries": ["Morocco", "Spain", "Portugal"],
    }
