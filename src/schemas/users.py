from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from .entities import BaseFile, ConfigDict


class BaseUser(BaseModel):
    '''Схема в базе данных.'''
    uid: int
    username: str
    password: str
    files: List[BaseFile]

    model_config = ConfigDict(from_attribute=True)


class UserCreate(BaseModel):
    '''Схема при создании объекта.'''
    username: str
    password: str


class UserUpdate(BaseModel):
    '''Схема при обновлении объекта.'''
    username: Optional[str]
    password: Optional[str]


class Token(BaseModel):
    '''Схема токена для авторизации.'''
    access_token: str
    token_type: str


class TokenData(BaseModel):
    '''Схема данных после проверки токена.'''
    username: str
