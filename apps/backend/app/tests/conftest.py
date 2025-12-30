import pytest
from typing import AsyncGenerator
from uuid import uuid4

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token

# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="function")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    TestSessionLocal = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    
    async def override_get_db():
        yield test_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(test_session: AsyncSession) -> User:
    """Create admin user for testing."""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        full_name="Test Admin",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True,
        must_change_password=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def dispatcher_user(test_session: AsyncSession) -> User:
    """Create dispatcher user for testing."""
    user = User(
        id=uuid4(),
        email="dispatcher@test.com",
        full_name="Test Dispatcher",
        password_hash=get_password_hash("dispatcher123"),
        role=UserRole.DISPATCHER,
        is_active=True,
        must_change_password=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
async def viewer_user(test_session: AsyncSession) -> User:
    """Create viewer user for testing."""
    user = User(
        id=uuid4(),
        email="viewer@test.com",
        full_name="Test Viewer",
        password_hash=get_password_hash("viewer123"),
        role=UserRole.VIEWER,
        is_active=True,
        must_change_password=False,
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Create admin access token."""
    return create_access_token({"sub": str(admin_user.id)})


@pytest.fixture
def dispatcher_token(dispatcher_user: User) -> str:
    """Create dispatcher access token."""
    return create_access_token({"sub": str(dispatcher_user.id)})


@pytest.fixture
def viewer_token(viewer_user: User) -> str:
    """Create viewer access token."""
    return create_access_token({"sub": str(viewer_user.id)})


def auth_header(token: str) -> dict:
    """Create authorization header."""
    return {"Authorization": f"Bearer {token}"}
