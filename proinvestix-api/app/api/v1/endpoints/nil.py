# ============================================================================
# ProInvestiX Enterprise API - NIL Endpoints
# News Intelligence Lab - Fact Checking & Misinformation Detection
# ============================================================================

from datetime import datetime
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import NILSignal, NILEvidence, NILFactCard, User
from app.core.dependencies import get_current_user, require_roles
from app.schemas.additional import (
    NILSignalCreate, NILSignalResponse,
    FactCardCreate, FactCardResponse,
)
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/nil", tags=["NIL - News Intelligence"])


# =============================================================================
# HELPERS
# =============================================================================

def generate_signal_id() -> str:
    return f"SIG-{uuid.uuid4().hex[:8].upper()}"

def generate_card_id() -> str:
    return f"FCT-{uuid.uuid4().hex[:8].upper()}"


# =============================================================================
# SIGNALS
# =============================================================================

@router.get("/signals", response_model=List[NILSignalResponse])
async def list_signals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    signal_type: Optional[str] = None,
    status_filter: Optional[str] = None,
    severity: Optional[str] = None,
) -> Any:
    """List NIL signals."""
    query = select(NILSignal)
    
    if signal_type:
        query = query.where(NILSignal.signal_type == signal_type)
    if status_filter:
        query = query.where(NILSignal.status == status_filter)
    if severity:
        query = query.where(NILSignal.severity == severity)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(NILSignal.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    signals = result.scalars().all()
    
    return [NILSignalResponse.model_validate(s) for s in signals]


@router.get("/signals/{signal_id}", response_model=NILSignalResponse)
async def get_signal(
    signal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get signal by ID."""
    result = await db.execute(select(NILSignal).where(NILSignal.id == signal_id))
    signal = result.scalar_one_or_none()
    
    if signal is None:
        raise NotFoundException(resource="Signal", resource_id=signal_id)
    
    return NILSignalResponse.model_validate(signal)


@router.post("/signals", response_model=NILSignalResponse, status_code=status.HTTP_201_CREATED)
async def create_signal(
    request: NILSignalCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Report misinformation signal."""
    signal = NILSignal(
        signal_id=generate_signal_id(),
        signal_type=request.signal_type,
        source_url=request.source_url,
        source_name=request.source_name,
        headline=request.headline,
        content_summary=request.content_summary,
        target_entity=request.target_entity,
        severity=request.severity,
        status="Pending",
        created_at=datetime.utcnow(),
    )
    
    db.add(signal)
    await db.commit()
    await db.refresh(signal)
    
    return NILSignalResponse.model_validate(signal)


@router.put("/signals/{signal_id}", response_model=NILSignalResponse)
async def update_signal(
    signal_id: int,
    new_status: Optional[str] = None,
    verification_status: Optional[str] = None,
    fact_check_result: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Update signal."""
    result = await db.execute(select(NILSignal).where(NILSignal.id == signal_id))
    signal = result.scalar_one_or_none()
    
    if signal is None:
        raise NotFoundException(resource="Signal", resource_id=signal_id)
    
    if new_status:
        signal.status = new_status
    if verification_status:
        signal.verification_status = verification_status
    if fact_check_result:
        signal.fact_check_result = fact_check_result
        signal.verified_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(signal)
    
    return NILSignalResponse.model_validate(signal)


# =============================================================================
# FACT CARDS
# =============================================================================

@router.get("/factcards", response_model=List[FactCardResponse])
async def list_factcards(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    verdict: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """List fact cards."""
    query = select(NILFactCard)
    
    if verdict:
        query = query.where(NILFactCard.verdict == verdict)
    
    query = query.order_by(NILFactCard.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    cards = result.scalars().all()
    
    return [FactCardResponse.model_validate(c) for c in cards]


@router.get("/factcards/{card_id}", response_model=FactCardResponse)
async def get_factcard(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get fact card by ID."""
    result = await db.execute(select(NILFactCard).where(NILFactCard.id == card_id))
    card = result.scalar_one_or_none()
    
    if card is None:
        raise NotFoundException(resource="Fact Card", resource_id=card_id)
    
    # Increment views
    card.views += 1
    await db.commit()
    
    return FactCardResponse.model_validate(card)


@router.post("/factcards", response_model=FactCardResponse, status_code=status.HTTP_201_CREATED)
async def create_factcard(
    request: FactCardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Create fact card."""
    card = NILFactCard(
        card_id=generate_card_id(),
        signal_id=request.signal_id,
        title=request.title,
        claim=request.claim,
        verdict=request.verdict,
        explanation=request.explanation,
        sources=request.sources,
        views=0,
        shares=0,
        created_at=datetime.utcnow(),
        published_at=datetime.utcnow(),
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    # Update signal if linked
    if request.signal_id:
        result = await db.execute(select(NILSignal).where(NILSignal.id == request.signal_id))
        signal = result.scalar_one_or_none()
        if signal:
            signal.status = "FactChecked"
            signal.fact_check_result = request.verdict
            await db.commit()
    
    return FactCardResponse.model_validate(card)


@router.post("/factcards/{card_id}/share")
async def share_factcard(
    card_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Track fact card share."""
    result = await db.execute(select(NILFactCard).where(NILFactCard.id == card_id))
    card = result.scalar_one_or_none()
    
    if card is None:
        raise NotFoundException(resource="Fact Card", resource_id=card_id)
    
    card.shares += 1
    await db.commit()
    
    return {"success": True, "shares": card.shares}


# =============================================================================
# SEARCH
# =============================================================================

@router.get("/search")
async def search_claims(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Search fact-checked claims."""
    search_query = select(NILFactCard).where(
        NILFactCard.claim.ilike(f"%{query}%") |
        NILFactCard.title.ilike(f"%{query}%")
    ).limit(20)
    
    result = await db.execute(search_query)
    cards = result.scalars().all()
    
    return {
        "query": query,
        "results": [FactCardResponse.model_validate(c) for c in cards],
        "total": len(cards),
    }


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats")
async def get_nil_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles("Admin", "SuperAdmin")),
) -> Any:
    """Get NIL statistics."""
    # Signals
    result = await db.execute(select(func.count(NILSignal.id)))
    total_signals = result.scalar() or 0
    
    result = await db.execute(
        select(NILSignal.signal_type, func.count(NILSignal.id))
        .group_by(NILSignal.signal_type)
    )
    by_type = {row[0]: row[1] for row in result.all()}
    
    # Fact cards
    result = await db.execute(select(func.count(NILFactCard.id)))
    total_cards = result.scalar() or 0
    
    result = await db.execute(
        select(NILFactCard.verdict, func.count(NILFactCard.id))
        .group_by(NILFactCard.verdict)
    )
    by_verdict = {row[0]: row[1] for row in result.all()}
    
    # Engagement
    result = await db.execute(select(func.sum(NILFactCard.views)))
    total_views = result.scalar() or 0
    
    result = await db.execute(select(func.sum(NILFactCard.shares)))
    total_shares = result.scalar() or 0
    
    return {
        "signals": {"total": total_signals, "by_type": by_type},
        "factcards": {"total": total_cards, "by_verdict": by_verdict},
        "engagement": {"views": total_views, "shares": total_shares},
    }
