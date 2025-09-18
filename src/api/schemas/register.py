from pyexpat import model
import string
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from src.auth.jwt import Auth


class CreateUserSchema(BaseModel):
    """Схема регистрации нового пользователя."""

    name: str = Field(min_length=2, max_length=50, examples=["Андрей"])
    last_name: str = Field(min_length=2, max_length=50, examples=["Иванов"])
    surname: str = Field(min_length=2, max_length=50, examples=["Петрович"])
    email: EmailStr
    password: str = Field(min_length=8, max_length=50, examples=["P@ssw0rd!"])
    confirm_password: str = Field(
        min_length=8, max_length=50, exclude=True, examples=["P@ssw0rd!"]
    )

    def hash_password(self) -> "CreateUserSchema":
        """Хеширует пароль и возвращает self для дальнейшего использования."""
        self.password = Auth().hash_password(self.password)
        return self

    @field_validator("password", mode="after")
    def password_must_have_special_char(cls, password_value: str) -> str:
        special_chars = string.punctuation
        if not any(char in special_chars for char in password_value):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return password_value

    @model_validator(mode="after")
    def passwords_match(cls, model: "CreateUserSchema") -> "CreateUserSchema":
        if model.password != model.confirm_password:
            raise ValueError("Пароли не совпадают")
        return model
