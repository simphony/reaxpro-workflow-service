"""osp-utilities for up/downloads with minio"""
import tempfile
from typing import TextIO, Union

from urllib3.response import HTTPResponse

from .helper import _get_download, _get_upload
from .minio import get_minio


def get_upload(file: Union[str, TextIO], uuid: str = None) -> str:
    """Upload file with minio client and return upload-id without `Depends`."""
    if hasattr(file, "filename"):
        file = file.filename
    elif hasattr(file, "name"):
        file = file.name
    minio_client = get_minio()
    return _get_upload(file, uuid, minio_client)


def get_download(uuid: str, as_file=False) -> Union[HTTPResponse, str]:
    """Return `io.BytesIO` from uuid through minio client without `Depends`."""
    minio_client = get_minio()
    response = _get_download(uuid, minio_client)
    if as_file:
        suffix = response.headers.get("x-amz-meta-suffix")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
            temp.write(response.data)
            response = temp.name
    return response
