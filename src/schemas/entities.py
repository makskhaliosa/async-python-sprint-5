from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseFile(BaseModel):
    '''Схема объекта в БД.'''
    fid: str
    name: str
    created: datetime
    path: str
    size: float | int
    extension: str
    user_id: str

    model_config = ConfigDict(from_attribute=True)


class FileCreate(BaseModel):
    '''Схема данных для создания объекта.'''
    name: str
    path: str
    size: float | int
    extension: str
    user_id: str


class FileUpdate(BaseModel):
    '''Схема данных для обновления объекта.'''
    name: Optional[str]
    path: Optional[str]
    size: Optional[float, int]
    extension: Optional[str]
    user_id: Optional[str]
