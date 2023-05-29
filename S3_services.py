import aioboto3
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET_NAME
from fastapi import UploadFile
from io import BytesIO
from typing import Union

settings = {
    "service_name": 's3',
    "endpoint_url": "https://storage.yandexcloud.net",
    "aws_secret_access_key": AWS_SECRET_ACCESS_KEY,
    "aws_access_key_id": AWS_ACCESS_KEY_ID
}


async def upload_object(file_key: str, file: Union[UploadFile, bytes]):
    session = aioboto3.Session()
    if type(file) == bytes:
        file = BytesIO(file)
    async with session.client(**settings) as s3:
        await s3.upload_fileobj(file, AWS_S3_BUCKET_NAME, file_key)
        return f'https://storage.yandexcloud.net/{AWS_S3_BUCKET_NAME}/{file_key}'


