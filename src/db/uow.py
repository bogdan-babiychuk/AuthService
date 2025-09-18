from sqlalchemy.ext.asyncio import AsyncSession
from typing import Callable

class UnitOfWork:
    """Единица работы (Unit of Work) для управления транзакцией.

    Создаёт сессию при входе в контекст, коммитит при успехе
    и делает откат при ошибке, затем закрывает сессию.
    """
    def __init__(self, session_factory: callable):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self.session_factory()  # создаём сессию
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()