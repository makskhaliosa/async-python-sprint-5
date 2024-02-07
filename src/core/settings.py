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
    PORT: int
    ACCESS_TOKEN_EXPIRE_DAYS: int
    # для получения секретного ключа в командной строке зпустите команду:
    # openssl rand -hex 32
    CRYPTO_SECRET_KEY: str
    CRYPTO_ALGORITHM: str
    POSTGRES_DSN: str


app_settings = Settings()

# Конфиг логера
config.dictConfig(LOGGING_CONFIG)

# Схема авторизации пользователей
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token', auto_error=False)

# Схема шифрования пароля пользователя
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Время действия токена авторизации
ACCESS_TOKEN_EXPIRES = timedelta(
    days=app_settings.ACCESS_TOKEN_EXPIRE_DAYS
)

# sqlalchemy url
SA_URL = app_settings.POSTGRES_DSN
