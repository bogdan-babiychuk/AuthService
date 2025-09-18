from random import choice
from fastapi import APIRouter, Depends, HTTPException, Path, status
from typing import Annotated
from src.api.dependencies.user import get_payload
from src.api.services.user import UserService
from src.api.services.utils import JOKES, ModeDelete
from src.api.schemas.delete import UserDeleteScheme
from src.db.engine import get_async_session
from src.db.roles import UserRole
from src.db.uow import UnitOfWork


router = APIRouter()

@router.patch(
    "/{user_oid}/role",
    summary="Изменение роли пользователя (только для админа)",
    description="Администратор может изменить роль другого пользователя.",
    responses={
        status.HTTP_200_OK: {
            "description": "Роль изменена",
            "content": {
                "application/json": {
                    "example": {
                        "200": "Роль пользователя успешно изменена, вступит в силу после перезахода"
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Ошибка изменения роли"},
        status.HTTP_403_FORBIDDEN: {"description": "Недостаточно прав"},
    },
)
async def change_user_role(
    user_oid: Annotated[str, Path(description="UUID пользователя")],
    payload: Annotated[dict, Depends(get_payload)],
    role: UserRole,
):
    """Изменяет роль указанного пользователя (только для админа)."""
    if payload["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для изменения роли пользователя",
        )
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            await service.change_user_role(payload, role, oid_user=user_oid)
        return {status.HTTP_200_OK: f"Роль пользователя успешно изменена, роль будет активна когда пользователь перезайдёт в аккаунт"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    


@router.delete(
    "/",
    summary="Перманентное удаление пользователя",
    description="Полное удаление пользователей, делают только админы",
    responses={
        status.HTTP_200_OK: {
            "description": "Пользователь успешно удалён",
            "content": {
                "application/json": {
                    "example": {
                        "200": "Пользователь user@com успешно удалён"
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {"description": "Ошибка удаления пользователя"},
        status.HTTP_403_FORBIDDEN: {"description": "Недостаточно прав"},
    }
)
async def hard_delete_user(
    request: UserDeleteScheme,
    payload: Annotated[dict, Depends(get_payload)],
):
    """Полное удаление пользователя (только для админа)."""
    if payload["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления пользователя") 
    try:
        async with UnitOfWork(get_async_session) as uow:
            service = UserService(uow)
            await service.delete_user(data=request, payload=payload, mode=ModeDelete.HARD)
        return {status.HTTP_200_OK: f"Пользователь {request.email} успешно удалён"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/admin/joke",
    summary="Админская шутка",
    description="Эндпоинт доступен только администраторам. Возвращает случайное забавное сообщение.",
    status_code=status.HTTP_200_OK,
)
async def admin_joke(
    _: Annotated[dict, Depends(get_payload)]
):
    """Возвращает случайную шутку. Доступно только администраторам."""
    joke = choice(JOKES)
    return {"message": joke} 