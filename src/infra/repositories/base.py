from abc import ABC
from dataclasses import dataclass
from sqlalchemy.orm import Session
from typing import ClassVar, Type
from unittest.mock import Base


@dataclass
class BaseRepository(ABC):
    """Базовый абстрактный репозиторий для работы с моделями БД."""

    model: ClassVar[Type[Base]]

    async def get_all(self):
        """Возвращает все записи модели."""
        raise NotImplementedError()

    async def get_one_or_none(self, **filter_by):
        """Возвращает одну запись по фильтру или None."""
        raise NotImplementedError()

    async def add(self, data):
        """Создаёт запись и возвращает её идентификатор."""
        raise NotImplementedError()

    async def edit(self, data, exclude_unset: bool = False, **filter_by):
        """Обновляет запись по фильтру и возвращает идентификатор."""
        raise NotImplementedError()

    async def delete(self, **filter_by):
        """Удаляет запись по фильтру и возвращает идентификатор."""
        raise NotImplementedError()
