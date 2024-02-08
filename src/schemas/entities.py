from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseFile(BaseModel):
    '''Схема объекта в БД.'''
    fid: UUID
    name: str
    created: datetime
    path: str
    size: float | int
    extension: str
    user_id: UUID

    model_config = ConfigDict(from_attribute=True)


class FileCreate(BaseModel):
    '''Схема данных для создания объекта.'''
    name: str
    path: str
    size: float | int
    extension: str
    user_id: UUID


class FileUpdate(BaseModel):
    '''Схема данных для обновления объекта.'''
    name: Optional[str]
    path: Optional[str]
    size: Union[float, int, None]
    extension: Optional[str]
    user_id: Optional[UUID]


class FileFilter(BaseModel):
    '''Набор фильтров для файлов.'''
    path: Optional[str] = None
    extension: Optional[str] = None
    order_by: Optional[str] = None
    limit: Optional[int] = None
    query: Optional[str] = None
