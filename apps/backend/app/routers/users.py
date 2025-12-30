from uuid import UUID
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
)
from app.services.user import UserService
from .deps import AdminUser, DbSession

router = APIRouter(prefix="/api/users", tags=["Users"])


class ResetPasswordRequest(BaseModel):
    """Reset password request schema."""
    new_password: str = Field(min_length=6, max_length=128)


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    data: UserCreate,
    current_user: AdminUser,
    db: DbSession,
):
    """
    Create a new user (admin only).
    """
    service = UserService(db)
    user = await service.create(data, current_user)
    return UserResponse.model_validate(user)


@router.get("", response_model=UserListResponse)
async def list_users(
    current_user: AdminUser,
    db: DbSession,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    """
    Get paginated list of users (admin only).
    """
    service = UserService(db)
    users, total = await service.get_list(limit=limit, offset=offset)
    
    return UserListResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    current_user: AdminUser,
    db: DbSession,
):
    """
    Get user by ID (admin only).
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: AdminUser,
    db: DbSession,
):
    """
    Update user (admin only).
    """
    service = UserService(db)
    user = await service.update(user_id, data, current_user)
    return UserResponse.model_validate(user)


@router.post("/{user_id}/reset-password", response_model=UserResponse)
async def reset_user_password(
    user_id: UUID,
    data: ResetPasswordRequest,
    current_user: AdminUser,
    db: DbSession,
):
    """
    Reset user password (admin only).
    """
    service = UserService(db)
    user = await service.reset_password(user_id, data.new_password, current_user)
    return UserResponse.model_validate(user)
