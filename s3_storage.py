import logging
from typing import BinaryIO, Dict
from dataclasses import dataclass

from minio import Minio


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
    

    def fetch_file(self, bucket_name, file_name) -> BinaryIO:
        object = self.client.get_object(bucket_name, file_name)
        return object
    
    def list_files(self, bucket_name):
        """List all files in a specified bucket."""
        objects = self.client.list_objects(bucket_name, include_user_meta=True)
        def _to_public_url(obj):
            if not len(self.public_url):
                return None
            if obj.is_dir: 
                return None
            return f"{self.public_url}/{obj.bucket_name}/{obj.object_name}"
        
        def _to_dict(obj):
            last_modified = obj.last_modified.strftime('%Y-%m-%dT%H:%M:%S%z') if obj.last_modified else None
            return {
                "bucket_name": obj.bucket_name,
                "object_name": obj.object_name,
                "size": obj.size,
                "metadata": obj.metadata,
                "etag": obj.etag,
                "last_modified": last_modified,
                "url": _to_public_url(obj)
            }
        
        return [_to_dict(obj) for obj in objects]


    def put_file(self, bucket_name, file_name, content: BinaryIO, length:int, content_type:str=None, metadata: Dict = None):
        """
        Upload a file to the specified MinIO bucket.

        Args:
            bucket_name (str): Name of the target bucket.
            file_path (str): Path to the local file to upload.
            file_name (str, optional): Object name in MinIO. Defaults to None which uses the filename from file_path.
        """
        result = self.client.put_object(bucket_name, file_name, content, length, content_type=content_type, metadata=metadata)
        self.logger.info(result)
        return {
            "status": "success",
            "object": {
                "bucket": result.bucket_name,
                "name": result.object_name,
                "etag": result.etag,
                "last_modified": result.last_modified,
                "version_id": result.version_id,
                "location": result.location,
            }
        }
