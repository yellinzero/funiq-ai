import uuid
from datetime import datetime, timezone
from typing import Any, Generic, Type, TypeVar, Union

import inflect
import stringcase
from sqlalchemy import DateTime, Integer, func, insert, update
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
from sqlalchemy.sql import Select
from sqlalchemy_utils import generic_repr

# Type variable for the generic DBBase
T = TypeVar("T", bound="DBBase")
ID = TypeVar("ID", bound=Union[int, uuid.UUID])


def resolve_table_name(name: str) -> str:
    """Convert class name to table name using snake_case and plural form."""
    p = inflect.engine()
    snake_name = stringcase.snakecase(name)
    parts = snake_name.split("_")
    parts[-1] = p.plural(parts[-1])
    return "_".join(parts)


@generic_repr
class DBBase(AsyncAttrs, DeclarativeBase):
    """
    Base class for ORM models, providing common database operations.
    Focuses on query building and basic operations without transaction management.
    Transaction management is left to the service layer.
    """

    @declared_attr.directive
    def __tablename__(self) -> str:
        """Generate table name based on class name."""
        return resolve_table_name(self.__name__)

    # ----- Query Building Methods -----
    @classmethod
    def select(cls: Type[T]) -> Select[T]:
        """Build a base SELECT statement for the model."""
        return select(cls)

    @classmethod
    def update(cls: Type[T], updates: dict[str, Any], **kwargs) -> update:
        """Build an UPDATE statement with the given values and filters."""
        return update(cls).filter_by(**kwargs).values(updates)

    @classmethod
    def insert(cls: Type[T], values: Union[dict[str, Any], list[dict[str, Any]]]) -> insert:
        """Build an INSERT statement with the given values."""
        return insert(cls).values(values)

    # ----- Query Methods -----
    @classmethod
    async def get(cls: Type[T], session: AsyncSession, ident: Any, **kwargs) -> Union[T, None]:
        """Retrieve a record by its primary key."""
        return await session.get(cls, ident, **kwargs)

    @classmethod
    async def exists(cls: Type[T], session: AsyncSession, **kwargs) -> bool:
        """Check if any record exists matching the given conditions."""
        result = await session.execute(
            select(func.count()).select_from(cls).filter_by(**kwargs)
        )
        return result.scalar() > 0

    @classmethod
    async def count(cls: Type[T], session: AsyncSession, **kwargs) -> int:
        """Get the count of records matching the given conditions."""
        result = await session.execute(
            select(func.count()).select_from(cls).filter_by(**kwargs)
        )
        return result.scalar()
    
    @classmethod
    async def first(cls: Type[T], session: AsyncSession, **kwargs) -> Union[T, None]:
        """Retrieve the first record matching the given conditions."""
        result = await session.scalars(select(cls).filter_by(**kwargs).limit(1))
        return result.first()

    @classmethod
    async def find_one(cls: Type[T], session: AsyncSession, **kwargs) -> Union[T, None]:
        """Find a single record matching the given conditions."""
        result = await session.execute(
            select(cls).filter_by(**kwargs).limit(1)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def find_all(cls: Type[T], session: AsyncSession, **kwargs) -> list[T]:
        """Find all records matching the given conditions."""
        result = await session.execute(select(cls).filter_by(**kwargs))
        return list(result.scalars().all())

    # ----- Instance Methods -----
    def to_dict(self) -> dict[str, Any]:
        """Convert the instance to a dictionary."""
        return {col.key: getattr(self, col.key) 
                for col in self.__table__.columns}

    def update_fields(self, updates: dict[str, Any]) -> None:
        """
        Update instance fields in memory without persisting to database.
        Transaction management should be handled by the caller.
        """
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @classmethod
    def get_column_names(cls) -> list[str]:
        """Get a list of all column names for the model."""
        return [col.key for col in cls.__table__.columns]
    
    def save(self, session: AsyncSession) -> None:
        """Save the current instance to the database."""
        session.add(self)

    def delete(self, session: AsyncSession) -> None:
        """Delete the current instance from the database."""
        session.delete(self)


class DBAuditFieldsMixin:
    """
    Mixin providing audit fields for tracking creation and modification times.
    All timestamps are stored in UTC.
    """
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        index=True
    )
    
    def refresh_updated_at(self) -> None:
        """Manually refresh the updated_at field to the current timestamp."""
        self.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)


class DBSoftDeleteMixin:
    """
    Mixin providing soft delete capability.
    Adds deleted_at timestamp and deleted_by user reference.
    """
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deleted_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        """Check if the record is marked as deleted."""
        return self.deleted_at is not None

    def mark_deleted(self, deleted_by: uuid.UUID | None = None) -> None:
        """
        Mark the record as deleted in memory.
        Does not persist changes to database - transaction management should be handled by the caller.
        """
        self.deleted_at = datetime.now(timezone.utc).replace(tzinfo=None)
        self.deleted_by = deleted_by


class DBBaseModelMixin(DBAuditFieldsMixin, Generic[ID]):
    """Base mixin combining audit fields with ID field."""
    id: Mapped[ID]


class DBIntegerModelMixin(DBBaseModelMixin[int]):
    """Mixin providing auto-incrementing integer primary key with audit fields."""
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class DBUUIDModelMixin(DBBaseModelMixin[uuid.UUID]):
    """Mixin providing UUID primary key with audit fields."""
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )