from pydantic import BaseModel, Field

from .user import UserResponse
from .common import EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Token response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    
    refresh_token: str


class RefreshResponse(BaseModel):
    """Refresh token response schema."""
    
    access_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    """Change password request schema."""
    
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6, max_length=128)
