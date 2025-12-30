from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models.route_stop import StopType


class RouteStopBase(BaseModel):
    """Base route stop schema."""
    
    address: str = Field(min_length=1, max_length=500)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    time_window_from: datetime | None = None
    time_window_to: datetime | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)


class RouteStopCreate(RouteStopBase):
    """Schema for creating a route stop."""
    
    seq: int = Field(ge=1)
    type: StopType


class RouteStopUpdate(BaseModel):
    """Schema for updating a route stop."""
    
    seq: int | None = Field(default=None, ge=1)
    type: StopType | None = None
    address: str | None = Field(default=None, min_length=1, max_length=500)
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    time_window_from: datetime | None = None
    time_window_to: datetime | None = None
    contact_name: str | None = Field(default=None, max_length=255)
    contact_phone: str | None = Field(default=None, max_length=50)


class RouteStopResponse(BaseModel):
    """Schema for route stop response."""
    
    id: UUID
    route_id: UUID
    seq: int
    type: StopType
    address: str
    lat: float | None
    lng: float | None
    time_window_from: datetime | None
    time_window_to: datetime | None
    contact_name: str | None
    contact_phone: str | None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
