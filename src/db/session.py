from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from core.settings import SA_URL

engine = create_async_engine(
    url=SA_URL,
    future=True
)

async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_session() -> AsyncSession:
    '''Генерирует новую сессию для операций с БД.'''
    async with async_session() as session:
        yield session
