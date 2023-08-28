"""Exceptions for osp-utilities"""


class MinioDownloadError(Exception):
    """Error while fetching object from MinIO-instance."""


class MinioConnectionError(Exception):
    """Error while connecting to MinIO-instance."""
