from pydantic import BaseModel, EmailStr


class UserDeleteScheme(BaseModel):
    """Схема запроса на удаление пользователя (по email)."""
    email: EmailStr

    