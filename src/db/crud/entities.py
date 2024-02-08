import logging
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User, File
from schemas.entities import FileCreate, FileUpdate
from schemas.users import UserCreate, UserUpdate
from .base import BaseManager

logger = logging.getLogger(__name__)


class UserManager(BaseManager[User, UserCreate, UserUpdate]):
    async def get(self, db: AsyncSession, uid: str) -> User:
        '''Ищет объект в базе по uid и возвращает его.'''
        try:
            stmt = select(self._model).where(self._model.uid == uid)
            obj = await db.execute(stmt)
            logger.info(f'Запрошен объект User {uid}')
            return obj.scalar_one_or_none()
        except Exception as err:
            logger.error(f'Error getting by uid {err}', exc_info=True)

    async def get_by_username(self, db: AsyncSession, username: str) -> User:
        '''Ищет объект в базе по username и возвращает его.'''
        try:
            stmt = select(self._model).where(self._model.username == username)
            obj = await db.execute(stmt)
            logger.info(f'Запрошен объект User {username}')
            return obj.scalar_one_or_none()
        except Exception as err:
            logger.error(f'Error getting by username {err}', exc_info=True)

    async def update(
        self,
        db: AsyncSession,
        db_obj: User,
        data_in: UserUpdate
    ) -> User:
        '''Обновляет объект в базе и возвращает его.'''
        try:
            data = data_in.model_dump()
            stmt = (
                update(self._model).
                where(self._model.uid == db_obj.uid).
                values(**data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f'Обновлен объект User {db_obj.username}')
            return db_obj
        except Exception as err:
            logger.error(f'Error updating user {err}', exc_info=True)


class FileManager(BaseManager[File, FileCreate, FileUpdate]):
    async def get(self, db: AsyncSession, fid: str) -> File:
        '''Ищет объект в базе по fid и возвращает его.'''
        try:
            stmt = select(self._model).where(self._model.fid == fid)
            obj = await db.execute(stmt)
            logger.info(f'Запрошен объект File {fid}')
            return obj.scalar_one_or_none()
        except Exception as err:
            logger.error(f'Error getting by fid {err}', exc_info=True)

    async def get_by_path(self, db: AsyncSession, path: str) -> File:
        '''Ищет объект в базе по path и возвращает его.'''
        try:
            stmt = select(self._model).where(self._model.path == path)
            obj = await db.execute(stmt)
            logger.info(f'Запрошен объект File {path}')
            return obj.scalar_one_or_none()
        except Exception as err:
            logger.error(f'Error getting by path {err}', exc_info=True)

    async def get_by_filters(self, db: AsyncSession, **options) -> List[File]:
        '''Ищет объекты в соответствии с заданными фильтрами.'''
        ordering = None
        limit = None
        stmt = select(self._model)

        if options.get('order_by'):
            ordering = options.pop('order_by')
            stmt = stmt.order_by(ordering)
        if options.get('limit'):
            limit = options.pop('limit')
            stmt = stmt.limit(limit)
        if options.get('query'):
            name = options.pop('query')
            stmt = stmt.where(self._model.name.like(f'%{name}%'))

        stmt = stmt.filter_by(**options)
        result = await db.execute(stmt)
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        db_obj: File,
        data_in: FileUpdate
    ) -> File:
        '''Обновляет объект в базе и возвращает его.'''
        try:
            data = data_in.model_dump()
            stmt = (
                update(self._model).
                where(self._model.fid == db_obj.fid).
                values(**data)
            )
            await db.execute(stmt)
            await db.commit()
            await db.refresh(db_obj)
            logger.info(f'Обновлен объект File {db_obj.path}')
            return db_obj
        except Exception as err:
            logger.error(f'Error updating file {err}', exc_info=True)


crud_user = UserManager(User)
crud_file = FileManager(File)
