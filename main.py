from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.api.handlers.user_handlers import router as user_router
from src.api.handlers.admin_handlers import router as admin_router
from src.api.handlers.mock_handlers import router as mock_router
from src.db.engine import engine
from src.db.engine import async_run_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await async_run_db()
    yield
    await engine.dispose()


def create() -> FastAPI:

    app = FastAPI(
        title="AuthService",
        description="Тестовое задание авторизации и аутентификации",
        docs_url="/api/docs",
        lifespan=lifespan,
    )

    app.include_router(prefix="/api/v1/users", router=user_router, tags=["Users"])
    app.include_router(prefix="/api/v1/users", router=admin_router, tags=["Admin"])
    app.include_router(prefix="/api/v1/mock", router=mock_router, tags=["Mock"])
    return app
