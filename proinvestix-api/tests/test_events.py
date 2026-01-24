# ============================================================================
# ProInvestiX Enterprise API - Event & Ticket Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestEventList:
    """Test event listing."""
    
    @pytest.mark.asyncio
    async def test_list_events_success(self, client: AsyncClient, user_headers: dict):
        """Test listing events."""
        response = await client.get("/api/v1/events", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_list_events_upcoming_only(self, client: AsyncClient, user_headers: dict):
        """Test listing only upcoming events."""
        response = await client.get(
            "/api/v1/events",
            headers=user_headers,
            params={"upcoming_only": True}
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_list_events_by_city(self, client: AsyncClient, user_headers: dict):
        """Test listing events by city."""
        response = await client.get(
            "/api/v1/events",
            headers=user_headers,
            params={"city": "Casablanca"}
        )
        assert response.status_code == 200


class TestEventCreate:
    """Test event creation."""
    
    @pytest.mark.asyncio
    async def test_create_event_success(
        self, client: AsyncClient, admin_headers: dict, sample_event_data: dict
    ):
        """Test creating an event (admin only)."""
        response = await client.post(
            "/api/v1/events",
            headers=admin_headers,
            json=sample_event_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_event_data["name"]
        assert "event_id" in data
        assert data["event_id"].startswith("EVT-")
    
    @pytest.mark.asyncio
    async def test_create_event_regular_user_forbidden(
        self, client: AsyncClient, user_headers: dict, sample_event_data: dict
    ):
        """Test that regular users cannot create events."""
        response = await client.post(
            "/api/v1/events",
            headers=user_headers,
            json=sample_event_data
        )
        assert response.status_code == 403


class TestEventStats:
    """Test event statistics."""
    
    @pytest.mark.asyncio
    async def test_get_event_stats(self, client: AsyncClient, user_headers: dict):
        """Test getting event statistics."""
        response = await client.get("/api/v1/events/stats/overview", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_events" in data


class TestTicketMint:
    """Test ticket minting."""
    
    @pytest.mark.asyncio
    async def test_mint_ticket_event_not_found(self, client: AsyncClient, user_headers: dict):
        """Test minting ticket for non-existent event."""
        response = await client.post(
            "/api/v1/events/99999/tickets/mint",
            headers=user_headers,
            json={
                "ticket_type": "Standard",
                "quantity": 1,
            }
        )
        assert response.status_code == 404


class TestTicketVerify:
    """Test ticket verification."""
    
    @pytest.mark.asyncio
    async def test_verify_ticket_not_found(self, client: AsyncClient):
        """Test verifying non-existent ticket."""
        response = await client.get("/api/v1/tickets/invalid-hash/verify")
        assert response.status_code == 404


class TestLoyalty:
    """Test loyalty system."""
    
    @pytest.mark.asyncio
    async def test_get_my_loyalty(self, client: AsyncClient, user_headers: dict):
        """Test getting user loyalty info."""
        response = await client.get("/api/v1/tickets/loyalty/me", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "points" in data
        assert "tier" in data


class TestMyTickets:
    """Test user tickets."""
    
    @pytest.mark.asyncio
    async def test_get_my_tickets(self, client: AsyncClient, user_headers: dict):
        """Test getting user's tickets."""
        response = await client.get("/api/v1/tickets/my/tickets", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
