"""osp-utilities for boto3"""
import boto3
from botocore.client import BaseClient

from osp.settings import AppConfig


def get_boto3() -> BaseClient:
    """Helper function for returning S3-client using MinIO."""
    settings = AppConfig()
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_user.get_secret_value(),
        aws_secret_access_key=settings.minio_password.get_secret_value(),
    )
