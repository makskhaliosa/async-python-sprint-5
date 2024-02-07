import logging
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import User, File
from src.schemas.entities import FileCreate, FileUpdate
from src.schemas.users import UserCreate, UserUpdate
from .base import BaseManager

logger = logging.getLogger(__name__)


class UserManager(BaseManager[User, UserCreate, UserUpdate]):
    def get(self, db: AsyncSession, uid: str) -> User:
        '''Ищет объект в базе по uid и возвращает его.'''
        stmt = select(self._model).where(self._model.uid == uid)
        obj = await db.execute(stmt)
        logger.info(f'Запрошен объект User {uid}')
        return obj.scalar_one_or_none()

    def get_by_username(self, db: AsyncSession, username: str) -> User:
        '''Ищет объект в базе по username и возвращает его.'''
        stmt = select(self._model).where(self._model.username == username)
        obj = await db.execute(stmt)
        logger.info(f'Запрошен объект User {username}')
        return obj.scalar_one_or_none()

    def update(
        self,
        db: AsyncSession,
        db_obj: User,
        data_in: UserUpdate
    ) -> User:
        '''Обновляет объект в базе и возвращает его.'''
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


class FileManager(BaseManager[File, FileCreate, FileUpdate]):
    def get(self, db: AsyncSession, fid: str) -> File:
        '''Ищет объект в базе по fid и возвращает его.'''
        stmt = select(self._model).where(self._model.fid == fid)
        obj = await db.execute(stmt)
        logger.info(f'Запрошен объект File {fid}')
        return obj.scalar_one_or_none()

    def get_by_path(self, db: AsyncSession, path: str) -> File:
        '''Ищет объект в базе по username и возвращает его.'''
        stmt = select(self._model).where(self._model.path == path)
        obj = await db.execute(stmt)
        logger.info(f'Запрошен объект File {path}')
        return obj.scalar_one_or_none()

    def update(
        self,
        db: AsyncSession,
        db_obj: File,
        data_in: FileUpdate
    ) -> File:
        '''Обновляет объект в базе и возвращает его.'''
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


crud_user = UserManager(User)
crud_file = FileManager(File)
