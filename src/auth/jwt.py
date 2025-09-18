from datetime import timedelta, datetime
from fastapi import HTTPException

from passlib.context import CryptContext
import jwt

from src.config import settings


class Auth:
    """Утилиты аутентификации: хеширование паролей и работа с JWT.

    - Хеширует и проверяет пароли через bcrypt
    - Создаёт и декодирует JWT-токены доступа
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """Проверяет соответствие пароля и его хеша.

        Args:
            plain_password: Обычный пароль в открытом виде.
            hashed_password: Хеш пароля из БД.

        Returns:
            bool: True, если пароль корректен.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def hash_password(self, password):
        """Возвращает bcrypt-хеш для переданного пароля."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict):
        """Создаёт JWT-токен доступа с истечением срока действия.

        В payload добавляется поле "exp" согласно настройке
        settings.ACCESS_TOKEN_EXPIRE_MINUTES.

        Args:
            data: Данные (payload), которые нужно закодировать в токен.

        Returns:
            str: Закодированный JWT-токен.
        """
        to_encode = data.copy()
        expire = datetime.now() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def decode_token(self, token):
        """Декодирует JWT-токен и возвращает payload.

        Поднимает HTTPException(401), если токен недействителен/просрочен.
        """
        try:
            return jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
        except Exception:
            raise HTTPException(
                status_code=401, detail="Could not validate credentials"
            )
