from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.repositories.user import UserRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = RefreshTokenRepository(db)
    
    async def login(self, email: str, password: str) -> tuple[str, str, User]:
        """
        Authenticate user and return tokens.
        Returns: (access_token, refresh_token, user)
        """
        # Get user
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.warning("login_failed", email=email, reason="user_not_found")
            raise AuthenticationError("Invalid email or password")
        
        # Check password
        if not verify_password(password, user.password_hash):
            logger.warning("login_failed", email=email, reason="invalid_password")
            raise AuthenticationError("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            logger.warning("login_failed", email=email, reason="user_inactive")
            raise AuthenticationError("User account is deactivated")
        
        # Create tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})
        
        # Store refresh token
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token_record = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=expires_at,
        )
        await self.token_repo.create(token_record)
        
        logger.info("login_success", user_id=str(user.id), email=email)
        return access_token, refresh_token, user
    
    async def refresh(self, refresh_token: str) -> str:
        """
        Refresh access token using refresh token.
        Returns: new access_token
        """
        # Decode token
        payload = decode_token(refresh_token)
        if not payload:
            raise AuthenticationError("Invalid refresh token")
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        # Check if token exists and is valid
        token_record = await self.token_repo.get_by_token(refresh_token)
        if not token_record:
            raise AuthenticationError("Refresh token not found")
        
        if token_record.is_revoked:
            raise AuthenticationError("Refresh token has been revoked")
        
        if token_record.expires_at < datetime.utcnow():
            raise AuthenticationError("Refresh token has expired")
        
        # Get user
        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive")
        
        # Create new access token
        access_token = create_access_token({"sub": str(user.id)})
        
        logger.info("token_refreshed", user_id=str(user.id))
        return access_token
    
    async def logout(self, refresh_token: str) -> bool:
        """
        Logout user by revoking refresh token.
        Returns: True if token was revoked
        """
        token_record = await self.token_repo.get_by_token(refresh_token)
        if token_record:
            await self.token_repo.revoke(token_record)
            logger.info("logout", user_id=str(token_record.user_id))
            return True
        return False
    
    async def logout_all(self, user_id) -> int:
        """
        Logout user from all sessions.
        Returns: number of tokens revoked
        """
        count = await self.token_repo.revoke_all_for_user(user_id)
        logger.info("logout_all", user_id=str(user_id), revoked_count=count)
        return count
