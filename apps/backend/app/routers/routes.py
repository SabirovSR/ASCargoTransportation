from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Query
from typing import Optional

from app.models.route import RouteStatus
from app.schemas.route import (
    RouteCreate,
    RouteUpdate,
    RouteResponse,
    RouteListResponse,
    RouteCancelResponse,
    StopsUpdate,
)
from app.services.route import RouteService
from .deps import CurrentUser, EditorUser, DbSession

router = APIRouter(prefix="/api/routes", tags=["Routes"])


@router.post("", response_model=RouteResponse, status_code=201)
async def create_route(
    data: RouteCreate,
    current_user: EditorUser,
    db: DbSession,
):
    """
    Create a new route (admin/dispatcher only).
    """
    service = RouteService(db)
    route = await service.create(data, current_user)
    return RouteResponse.model_validate(route)


@router.get("", response_model=RouteListResponse)
async def list_routes(
    current_user: CurrentUser,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: Optional[RouteStatus] = Query(default=None),
    q: Optional[str] = Query(default=None, description="Search by route number or title"),
    created_by: Optional[UUID] = Query(default=None),
    from_date: Optional[datetime] = Query(default=None, alias="from"),
    to_date: Optional[datetime] = Query(default=None, alias="to"),
):
    """
    Get paginated list of routes with filters.
    """
    service = RouteService(db)
    routes, total = await service.get_list(
        limit=limit,
        offset=offset,
        status=status,
        q=q,
        created_by=created_by,
        from_date=from_date,
        to_date=to_date,
    )
    
    return RouteListResponse(
        items=[RouteResponse.model_validate(r) for r in routes],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(
    route_id: UUID,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Get route by ID.
    """
    service = RouteService(db)
    route = await service.get_by_id(route_id)
    return RouteResponse.model_validate(route)


@router.patch("/{route_id}", response_model=RouteResponse)
async def update_route(
    route_id: UUID,
    data: RouteUpdate,
    current_user: EditorUser,
    db: DbSession,
):
    """
    Update route (admin/dispatcher only).
    """
    service = RouteService(db)
    route = await service.update(route_id, data, current_user)
    return RouteResponse.model_validate(route)


@router.put("/{route_id}/stops", response_model=RouteResponse)
async def update_route_stops(
    route_id: UUID,
    data: StopsUpdate,
    current_user: EditorUser,
    db: DbSession,
):
    """
    Replace all route stops (admin/dispatcher only).
    """
    service = RouteService(db)
    route = await service.update_stops(route_id, data, current_user)
    return RouteResponse.model_validate(route)


@router.post("/{route_id}/cancel", response_model=RouteCancelResponse)
async def cancel_route(
    route_id: UUID,
    current_user: EditorUser,
    db: DbSession,
):
    """
    Cancel a route (admin/dispatcher only).
    """
    service = RouteService(db)
    route = await service.cancel(route_id, current_user)
    return RouteCancelResponse(
        id=route.id,
        route_number=route.route_number,
        status=route.status,
    )
