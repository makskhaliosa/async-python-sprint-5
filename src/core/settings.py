from pathlib import Path
from datetime import timedelta
from logging import config

from fastapi.security.oauth2 import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

from .logger import LOGGING_CONFIG


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

    APP_TITLE: str = 'File Storage'
    HOST: str
    HOST_TEST: str
    PORT: int
    ACCESS_TOKEN_EXPIRE_DAYS: int
    # для получения секретного ключа в командной строке зпустите команду:
    # openssl rand -hex 32
    CRYPTO_SECRET_KEY: str
    CRYPTO_ALGORITHM: str
    POSTGRES_DSN: str
    POSTGRES_DSN_TEST: str
    ALLOWED_ORIGINS: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_HOST_TEST: str
    TESTING: bool


app_settings = Settings()

# Конфиг логера
config.dictConfig(LOGGING_CONFIG)

# Схема авторизации пользователей
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/token', auto_error=False)

# Схема шифрования пароля пользователя
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Время действия токена авторизации
ACCESS_TOKEN_EXPIRES = timedelta(
    days=app_settings.ACCESS_TOKEN_EXPIRE_DAYS
)

# sqlalchemy url
SA_URL = (
    app_settings.POSTGRES_DSN_TEST
    if app_settings.TESTING
    else app_settings.POSTGRES_DSN
)

APP_HOST = (
    app_settings.HOST_TEST
    if app_settings.TESTING
    else app_settings.HOST
)


# Корневая директория
BASE_DIR = Path().resolve()
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)
BASE_URL = f'http://{APP_HOST}:{app_settings.PORT}'

# Redis settings
REDIS_TTL = 1  # TTL в днях
