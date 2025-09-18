from typing import Annotated
from fastapi import Depends, HTTPException, Request

from src.auth.jwt import Auth


async def get_token(request: Request)-> str:
    """Извлекает JWT из cookie запроса.

    Поднимает 401, если токен отсутствует.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Вы не аутентифицированы")
    return token


async def get_payload(token:str = Depends(get_token)):
    """Декодирует JWT и возвращает payload."""
    payload = Auth().decode_token(token)
    return payload

UserTokenDep = Annotated[str, Depends(get_token)]
PayloadDep = Annotated[dict, Depends(get_payload)]