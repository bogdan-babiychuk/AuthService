
from dataclasses import dataclass
import email
from http.client import PRECONDITION_FAILED
from math import e
from typing import ClassVar, Type

from fastapi import Response
from fastapi.background import P

from src.api.schemas.delete import UserDeleteScheme
from src.api.schemas.edit_profile import UserUpdateSchema
from src.api.schemas.login import ChangePasswordUserSchema, LoginUserSchema
from src.api.schemas.register import CreateUserSchema
from src.api.services.utils import ModeDelete
from src.auth.jwt import Auth
from src.db.model_user import User
from src.db.roles import UserRole
from src.db.uow import UnitOfWork
from src.infra.repositories.user import UserRepository


@dataclass
class UserService:
    """Сервис работы с пользователями.

    Инкапсулирует бизнес-логику регистрации, входа, удаления,
    смены роли и пароля, а также обновления профиля. Работает через
    `UnitOfWork` и `UserRepository`.
    """

    user_repository: ClassVar[Type[UserRepository]] = UserRepository
    uow: UnitOfWork


    async def register_user(self, data: CreateUserSchema)-> int:
        """Регистрирует нового пользователя.

        Проверяет уникальность email, хеширует пароль и сохраняет запись.

        Args:
            data: Валидационная схема создания пользователя.

        Returns:
            int: Идентификатор созданного пользователя.
        """
        existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=data.email)
        if existing:
            raise ValueError("Пользователь с таким email уже существует")
        
        user_data = data.hash_password()
        user = await self.user_repository(session=self.uow.session).add(data=user_data)
        return user


    async def login_user(self, data: LoginUserSchema, response: Response) -> str:
        """Выполняет аутентификацию пользователя.

        Проверяет пароль и, если успешна, создаёт JWT и кладёт его в cookie.

        Args:
            data: Схема входа (email и пароль).
            response: Ответ FastAPI для установки cookie.

        Returns:
            str: Созданный JWT-токен.
        """
        existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=data.email)
        if existing and existing.is_active:
            valid_password = data.check_password(existing.password)
            if valid_password:
                token = Auth().create_access_token({"email": existing.email,
                                                    "role": existing.role})
                response.set_cookie("access_token", token, httponly=True, secure=False) #В продакшене secure=True, чтобы работал только с Https
                return token 
            else:
                raise ValueError("Неверный пароль")

        raise ValueError("Неверный email")
    

    async def delete_user(self, payload: dict, mode: ModeDelete, response: Response = None, data: UserDeleteScheme = None) -> None:
        """Удаляет аккаунт пользователя.

        Поддерживает SOFT (деактивация) и HARD (физическое удаление) режимы.
        Требует совпадения email из payload и запроса пользователя.
        """
        email = payload["email"]
        match mode:
            case ModeDelete.SOFT:
                existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=email)
                if not existing:
                    raise ValueError("Пользователь не найден")

                if payload["email"] == data.email:
                    raise ValueError("Вы можете удалить только свой аккаунт")
                existing.is_active = False
                response.delete_cookie(
                                    key="access_token",
                                    httponly=True,
                                    secure=False,      
                                    samesite="lax")
                
            case ModeDelete.HARD:
                existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=data.email)
                if not existing:
                    raise ValueError("Пользователь не найден")
                if existing.role == UserRole.ADMIN:
                    raise ValueError("Вы не можете удалить другого админа")
                await self.user_repository(session=self.uow.session).delete(email=data.email)
            case _:
                raise ValueError("Неверный режим удаления")
        return



    async def change_user_role(self, payload: dict, new_role: UserRole, oid_user: str = None, response: Response = None) -> User:
        """Меняет роль пользователя.

        Если указан `oid_user` — меняет роль целевого пользователя (для админов),
        иначе — меняет роль пользователя из payload и очищает cookie токена.

        Returns:
            User: Обновлённый объект пользователя.
        """
        if oid_user:
            existing = await self.user_repository(session=self.uow.session).get_one_or_none(uuid=oid_user)
            if not existing:
                raise ValueError("Пользователь не найден")
            if existing.role == new_role or existing.role == UserRole.ADMIN:
                raise ValueError("Невозможно изменить роль данного пользователя")
            
            
            existing.role = new_role
        else:
            existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=payload["email"])
            if not existing:
                raise ValueError("Пользователь не найден")
            if existing.role == new_role:
                raise ValueError("Ваша роль уже установлена")
            
            existing.role = new_role
            
            response.delete_cookie(
                key="access_token",
                httponly=True,
                secure=False,    
                samesite="lax"
            )
        
        return existing

    async def change_user_password(self, data: ChangePasswordUserSchema, payload: dict) -> None:
        """Сменяет пароль пользователя после проверки текущего пароля."""
        existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=payload["email"])
        if not existing:
            raise ValueError("Пользователь не найден")
        
        if data.check_password(existing.password):
            existing.password = Auth().hash_password(data.new_password)
            return
        
        raise ValueError("Неверный пароль для аккаунта")
    
    async def update_user_profile(self, data: UserUpdateSchema, payload: dict) -> User:
        """Обновляет профиль пользователя (имя/фамилия/отчество)."""
        existing = await self.user_repository(session=self.uow.session).get_one_or_none(email=payload["email"])
        if existing:
            await self.user_repository(session=self.uow.session).edit(data=data, exlude_none=True, email=payload["email"])
            
        return existing
