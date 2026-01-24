# ============================================================================
# ProInvestiX Enterprise API - Admin Tests
# ============================================================================

import pytest
from httpx import AsyncClient


class TestAdminUsers:
    """Test admin user management."""
    
    @pytest.mark.asyncio
    async def test_list_users_admin_only(self, client: AsyncClient, admin_headers: dict):
        """Test listing users (admin only)."""
        response = await client.get("/api/v1/admin/users", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_list_users_regular_user_forbidden(self, client: AsyncClient, user_headers: dict):
        """Test that regular users cannot list all users."""
        response = await client.get("/api/v1/admin/users", headers=user_headers)
        assert response.status_code == 403
    
    @pytest.mark.asyncio
    async def test_list_users_with_filters(self, client: AsyncClient, admin_headers: dict):
        """Test listing users with filters."""
        response = await client.get(
            "/api/v1/admin/users",
            headers=admin_headers,
            params={
                "role": "User",
                "is_active": True,
            }
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, client: AsyncClient, admin_headers: dict):
        """Test getting user by ID."""
        # First get list to find a user ID
        list_response = await client.get("/api/v1/admin/users", headers=admin_headers)
        users = list_response.json()
        
        if users:
            user_id = users[0]["id"]
            response = await client.get(f"/api/v1/admin/users/{user_id}", headers=admin_headers)
            assert response.status_code == 200


class TestAdminCreateUser:
    """Test admin user creation."""
    
    @pytest.mark.asyncio
    async def test_create_user_superadmin_only(self, client: AsyncClient, superadmin_headers: dict):
        """Test creating user (superadmin only)."""
        response = await client.post(
            "/api/v1/admin/users",
            headers=superadmin_headers,
            json={
                "username": "newadminuser",
                "email": "newadmin@example.com",
                "password": "adminpassword123",
                "role": "Admin",
            }
        )
        assert response.status_code == 201
    
    @pytest.mark.asyncio
    async def test_create_user_admin_forbidden(self, client: AsyncClient, admin_headers: dict):
        """Test that admins cannot create users."""
        response = await client.post(
            "/api/v1/admin/users",
            headers=admin_headers,
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "password123",
                "role": "User",
            }
        )
        assert response.status_code == 403


class TestAdminSessions:
    """Test admin session management."""
    
    @pytest.mark.asyncio
    async def test_list_sessions_admin_only(self, client: AsyncClient, admin_headers: dict):
        """Test listing sessions (admin only)."""
        response = await client.get("/api/v1/admin/sessions", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_list_sessions_regular_user_forbidden(self, client: AsyncClient, user_headers: dict):
        """Test that regular users cannot list sessions."""
        response = await client.get("/api/v1/admin/sessions", headers=user_headers)
        assert response.status_code == 403


class TestAdminAudit:
    """Test admin audit logs."""
    
    @pytest.mark.asyncio
    async def test_get_audit_logs(self, client: AsyncClient, admin_headers: dict):
        """Test getting audit logs."""
        response = await client.get("/api/v1/admin/audit", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAdminHealth:
    """Test system health check."""
    
    @pytest.mark.asyncio
    async def test_system_health(self, client: AsyncClient, admin_headers: dict):
        """Test system health endpoint."""
        response = await client.get("/api/v1/admin/health", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data


class TestAdminStats:
    """Test admin statistics."""
    
    @pytest.mark.asyncio
    async def test_get_admin_stats(self, client: AsyncClient, admin_headers: dict):
        """Test getting admin statistics."""
        response = await client.get("/api/v1/admin/stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert "sessions" in data
