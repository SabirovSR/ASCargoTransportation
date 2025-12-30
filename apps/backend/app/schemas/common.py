from pydantic import BaseModel, Field, field_validator
from typing import Any, Annotated
import re


# Custom email type that allows development domains like .local, .test
class EmailStr(str):
    """Custom email string that allows special-use domains for development."""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.with_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )
    
    @classmethod
    def _validate(cls, value: str, _info) -> str:
        """Validate email with relaxed rules for development domains."""
        if not isinstance(value, str):
            raise ValueError("Email must be a string")
        
        # Basic email pattern validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            raise ValueError("Invalid email format")
        
        return value.lower()


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
