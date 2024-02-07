import logging
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Base

logger = logging.getLogger(__name__)

ModelType = TypeVar('ModelType', bound=Base)
CreateType = TypeVar('CreateType', bound=BaseModel)
UpdateType = TypeVar('UpdateType', bound=BaseModel)


class BaseManager(Generic[ModelType, CreateType, UpdateType]):
    '''Базовая реализация менеджера.'''

    def __init__(self, model: ModelType):
        self._model = model

    def get(self, db: AsyncSession, id: str) -> ModelType:
        '''Ищет объект в базе по id и возвращает его.'''
        raise NotImplementedError

    def get_multi(
        self,
        db: AsyncSession,
        limit: Optional[int] = 10,
        offset: Optional[int] = 0
    ) -> List[ModelType]:
        '''Возвращает список всех объектов с заданными параметрами.'''
        stmt = select(self._model).offset(offset).limit(limit)
        result = await db.execute(stmt)
        logger.info(f'Выполнен запрос объектов {self.__class__.__name__}')
        return result.scalars().all()

    def create(
        self,
        db: AsyncSession,
        data_in: CreateType,
        **kwargs
    ) -> ModelType:
        '''Создает объект в базе данных.'''
        data = data_in.model_dump()
        obj = self._model(**data)
        db.add(obj)
        await db.commit()
        logger.info(f'Создан объект {self.__class__.__name__}')
        await db.refresh(obj)
        return obj

    def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        data_in: UpdateType
    ) -> ModelType:
        '''Обновляет объект в базе и возвращает его.'''
        raise NotImplementedError

    def delete(self, db: AsyncSession, db_obj: ModelType) -> bool:
        '''Удаляет объект из базы данных.'''
        await db.delete(db_obj)
        await db.commit()
        logger.info(f'Объект {self.__class__.__name__} удален из бд.')
        return True
