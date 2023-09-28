"""Module for injection of dependencies into fastapi-endpoints and routers"""

import logging
import os
import tempfile
from importlib import import_module
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional
from uuid import UUID

from celery import Celery
from celery.app.control import Inspect
from fastapi import Depends, Query, UploadFile
from minio import Minio
from shieldapi.frameworks.fastapi import AuthTokenBearer
from urllib3.response import HTTPResponse

from osp.settings import AppConfig
from osp.utilities.helper import _get_download, _get_upload

if TYPE_CHECKING:  # pragma: no cover
    from typing import Collection


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_app() -> "Celery":
    """Return celery app"""
    from .tasks import celery  # pylint: disable=import-outside-toplevel

    return celery


def get_method() -> Callable:
    """Return celery-tasks for running simulation"""
    from .tasks import run_simulation  # pylint: disable=import-outside-toplevel

    return run_simulation


def get_appconfig() -> AppConfig:
    """Returns app-config."""
    return AppConfig()


def get_dependencies() -> "List[Depends]":
    """Return dependencies for FastAPI-middleware for authentication"""
    app_config = get_appconfig()

    if app_config.authentication_dependencies:
        dependencies = [Depends(AuthTokenBearer(bearerFormat="JWT"))]
    else:
        dependencies = []
        logger.info("No dependencies for authentication assigned.")
    return dependencies


def get_models() -> "Dict[str, Callable]":
    """Get registry of pydantic models."""
    app_config = AppConfig()
    modules = [module.strip().split(":") for module in app_config.schemas.split("|")]
    return {
        classname: getattr(import_module(module), classname)
        for (module, classname) in modules
    }


def depends_modellist() -> "List[str]":
    """Get list of model names."""
    registry = get_models()
    return list(registry.keys())


def depends_inspect(celery_app: "Celery" = Depends(get_app)) -> Inspect:
    """Return the object from the celery app for the backend inspection."""
    return celery_app.control.inspect()


def depends_registry(
    inspect: Inspect = Depends(depends_inspect),
) -> "Dict[Any, Collection[str]]":
    """Return a mapping between the workers id and registered tasks"""
    registry = inspect.registered_tasks()
    if not registry:
        registry = {}
    return registry


def depends_tasks(registry: dict = Depends(depends_registry)) -> "List[str]":
    """Return the list of tasks available from the message broker."""
    task_list: List[str] = []
    if not registry:
        return task_list
    for tasks in registry.values():
        task_list += tasks
    return task_list


def depends_minio(settings: AppConfig = Depends(get_appconfig)) -> Minio:
    """Instantiate MinIO-client via `Depends`."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_user.get_secret_value(),
        secret_key=settings.minio_password.get_secret_value(),
        secure=False,
    )


def depends_upload(
    file: UploadFile,
    uuid: Optional[UUID] = None,
    minio_client: Minio = Depends(depends_minio),
) -> UUID:
    """Upload file with minio client and return upload-id via `Depends`."""
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp:
        temp.write(file.file.read())
    return _get_upload(temp.name, uuid, minio_client)


def depends_upload_enabled(config: AppConfig = Depends(get_appconfig)) -> bool:
    """Check whether direct upoad to data cache is enabled or not"""
    return config.enable_upload


def depends_download(
    dataset_name: str = Query(..., title="Cache ID received after the upload."),
    minio_client: Minio = Depends(depends_minio),
) -> HTTPResponse:
    """Return `HTTPResponse` from uuid through minio client via `Depends`."""
    return _get_download(dataset_name, minio_client)


def depends_logs(
    transformation_id: str = Query(..., title="task id of the submitted job"),
    minio_client: Minio = Depends(depends_minio),
) -> HTTPResponse:
    """Return `HTTPResponse` from uuid through minio client via `Depends`."""
    return _get_download(transformation_id, minio_client)
