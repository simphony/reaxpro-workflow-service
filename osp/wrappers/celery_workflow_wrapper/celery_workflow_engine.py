"""Module for Celery-workflow engine."""
import logging
import tempfile
from typing import TYPE_CHECKING

from celery import Celery, signals
from celery.result import allow_join_result

from osp.core.namespaces import emmo, get_entity
from osp.core.session import CoreSession
from osp.core.utils import export_cuds, import_cuds
from osp.settings import AppConfig
from osp.utilities.load import get_download, get_upload

if TYPE_CHECKING:
    from typing import UUID, Any, Dict, List, Optional, Tuple

    from osp.core.cuds import Cuds
    from osp.core.ontology import OntologyClass


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@signals.setup_logging.connect
def on_setup_logging(**kwargs):  # pylint: disable=unused-argument
    """Specify logging handler for tasks in celery worker."""
    # Get the root logger
    celery_logger = logging.getLogger()

    # Set the logging level to INFO
    celery_logger.setLevel(logging.INFO)

    # Add a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    celery_logger.addHandler(console_handler)


class CeleryWorkflowEngine:
    """Class definition for Celery-workflow engine."""

    def __init__(
        self,
        input_uuid: "UUID",
        app: Celery = None,
        settings: AppConfig = None,
        logging_id: str = None,
    ) -> None:
        """Initalize the Celery-Workflow engine."""
        if not settings:
            settings = AppConfig()
        self._settings = settings
        if not app:
            address = self._settings.get_redis_address()
            app = Celery(broker=address, backend=address)
        self._logging_id: str = logging_id
        self._app: Celery = app
        self._input_uuid: "UUID" = input_uuid
        self._task_id: "Optional[UUID]" = None
        self._tasks: List = []
        self._results: List = []

    def add_task(self, mapping: "Tuple[Cuds, str]") -> None:
        """Add the name of an existing worker and the
        calculation type to batch."""
        self._tasks.append(mapping)

    def run(self) -> str:
        """Run the celery workflow engine"""
        return self._create_pipeline()

    # define a function to execute a task on a remote Celery worker
    def _execute_task(self, worker_name: str, task_id: str) -> "str":
        """Send a task to the Celery-app"""
        task = self._app.send_task(
            worker_name,
            kwargs={"cache_key": task_id, "task_id": self._logging_id},
            queue=worker_name,
        )
        with allow_join_result():
            result = task.get()
        self._results.append((worker_name, result))
        return result["cache_meta"]

    # define a function to create a chain of tasks based on the list of workers
    def _create_pipeline(self) -> str:
        """Create a list of tasks to execute in a chain"""
        uuid = self._input_uuid
        for calculation_cuds, worker_name in self._tasks:
            uuid = self._make_output_mapping(calculation_cuds, uuid)
            uuid = self._execute_task(worker_name, uuid)
        return uuid

    def _make_output_mapping(self, calculation: "Cuds", uuid: "UUID") -> "UUID":
        mappings = self._scan_output_mapping(calculation)
        if mappings:
            logger.info(
                """Found a match for input mapping for %s
                cue to outputs from a previous calculation: %s""",
                calculation,
                mappings,
            )
            cuds_file = get_download(uuid, as_file=True)
            core_session = CoreSession()
            import_cuds(cuds_file, session=core_session)
            query = core_session.load_from_iri(str(calculation.iri))
            current = query.first()  # pylint: disable=no-member
            if not current:
                raise ValueError(
                    f"Current calculation `{calculation}` not found in graph with object-id {uuid}"
                )
            for mapping in mappings:
                previous = mapping["previous"].iri
                output = mapping["output"].iri
                result = core_session.sparql(
                    f"""select ?output where {{
                        ?previous rdf:type <{previous}> .
                        ?previous <{emmo.hasOutput.iri}> ?output .
                        ?output rdf:type <{output}> .
                    }}"""
                )
                for row in result(output="cuds"):
                    current.add(row["output"], rel=emmo.hasInput)
            with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as file:
                export_cuds(core_session, file.name)
                uuid = get_upload(file, uuid=uuid)
        return uuid

    def _scan_output_mapping(
        self, calculation: "Cuds"
    ) -> "List[Dict[str, OntologyClass]]":
        response = []
        for superclass, mapping in self.output_mapping.items():
            if calculation.is_a(superclass):
                response.append(mapping)
        if response:
            response = response.pop()
        return response

    @property
    def settings(cls):
        """Return the engine settings."""
        return cls._settings

    @property
    def worker_mapping(cls) -> "Dict[str, Any]":
        """Return the mappings of the ontology class and worker name"""
        return {
            get_entity(mapping.split(":")[0].strip()): mapping.split(":")[-1]
            for mapping in cls.settings.worker_mapping.split("|")
        }

    @property
    def output_mapping(cls) -> "Dict[str, Any]":
        "Output mapping for previous calculations for next calculation"
        mapping = {}
        for entry in cls.settings.output_mapping.split("|"):
            entities = [get_entity(entity.strip()) for entity in entry.split(":")]
            key = entities[0]
            values = [{"previous": entities[1], "output": entities[2]}]
            if key in mapping:
                mapping[key] += values
            else:
                mapping[key] = values
        return mapping

    @property
    def result(cls) -> "Dict[str, Any]":
        """Return the final result of the workflow"""
        return {
            f"{n}_{worker_name}": result["cache_raw"]
            for n, (worker_name, result) in enumerate(cls.results)
        }

    @property
    def results(cls) -> "List[Dict[str, Any]]":
        """Return the results from the celery engine."""
        return cls._results

    @property
    def tasks(cls) -> "List[str]":
        """Return the list of tasks to pass the knowledge graph in a chain."""
        return cls._tasks
