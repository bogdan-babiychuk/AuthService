from pydantic import BaseModel, Field


class UserUpdateSchema(BaseModel):
    """Схема обновления профиля пользователя (частичное обновление)."""

    name: str | None = Field(None, min_length=2, max_length=50)
    last_name: str | None = Field(None, min_length=2, max_length=50)
    surname: str | None = Field(None, min_length=2, max_length=50)
