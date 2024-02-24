import logging
from datetime import timedelta
from functools import partial
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import redis_client
from core.settings import DATA_DIR, REDIS_TTL
from db.crud import crud_file
from db.session import get_session
from schemas.entities import BaseFile, FileCreate, FileFilter
from schemas.users import BaseUser
from utils.auth import get_current_user
from utils.services import get_path_name, run_in_executor, write_data

logger = logging.getLogger(__name__)

file_router = APIRouter(prefix='/files', tags=['files'])


@file_router.post(path='/upload', response_model=BaseFile)
async def upload_file(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    file: UploadFile,
    path: str
) -> BaseFile:
    '''Принимает и сохраняет файл по указанному пути.'''
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Войдите в личный кабинет для доступа к сайту.'
        )

    data = await file.read()

    USER_DIR = DATA_DIR / current_user.username
    path_for_user, data_path, filename = get_path_name(path, USER_DIR)

    path_for_user = f'{current_user.username}/{path_for_user}'

    if not filename:
        filename = file.filename
        data_path = data_path / filename
        path_for_user = f'{path_for_user}/{filename}'
    ext = filename.split('.')[-1]

    await run_in_executor(
        partial(write_data, filepath=data_path, data=data)
    )

    file_schema = FileCreate(
        name=filename,
        path=path_for_user,
        size=file.size,
        extension=ext,
        user_id=current_user.uid
    )

    new_file = await crud_file.create(db=db, data_in=file_schema)
    return new_file


@file_router.get(path='/download', response_class=FileResponse)
async def download_file(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    path: Optional[str] = None,
    file_id: Optional[UUID] = None
) -> FileResponse:
    '''Получает путь до файла или id файла и переадресовывает на нужный url.'''
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Войдите в личный кабинет для доступа к сайту.'
        )

    file_not_found_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Файл не найден в базе, проверьте введенные данные.'
    )

    if path:
        file_name = await redis_client.get(path)
        logger.info(f"Ping successful: {await redis_client.ping()}")
        logger.info(file_name)
        await redis_client.aclose()
        if not file_name:
            file = await crud_file.get_by_path(db=db, path=path)
            if not file:
                raise file_not_found_error

            await redis_client.setex(
                name=path,
                time=timedelta(days=REDIS_TTL),
                value=file.name
            )
            await redis_client.aclose()
            file_name = file.name

        file_url = f'{DATA_DIR}/{path}'
        return FileResponse(path=file_url, filename=file_name)

    elif file_id:
        file_name = await redis_client.get(file_id)
        logger.info(f"Ping successful: {await redis_client.ping()}")
        logger.info(file_name)
        await redis_client.aclose()
        if not file_name:
            file = await crud_file.get(db=db, fid=file_id)
            if not file:
                raise file_not_found_error

            await redis_client.setex(
                name=file_id,
                time=timedelta(days=REDIS_TTL),
                value=file.name
            )
            await redis_client.aclose()

        file_url = f'{DATA_DIR}/{file.path}'
        return FileResponse(path=file_url, filename=file.name)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Введите путь к файлу или его id.'
    )


@file_router.post(path='/search', response_model=List[BaseFile])
async def file_search(
    db: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[BaseUser, Depends(get_current_user)],
    options: Optional[FileFilter] = None
) -> List[BaseFile]:
    '''Возвращает список файлов по заданным параметрам.'''
    filters = {k: v for k, v in options.model_dump().items() if v}
    filters.update({'user_id': current_user.uid})
    logger.info(filters)
    result = await crud_file.get_by_filters(db=db, options=filters)
    return result
