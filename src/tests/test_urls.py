import io
import random
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import status

from src.core.settings import BASE_URL
from src.main import app

# Относительные url приложения
register = '/api/auth/register'
login = '/api/auth/token'
user_files = '/api/auth/user/files'
upload_file = '/api/files/upload'
download_file = '/api/files/download'
search_file = '/api/files/search'

pytestmark = pytest.mark.asyncio(scope='session')


@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncGenerator[AsyncClient, Any]:
    '''Асинхронный клиент для pytest.'''
    async with AsyncClient(app=app, base_url=BASE_URL) as client:
        yield client


class TestUrls:
    '''Класс с тестами конечных точек.'''

    uploaded_path = 'data'
    upload_filename = 'test.txt'
    serach_data = {
        'query': 'test'
    }
    download_path = 'testuser/data/test.txt'
    create_user_data = {
        'username': f'testuser{random.randrange(1, 1000)}',
        'password': 'Changeme1!'
    }
    login_data = {
        'username': 'testuser2',
        'password': 'Changeme1!'
    }
    tmp_file_content = 'Test content.'
    auth_headers = {
        'Authorization': ''
    }

    async def test_register_user(self, client: AsyncClient):
        '''Проверяет доступность url для создания пользователя.'''
        response = await client.post(
            register,
            json=self.create_user_data
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()['username'] == self.create_user_data['username']

    async def test_login_user(self, client: AsyncClient):
        '''
        Проверяет доступность url для авторизации пользователя.

        Проверяет корректность возвращаемых данных.'''
        await client.post(register, json=self.login_data)
        login_response = await client.post(
            login,
            data=self.login_data
        )
        login_data = login_response.json()
        assert login_response.status_code == status.HTTP_200_OK
        assert 'access_token' in login_data
        assert login_data['token_type'] == 'Bearer'

    # Не знаю как протестировать загрузку файлов
    async def test_file_uploaded(
        self,
        client: AsyncClient,
        tmp_path_factory: pytest.TempPathFactory
    ):
        '''Проверяет url для загрузки файлов.'''
        login_response = (await client.post(
            login,
            data=self.login_data
        )).json()
        self.auth_headers['Authorization'] = (
            f'{login_response["token_type"]} {login_response["access_token"]}'
        )

        temp_file = tmp_path_factory.mktemp('text') / self.upload_filename

        temp_file.write_text(self.tmp_file_content, encoding='utf-8')

        with open('data/test6/docs/win.docs', mode='rb') as f:
            file_bytes = io.BytesIO(f.read())

            data = {'upload-file': file_bytes}

            response = await client.post(
                upload_file, files=data, headers=self.auth_headers
            )
            assert response.status_code == status.HTTP_200_OK
            assert response.json().get('path') == self.download_path

    async def test_user_files(self, client: AsyncClient):
        '''Проверяет url с информацией о файлах пользователя.'''
        login_response = (await client.post(
            login,
            data=self.login_data
        )).json()
        self.auth_headers['Authorization'] = (
            f'{login_response["token_type"]} {login_response["access_token"]}'
        )

        files_response = await client.get(
            user_files,
            headers=self.auth_headers
        )

        assert files_response.status_code == status.HTTP_200_OK
        files_response = files_response.json()
        files_in_db = files_response.get('files')
        assert len(files_in_db) > 0
        assert files_in_db[0].get('path') == self.download_path
