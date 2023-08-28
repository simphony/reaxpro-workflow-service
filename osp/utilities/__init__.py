"""OSP-utilities"""

from .boto3 import get_boto3
from .load import get_download, get_upload
from .minio import get_minio

__all__ = [
    "get_download",
    "get_upload",
    "get_boto3",
    "get_minio",
]
