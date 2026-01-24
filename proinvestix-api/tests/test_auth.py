# ============================================================================
# ProInvestiX Enterprise API - Auth Tests
# ============================================================================

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class TestAuthRegister:
    """Test user registration."""
    
    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient):
        """Test successful registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123",
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User):
        """Test registration with existing email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "anotheruser",
                "email": test_user.email,
                "password": "password123",
            }
        )
        assert response.status_code == 409
    
    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        """Test registration with invalid email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "invalid-email",
                "password": "password123",
            }
        )
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        """Test registration with short password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short",
            }
        )
        assert response.status_code == 422


class TestAuthLogin:
    """Test user login."""
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "testpassword123",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, client: AsyncClient, test_user: User):
        """Test login with wrong password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "wrongpassword",
            }
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123",
            }
        )
        assert response.status_code == 401


class TestAuthMe:
    """Test get current user."""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self, client: AsyncClient, user_headers: dict, test_user: User):
        """Test get current user info."""
        response = await client.get("/api/v1/auth/me", headers=user_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
    
    @pytest.mark.asyncio
    async def test_get_me_no_token(self, client: AsyncClient):
        """Test get me without token."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_get_me_invalid_token(self, client: AsyncClient):
        """Test get me with invalid token."""
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestAuthRefresh:
    """Test token refresh."""
    
    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user: User):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user.username,
                "password": "testpassword123",
            }
        )
        refresh_token = login_response.json()["refresh_token"]
        
        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestAuthChangePassword:
    """Test password change."""
    
    @pytest.mark.asyncio
    async def test_change_password_success(self, client: AsyncClient, user_headers: dict):
        """Test successful password change."""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "testpassword123",
                "new_password": "newpassword456",
            }
        )
        assert response.status_code == 200
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(self, client: AsyncClient, user_headers: dict):
        """Test password change with wrong current password."""
        response = await client.post(
            "/api/v1/auth/change-password",
            headers=user_headers,
            json={
                "current_password": "wrongpassword",
                "new_password": "newpassword456",
            }
        )
        assert response.status_code == 400
