from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user import UserRepository
from app.core.security import get_password_hash
from app.core.exceptions import NotFoundError, ConflictError, AuthorizationError
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)
    
    async def get_by_id(self, user_id: UUID) -> User:
        """Get user by ID."""
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        return user
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return await self.repo.get_by_email(email)
    
    async def get_list(
        self,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[User], int]:
        """Get paginated list of users."""
        return await self.repo.get_list(limit=limit, offset=offset)
    
    async def create(
        self,
        data: UserCreate,
        created_by: User,
    ) -> User:
        """Create a new user (admin only)."""
        # Check permission
        if created_by.role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can create users")
        
        # Check if email already exists
        existing = await self.repo.get_by_email(data.email)
        if existing:
            raise ConflictError(f"User with email '{data.email}' already exists")
        
        # Create user
        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=get_password_hash(data.password),
            role=data.role,
            must_change_password=True,
        )
        
        user = await self.repo.create(user)
        logger.info("user_created", user_id=str(user.id), email=user.email, created_by=str(created_by.id))
        return user
    
    async def update(
        self,
        user_id: UUID,
        data: UserUpdate,
        updated_by: User,
    ) -> User:
        """Update a user (admin only)."""
        # Check permission
        if updated_by.role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can update users")
        
        # Get user
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        # Update fields
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.role is not None:
            user.role = data.role
        if data.is_active is not None:
            user.is_active = data.is_active
        
        user = await self.repo.update(user)
        logger.info("user_updated", user_id=str(user.id), updated_by=str(updated_by.id))
        return user
    
    async def reset_password(
        self,
        user_id: UUID,
        new_password: str,
        reset_by: User,
    ) -> User:
        """Reset user password (admin only)."""
        # Check permission
        if reset_by.role != UserRole.ADMIN:
            raise AuthorizationError("Only admins can reset passwords")
        
        # Get user
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", str(user_id))
        
        # Reset password
        user.password_hash = get_password_hash(new_password)
        user.must_change_password = True
        
        user = await self.repo.update(user)
        logger.info("password_reset", user_id=str(user.id), reset_by=str(reset_by.id))
        return user
    
    async def change_password(
        self,
        user: User,
        new_password: str,
    ) -> User:
        """Change own password."""
        user.password_hash = get_password_hash(new_password)
        user.must_change_password = False
        
        user = await self.repo.update(user)
        logger.info("password_changed", user_id=str(user.id))
        return user
    
    async def create_admin_if_not_exists(
        self,
        email: str,
        password: str,
        full_name: str = "System Admin",
    ) -> User | None:
        """Create admin user if not exists (for initial setup)."""
        existing = await self.repo.get_by_email(email)
        if existing:
            return None
        
        user = User(
            email=email,
            full_name=full_name,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
            must_change_password=False,
        )
        
        user = await self.repo.create(user)
        logger.info("admin_user_created", user_id=str(user.id), email=user.email)
        return user
