"""MinIO-related utilities for SimPhoNy-OSP"""
from minio import Minio

from osp.settings import AppConfig


def get_minio() -> Minio:
    """Instantiate MinIO-client without `Depends`."""
    settings = AppConfig()
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_user.get_secret_value(),
        secret_key=settings.minio_password.get_secret_value(),
        secure=False,
    )
