import pytest
from httpx import AsyncClient

from app.models.user import User
from .conftest import auth_header


@pytest.mark.asyncio
async def test_create_route_with_two_stops(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test creating route with minimum 2 stops succeeds."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Test Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Route"
    assert data["status"] == "draft"
    assert len(data["stops"]) == 2
    assert data["route_number"].startswith("RT-")


@pytest.mark.asyncio
async def test_create_route_with_one_stop_fails(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test creating route with 1 stop fails (422)."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Invalid Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
            ],
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_route_without_origin_fails(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test creating route without origin fails."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "No Origin Route",
            "stops": [
                {"seq": 1, "type": "stop", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_route_without_destination_fails(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test creating route without destination fails."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "No Destination Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "stop", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_route_as_viewer_forbidden(
    client: AsyncClient,
    viewer_user: User,
    viewer_token: str,
):
    """Test viewer cannot create route."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(viewer_token),
        json={
            "title": "Forbidden Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_routes(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test listing routes."""
    # Create a route first
    await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "List Test Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    response = await client.get(
        "/api/routes",
        headers=auth_header(dispatcher_token),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_list_routes_with_filters(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test listing routes with filters."""
    # Create a route
    await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Filterable Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    # Filter by status
    response = await client.get(
        "/api/routes?status=draft",
        headers=auth_header(dispatcher_token),
    )
    
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["status"] == "draft"
    
    # Search by title
    response = await client.get(
        "/api/routes?q=Filterable",
        headers=auth_header(dispatcher_token),
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_route(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test cancelling a route."""
    # Create a route
    create_response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Route to Cancel",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    route_id = create_response.json()["id"]
    
    # Cancel route
    response = await client.post(
        f"/api/routes/{route_id}/cancel",
        headers=auth_header(dispatcher_token),
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "cancelled"


@pytest.mark.asyncio
async def test_edit_cancelled_route_fails(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test editing cancelled route fails (409/400)."""
    # Create a route
    create_response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Route to Cancel and Edit",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    route_id = create_response.json()["id"]
    
    # Cancel route
    await client.post(
        f"/api/routes/{route_id}/cancel",
        headers=auth_header(dispatcher_token),
    )
    
    # Try to edit
    response = await client.patch(
        f"/api/routes/{route_id}",
        headers=auth_header(dispatcher_token),
        json={"title": "New Title"},
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_route_with_multiple_stops(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test creating route with multiple intermediate stops."""
    response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Multi-Stop Route",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "stop", "address": "Tver, Russia"},
                {"seq": 3, "type": "stop", "address": "Veliky Novgorod, Russia"},
                {"seq": 4, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert len(data["stops"]) == 4


@pytest.mark.asyncio
async def test_update_route_stops(
    client: AsyncClient,
    dispatcher_user: User,
    dispatcher_token: str,
):
    """Test updating route stops."""
    # Create a route
    create_response = await client.post(
        "/api/routes",
        headers=auth_header(dispatcher_token),
        json={
            "title": "Route to Update Stops",
            "stops": [
                {"seq": 1, "type": "origin", "address": "Moscow, Russia"},
                {"seq": 2, "type": "destination", "address": "Saint Petersburg, Russia"},
            ],
        },
    )
    route_id = create_response.json()["id"]
    
    # Update stops
    response = await client.put(
        f"/api/routes/{route_id}/stops",
        headers=auth_header(dispatcher_token),
        json={
            "stops": [
                {"seq": 1, "type": "origin", "address": "New Moscow, Russia"},
                {"seq": 2, "type": "stop", "address": "Tver, Russia"},
                {"seq": 3, "type": "destination", "address": "New Saint Petersburg, Russia"},
            ],
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["stops"]) == 3
    assert data["stops"][0]["address"] == "New Moscow, Russia"
