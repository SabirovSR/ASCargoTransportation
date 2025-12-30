from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
    ChangePasswordRequest,
)
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.services.user import UserService
from app.core.security import verify_password
from app.core.exceptions import AuthenticationError
from .deps import CurrentUser, DbSession

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    db: DbSession,
):
    """
    Authenticate user and return tokens.
    """
    service = AuthService(db)
    access_token, refresh_token, user = await service.login(data.email, data.password)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    data: RefreshRequest,
    db: DbSession,
):
    """
    Refresh access token using refresh token.
    """
    service = AuthService(db)
    access_token = await service.refresh(data.refresh_token)
    
    return RefreshResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshRequest,
    db: DbSession,
):
    """
    Logout user by revoking refresh token.
    """
    service = AuthService(db)
    await service.logout(data.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
):
    """
    Get current authenticated user information.
    """
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=UserResponse)
async def change_password(
    data: ChangePasswordRequest,
    current_user: CurrentUser,
    db: DbSession,
):
    """
    Change current user's password.
    """
    # Verify current password
    if not verify_password(data.current_password, current_user.password_hash):
        raise AuthenticationError("Current password is incorrect")
    
    service = UserService(db)
    user = await service.change_password(current_user, data.new_password)
    
    return UserResponse.model_validate(user)
