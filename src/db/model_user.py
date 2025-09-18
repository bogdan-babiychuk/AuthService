import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, Enum, String, false

from src.db.roles import UserRole


class Base(DeclarativeBase):
    """Базовый класс декларативных моделей SQLAlchemy."""


class User(Base):
    """Модель пользователя.

    Содержит поля идентификатора, UUID, ФИО, email, пароль, роль и статус.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(
        String, default=lambda: str(uuid.uuid4()), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(length=50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=50), nullable=False)
    surname: Mapped[str] = mapped_column(String(length=50), nullable=False)
    email: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)
    role: Mapped[str] = mapped_column(nullable=false, default=UserRole.SIMPLE_USER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
