from uuid import UUID
from typing import Annotated
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.core.security import decode_token
from app.core.exceptions import AuthenticationError, AuthorizationError

security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Get current authenticated user from JWT token."""
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired token")
    
    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")
    
    # Get user ID from token
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Invalid token payload")
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token")
    
    # Get user from database
    repo = UserRepository(db)
    user = await repo.get_by_id(user_id)
    
    if not user:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is deactivated")
    
    return user


async def get_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user and verify admin role."""
    if current_user.role != UserRole.ADMIN:
        raise AuthorizationError("Admin access required")
    return current_user


async def get_editor_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current user and verify editor role (admin or dispatcher)."""
    if current_user.role not in (UserRole.ADMIN, UserRole.DISPATCHER):
        raise AuthorizationError("Editor access required")
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(get_admin_user)]
EditorUser = Annotated[User, Depends(get_editor_user)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
