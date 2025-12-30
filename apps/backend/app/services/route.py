from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.route import Route, RouteStatus
from app.models.route_stop import RouteStop
from app.schemas.route import RouteCreate, RouteUpdate, StopsUpdate
from app.repositories.route import RouteRepository
from app.core.exceptions import (
    NotFoundError,
    ConflictError,
    AuthorizationError,
    BusinessRuleError,
)
from app.core.logging import get_logger

logger = get_logger(__name__)


class RouteService:
    """Service for route operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RouteRepository(db)
    
    def _can_edit_routes(self, user: User) -> bool:
        """Check if user can create/edit routes."""
        return user.role in (UserRole.ADMIN, UserRole.DISPATCHER)
    
    async def get_by_id(self, route_id: UUID) -> Route:
        """Get route by ID."""
        route = await self.repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route", str(route_id))
        return route
    
    async def get_list(
        self,
        limit: int = 20,
        offset: int = 0,
        status: RouteStatus | None = None,
        q: str | None = None,
        created_by: UUID | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> tuple[list[Route], int]:
        """Get paginated list of routes with filters."""
        return await self.repo.get_list(
            limit=limit,
            offset=offset,
            status=status,
            q=q,
            created_by=created_by,
            from_date=from_date,
            to_date=to_date,
        )
    
    async def create(
        self,
        data: RouteCreate,
        created_by: User,
    ) -> Route:
        """Create a new route."""
        # Check permission
        if not self._can_edit_routes(created_by):
            raise AuthorizationError("You don't have permission to create routes")
        
        # Generate route number if not provided
        route_number = data.route_number
        if not route_number:
            route_number = await self.repo.get_next_route_number()
        else:
            # Check if route number already exists
            existing = await self.repo.get_by_route_number(route_number)
            if existing:
                raise ConflictError(f"Route with number '{route_number}' already exists")
        
        # Create route
        route = Route(
            route_number=route_number,
            title=data.title,
            status=RouteStatus.DRAFT,
            created_by=created_by.id,
            planned_departure_at=data.planned_departure_at,
            comment=data.comment,
        )
        
        route = await self.repo.create(route)
        
        # Create stops
        stops = []
        for stop_data in data.stops:
            stop = RouteStop(
                route_id=route.id,
                seq=stop_data.seq,
                type=stop_data.type,
                address=stop_data.address,
                lat=stop_data.lat,
                lng=stop_data.lng,
                time_window_from=stop_data.time_window_from,
                time_window_to=stop_data.time_window_to,
                contact_name=stop_data.contact_name,
                contact_phone=stop_data.contact_phone,
            )
            stops.append(stop)
        
        await self.repo.add_stops(stops)
        await self.db.flush()
        
        # Expire and refresh to get updated stops
        await self.db.refresh(route, ["stops"])
        
        logger.info(
            "route_created",
            route_id=str(route.id),
            route_number=route.route_number,
            created_by=str(created_by.id),
        )
        return route
    
    async def update(
        self,
        route_id: UUID,
        data: RouteUpdate,
        updated_by: User,
    ) -> Route:
        """Update a route."""
        # Check permission
        if not self._can_edit_routes(updated_by):
            raise AuthorizationError("You don't have permission to update routes")
        
        # Get route
        route = await self.repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route", str(route_id))
        
        # Check if route can be edited
        if route.status == RouteStatus.CANCELLED:
            raise BusinessRuleError("Cancelled routes cannot be edited")
        
        # Validate status transition
        if data.status is not None:
            if not self._is_valid_status_transition(route.status, data.status):
                raise BusinessRuleError(
                    f"Invalid status transition from {route.status.value} to {data.status.value}"
                )
            
            # Check if route has required stops for activation
            if data.status == RouteStatus.ACTIVE:
                if not self._has_origin_and_destination(route):
                    raise BusinessRuleError(
                        "Route must have origin and destination stops before activation"
                    )
        
        # Update fields
        if data.title is not None:
            route.title = data.title
        if data.planned_departure_at is not None:
            route.planned_departure_at = data.planned_departure_at
        if data.comment is not None:
            route.comment = data.comment
        if data.status is not None:
            route.status = data.status
        
        route = await self.repo.update(route)
        
        logger.info(
            "route_updated",
            route_id=str(route.id),
            updated_by=str(updated_by.id),
        )
        return route
    
    async def update_stops(
        self,
        route_id: UUID,
        data: StopsUpdate,
        updated_by: User,
    ) -> Route:
        """Update route stops (replace all)."""
        # Check permission
        if not self._can_edit_routes(updated_by):
            raise AuthorizationError("You don't have permission to update routes")
        
        # Get route
        route = await self.repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route", str(route_id))
        
        # Check if route can be edited
        if route.status in (RouteStatus.ACTIVE, RouteStatus.CANCELLED):
            raise BusinessRuleError(
                f"Cannot modify stops of {route.status.value} routes"
            )
        
        # Delete existing stops
        await self.repo.delete_stops(route_id)
        
        # Create new stops
        stops = []
        for stop_data in data.stops:
            stop = RouteStop(
                route_id=route.id,
                seq=stop_data.seq,
                type=stop_data.type,
                address=stop_data.address,
                lat=stop_data.lat,
                lng=stop_data.lng,
                time_window_from=stop_data.time_window_from,
                time_window_to=stop_data.time_window_to,
                contact_name=stop_data.contact_name,
                contact_phone=stop_data.contact_phone,
            )
            stops.append(stop)
        
        await self.repo.add_stops(stops)
        await self.db.flush()
        
        # Expire and refresh to get updated stops
        await self.db.refresh(route, ["stops"])
        
        logger.info(
            "route_stops_updated",
            route_id=str(route.id),
            updated_by=str(updated_by.id),
            stops_count=len(stops),
        )
        return route
    
    async def cancel(
        self,
        route_id: UUID,
        cancelled_by: User,
    ) -> Route:
        """Cancel a route."""
        # Check permission
        if not self._can_edit_routes(cancelled_by):
            raise AuthorizationError("You don't have permission to cancel routes")
        
        # Get route
        route = await self.repo.get_by_id(route_id)
        if not route:
            raise NotFoundError("Route", str(route_id))
        
        # Check if route can be cancelled
        if route.status == RouteStatus.CANCELLED:
            raise BusinessRuleError("Route is already cancelled")
        if route.status == RouteStatus.COMPLETED:
            raise BusinessRuleError("Completed routes cannot be cancelled")
        
        # Cancel route
        route.status = RouteStatus.CANCELLED
        route = await self.repo.update(route)
        
        logger.info(
            "route_cancelled",
            route_id=str(route.id),
            cancelled_by=str(cancelled_by.id),
        )
        return route
    
    def _is_valid_status_transition(
        self,
        current: RouteStatus,
        new: RouteStatus,
    ) -> bool:
        """Check if status transition is valid."""
        valid_transitions = {
            RouteStatus.DRAFT: {RouteStatus.ACTIVE, RouteStatus.CANCELLED},
            RouteStatus.ACTIVE: {RouteStatus.COMPLETED, RouteStatus.CANCELLED},
            RouteStatus.COMPLETED: set(),  # No transitions from completed
            RouteStatus.CANCELLED: set(),  # No transitions from cancelled
        }
        return new in valid_transitions.get(current, set())
    
    def _has_origin_and_destination(self, route: Route) -> bool:
        """Check if route has origin and destination stops."""
        has_origin = False
        has_destination = False
        for stop in route.stops:
            if stop.type.value == "origin":
                has_origin = True
            elif stop.type.value == "destination":
                has_destination = True
        return has_origin and has_destination
