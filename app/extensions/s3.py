import boto3

from app.backends.bucket import Bucket
from app.config import settings
from fastapi import status


class S3Bucket(Bucket):

    def __init__(self):
        self.client = boto3.resource(
            service_name=settings.BUCKET_SERVICE_NAME,
            region_name=settings.BUCKET_REGION,
            aws_access_key_id=settings.BUCKET_ACCESS_KEY_ID,
            aws_secret_access_key=settings.BUCKET_SECRET_ACCESS_KEY,
            endpoint_url=settings.BUCKET_ENDPOINT_URL,
        )

    def save_file(self, file: any, key: str):
        try:
            self.client.Bucket(settings.BUCKET_NAME).upload_fileobj(
                file,
                key,
            )
        except Exception as e:
            print(f"Error on upload file {e}")
            raise

    def get_file(self, key: str) -> str:
        try:
            path = f"./app/tmp/{key}"
            self.client.Bucket(settings.BUCKET_NAME).download_file(
                key, path
            )
            return path
        except Exception as e:
            print(f"Error on download file {e}")
            raise

    def delete_file(self, key: str):
        try:
            bucket = self.client.Bucket(settings.BUCKET_NAME)
            resp = bucket.delete_objects(
                Delete={
                    'Objects': [
                        {
                            'Key': key
                        }
                    ]
                }
            )
            if resp['ResponseMetadata'].get(
                'HTTPStatusCode'
            ) != status.HTTP_200_OK:
                raise ValueError(f'Error on delete file {key}')
        except Exception as e:
            print(f"Error on deleting file {e}")
            raise
