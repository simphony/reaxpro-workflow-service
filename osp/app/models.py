"""Pydantic Models for FastAPI-celery"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
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


class TransformationStatus(str, Enum):
    """Status of the task."""

    CREATED = "CREATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    STOPPED = "STOPPED"
    RUNNING = "RUNNING"


task_to_transformation_map = {
    TaskStatus.PENDING: TransformationStatus.RUNNING,
    TaskStatus.SUCCESS: TransformationStatus.COMPLETED,
    TaskStatus.FAILURE: TransformationStatus.FAILED,
    TaskStatus.REVOKED: TransformationStatus.STOPPED,
}


UpdateTaskStates = Literal[TransformationStatus.RUNNING, TransformationStatus.STOPPED]


class TaskStatusModel(BaseModel):
    """Data model of the task status"""

    status: TaskStatus = Field(..., description="Status of the remote task.")
    state: TransformationStatus = Field(..., description="State of the remote task.")
    id: UUID = Field(..., description="UUID of the submitted task.")
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

    id: UUID = Field(..., description="UUID of the submitted task.")
    parameters: Optional[Any] = Field(
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

    id: str = Field(..., description="UUID of the instanciated data model in the cache")


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

    state: UpdateTaskStates

    format: str = Field(
        "turtle", description="Format of the RDF-file to be consumed by the worker."
    )

    class Config:
        """Pydantic configuration for submission body"""

        schema_extra = {
            "example": {
                "state": "RUNNING",
                "format": "turtle",
            }
        }


class UploadDataResponse(BaseModel):
    """Body of the data upload response"""

    id: UUID = Field(
        ..., description="UUID of the data which was uploaded to the cache."
    )

    last_modified: str = Field(..., description="created time of the data.")


class InfoType(str, Enum):
    """Types of information to be returned from app"""

    SCHEMA = "Schema"
    EXAMPLE = "Example"


class UploadNotEnabledError(Exception):
    """Upload not permitted since not enabled by admin."""
