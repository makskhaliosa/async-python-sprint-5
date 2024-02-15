from boto3 import client

from .settings import app_settings


s3 = client(
    service_name='s3',
    region_name='ru-1',
    endpoint_url='https://s3.ru-1.storage.selcloud.ru',
    aws_access_key_id=app_settings.S3_ACCESS_KEY,
    aws_secret_access_key=app_settings.S3_SECRET_KEY
)
