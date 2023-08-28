"""Helper functions for OSP-utilities."""
import io
import os
from uuid import uuid4

from minio import Minio
from urllib3.response import HTTPResponse

from .exceptions import MinioConnectionError, MinioDownloadError


def _get_upload(filepath: str, uuid: str, minio_client: Minio) -> str:
    """Helper function for `depends_upload` and `get_upload`."""
    suffix = os.path.splitext(filepath)[-1]
    # Generate a unique UUID as the object key
    object_key = uuid or str(uuid4())

    # Upload the file to MinIO
    try:
        if not minio_client.bucket_exists(object_key):
            minio_client.make_bucket(object_key)
        minio_client.fput_object(
            object_key,
            object_key,
            filepath,
            metadata={"suffix": suffix},
        )
    except Exception as err:
        raise MinioConnectionError(err.args) from err
    return object_key


def _get_download(uuid: str, minio_client: Minio) -> HTTPResponse:
    """Helper function for `depends_download` and `get_download`."""
    file_data = io.BytesIO()
    if not minio_client.bucket_exists(uuid):
        raise MinioDownloadError("Bucket does not exist.")
    try:
        response = minio_client.get_object(
            uuid,
            uuid,
            file_data,
        )
    except Exception as err:
        raise MinioConnectionError(err) from err
    return response
