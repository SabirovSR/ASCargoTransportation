from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Get user by ID."""
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """Get paginated list of users."""
        # Get total count
        count_query = select(func.count()).select_from(User)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get users
        query = select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """Update a user."""
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user: User) -> None:
        """Delete a user."""
        await self.db.delete(user)
        await self.db.flush()
