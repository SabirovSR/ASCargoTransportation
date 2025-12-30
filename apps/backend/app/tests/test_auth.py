import pytest
from httpx import AsyncClient

from app.models.user import User
from .conftest import auth_header


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, admin_user: User):
    """Test successful login."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "admin123"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "admin@test.com"
    assert data["user"]["role"] == "admin"


@pytest.mark.asyncio
async def test_login_invalid_email(client: AsyncClient):
    """Test login with invalid email."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "nonexistent@test.com", "password": "password"},
    )
    
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient, admin_user: User):
    """Test login with invalid password."""
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "wrongpassword"},
    )
    
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient, admin_user: User, admin_token: str):
    """Test get current user."""
    response = await client.get(
        "/api/auth/me",
        headers=auth_header(admin_token),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """Test get current user without token."""
    response = await client.get("/api/auth/me")
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(client: AsyncClient):
    """Test get current user with invalid token."""
    response = await client.get(
        "/api/auth/me",
        headers=auth_header("invalid_token"),
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, admin_user: User, admin_token: str):
    """Test change password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_header(admin_token),
        json={
            "current_password": "admin123",
            "new_password": "newpassword123",
        },
    )
    
    assert response.status_code == 200
    
    # Try to login with new password
    response = await client.post(
        "/api/auth/login",
        json={"email": "admin@test.com", "password": "newpassword123"},
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_current(client: AsyncClient, admin_user: User, admin_token: str):
    """Test change password with wrong current password."""
    response = await client.post(
        "/api/auth/change-password",
        headers=auth_header(admin_token),
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword123",
        },
    )
    
    assert response.status_code == 401
