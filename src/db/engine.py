from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.db.model_user import Base

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


def get_async_session() -> AsyncSession:
    """Возвращает новую асинхронную сессию БД."""
    return async_session()


async def async_run_db():
    """Создаёт все таблицы в БД (инициализация схемы)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
