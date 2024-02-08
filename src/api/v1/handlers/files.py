import logging
from functools import partial
from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import DATA_DIR
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
    filepath, data_path, filename = get_path_name(path, USER_DIR)
    if not filename:
        filename = file.filename
        data_path = data_path / filename
    ext = filename.split('.')[-1]

    await run_in_executor(
        partial(write_data, filepath=data_path, data=data)
    )

    file_schema = FileCreate(
        name=filename,
        path=filepath,
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

    USER_DIR = f'{DATA_DIR}/{current_user.username}'
    if path:
        file = await crud_file.get_by_path(db=db, path=path)
        if not file:
            raise file_not_found_error

        file_url = f'{USER_DIR}/{path}'
        return FileResponse(path=file_url, filename=file.name)

    elif file_id:
        file = await crud_file.get(db=db, fid=file_id)
        if not file:
            raise file_not_found_error

        file_url = f'{USER_DIR}/{file.path}'
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
    filters = {'user_id': current_user.uid}
    result = await crud_file.get_by_filters(db=db, **filters)
    return result
