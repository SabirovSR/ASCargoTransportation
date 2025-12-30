import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Numeric, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class StopType(str, Enum):
    ORIGIN = "origin"
    STOP = "stop"
    DESTINATION = "destination"


class RouteStop(Base):
    """Route stop model."""
    
    __tablename__ = "route_stops"
    __table_args__ = (
        UniqueConstraint("route_id", "seq", name="uq_route_stops_route_seq"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    route_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("routes.id", ondelete="CASCADE"),
        nullable=False,
    )
    seq: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[StopType] = mapped_column(
        SQLEnum(StopType),
        nullable=False,
    )
    address: Mapped[str] = mapped_column(Text, nullable=False)
    lat: Mapped[float | None] = mapped_column(Numeric(10, 8), nullable=True)
    lng: Mapped[float | None] = mapped_column(Numeric(11, 8), nullable=True)
    time_window_from: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    time_window_to: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    
    # Relationships
    route: Mapped["Route"] = relationship(
        "Route",
        back_populates="stops",
        lazy="selectin",
    )
    
    def __repr__(self) -> str:
        return f"<RouteStop {self.route_id}:{self.seq}>"


# Import at end to avoid circular imports
from .route import Route
