from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из переменных окружения/.env."""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"

    ADMIN_PASSWORD: str = Field(default="123")

    model_config = SettingsConfigDict(env_file=ENV_PATH)

settings = Settings()