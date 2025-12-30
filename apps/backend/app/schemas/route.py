from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models.route import RouteStatus
from .route_stop import RouteStopCreate, RouteStopResponse
from .user import UserResponse


class RouteBase(BaseModel):
    """Base route schema."""
    
    title: str = Field(min_length=1, max_length=255)
    planned_departure_at: datetime | None = None
    comment: str | None = Field(default=None, max_length=2000)


class RouteCreate(RouteBase):
    """Schema for creating a route."""
    
    route_number: str | None = Field(default=None, max_length=50)
    stops: list[RouteStopCreate] = Field(min_length=2)
    
    @field_validator("stops")
    @classmethod
    def validate_stops(cls, v: list[RouteStopCreate]) -> list[RouteStopCreate]:
        """Validate stops have origin and destination."""
        if len(v) < 2:
            raise ValueError("Route must have at least 2 stops")
        
        # Check for origin and destination
        types = [stop.type.value for stop in v]
        if "origin" not in types:
            raise ValueError("Route must have an origin stop")
        if "destination" not in types:
            raise ValueError("Route must have a destination stop")
        
        # Check seq uniqueness
        seqs = [stop.seq for stop in v]
        if len(seqs) != len(set(seqs)):
            raise ValueError("Stop sequences must be unique")
        
        return v


class RouteUpdate(BaseModel):
    """Schema for updating a route."""
    
    title: str | None = Field(default=None, min_length=1, max_length=255)
    planned_departure_at: datetime | None = None
    comment: str | None = Field(default=None, max_length=2000)
    status: RouteStatus | None = None


class StopsUpdate(BaseModel):
    """Schema for updating route stops."""
    
    stops: list[RouteStopCreate] = Field(min_length=2)
    
    @field_validator("stops")
    @classmethod
    def validate_stops(cls, v: list[RouteStopCreate]) -> list[RouteStopCreate]:
        """Validate stops have origin and destination."""
        if len(v) < 2:
            raise ValueError("Route must have at least 2 stops")
        
        types = [stop.type.value for stop in v]
        if "origin" not in types:
            raise ValueError("Route must have an origin stop")
        if "destination" not in types:
            raise ValueError("Route must have a destination stop")
        
        seqs = [stop.seq for stop in v]
        if len(seqs) != len(set(seqs)):
            raise ValueError("Stop sequences must be unique")
        
        return v


class RouteResponse(BaseModel):
    """Schema for route response."""
    
    id: UUID
    route_number: str
    title: str
    status: RouteStatus
    created_by: UUID
    created_by_user: UserResponse | None = None
    planned_departure_at: datetime | None
    comment: str | None
    stops: list[RouteStopResponse] = []
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RouteListResponse(BaseModel):
    """Schema for paginated route list response."""
    
    items: list[RouteResponse]
    total: int
    limit: int
    offset: int


class RouteCancelResponse(BaseModel):
    """Schema for route cancellation response."""
    
    id: UUID
    route_number: str
    status: RouteStatus
    message: str = "Route cancelled successfully"
