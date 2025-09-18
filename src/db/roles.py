import enum


class UserRole(str, enum.Enum): #экземпляры класса будут строками enum (для совместимости с БД и pydantic)
    """Роли пользователей в системе."""

    ADMIN = "admin"
    SIMPLE_USER = "simple_user"

