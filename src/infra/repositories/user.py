from dataclasses import dataclass
from typing import ClassVar, Type
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession 

from src.db.model_user import User
from src.infra.repositories.base import BaseRepository

@dataclass
class UserRepository(BaseRepository):
    """Репозиторий для модели `User`.

    Содержит CRUD-методы, работающие через `AsyncSession` и SQLAlchemy Core.
    """
    model: ClassVar[Type[User]] = User
    session: AsyncSession

    async def get_all(self):
        """Возвращает список всех пользователей."""
        query = select(self.model)
        result = await self.session.execute(query)
        users = result.scalars().all()
        return users
    
    async def get_one_or_none(self, **filter_by):
        """Возвращает одного пользователя по фильтрам или None."""
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().one_or_none()

    
    async def add(self, data: BaseModel):
        """Создаёт пользователя и возвращает его идентификатор."""
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()
    
    async def edit(self, data: BaseModel, exclude_unset: bool = False, exlude_none: bool = False, **filter_by):
        """Обновляет поля пользователя и возвращает идентификатор."""
        stmt = update(self.model).filter_by(**filter_by).values(**data.model_dump(exclude_unset=exclude_unset, exclude_none=exlude_none)).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def delete(self, **filter_by):
        """Удаляет пользователя по фильтрам и возвращает идентификатор удалённой записи."""
        stmt = delete(self.model).filter_by(**filter_by).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()