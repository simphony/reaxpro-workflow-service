"""Celery tasks for FastAPI"""

import logging
import tempfile
from importlib import import_module
from typing import TYPE_CHECKING

from celery import Celery, current_task, signals

from osp.app.s3 import get_s3handler
from osp.core.cuds import Cuds
from osp.core.namespaces import cuba
from osp.core.utils import export_cuds, import_cuds
from osp.settings import AppConfig
from osp.utilities import get_download, get_upload

if TYPE_CHECKING:
    from typing import Callable


def get_wrapper_class(module: str) -> "Callable":
    """Get wrapper from import-specification"""
    module, classname = module.strip().split(":")
    return getattr(import_module(module), classname)


settings = AppConfig()
address = settings.get_redis_address()
celery = Celery(settings.worker_name, broker=address, backend=address)
celery.conf.CELERYD_HIJACK_ROOT_LOGGER = False


@signals.setup_logging.connect
def on_setup_logging(**kwargs):  # pylint: disable=unused-argument
    """Specify logging handler for tasks in celery worker."""
    # Get the root logger
    logger = logging.getLogger()

    # Set the logging level to INFO
    logger.setLevel(logging.INFO)

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)


@celery.task(name=settings.worker_name)
def run_simulation(
    cache_key: str = None, task_id: str = None, store_tarball: bool = True
) -> str:
    """Run celery-workflow wrapper as celery-task."""

    # Configure the logging module
    task_id = task_id or current_task.request.id
    s3_handler = get_s3handler(task_id)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    s3_handler.setFormatter(formatter)
    logging.basicConfig(level=logging.INFO)
    logging.root.addHandler(s3_handler)

    # download cuds
    logging.info("received cache_key %s", cache_key)
    cudspath = get_download(cache_key, as_file=True)

    # run wrapper
    session_class = get_wrapper_class(settings.wrapper_name)
    with session_class(input_uuid=cache_key, logging_id=task_id) as session:
        wrapper = cuba.Wrapper(session=session)
        cuds = import_cuds(cudspath, session=session)
        if isinstance(cuds, list):
            wrapper.add(*cuds, rel=cuba.relationship)
        elif isinstance(cuds, Cuds):
            wrapper.add(cuds, rel=cuba.relationship)
        session.run()

    # upload Cuds
    with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as file:
        export_cuds(session, file.name)
        meta_key = get_upload(file)

    # get tarball keys
    if store_tarball:
        with open(session.tarball, "rb") as tar:
            tar_key = get_upload(tar)
    else:
        tar_key = session.result

    return {"cache_meta": meta_key, "cache_raw": tar_key}
