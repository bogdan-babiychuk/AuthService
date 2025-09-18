import stat
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from src.api.dependencies.user import get_payload
from src.api.schemas.edit_profile import UserUpdateSchema
from src.api.services.utils import ModeDelete
from src.config import settings
from src.api.schemas.login import ChangePasswordUserSchema, LoginUserSchema
from src.api.schemas.delete import UserDeleteScheme
from src.api.schemas.register import CreateUserSchema
from src.api.services.user import UserService
from src.db.engine import get_async_session
from src.db.roles import UserRole
from src.db.uow import UnitOfWork


router = APIRouter()


@router.post(
    "/",
    summary="Регистрация новых пользователей",
    description="Создаёт нового пользователя в системе.",
    status_code=status.HTTP_201_CREATED,
    response_model=dict,
    responses={
        status.HTTP_201_CREATED: {
            "description": "Пользователь успешно зарегистрирован",
            "content": {
                "application/json": {
                    "example": {"201": "Пользователь успешно зарегистрирован"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Ошибка валидации или пользователь уже существует"
        },
    },
)
async def register_user(schema: CreateUserSchema):
    """Регистрация нового пользователя."""
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            await service.register_user(schema)
        return {status.HTTP_201_CREATED: "Пользватель успешно зарегистрирован"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/login",
    summary="Аутентификация пользователей",
    description="Авторизация по email и паролю. Возвращает JWT-токен в cookie.",
    responses={
        status.HTTP_201_CREATED: {
            "description": "Успешная авторизация",
            "content": {
                "application/json": {"example": {"access_token": "jwt_token_here"}}
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Неверные данные или пользователь не найден"
        },
    },
)
async def login_user(data: LoginUserSchema, response: Response):
    """Аутентификация пользователя и установка JWT в cookie."""
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            token = await service.login_user(data=data, response=response)
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет JWT-токен из cookie.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Вы успешно вышли из системы",
            "content": {
                "application/json": {"example": {"200": "Вы успешно вышли из системы"}}
            },
        }
    },
)
async def logout_user(response: Response):
    """Выход пользователя: удаление JWT из cookie."""
    response.delete_cookie(
        key="access_token", httponly=True, secure=False, samesite="lax"
    )
    return {status.HTTP_200_OK: "Вы успешно вышли из системы"}


@router.patch(
    "/password",
    summary="Изменить Пароль",
    description="Позволяет любому пользователю изменить собственный пароль",
    responses={
        status.HTTP_200_OK: {
            "description": "Пароль успешно изменён",
            "content": {
                "application/json": {
                    "example": {"200": "Пароль пользователя успешно изменён"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Неверный пароль"},
        status.HTTP_403_FORBIDDEN: {"description": "Не предоставлен токен"},
    },
)
async def change_user_password(
    request: ChangePasswordUserSchema, payload: Annotated[dict, Depends(get_payload)]
):
    """Смена пароля текущего пользователя."""
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            await service.change_user_password(data=request, payload=payload)
        return {status.HTTP_200_OK: "Пароль пользователя успешно изменён"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/me",
    summary="Редактирование профиля пользователя",
    description="Эндпоинт для изменения имени, фамилии и отчества текущего пользователя",
    status_code=status.HTTP_200_OK,
)
async def update_profile(
    data: UserUpdateSchema,
    payload: Annotated[dict, Depends(get_payload)],
):
    """Частичное обновление профиля текущего пользователя."""
    try:
        async with UnitOfWork(get_async_session) as uof:
            service = UserService(uof)
            await service.update_user_profile(data=data, payload=payload)
        return {"message": "Профиль успешно обновлён"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch(
    "/admin",
    summary="Получить права администратора",
    description="Позволяет простому пользователю получить роль администратора при вводе правильного пароля.",
    responses={
        status.HTTP_200_OK: {
            "description": "Роль успешно изменена на ADMIN",
            "content": {
                "application/json": {
                    "example": {
                        "200": "Админка успешно добавлена! В аккаунт необходимо зайти заново"
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Неверный пароль или пользователь уже админ"
        },
        status.HTTP_403_FORBIDDEN: {"description": "Не предоставлен токен"},
    },
)
async def change_own_role(
    response: Response, payload: Annotated[dict, Depends(get_payload)], password: str
):
    if payload["role"] != UserRole.ADMIN:
        if password == settings.ADMIN_PASSWORD:
            async with UnitOfWork(get_async_session) as uow:
                service = UserService(uow)
                await service.change_user_role(
                    payload, UserRole.ADMIN, response=response
                )

            return {
                status.HTTP_200_OK: f"Админка успешно добавлена!В аккаунт необходимо зайти заново"
            }

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный пароль для админа",
            )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="У вас уже активна роль админа"
    )


@router.delete(
    "/deactivate",
    summary="Мягкое удаление пользователя",
    description="Мягкое удаление аккаунта текущего пользователя из системы, эту операцию может делать владелец аккаунта",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "description": "Пользователь успешно удалён",
            "content": {
                "application/json": {
                    "example": {"200": "Аккаунт user@example.com успешно удален"}
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Пользователь не найден или попытка удаления чужого аккаунта"
        },
    },
)
async def soft_delete_user(
    payload: Annotated[dict, Depends(get_payload)], response: Response
):
    """Мягкое удаление текущего пользователя (деактивация аккаунта)."""
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            await service.delete_user(
                response=response, payload=payload, mode=ModeDelete.SOFT
            )
        return {status.HTTP_200_OK: f"Аккаунт {payload["email"]} успешно удален"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
