"""Pydantic Models for FastAPI-celery"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class RemoteWorker(str):
    """Identifier of the remote celery worker."""


class RemoteTaskName(str):
    """Task name which can be executed on remote worker."""


class ModelName(str):
    """Model name which can be instanciated via pydantic."""


class Registry(Dict):
    """Registry with available tasks available on remote workers."""


class TaskStatus(str, Enum):
    """Status of the task."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    REVOKED = "REVOKED"


class TaskStatusModel(BaseModel):
    """Data model of the task status"""

    status: TaskStatus = Field(..., description="Status of the remote task.")
    state: TaskStatus = Field(..., description="State of the remote task.")
    task_id: UUID = Field(..., description="UUID of the submitted task.")
    args: Optional["List[Any]"] = Field(
        ..., description="Arguments passed during the task submission."
    )
    kwargs: Optional["Dict[Any, Any]"] = Field(
        ..., description="Keyword arguments passed during the task submission."
    )
    traceback: Optional[str] = Field(
        ..., description="Traceback message about potential errors."
    )
    date_done: Optional[datetime] = Field(
        ..., description="Datetime when the submitted job finished."
    )


class TaskKillModel(TaskStatusModel):
    """Response model of the API when process of the task is killed."""

    message: str = Field(
        ...,
        description="""Human readable message with info
        if killing of task was successful.""",
    )


class TaskResultModel(BaseModel):
    """Data model of the task result"""

    task_id: UUID = Field(..., description="UUID of the submitted task.")
    result: Optional[Any] = Field(
        ..., description="Result of the task forwarded by celery-worker."
    )
    traceback: Optional[str] = Field(
        ..., description="Traceback message about potential errors."
    )
    date_done: Optional[datetime] = Field(
        ..., description="Datetime when the submitted job finished."
    )


class TaskResponseModel(BaseModel):
    """Response of the API with response to the task status"""

    message: str = Field(
        ..., description="Human readable message as response from request."
    )
    metadata: TaskStatusModel = Field(
        ..., description="Metadata about the task at the time of the request."
    )


class RegisteredTaskModel(BaseModel):
    """Response of the API data of the task status."""

    message: str = Field(
        ..., description="Human readable message as response from request."
    )
    registered_tasks: Dict[RemoteWorker, List[RemoteTaskName]] = Field(
        ..., description="Registry with tasks available on remote workers."
    )


class TaskCreateModel(BaseModel):
    """Response of the API when instanciating a data model."""

    cache_id: str = Field(
        ..., description="UUID of the instanciated data model in the cache"
    )


class RegisteredModels(BaseModel):
    """Response of the API data of the task status."""

    message: str = Field(
        ..., description="Human readable message as response from request."
    )
    registered_models: List[ModelName] = Field(
        ..., description="Registry with data models available."
    )


class SubmissionBody(BaseModel):
    """Body of the workflow request."""

    cache_id: str = Field(
        ..., description="UUID of the data to be passed as input to remote worker"
    )

    format: Optional[str] = Field(
        "turtle", description="Format of the RDF-file to be consumed by the worker."
    )


class UploadDataResponse(BaseModel):
    """Body of the data upload response"""

    cache_id: UUID = Field(
        ..., description="UUID of the data which was uploaded to the cache."
    )
