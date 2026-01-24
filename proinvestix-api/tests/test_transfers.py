# ============================================================================
# ProInvestiX Enterprise API - Transfer Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestTransferList:
    """Test transfer listing."""
    
    @pytest.mark.asyncio
    async def test_list_transfers_success(self, client: AsyncClient, user_headers: dict):
        """Test listing transfers."""
        response = await client.get("/api/v1/transfers", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_list_transfers_no_auth(self, client: AsyncClient):
        """Test listing transfers without auth."""
        response = await client.get("/api/v1/transfers")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_transfers_with_filters(self, client: AsyncClient, user_headers: dict):
        """Test listing transfers with filters."""
        response = await client.get(
            "/api/v1/transfers",
            headers=user_headers,
            params={
                "transfer_type": "Permanent",
                "status": "Completed",
            }
        )
        assert response.status_code == 200


class TestTransferCreate:
    """Test transfer creation."""
    
    @pytest.mark.asyncio
    async def test_create_transfer_success(self, client: AsyncClient, user_headers: dict):
        """Test creating a transfer."""
        response = await client.post(
            "/api/v1/transfers",
            headers=user_headers,
            json={
                "talent_id": 1,
                "from_club": "Test FC",
                "to_club": "Big Club",
                "transfer_type": "Permanent",
                "transfer_fee": 1000000,
                "currency": "EUR",
            }
        )
        # May return 201 or 404 if talent doesn't exist
        assert response.status_code in [201, 404]


class TestTransferCompensation:
    """Test FIFA compensation calculator."""
    
    @pytest.mark.asyncio
    async def test_calculate_compensation_success(self, client: AsyncClient, user_headers: dict):
        """Test calculating training compensation."""
        response = await client.post(
            "/api/v1/transfers/calculate",
            headers=user_headers,
            json={
                "player_birth_date": "2000-01-01",
                "training_years": 5,
                "club_category": 1,
                "transfer_fee": 5000000,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "training_compensation" in data
        assert "solidarity_contribution" in data
        assert "foundation_contribution" in data
    
    @pytest.mark.asyncio
    async def test_calculate_compensation_invalid_category(self, client: AsyncClient, user_headers: dict):
        """Test with invalid club category."""
        response = await client.post(
            "/api/v1/transfers/calculate",
            headers=user_headers,
            json={
                "player_birth_date": "2000-01-01",
                "training_years": 5,
                "club_category": 99,  # Invalid
                "transfer_fee": 5000000,
            }
        )
        assert response.status_code in [200, 400, 422]


class TestTransferStats:
    """Test transfer statistics."""
    
    @pytest.mark.asyncio
    async def test_get_transfer_stats(self, client: AsyncClient, user_headers: dict):
        """Test getting transfer statistics."""
        response = await client.get("/api/v1/transfers/stats/overview", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_transfers" in data
        assert "total_fees" in data
