# ============================================================================
# ProInvestiX Enterprise API - Wallets Endpoints
# Diaspora Wallet
# ============================================================================

from datetime import datetime
from typing import Any, Optional
import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Wallet, WalletTransaction, DiasporaCard, User
from app.core.dependencies import get_current_user
from app.schemas.wallet import (
    WalletCreate,
    WalletResponse,
    WalletDetailResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionListResponse,
    WalletTransferRequest,
    CardResponse,
    CardCreateRequest,
    WalletStats,
)
from app.core.exceptions import NotFoundException, BusinessLogicException

router = APIRouter(prefix="/wallets", tags=["Diaspora Wallet"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_wallet_id() -> str:
    return f"WAL-{uuid.uuid4().hex[:8].upper()}"


def generate_wallet_address() -> str:
    """Generate blockchain-style wallet address."""
    return "0x" + hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:40]


def generate_transaction_id() -> str:
    return f"TXN-{uuid.uuid4().hex[:8].upper()}"


def generate_card_id() -> str:
    return f"CRD-{uuid.uuid4().hex[:8].upper()}"


def generate_blockchain_hash() -> str:
    return "0x" + hashlib.sha256(f"{uuid.uuid4()}{datetime.utcnow()}".encode()).hexdigest()


# =============================================================================
# GET MY WALLET
# =============================================================================

@router.get("/me", response_model=WalletDetailResponse)
async def get_my_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user's wallet. Creates one if doesn't exist."""
    result = await db.execute(
        select(Wallet).where(Wallet.user_id == current_user.id)
    )
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        # Create wallet
        wallet = Wallet(
            wallet_id=generate_wallet_id(),
            wallet_address=generate_wallet_address(),
            user_id=current_user.id,
            balance=0,
            currency="EUR",
            kyc_level=0,
            kyc_verified=False,
            status="Active",
            created_at=datetime.utcnow(),
        )
        db.add(wallet)
        await db.commit()
        await db.refresh(wallet)
    
    return WalletDetailResponse(success=True, data=WalletResponse.model_validate(wallet))


# =============================================================================
# GET WALLET BY ID
# =============================================================================

@router.get("/{wallet_id}", response_model=WalletDetailResponse)
async def get_wallet(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get wallet by ID."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    # Check ownership (unless admin)
    if wallet.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return WalletDetailResponse(success=True, data=WalletResponse.model_validate(wallet))


# =============================================================================
# GET BALANCE
# =============================================================================

@router.get("/{wallet_id}/balance")
async def get_balance(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get wallet balance."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    return {
        "wallet_id": wallet.wallet_id,
        "balance": wallet.balance,
        "currency": wallet.currency,
    }


# =============================================================================
# GET TRANSACTIONS
# =============================================================================

@router.get("/{wallet_id}/transactions", response_model=TransactionListResponse)
async def get_transactions(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    type: Optional[str] = None,
) -> Any:
    """Get wallet transactions."""
    # Verify wallet
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    if wallet.user_id != current_user.id and current_user.role not in ["Admin", "SuperAdmin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    query = select(WalletTransaction).where(WalletTransaction.wallet_id == wallet_id)
    
    if type:
        query = query.where(WalletTransaction.type == type)
    
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    query = query.order_by(WalletTransaction.created_at.desc())
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return TransactionListResponse(
        success=True,
        data=[TransactionResponse.model_validate(t) for t in transactions],
        meta={"total": total, "page": page, "per_page": per_page}
    )


# =============================================================================
# DEPOSIT
# =============================================================================

@router.post("/{wallet_id}/deposit", response_model=TransactionResponse)
async def deposit(
    wallet_id: int,
    request: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Deposit funds into wallet."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create transaction
    transaction = WalletTransaction(
        transaction_id=generate_transaction_id(),
        wallet_id=wallet_id,
        type="Deposit",
        direction="In",
        amount=request.amount,
        currency=wallet.currency,
        reference=request.reference,
        description=request.description or "Deposit",
        blockchain_hash=generate_blockchain_hash(),
        status="Completed",
        created_at=datetime.utcnow(),
    )
    
    # Update balance
    wallet.balance += request.amount
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse.model_validate(transaction)


# =============================================================================
# WITHDRAW
# =============================================================================

@router.post("/{wallet_id}/withdraw", response_model=TransactionResponse)
async def withdraw(
    wallet_id: int,
    request: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Withdraw funds from wallet."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if wallet.balance < request.amount:
        raise BusinessLogicException(
            detail=f"Insufficient balance. Available: {wallet.balance}",
            error_code="INSUFFICIENT_BALANCE"
        )
    
    transaction = WalletTransaction(
        transaction_id=generate_transaction_id(),
        wallet_id=wallet_id,
        type="Withdraw",
        direction="Out",
        amount=request.amount,
        currency=wallet.currency,
        reference=request.reference,
        description=request.description or "Withdrawal",
        blockchain_hash=generate_blockchain_hash(),
        status="Completed",
        created_at=datetime.utcnow(),
    )
    
    wallet.balance -= request.amount
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return TransactionResponse.model_validate(transaction)


# =============================================================================
# TRANSFER
# =============================================================================

@router.post("/{wallet_id}/transfer", response_model=TransactionResponse)
async def transfer(
    wallet_id: int,
    request: WalletTransferRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Transfer funds to another wallet."""
    # Get sender wallet
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    sender_wallet = result.scalar_one_or_none()
    
    if sender_wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    if sender_wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if sender_wallet.balance < request.amount:
        raise BusinessLogicException(
            detail=f"Insufficient balance. Available: {sender_wallet.balance}",
            error_code="INSUFFICIENT_BALANCE"
        )
    
    # Get recipient wallet
    result = await db.execute(
        select(Wallet).where(Wallet.wallet_address == request.recipient_wallet_address)
    )
    recipient_wallet = result.scalar_one_or_none()
    
    if recipient_wallet is None:
        raise NotFoundException(resource="Recipient wallet", resource_id=request.recipient_wallet_address)
    
    # Create outgoing transaction
    out_transaction = WalletTransaction(
        transaction_id=generate_transaction_id(),
        wallet_id=wallet_id,
        type="Transfer",
        direction="Out",
        amount=request.amount,
        currency=sender_wallet.currency,
        recipient_wallet=request.recipient_wallet_address,
        description=request.description or "Transfer",
        blockchain_hash=generate_blockchain_hash(),
        status="Completed",
        created_at=datetime.utcnow(),
    )
    
    # Create incoming transaction
    in_transaction = WalletTransaction(
        transaction_id=generate_transaction_id(),
        wallet_id=recipient_wallet.id,
        type="Transfer",
        direction="In",
        amount=request.amount,
        currency=sender_wallet.currency,
        description=f"Transfer from {sender_wallet.wallet_address[:10]}...",
        blockchain_hash=out_transaction.blockchain_hash,
        status="Completed",
        created_at=datetime.utcnow(),
    )
    
    # Update balances
    sender_wallet.balance -= request.amount
    recipient_wallet.balance += request.amount
    
    db.add(out_transaction)
    db.add(in_transaction)
    await db.commit()
    await db.refresh(out_transaction)
    
    return TransactionResponse.model_validate(out_transaction)


# =============================================================================
# CARDS
# =============================================================================

@router.get("/{wallet_id}/cards")
async def get_cards(
    wallet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get wallet cards."""
    result = await db.execute(
        select(DiasporaCard).where(DiasporaCard.wallet_id == wallet_id)
    )
    cards = result.scalars().all()
    
    return {
        "success": True,
        "data": [CardResponse.model_validate(c) for c in cards]
    }


@router.post("/{wallet_id}/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def request_card(
    wallet_id: int,
    request: CardCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Request a new diaspora card."""
    result = await db.execute(select(Wallet).where(Wallet.id == wallet_id))
    wallet = result.scalar_one_or_none()
    
    if wallet is None:
        raise NotFoundException(resource="Wallet", resource_id=wallet_id)
    
    if wallet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Set limits based on card type
    limits = {
        "Standard": (1000, 10000),
        "Gold": (5000, 50000),
        "Platinum": (10000, 100000),
    }
    daily, monthly = limits.get(request.card_type, (1000, 10000))
    
    card = DiasporaCard(
        card_id=generate_card_id(),
        wallet_id=wallet_id,
        user_id=current_user.id,
        card_type=request.card_type,
        card_number_last4=str(uuid.uuid4().int)[:4],
        is_active=True,
        is_blocked=False,
        daily_limit=daily,
        monthly_limit=monthly,
        created_at=datetime.utcnow(),
    )
    
    db.add(card)
    await db.commit()
    await db.refresh(card)
    
    return CardResponse.model_validate(card)


# =============================================================================
# STATISTICS
# =============================================================================

@router.get("/stats/overview", response_model=WalletStats)
async def get_wallet_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get wallet statistics."""
    # Total wallets
    result = await db.execute(select(func.count(Wallet.id)))
    total_wallets = result.scalar() or 0
    
    # Total balance
    result = await db.execute(select(func.sum(Wallet.balance)))
    total_balance = result.scalar() or 0
    
    # Total transactions
    result = await db.execute(select(func.count(WalletTransaction.id)))
    total_transactions = result.scalar() or 0
    
    # Transaction volume
    result = await db.execute(select(func.sum(WalletTransaction.amount)))
    transaction_volume = result.scalar() or 0
    
    # By region
    result = await db.execute(
        select(Wallet.diaspora_region, func.count(Wallet.id))
        .group_by(Wallet.diaspora_region)
    )
    by_region = {row[0] or "Unknown": row[1] for row in result.all()}
    
    # By KYC level
    result = await db.execute(
        select(Wallet.kyc_level, func.count(Wallet.id))
        .group_by(Wallet.kyc_level)
    )
    by_kyc = {f"Level {row[0]}": row[1] for row in result.all()}
    
    return WalletStats(
        total_wallets=total_wallets,
        total_balance=total_balance,
        total_transactions=total_transactions,
        transaction_volume=transaction_volume,
        by_region=by_region,
        by_kyc_level=by_kyc,
    )
