"""Commandline tool for starting the reaxpro platform"""

import atexit
import os
import subprocess  # nosec
import sys
from typing import Dict, List, Optional

import click
import uvicorn
import yaml
from pydantic import BaseModel


class WorkerModel(BaseModel):
    """Pydantic model for all workers orechestered by head worker"""

    name: str
    wrapper: str
    extra_env: Optional[Dict[str, str]]


class HeadModel(BaseModel):
    """Pydantic model for head worker"""

    name: str
    mapping: str


class BrokerModel(BaseModel):
    """Pydantic model message broker details"""

    type: str
    host: str
    port: int
    db: int


class MinioModel(BaseModel):
    """Pydantic model minio object store details"""

    user: str
    password: str
    endpoint: str


class FastAPIModel(BaseModel):
    """Pydantic model FastAPI app details"""

    host: str
    port: int
    schemas: str


class AppConfigModel(BaseModel):
    """Pydantic model overall app config"""

    fastapi: Optional[FastAPIModel]
    minio: MinioModel
    broker: BrokerModel
    head: Optional[HeadModel]
    workers: Optional[List[WorkerModel]]


class ReaxProConfigModel(BaseModel):
    """Pydantic model overall app config defined by `reaxpro`-submodel"""

    reaxpro: AppConfigModel


@click.command()
@click.option(
    "--config",
    default="cmdline-config.yml",
    type=click.Path(exists=True, dir_okay=False),
    multiple=False,
    help="Config starting platform",
    envvar="REAXPRO_CMDLINE_CONFIG",
)
def start_platform(config):
    """Run reaxpro platform with respect to the passed configuration"""
    # define colors for echo
    green = "\033[92m"
    red = "\033[91m"
    reset = "\033[0m"

    # open the yml file
    with open(config, "r", encoding="utf-8") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise ValueError(
                f"Could not parse YML due to following error: {exc}"
            ) from exc

    # parse and validate model due to config
    try:
        model = ReaxProConfigModel(**config)
    except Exception as execp:
        raise ValueError(f"Invalid configuration: {execp}") from execp

    # export minio variables
    os.environ["REAXPRO_MINIO_USER"] = model.reaxpro.minio.user
    os.environ["REAXPRO_MINIO_PASSWORD"] = model.reaxpro.minio.password
    os.environ["REAXPRO_MINIO_ENDPOINT"] = model.reaxpro.minio.endpoint

    # export redis variables
    os.environ["REAXPRO_REDIS_TYPE"] = model.reaxpro.broker.type
    os.environ["REAXPRO_REDIS_HOST"] = model.reaxpro.broker.host
    os.environ["REAXPRO_REDIS_PORT"] = str(model.reaxpro.broker.port)
    os.environ["REAXPRO_REDIS_DB"] = str(model.reaxpro.broker.db)

    # define processes varaible
    reaxpro_processes = {}

    # define cleanup function when tool is exciting
    def cleanup():
        """Terminate worker processes."""
        for name, process in reaxpro_processes.items():
            click.echo(
                f"""{green}INFO{reset}:\tTerminating"""
                f"""worker with name `{name}` and pid `{process.pid}`"""
            )
            process.terminate()
            process.wait()

    # register cleanup
    atexit.register(cleanup)

    if model.reaxpro.head:
        click.echo(f"{green}INFO{reset}:\tStarting head worker with Celery...")
        reaxpro_processes["headworker"] = _run_head(model.reaxpro.head)

    if model.reaxpro.workers:
        for worker_model in model.reaxpro.workers:
            click.echo(
                f"""{green}INFO{reset}:\t"""
                f"""Starting {worker_model.name}-worker with Celery..."""
            )
            reaxpro_processes[worker_model.name] = _run_worker(worker_model)

    if model.reaxpro.fastapi:
        from .main import app  # pylint: disable=import-outside-toplevel

        # fastapi variables
        os.environ["REAXPRO_SCHEMAS"] = model.reaxpro.fastapi.schemas

        # start fastapi
        click.echo(f"{green}INFO{reset}:\tStarting FastAPI...")
        uvicorn.run(
            app,
            host=model.reaxpro.fastapi.host,
            port=model.reaxpro.fastapi.port,
            log_level="debug",
        )

    elif reaxpro_processes:
        # grab any of the workers and let wait for the process
        workers = ",".join([f"`{worker}`" for worker in reaxpro_processes])
        click.echo(
            f"{green}INFO{reset}:\t Workers are ready for receiving tasks: {workers}"
        )
        process = next(iter(reaxpro_processes.values()))
        process.wait()

    else:
        click.echo(
            f"{red}ERROR{reset}:\tNo processes defined, will shutdown application..."
        )
        sys.exit(1)


def _run_head(model: HeadModel) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "osp.app.tasks:celery",
        "worker",
        "-Q",
        model.name,
        "-n",
        model.name,
    ]
    env = os.environ.copy()
    env["REAXPRO_WORKER_NAME"] = model.name
    env["REAXPRO_WORKER_MAPPING"] = model.mapping
    return _run_command(command, env)


def _run_worker(model: WorkerModel) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "celery",
        "-A",
        "osp.app.tasks:celery",
        "worker",
        "-Q",
        model.name,
        "-n",
        model.name,
    ]
    env = os.environ.copy()
    env["REAXPRO_WORKER_NAME"] = model.name
    env["REAXPRO_WRAPPER_NAME"] = model.wrapper
    if model.extra_env:
        for key, value in model.extra_env.items():
            env[key] = value
    return _run_command(command, env)


def _run_command(command: List[str], env: Dict[str, str]) -> subprocess.Popen:
    return subprocess.Popen(
        command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )  # nosec


if __name__ == "__main__":
    start_platform()  # pylint: disable=no-value-for-parameter
