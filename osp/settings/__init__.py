"""Pydantic settings for FastAPI and Celery."""

from typing import Optional

from fastapi_plugins import RedisSettings
from pydantic import Field, SecretStr


class AppConfig(RedisSettings):
    """Main configuration for based on redis-settings"""

    worker_name: str = Field(
        "simphony-workflows",
        description="Name of the worker displayed in the services",
    )

    output_mapping: str = Field(
        """emmo.MesoscopicCalculation:emmo.BindingSites:crystallography.UnitCell |
        emmo.MesoscopicCalculation:emmo.ProcessSearch:emmo.ClusterExpansion |
        emmo.MesoscopicCalculation:emmo.ProcessSearch:emmo.ChemicalReactionMechanism"""
    )

    worker_mapping: str = Field(
        "emmmo:ContinuumCalculation:simphony-catalyticfoam",
        description="""Mapping between the label of the entity in EMMO representing
        a calculation e.g. `ContinuumCalculation` for the CO-Usecase in CatalyticFoam
        and the name of the worker executing the wrapper, e.g. `simphony-catalyticfoam`.
        Key-value sepator is `:` whereas the item-separator is `|`.""",
    )

    schemas: str = Field(
        "osp.models.co_catalyticfoam:COCatalyticFOAMModel",
        description="""Models available to be instanciated via Pydantic.
        Each item is a python class to be imported from a modle.
        e.g. `COCatalyticFOAMModel` for the CO-Usecase in CatalyticFoam
        with `osp.models.co_catalyticfoam` as respective Python-modle.
        Key-value sepator is `:` whereas the item-separator is `|`.""",
    )

    authentication_dependencies: bool = Field(
        False, description="If authentication should be enabled or not."
    )

    wrapper_name: str = Field(
        "osp.wrappers.celery_workflow_wrapper:CeleryWorkflowSession",
        description="""SimWrapperSession class to be loaded from a python module
        for wrapping to the celery backend. The regex is: mypackage.mymodule:MyClass""",
    )

    minio_user: SecretStr = Field(..., description="User to MinIO instance.")
    minio_password: SecretStr = Field(..., description="Password to MinIO instance.")
    minio_endpoint: str = Field(
        "localhost:9000",
        description="Resolvable endpoint to contact MinIO instance.",
    )
    external_hostname: Optional[str] = Field(
        None, description="Resolvable hostname to the outside world."
    )

    enable_upload: Optional[bool] = Field(
        False,
        description="""Whether direct data upload into
        the cache should be enabled or not""",
    )

    class Config:
        """Pydantic config for FastAPI-celery settings"""

        env_prefix = "REAXPRO_"
