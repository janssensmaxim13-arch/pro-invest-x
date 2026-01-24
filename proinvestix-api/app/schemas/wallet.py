# ============================================================================
# ProInvestiX Enterprise API - Wallet Schemas
# Diaspora Wallet
# ============================================================================

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# =============================================================================
# WALLET SCHEMAS
# =============================================================================

class WalletBase(BaseModel):
    """Base wallet fields."""
    country_of_residence: Optional[str] = None
    diaspora_region: Optional[str] = None


class WalletCreate(WalletBase):
    """Create wallet request."""
    pass


class WalletResponse(WalletBase):
    """Wallet response."""
    id: int
    wallet_id: str
    wallet_address: str
    user_id: int
    balance: float
    currency: str
    kyc_level: int
    kyc_verified: bool
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class WalletDetailResponse(BaseModel):
    """Single wallet response."""
    success: bool = True
    data: WalletResponse


# =============================================================================
# TRANSACTION SCHEMAS
# =============================================================================

class TransactionCreate(BaseModel):
    """Create transaction request."""
    type: str = Field(..., description="Deposit, Withdraw, Transfer, Payment")
    amount: float = Field(..., gt=0)
    recipient_wallet: Optional[str] = None
    recipient_name: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    """Transaction response."""
    id: int
    transaction_id: str
    wallet_id: int
    type: str
    direction: str
    amount: float
    currency: str
    recipient_wallet: Optional[str] = None
    recipient_name: Optional[str] = None
    reference: Optional[str] = None
    description: Optional[str] = None
    blockchain_hash: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Transaction list response."""
    success: bool = True
    data: List[TransactionResponse]
    meta: dict


# =============================================================================
# TRANSFER SCHEMAS
# =============================================================================

class WalletTransferRequest(BaseModel):
    """Transfer between wallets."""
    recipient_wallet_address: str
    amount: float = Field(..., gt=0)
    description: Optional[str] = None


# =============================================================================
# CARD SCHEMAS
# =============================================================================

class CardResponse(BaseModel):
    """Diaspora card response."""
    id: int
    card_id: str
    wallet_id: int
    card_type: str
    card_number_last4: Optional[str] = None
    expiry_date: Optional[str] = None
    is_active: bool
    is_blocked: bool
    daily_limit: float
    monthly_limit: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class CardCreateRequest(BaseModel):
    """Request new card."""
    card_type: str = Field(default="Standard", description="Standard, Gold, Platinum")


# =============================================================================
# STATS
# =============================================================================

class WalletStats(BaseModel):
    """Wallet statistics."""
    total_wallets: int
    total_balance: float
    total_transactions: int
    transaction_volume: float
    by_region: dict
    by_kyc_level: dict
