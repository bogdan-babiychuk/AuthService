import string
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from src.auth.jwt import Auth


class LoginUserSchema(BaseModel):
    """Схема входа пользователя по email и паролю."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=50)

    def check_password(self, hashed_password) -> bool:
        """Проверяет введённый пароль относительно хеша из БД."""
        return Auth().verify_password(self.password, hashed_password)


class ChangePasswordUserSchema(BaseModel):
    """Схема смены пароля: текущий, новый и подтверждение нового."""

    recent_password: str = Field(
        min_length=8, max_length=50, exclude=True, examples=["P@ssw0rd!"]
    )
    new_password: str = Field(min_length=8, max_length=50)
    confirm_new_password: str = Field(
        min_length=8, max_length=50, exclude=True, examples=["P@ssw0rd!"]
    )

    @field_validator("new_password", mode="after")
    def password_must_have_special_char(cls, password_value: str) -> str:
        special_chars = string.punctuation
        if not any(char in special_chars for char in password_value):
            raise ValueError("Пароль должен содержать хотя бы один специальный символ")
        return password_value

    @model_validator(mode="after")
    def passwords_match(
        cls, model: "ChangePasswordUserSchema"
    ) -> "ChangePasswordUserSchema":
        if model.new_password != model.confirm_new_password:
            raise ValueError("Пароли не совпадают")
        return model

    def check_password(self, hashed_password) -> bool:
        """Проверяет текущий пароль относительно хеша из БД."""
        return Auth().verify_password(self.recent_password, hashed_password)
