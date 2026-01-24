# ============================================================================
# ProInvestiX Enterprise API - Wallet Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestWalletGet:
    """Test wallet retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_my_wallet_creates_if_not_exists(self, client: AsyncClient, user_headers: dict):
        """Test getting wallet auto-creates if not exists."""
        response = await client.get("/api/v1/wallets/me", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "wallet_address" in data
        assert data["wallet_address"].startswith("0x")
        assert "balance" in data
    
    @pytest.mark.asyncio
    async def test_get_wallet_no_auth(self, client: AsyncClient):
        """Test getting wallet without auth."""
        response = await client.get("/api/v1/wallets/me")
        assert response.status_code == 401


class TestWalletDeposit:
    """Test wallet deposits."""
    
    @pytest.mark.asyncio
    async def test_deposit_success(self, client: AsyncClient, user_headers: dict):
        """Test successful deposit."""
        # First get/create wallet
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/deposit",
            headers=user_headers,
            json={
                "amount": 100.0,
                "currency": "EUR",
                "payment_method": "Card",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
    
    @pytest.mark.asyncio
    async def test_deposit_negative_amount(self, client: AsyncClient, user_headers: dict):
        """Test deposit with negative amount."""
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/deposit",
            headers=user_headers,
            json={
                "amount": -100.0,
                "currency": "EUR",
            }
        )
        assert response.status_code == 422


class TestWalletWithdraw:
    """Test wallet withdrawals."""
    
    @pytest.mark.asyncio
    async def test_withdraw_insufficient_funds(self, client: AsyncClient, user_headers: dict):
        """Test withdrawal with insufficient funds."""
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/withdraw",
            headers=user_headers,
            json={
                "amount": 1000000.0,  # Large amount
                "currency": "EUR",
            }
        )
        assert response.status_code == 400


class TestWalletTransfer:
    """Test wallet transfers."""
    
    @pytest.mark.asyncio
    async def test_transfer_to_nonexistent_wallet(self, client: AsyncClient, user_headers: dict):
        """Test transfer to non-existent wallet."""
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/transfer",
            headers=user_headers,
            json={
                "to_wallet_id": 99999,
                "amount": 10.0,
            }
        )
        assert response.status_code in [400, 404]


class TestWalletCards:
    """Test diaspora cards."""
    
    @pytest.mark.asyncio
    async def test_get_cards(self, client: AsyncClient, user_headers: dict):
        """Test getting wallet cards."""
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.get(
            f"/api/v1/wallets/{wallet_id}/cards",
            headers=user_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    @pytest.mark.asyncio
    async def test_create_card(self, client: AsyncClient, user_headers: dict):
        """Test creating diaspora card."""
        wallet_response = await client.get("/api/v1/wallets/me", headers=user_headers)
        wallet_id = wallet_response.json()["id"]
        
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/cards",
            headers=user_headers,
            json={
                "card_type": "Standard",
                "delivery_address": "Test Address 123",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "card_number" in data


class TestWalletStats:
    """Test wallet statistics."""
    
    @pytest.mark.asyncio
    async def test_get_wallet_stats(self, client: AsyncClient, admin_headers: dict):
        """Test getting wallet statistics (admin only)."""
        response = await client.get("/api/v1/wallets/stats/overview", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_wallets" in data
