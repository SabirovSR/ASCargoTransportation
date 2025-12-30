import pytest
from httpx import AsyncClient

from app.models.user import User
from .conftest import auth_header


@pytest.mark.asyncio
async def test_create_user_as_admin(client: AsyncClient, admin_user: User, admin_token: str):
    """Test admin can create user."""
    response = await client.post(
        "/api/users",
        headers=auth_header(admin_token),
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "password123",
            "role": "dispatcher",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "dispatcher"
    assert data["must_change_password"] is True


@pytest.mark.asyncio
async def test_create_user_as_dispatcher_forbidden(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test dispatcher cannot create user."""
    response = await client.post(
        "/api/users",
        headers=auth_header(dispatcher_token),
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "password123",
            "role": "viewer",
        },
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_as_viewer_forbidden(
    client: AsyncClient,
    viewer_user: User,
    viewer_token: str,
):
    """Test viewer cannot create user."""
    response = await client.post(
        "/api/users",
        headers=auth_header(viewer_token),
        json={
            "email": "newuser@test.com",
            "full_name": "New User",
            "password": "password123",
            "role": "viewer",
        },
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    client: AsyncClient,
    admin_user: User,
    admin_token: str,
):
    """Test cannot create user with duplicate email."""
    response = await client.post(
        "/api/users",
        headers=auth_header(admin_token),
        json={
            "email": "admin@test.com",  # Already exists
            "full_name": "Duplicate User",
            "password": "password123",
            "role": "viewer",
        },
    )
    
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_list_users_as_admin(client: AsyncClient, admin_user: User, admin_token: str):
    """Test admin can list users."""
    response = await client.get(
        "/api/users",
        headers=auth_header(admin_token),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_users_as_dispatcher_forbidden(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test dispatcher cannot list users."""
    response = await client.get(
        "/api/users",
        headers=auth_header(dispatcher_token),
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_role(client: AsyncClient, admin_user: User, admin_token: str):
    """Test admin can update user role."""
    # Create a user first
    create_response = await client.post(
        "/api/users",
        headers=auth_header(admin_token),
        json={
            "email": "updatable@test.com",
            "full_name": "Updatable User",
            "password": "password123",
            "role": "viewer",
        },
    )
    user_id = create_response.json()["id"]
    
    # Update role
    response = await client.patch(
        f"/api/users/{user_id}",
        headers=auth_header(admin_token),
        json={"role": "dispatcher"},
    )
    
    assert response.status_code == 200
    assert response.json()["role"] == "dispatcher"


@pytest.mark.asyncio
async def test_deactivate_user(client: AsyncClient, admin_user: User, admin_token: str):
    """Test admin can deactivate user."""
    # Create a user first
    create_response = await client.post(
        "/api/users",
        headers=auth_header(admin_token),
        json={
            "email": "deactivatable@test.com",
            "full_name": "Deactivatable User",
            "password": "password123",
            "role": "viewer",
        },
    )
    user_id = create_response.json()["id"]
    
    # Deactivate
    response = await client.patch(
        f"/api/users/{user_id}",
        headers=auth_header(admin_token),
        json={"is_active": False},
    )
    
    assert response.status_code == 200
    assert response.json()["is_active"] is False
