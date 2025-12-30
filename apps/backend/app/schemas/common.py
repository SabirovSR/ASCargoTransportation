from pydantic import BaseModel, Field
from typing import Any


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class ErrorDetail(BaseModel):
    """Error detail item."""
    
    field: str | None = None
    message: str


class ErrorContent(BaseModel):
    """Error content."""
    
    code: str
    message: str
    details: list[ErrorDetail] = []


class ErrorResponse(BaseModel):
    """Standard error response."""
    
    error: ErrorContent


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = "healthy"
    version: str
