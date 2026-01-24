# ============================================================================
# ProInvestiX Enterprise API - Foundation Bank Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestFoundationStats:
    """Test foundation statistics."""
    
    @pytest.mark.asyncio
    async def test_get_foundation_stats(self, client: AsyncClient, user_headers: dict):
        """Test getting foundation stats."""
        response = await client.get("/api/v1/foundation/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_donations" in data
        assert "total_contributions" in data


class TestFoundationDonations:
    """Test foundation donations."""
    
    @pytest.mark.asyncio
    async def test_list_donations(self, client: AsyncClient, user_headers: dict):
        """Test listing donations."""
        response = await client.get("/api/v1/foundation/donations", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_create_donation(self, client: AsyncClient, user_headers: dict):
        """Test creating a donation."""
        response = await client.post(
            "/api/v1/foundation/donations",
            headers=user_headers,
            json={
                "amount": 50.0,
                "currency": "EUR",
                "donation_type": "OneTime",
                "is_anonymous": False,
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert "receipt_number" in data
        assert data["receipt_number"].startswith("RCP-")
    
    @pytest.mark.asyncio
    async def test_create_anonymous_donation(self, client: AsyncClient, user_headers: dict):
        """Test creating anonymous donation."""
        response = await client.post(
            "/api/v1/foundation/donations",
            headers=user_headers,
            json={
                "amount": 100.0,
                "currency": "EUR",
                "donation_type": "Sadaka",
                "is_anonymous": True,
            }
        )
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_donation_invalid_amount(self, client: AsyncClient, user_headers: dict):
        """Test donation with invalid amount."""
        response = await client.post(
            "/api/v1/foundation/donations",
            headers=user_headers,
            json={
                "amount": -10.0,
                "currency": "EUR",
                "donation_type": "OneTime",
            }
        )
        assert response.status_code == 422


class TestFoundationContributions:
    """Test foundation contributions."""
    
    @pytest.mark.asyncio
    async def test_list_contributions(self, client: AsyncClient, user_headers: dict):
        """Test listing auto-contributions."""
        response = await client.get("/api/v1/foundation/contributions", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestFoundationProjects:
    """Test foundation projects."""
    
    @pytest.mark.asyncio
    async def test_list_projects(self, client: AsyncClient, user_headers: dict):
        """Test listing foundation projects."""
        response = await client.get("/api/v1/foundation/projects", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestMyDonations:
    """Test user's donations."""
    
    @pytest.mark.asyncio
    async def test_get_my_donations(self, client: AsyncClient, user_headers: dict):
        """Test getting user's donations."""
        response = await client.get("/api/v1/foundation/my-donations", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
