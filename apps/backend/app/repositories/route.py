from uuid import UUID
from datetime import datetime
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.route import Route, RouteStatus
from app.models.route_stop import RouteStop


class RouteRepository:
    """Repository for route operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, route_id: UUID) -> Route | None:
        """Get route by ID with stops."""
        query = (
            select(Route)
            .options(selectinload(Route.stops), selectinload(Route.created_by_user))
            .where(Route.id == route_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_route_number(self, route_number: str) -> Route | None:
        """Get route by route number."""
        result = await self.db.execute(
            select(Route).where(Route.route_number == route_number)
        )
        return result.scalar_one_or_none()
    
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
        # Base query
        base_query = select(Route).options(
            selectinload(Route.stops),
            selectinload(Route.created_by_user)
        )
        count_query = select(func.count()).select_from(Route)
        
        # Apply filters
        filters = []
        if status:
            filters.append(Route.status == status)
        if created_by:
            filters.append(Route.created_by == created_by)
        if from_date:
            filters.append(Route.created_at >= from_date)
        if to_date:
            filters.append(Route.created_at <= to_date)
        if q:
            search_filter = or_(
                Route.route_number.ilike(f"%{q}%"),
                Route.title.ilike(f"%{q}%"),
            )
            filters.append(search_filter)
        
        if filters:
            base_query = base_query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get routes
        query = base_query.order_by(Route.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        routes = list(result.scalars().all())
        
        return routes, total
    
    async def create(self, route: Route) -> Route:
        """Create a new route."""
        self.db.add(route)
        await self.db.flush()
        await self.db.refresh(route)
        return route
    
    async def update(self, route: Route) -> Route:
        """Update a route."""
        await self.db.flush()
        await self.db.refresh(route)
        return route
    
    async def delete(self, route: Route) -> None:
        """Delete a route."""
        await self.db.delete(route)
        await self.db.flush()
    
    async def get_next_route_number(self) -> str:
        """Generate next route number."""
        year = datetime.utcnow().year
        prefix = f"RT-{year}-"
        
        # Find highest number for this year
        query = select(Route.route_number).where(
            Route.route_number.like(f"{prefix}%")
        ).order_by(Route.route_number.desc()).limit(1)
        
        result = await self.db.execute(query)
        last_number = result.scalar_one_or_none()
        
        if last_number:
            try:
                num = int(last_number.split("-")[-1]) + 1
            except (ValueError, IndexError):
                num = 1
        else:
            num = 1
        
        return f"{prefix}{num:04d}"
    
    async def delete_stops(self, route_id: UUID) -> None:
        """Delete all stops for a route."""
        query = select(RouteStop).where(RouteStop.route_id == route_id)
        result = await self.db.execute(query)
        stops = result.scalars().all()
        for stop in stops:
            await self.db.delete(stop)
        await self.db.flush()
    
    async def add_stops(self, stops: list[RouteStop]) -> list[RouteStop]:
        """Add stops to a route."""
        for stop in stops:
            self.db.add(stop)
        await self.db.flush()
        return stops
