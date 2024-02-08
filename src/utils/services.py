import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Awaitable, Callable, Optional, Tuple

from fastapi import HTTPException, status
from pydantic import FilePath

logger = logging.getLogger(__name__)


def write_data(filepath: FilePath, data: bytes | str):
    '''Сохраняет данные в файл filepath.'''
    try:
        mode = 'wb'
        if isinstance(data, str):
            mode = 'w'
        with open(filepath, mode=mode) as f:
            f.write(data)
    except Exception as err:
        logger.error(f'Error writing data {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Ошибка при сохранении файла, попробуйте позже.'
        )


async def run_in_executor(func: Callable) -> Awaitable:
    '''Выполнить блокирующую операцию в отдельном потоке.'''
    try:
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, func)
        return result
    except Exception as err:
        logger.error(f'Error in run in executor {err}', exc_info=True)


def get_path_name(
    filepath: str,
    base_dir: Path
) -> Tuple[str, Path, Optional[str]]:
    '''Проверяет путь к файлу на корректность и наличие названия файла.'''
    try:
        # Убираем лишние слэши вначале, если такие есть
        paths = [path for path in filepath.split('/') if path]
        filename = paths[-1] if '.' in paths[-1] else None
        filepath = '/'.join(paths)

        # Создаем директории, указанные пользователем, если они еще не созданы
        data_dir = '/'.join(paths[:-1]) if filename else '/'.join(paths)
        data_path = base_dir.joinpath(data_dir)

        if not data_path.exists():
            logger.info(f'Created dir {filepath}')
            data_path.mkdir(parents=True, exist_ok=True)

        if filename:
            data_path = base_dir.joinpath(filepath)
        return filepath, data_path, filename
    except IndexError as err:
        logger.error(f'Index error in get_path_name {err}', exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Нужно указать путь к файлу или директории.'
        )
