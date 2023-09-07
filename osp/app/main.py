"""Main FastAPI-middleware for running remote celery tasks"""
import logging
import os
from datetime import datetime
from typing import Annotated, Any, Dict, List, Optional, Union
from uuid import UUID

import pkg_resources
import uvicorn
from celery import Celery
from fastapi import Body, Depends, FastAPI, HTTPException, Query, Response
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, RedirectResponse

# from fastapi.responses import StreamingResponse
from fastapi_plugins import (
    config_plugin,
    get_config,
    redis_plugin,
    register_config,
    register_middleware,
)
from minio import ServerError
from pydantic.error_wrappers import ValidationError
from pydantic.schema import schema
from urllib3.response import HTTPResponse

from osp.settings import AppConfig

from .dependencies import (
    depends_download,
    depends_logs,
    depends_modellist,
    depends_registry,
    depends_upload,
    depends_upload_enabled,
    get_app,
    get_appconfig,
    get_dependencies,
    get_models,
)
from .models import (
    InfoType,
    RegisteredModels,
    RegisteredTaskModel,
    SubmissionBody,
    TaskCreateModel,
    TaskKillModel,
    TaskResultModel,
    TaskStatusModel,
    TransformationStatus,
    UploadDataResponse,
    UploadNotEnabledError,
    task_to_transformation_map,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
PACKAGE_NAME = "reaxpro-workflow-service"


app = register_middleware(FastAPI(dependencies=get_dependencies()))
register_config(AppConfig)
config = get_config()


def custom_openapi():
    """Overwrite openapi schema"""
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ReaxPro Workflow Service",
        description="Multi-scale simulation platform for reactive processes",
        version=pkg_resources.get_distribution(PACKAGE_NAME).version,
        contact={
            "name": "Matthias Büschelberger",
            "url": "https://materials-marketplace.eu/",
            "email": "matthias.bueschelberger@iwm.fraunhofer.de",
        },
        license_info={
            "name": "BSD-3-clause",
            "url": "https://opensource.org/licenses/bsd-3-clause",
        },
        servers=[{"url": config.external_hostname}]
        if config.external_hostname
        else config.external_hostname,
        routes=app.routes,
    )
    openapi_schema["info"]["x-api-version"] = "0.4.0"
    openapi_schema["info"]["x-products"] = [{"name": "Monthly"}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to /docs page"""
    return RedirectResponse(url="/docs")


@app.put("/data/cache", operation_id="createDataset")
async def upload_data(
    object_key: UUID = Depends(depends_upload),
    upload_enabled: bool = Depends(depends_upload_enabled),
) -> UploadDataResponse:
    """Upload data from internal cache"""
    if not upload_enabled:
        raise UploadNotEnabledError("Direct upload to cache is not enabled")
    return UploadDataResponse(id=object_key, last_modified=str(datetime.now()))


@app.get("/data/cache/{dataset_name}", operation_id="getDataset")
async def download_data(
    dataset_name: str,
    response=Depends(depends_download),
) -> Response:
    """Download file via StreamingResponse"""
    filename = str(dataset_name) + response.headers.get("x-amz-meta-suffix")
    # return StreamingResponse(
    #     iter(response.readlines()),
    #     media_type="multipart/form-data",
    #     headers={"Content-Disposition": f"attachment; filename={filename}"},
    # )
    response = Response(response.data)
    # Set the appropriate headers
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.headers["Content-Type"] = "application/octet-stream"
    return response


@app.get("/workers/registered")
async def get_workers_available(
    registry: Union[dict, None] = Depends(depends_registry)
) -> RegisteredTaskModel:
    """Return the list of runable and registered tasks"""
    return RegisteredTaskModel(
        **{
            "message": "Fetched registry of executable tasks on remote workers.",
            "registered_tasks": registry,
        }
    )


@app.get("/models", operation_id="getModels")
async def get_model_available(
    registry: List[str] = Depends(depends_modellist),
) -> RegisteredModels:
    """Return the list of runable and registered tasks"""
    return RegisteredModels(
        **{
            "message": "Fetched registry of data models.",
            "registered_models": registry,
        }
    )


@app.get("/info", operation_id="getInfo")
async def get_info(
    info_type: InfoType = Query(
        ..., title="Type of info to be retrieved. schema or example"
    ),
    model_name: Optional[str] = Query(
        ...,
        enum=depends_modellist(),
        title="Name of the data model for which info should be retrieved.",
    ),
) -> Union[Dict[Any, Any], Any]:
    """Get specific app info"""
    if info_type == InfoType.SCHEMA:
        # Retreive schema of a model registered in the app
        models = get_models()
        model = models.get(model_name)
        response = schema([model])
    elif info_type == InfoType.EXAMPLE:
        # Retrieve an example for a model registered in the app
        models = get_models()
        model = models.get(model_name)
        response = JSONResponse(model.Config.schema_extra["example"])
    return response


@app.post("/transformations", operation_id="newTransformation")
async def create_model(
    model_name: str = Query(
        ...,
        enum=depends_modellist(),
        title="Name of the data model to be instanciated.",
    ),
    body=Body(..., media_type="application/json"),
    models=Depends(get_models),
) -> TaskCreateModel:
    """Initialize transformation with respect to a certain model."""
    if "parameters" in body:
        body = body["parameters"]
    # Create a semantic model regisered in the app
    model = models.get(model_name)
    instance = model(**body)
    return TaskCreateModel(id=instance.uuid)


@app.patch("/transformations/{transformation_id}", operation_id="updateTransformation")
async def update_task(
    transformation_id: str,
    body: Annotated[
        SubmissionBody,
        Body(),
    ],
    celery_app: "Celery" = Depends(get_app),
    settings: AppConfig = Depends(get_appconfig),
) -> TaskStatusModel:
    """Get status of the transformation."""
    state = body.state
    if state == TransformationStatus.RUNNING:
        # Send a task to a remote celery worker
        task = celery_app.send_task(
            settings.worker_name,
            kwargs={"cache_key": transformation_id, "store_tarball": False},
            queue=settings.worker_name,
        )
        response = TaskStatusModel(
            status=task.status,
            state=task_to_transformation_map[task.state],
            result=task.result,
            traceback=task.traceback,
            id=task.id,
            args=task.args,
            kwargs=task.kwargs,
            date_done=task.date_done,
        )
    elif state == TransformationStatus.STOPPED:
        # Kill a submitted task with certain id
        task = celery_app.AsyncResult(transformation_id)
        if not task.date_done:
            task.revoke(terminate=True)
            message = "Killing scheduled."
        else:
            message = "Task already terminated."
        response = TaskKillModel(
            message=message,
            status=task.status,
            state=task_to_transformation_map[task.state],
            result=task.result,
            traceback=task.traceback,
            id=task.id,
            args=task.args,
            kwargs=task.kwargs,
            date_done=task.date_done,
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown task status: {state}")
    return response


@app.get("/logs", operation_id="getLogs")
def get_logs(
    transformation_id: str = Query(  # pylint: disable=unused-argument
        ..., title="task id of the submitted job"
    ),
    response: HTTPResponse = Depends(depends_logs),
) -> Response:
    """Get logging messages from a task."""
    return Response(content=response.data, media_type="text/plain")


@app.get(
    "/transformations/{transformation_id}/state", operation_id="getTransformationState"
)
async def get_status(
    transformation_id: str = Query(..., title="task id of the job to be killed"),
    celery_app: "Celery" = Depends(get_app),
) -> TaskStatusModel:
    """Fetch the status of a submitted task with certain id"""
    task = celery_app.AsyncResult(transformation_id)
    return TaskStatusModel(
        status=task.status,
        state=task_to_transformation_map[task.state],
        traceback=task.traceback,
        id=task.id,
        args=task.args,
        kwargs=task.kwargs,
        date_done=task.date_done,
    )


@app.get("/transformations/{transformation_id}", operation_id="getTransformation")
async def get_result(
    transformation_id: str = Query(..., title="task id of the submitted job"),
    celery_app: "Celery" = Depends(get_app),
) -> TaskResultModel:
    """Return the results for submitted task with a certain id"""
    result = celery_app.AsyncResult(transformation_id)
    if not result.ready():
        raise HTTPException(status_code=400, detail="Task is not ready yet.")
    return TaskResultModel(
        parameters=result.result,
        id=transformation_id,
        traceback=result.traceback,
        date_done=result.date_done,
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):  # pylint: disable=unused-argument
    """Return response based on the error"""
    # Convert the error into a list of error messages
    error_messages = []
    for error in exc.errors():
        error_messages.append(f"Field '{':'.join(error['loc'])}' {error['msg']}")

    # Raise an HTTPException with a 422 status code and the error messages
    return JSONResponse(status_code=422, content=error_messages)


# @app.exception_handler(ValueError)
# async def value_error_handler(request, exc):  # pylint: disable=unused-argument
#     """Return response based on the error"""
#     # Raise an HTTPException with a 422 status code and the error messages
#     return JSONResponse(status_code=422, content=list(exc.args))


@app.exception_handler(ServerError)
async def download_error_handler(request, exc):  # pylint: disable=unused-argument
    """Return response based on the MinioDownloadError"""
    # Raise an HTTPException with a 422 status code and the error messages
    return JSONResponse(status_code=422, content="Error while fetching the resource")


@app.exception_handler(UploadNotEnabledError)
async def upload_error_handler(request, exc):  # pylint: disable=unused-argument
    """Return response based on the MinioDownloadError"""
    # Raise an HTTPException with a 422 status code and the error messages
    return JSONResponse(
        status_code=403,
        content="""Direct upload to cache is not enabled.
    Please contact an administrator.""",
    )


# @app.exception_handler(MinioConnectionError)
# async def connection_error_handler(request, exc):  # pylint: disable=unused-argument
#     """Return response based on the MinioDownloadError"""
#     # Raise an HTTPException with a 422 status code and the error messages
#     return JSONResponse(
#         status_code=404, content="The requested resource does not exist."
#     )


@app.on_event("startup")
async def on_startup() -> None:
    """Define functions for app during startup"""
    await config_plugin.init_app(app, config)
    await config_plugin.init()
    await redis_plugin.init_app(app, config=config)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    """Define functions for app during shutdown"""
    await redis_plugin.terminate()
    await config_plugin.terminate()


if __name__ == "__main__":
    host = os.environ["REAXPRO_FASTAPI_HOST"]
    port = int(os.environ["REAXPRO_FASTAPI_PORT"])
    uvicorn.run(app, host=host, port=port, log_level="debug")
