# ============================================================================
# ProInvestiX Enterprise API - Academy Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestAcademyList:
    """Test academy listing."""
    
    @pytest.mark.asyncio
    async def test_list_academies_success(self, client: AsyncClient, user_headers: dict):
        """Test listing academies."""
        response = await client.get("/api/v1/academies", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
    
    @pytest.mark.asyncio
    async def test_list_academies_with_filters(self, client: AsyncClient, user_headers: dict):
        """Test listing academies with filters."""
        response = await client.get(
            "/api/v1/academies",
            headers=user_headers,
            params={
                "region": "Casablanca-Settat",
                "license_level": "A",
            }
        )
        assert response.status_code == 200


class TestAcademyCreate:
    """Test academy creation."""
    
    @pytest.mark.asyncio
    async def test_create_academy_admin_only(
        self, client: AsyncClient, admin_headers: dict, sample_academy_data: dict
    ):
        """Test creating academy (admin only)."""
        response = await client.post(
            "/api/v1/academies",
            headers=admin_headers,
            json=sample_academy_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_academy_data["name"]
        assert "academy_id" in data
    
    @pytest.mark.asyncio
    async def test_create_academy_regular_user_forbidden(
        self, client: AsyncClient, user_headers: dict, sample_academy_data: dict
    ):
        """Test that regular users cannot create academies."""
        response = await client.post(
            "/api/v1/academies",
            headers=user_headers,
            json=sample_academy_data
        )
        assert response.status_code == 403


class TestAcademyTeams:
    """Test academy teams."""
    
    @pytest.mark.asyncio
    async def test_get_academy_teams_not_found(self, client: AsyncClient, user_headers: dict):
        """Test getting teams for non-existent academy."""
        response = await client.get("/api/v1/academies/99999/teams", headers=user_headers)
        # Returns empty list or 404
        assert response.status_code in [200, 404]


class TestAcademyStaff:
    """Test academy staff."""
    
    @pytest.mark.asyncio
    async def test_get_academy_staff_not_found(self, client: AsyncClient, user_headers: dict):
        """Test getting staff for non-existent academy."""
        response = await client.get("/api/v1/academies/99999/staff", headers=user_headers)
        assert response.status_code in [200, 404]


class TestAcademyStats:
    """Test academy statistics."""
    
    @pytest.mark.asyncio
    async def test_get_academy_stats(self, client: AsyncClient, user_headers: dict):
        """Test getting academy statistics."""
        response = await client.get("/api/v1/academies/stats/overview", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_academies" in data
        assert "total_talents" in data
