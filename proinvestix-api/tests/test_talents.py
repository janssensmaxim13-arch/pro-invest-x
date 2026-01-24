# ============================================================================
# ProInvestiX Enterprise API - Talent Tests
# ============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User, Talent


class TestTalentList:
    """Test talent listing."""
    
    @pytest.mark.asyncio
    async def test_list_talents_success(self, client: AsyncClient, user_headers: dict):
        """Test listing talents."""
        response = await client.get("/api/v1/talents", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert isinstance(data["data"], list)
    
    @pytest.mark.asyncio
    async def test_list_talents_no_auth(self, client: AsyncClient):
        """Test listing talents without auth."""
        response = await client.get("/api/v1/talents")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_list_talents_with_pagination(self, client: AsyncClient, user_headers: dict):
        """Test listing talents with pagination."""
        response = await client.get(
            "/api/v1/talents",
            headers=user_headers,
            params={"page": 1, "per_page": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 10
    
    @pytest.mark.asyncio
    async def test_list_talents_with_filters(self, client: AsyncClient, user_headers: dict):
        """Test listing talents with filters."""
        response = await client.get(
            "/api/v1/talents",
            headers=user_headers,
            params={
                "nationality": "Moroccan",
                "position": "Midfielder",
                "is_diaspora": True,
            }
        )
        assert response.status_code == 200


class TestTalentCreate:
    """Test talent creation."""
    
    @pytest.mark.asyncio
    async def test_create_talent_success(
        self, client: AsyncClient, user_headers: dict, sample_talent_data: dict
    ):
        """Test creating a talent."""
        response = await client.post(
            "/api/v1/talents",
            headers=user_headers,
            json=sample_talent_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == sample_talent_data["first_name"]
        assert data["last_name"] == sample_talent_data["last_name"]
        assert "talent_id" in data
        assert data["talent_id"].startswith("TLN-")
    
    @pytest.mark.asyncio
    async def test_create_talent_missing_fields(self, client: AsyncClient, user_headers: dict):
        """Test creating talent with missing required fields."""
        response = await client.post(
            "/api/v1/talents",
            headers=user_headers,
            json={"first_name": "Test"}  # Missing required fields
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_create_talent_no_auth(self, client: AsyncClient, sample_talent_data: dict):
        """Test creating talent without auth."""
        response = await client.post("/api/v1/talents", json=sample_talent_data)
        assert response.status_code == 401


class TestTalentGet:
    """Test getting single talent."""
    
    @pytest.mark.asyncio
    async def test_get_talent_not_found(self, client: AsyncClient, user_headers: dict):
        """Test getting non-existent talent."""
        response = await client.get("/api/v1/talents/99999", headers=user_headers)
        assert response.status_code == 404


class TestTalentUpdate:
    """Test talent updates."""
    
    @pytest.mark.asyncio
    async def test_update_talent_not_found(self, client: AsyncClient, user_headers: dict):
        """Test updating non-existent talent."""
        response = await client.put(
            "/api/v1/talents/99999",
            headers=user_headers,
            json={"first_name": "Updated"}
        )
        assert response.status_code == 404


class TestTalentDelete:
    """Test talent deletion."""
    
    @pytest.mark.asyncio
    async def test_delete_talent_requires_admin(self, client: AsyncClient, user_headers: dict):
        """Test that regular users cannot delete talents."""
        response = await client.delete("/api/v1/talents/1", headers=user_headers)
        # Should be 403 or 404 depending on implementation
        assert response.status_code in [403, 404]


class TestTalentStats:
    """Test talent statistics."""
    
    @pytest.mark.asyncio
    async def test_get_talent_stats(self, client: AsyncClient, user_headers: dict):
        """Test getting talent statistics."""
        response = await client.get("/api/v1/talents/stats/overview", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_talents" in data


class TestTalentFilters:
    """Test talent filter options."""
    
    @pytest.mark.asyncio
    async def test_get_filter_options(self, client: AsyncClient, user_headers: dict):
        """Test getting filter options."""
        response = await client.get("/api/v1/talents/filters/options", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert "nationalities" in data
        assert "positions" in data
