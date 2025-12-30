from uuid import UUID
from datetime import datetime
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    """Repository for refresh token operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_token(self, token: str) -> RefreshToken | None:
        """Get refresh token by token string."""
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
    
    async def create(self, refresh_token: RefreshToken) -> RefreshToken:
        """Create a new refresh token."""
        self.db.add(refresh_token)
        await self.db.flush()
        await self.db.refresh(refresh_token)
        return refresh_token
    
    async def revoke(self, refresh_token: RefreshToken) -> RefreshToken:
        """Revoke a refresh token."""
        refresh_token.is_revoked = True
        await self.db.flush()
        await self.db.refresh(refresh_token)
        return refresh_token
    
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all refresh tokens for a user."""
        query = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False,
        )
        result = await self.db.execute(query)
        tokens = result.scalars().all()
        count = 0
        for token in tokens:
            token.is_revoked = True
            count += 1
        await self.db.flush()
        return count
    
    async def cleanup_expired(self) -> int:
        """Delete expired tokens."""
        query = delete(RefreshToken).where(
            RefreshToken.expires_at < datetime.utcnow()
        )
        result = await self.db.execute(query)
        await self.db.flush()
        return result.rowcount or 0
