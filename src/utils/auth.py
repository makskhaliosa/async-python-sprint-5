import logging
import re
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import app_settings, oauth2_scheme, pwd_context
from db.session import get_session
from db.crud import crud_user
from schemas.users import BaseUser, TokenData

logger = logging.getLogger(__name__)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    '''Верифицирует совпадение введенного пароля с зашифрованным.'''
    return pwd_context.verify(raw_password, hashed_password)


def hash_password(raw_password: str) -> str:
    '''Хэширует пароль пользователя.'''
    return pwd_context.hash(raw_password)


def validate_password(raw_password: str) -> bool:
    '''Валидирует пароль пользователя при создании.'''
    pwd_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=(
            'Пароль должен содержать минимум 6 символов, цифры и буквы '
            'латинского алфавита. В пароле не должно быть небуквенных '
            'символов, таких как ",.<>?:[]()/\\{}|".'
        )
    )
    try:
        forbidden_chars = r'[\,\.\<\>\?\:\[\]\(\)\/\\\{\}\|\"\.]'
        upper_chars = r'[A-Z]+'
        lower_chars = r'[a-z]+'
        numbers = r'[0-9]+'
        if (
            len(raw_password) < 6
            or re.search(forbidden_chars, raw_password)
            or not re.search(upper_chars, raw_password)
            or not re.search(lower_chars, raw_password)
            or not re.search(numbers, raw_password)
        ):
            logger.error('Error validating password')
            raise pwd_error
        else:
            return True
    except AttributeError as err:
        logger.error(f'Attr error validating password {err}', exc_info=True)
    except ValueError as err:
        logger.error(f'Value error validating password {err}', exc_info=True)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_session)]
) -> BaseUser:
    '''
    Проверяет токен пользователя.

    Если пользователь найден, возвращает объект пользователя.
    '''
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Логин и пароль не найдены, попробуйте снова.',
        headers={'WWW-Authenticate': 'Bearer'}
    )
    if not token:
        return None

    try:
        payload = jwt.decode(
            token,
            app_settings.CRYPTO_SECRET_KEY,
            algorithms=[app_settings.CRYPTO_ALGORITHM]
        )
    except JWTError as err:
        logger.error(f'Error checking user token: {err}')
        raise credentials_error

    username = payload.get('sub')
    if username is None:
        raise credentials_error
    token_data = TokenData(username=username)
    user = await crud_user.get_by_username(
        db=db,
        username=token_data.username
    )
    if user is None:
        logger.error(f'User {username} not found')
        raise credentials_error
    return user


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str
) -> BaseUser:
    '''Авторизует и возвращает пользователя.'''
    try:
        user = await crud_user.get_by_username(db=db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user
    except Exception as err:
        logger.error(f'Error authenticating user {err}.', exc_info=True)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: timedelta = timedelta(days=1)
) -> str:
    '''Генерирует новый токен.'''
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(
            to_encode,
            app_settings.CRYPTO_SECRET_KEY,
            algorithm=app_settings.CRYPTO_ALGORITHM
        )
        return encoded_jwt
    except Exception as err:
        logger.error(f'Error creating token {err}', exc_info=True)
