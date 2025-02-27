import logging
from typing import BinaryIO, Dict
from dataclasses import dataclass
from datetime import datetime

from minio import Minio
from minio.helpers import ObjectWriteResult
from minio.datatypes import Object

@dataclass
class CreatedFileObject:
    bucket_name: str
    object_name: str
    etag: str
    
    @classmethod
    def from_response(cls, response: ObjectWriteResult):
        return cls(
            bucket_name=response.bucket_name,
            object_name=response.object_name,
            etag=response.etag,
        )

    
class S3Storage:
    client: Minio
    logger: logging.Logger
    public_url: str
    
    def __init__(self, host: str, access_key: str, secret_key: str, logger: logging.Logger, secure: bool=False, public_url=""):
        # Initialize Minio client
        self.logger = logger
        self.logger.info(f"Initializing S3 client with host: {host}, access_key: {access_key[:4]}..., secret_key: {secret_key[:4]}..., secure: {secure}")
        self.client = Minio(
            host,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            )
        self.public_url = public_url
    
    def put_file(self, bucket_name, file_name, content: BinaryIO, length:int, content_type:str=None, metadata: Dict = None) -> CreatedFileObject:
        """
        Upload a file to the specified MinIO bucket.

        Args:
            bucket_name (str): Name of the target bucket.
            file_path (str): Path to the local file to upload.
            file_name (str, optional): Object name in MinIO. Defaults to None which uses the filename from file_path.
        """
        result = self.client.put_object(bucket_name, file_name, content, length, content_type=content_type, metadata=metadata)
        self.logger.info(result)
        return CreatedFileObject.from_response(result)

    def get_public_url(self, file_object: CreatedFileObject) -> str | None:
        if not len(self.public_url):
            return None
        return f"{self.public_url}/{file_object.bucket_name}/{file_object.object_name}"
