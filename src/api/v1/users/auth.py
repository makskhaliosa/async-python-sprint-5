import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from db.crud import crud_user
from core.settings import ACCESS_TOKEN_EXPIRES
from schemas.users import BaseUser, UserGet, UserCreate, Token
from utils.auth import (
    authenticate_user,
    create_access_token,
    hash_password,
    get_current_user,
    validate_password
)

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix='/auth', tags=['auth'])


@auth_router.post(path='/token', response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> Token:
    '''Авторизует пользователя.'''
    user = await authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password
    )

    if not user:
        logger.error('Пользователь не авторизован.')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверный логин или пароль.',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token = create_access_token(
        data={'sub': user.username},
        expires_delta=ACCESS_TOKEN_EXPIRES
    )
    logger.info(f'Пользователь {user.username} авторизован.')
    return Token(access_token=access_token, token_type='Bearer')


@auth_router.post('/register', response_model=UserGet)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    data: UserCreate
) -> UserGet:
    '''Создание пользователя.'''
    if current_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Вы уже авторизованы. Для создания нового пользователя, '
                'выйдите из аккаунта.'
            )
        )

    user_in_db = await crud_user.get_by_username(db=db, username=data.username)
    if user_in_db:
        logger.error('User exists, cant create.')
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Пользователь с таким именем уже существует, попробуйте '
                'другое имя.'
            )
        )

    logger.info(f'Creating user {data.username}')
    validate_password(data.password)
    hashed_pwd = hash_password(data.password)
    data.password = hashed_pwd
    new_user = await crud_user.create(db=db, data_in=data)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Не удалось создать пользователя. Попробуйте позже.'
        )
    logger.info(f'User created {data.username}')
    return new_user


@auth_router.get(path='/user/files', response_model=UserGet)
async def user_status(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[BaseUser, Depends(get_current_user)]
) -> UserGet:
    '''Получить информацию о пользователе.'''
    return current_user
