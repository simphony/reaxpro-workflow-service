"""S3Handler for logging of celery-tasks"""
import logging

from osp.utilities import get_boto3, get_minio


class S3Handler(logging.Handler):
    """Logging handler related to the S3-client"""

    def __init__(self, task_id, s3_client):
        """Initalize the class with the bucket name and key."""
        super().__init__()
        self._task_id = task_id
        self._s3_client = s3_client

    def emit(self, record):
        """Emit the record and push object to minio via S3-client."""
        log_entry = self.format(record)
        try:
            existing_object = self._s3_client.get_object(
                Bucket=self._task_id, Key=self._task_id
            )
            existing_logs = existing_object["Body"].read().decode()
        except Exception:
            existing_logs = ""

        updated_logs = existing_logs + log_entry + "\n"

        self._s3_client.put_object(
            Bucket=self._task_id,
            Key=self._task_id,
            Body=updated_logs.encode(),
        )


def get_s3handler(task_id: str) -> S3Handler:
    """Get S3 handler for logging."""
    minio_client = get_minio()
    if not minio_client.bucket_exists(task_id):
        minio_client.make_bucket(task_id)
    s3_client = get_boto3()
    return S3Handler(
        task_id,
        s3_client,
    )
