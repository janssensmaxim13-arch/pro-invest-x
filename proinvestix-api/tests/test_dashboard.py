# ============================================================================
# ProInvestiX Enterprise API - Dashboard Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestDashboardStats:
    """Test dashboard statistics."""
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, client: AsyncClient, user_headers: dict):
        """Test getting dashboard stats."""
        response = await client.get("/api/v1/dashboard/stats", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_talents" in data
        assert "total_transfers" in data
        assert "total_events" in data
    
    @pytest.mark.asyncio
    async def test_get_stats_no_auth(self, client: AsyncClient):
        """Test getting stats without auth."""
        response = await client.get("/api/v1/dashboard/stats")
        assert response.status_code == 401


class TestDashboardKPIs:
    """Test dashboard KPIs."""
    
    @pytest.mark.asyncio
    async def test_get_kpis_success(self, client: AsyncClient, user_headers: dict):
        """Test getting KPIs."""
        response = await client.get("/api/v1/dashboard/kpis", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Each KPI should have label, value, change
        for kpi in data:
            assert "label" in kpi
            assert "value" in kpi


class TestDashboardCharts:
    """Test dashboard charts."""
    
    @pytest.mark.asyncio
    async def test_get_transfers_chart(self, client: AsyncClient, user_headers: dict):
        """Test getting transfers chart data."""
        response = await client.get("/api/v1/dashboard/charts/transfers", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_get_tickets_chart(self, client: AsyncClient, user_headers: dict):
        """Test getting tickets chart data."""
        response = await client.get("/api/v1/dashboard/charts/tickets", headers=user_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_talents_chart(self, client: AsyncClient, user_headers: dict):
        """Test getting talents chart data."""
        response = await client.get("/api/v1/dashboard/charts/talents", headers=user_headers)
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_invalid_chart(self, client: AsyncClient, user_headers: dict):
        """Test getting invalid chart type."""
        response = await client.get("/api/v1/dashboard/charts/invalid", headers=user_headers)
        assert response.status_code == 400


class TestDashboardActivity:
    """Test dashboard activity feed."""
    
    @pytest.mark.asyncio
    async def test_get_activity_success(self, client: AsyncClient, user_headers: dict):
        """Test getting activity feed."""
        response = await client.get("/api/v1/dashboard/activity", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_activity_with_limit(self, client: AsyncClient, user_headers: dict):
        """Test getting activity with limit."""
        response = await client.get(
            "/api/v1/dashboard/activity",
            headers=user_headers,
            params={"limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5


class TestDashboardWKCountdown:
    """Test WK 2030 countdown."""
    
    @pytest.mark.asyncio
    async def test_get_wk_countdown(self, client: AsyncClient, user_headers: dict):
        """Test getting WK 2030 countdown."""
        response = await client.get("/api/v1/dashboard/wk-countdown", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "event" in data
        assert "days_remaining" in data
        assert "target_date" in data
