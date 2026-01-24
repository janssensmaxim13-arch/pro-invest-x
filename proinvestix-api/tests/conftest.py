# ============================================================================
# ProInvestiX Enterprise API - Test Configuration & Fixtures
# ============================================================================

import asyncio
from datetime import datetime, timedelta
from typing import AsyncGenerator, Generator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import get_db, Base
from app.db.models import User
from app.core.security import get_password_hash, create_access_token


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

# Test database URL (SQLite in-memory)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Test session factory
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """Override database dependency for tests."""
    async with TestSessionLocal() as session:
        yield session


# =============================================================================
# CLIENT FIXTURES
# =============================================================================

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a regular test user."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        role="User",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin test user."""
    user = User(
        username="adminuser",
        email="admin@example.com",
        password_hash=get_password_hash("adminpassword123"),
        role="Admin",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def superadmin_user(db_session: AsyncSession) -> User:
    """Create a superadmin test user."""
    user = User(
        username="superadmin",
        email="superadmin@example.com",
        password_hash=get_password_hash("superadminpass123"),
        role="SuperAdmin",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# =============================================================================
# TOKEN FIXTURES
# =============================================================================

@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate access token for test user."""
    return create_access_token(data={"sub": test_user.username, "user_id": test_user.id})


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate access token for admin user."""
    return create_access_token(data={"sub": admin_user.username, "user_id": admin_user.id})


@pytest.fixture
def superadmin_token(superadmin_user: User) -> str:
    """Generate access token for superadmin user."""
    return create_access_token(data={"sub": superadmin_user.username, "user_id": superadmin_user.id})


# =============================================================================
# AUTH HEADERS
# =============================================================================

@pytest.fixture
def user_headers(user_token: str) -> dict:
    """Auth headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Auth headers for admin user."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def superadmin_headers(superadmin_token: str) -> dict:
    """Auth headers for superadmin user."""
    return {"Authorization": f"Bearer {superadmin_token}"}


# =============================================================================
# HELPER FIXTURES
# =============================================================================

@pytest.fixture
def sample_talent_data() -> dict:
    """Sample talent data for testing."""
    return {
        "first_name": "Test",
        "last_name": "Talent",
        "date_of_birth": "2005-01-15",
        "nationality": "Moroccan",
        "position": "Midfielder",
        "current_club": "Test FC",
        "is_diaspora": True,
        "diaspora_country": "Netherlands",
    }


@pytest.fixture
def sample_event_data() -> dict:
    """Sample event data for testing."""
    return {
        "name": "Test Match",
        "event_type": "Match",
        "venue": "Test Stadium",
        "city": "Casablanca",
        "country": "Morocco",
        "event_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "total_tickets": 1000,
        "ticket_price": 50.0,
    }


@pytest.fixture
def sample_academy_data() -> dict:
    """Sample academy data for testing."""
    return {
        "name": "Test Academy",
        "city": "Rabat",
        "region": "Rabat-Salé-Kénitra",
        "country": "Morocco",
        "license_level": "A",
        "capacity": 100,
    }
