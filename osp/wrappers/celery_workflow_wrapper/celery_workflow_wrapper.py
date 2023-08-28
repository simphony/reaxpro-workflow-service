"""SimPhoNy-wrapper for celery-workflows"""

import logging
from typing import TYPE_CHECKING

from osp.core.namespaces import emmo
from osp.core.session import SimWrapperSession

from .celery_workflow_engine import CeleryWorkflowEngine

if TYPE_CHECKING:
    from typing import UUID, Any, Dict, List, Optional

    from pydantic import BaseSettings

    from osp.core.cuds import Cuds


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class CeleryWorkflowSession(SimWrapperSession):
    """SimPhoNy-wrapper session for Celery-Chains and Worklows"""

    def __init__(
        self,
        input_uuid: "UUID",
        engine: CeleryWorkflowEngine = None,
        logging_id: str = None,
    ) -> None:
        """Initalite the session."""
        if not engine:
            engine = CeleryWorkflowEngine(input_uuid, logging_id=logging_id)
        super().__init__(engine=engine)

    # OVERRIDE
    def __str__(self):
        return "CeleryWorkflowSession"

    # OVERRIDE
    def _run(self, root_cuds_object) -> str:
        """Run the wrapper session."""
        return self._engine.run()

    # OVERRIDE
    def _apply_added(self, root_obj, buffer) -> None:
        """Apply scans of added cuds in buffer."""
        for obj in buffer.values():
            if obj.is_a(emmo.Workflow):
                message = """Found %s. Will search for workflow steps
                    and related workers on the platform."""
                logger.info(message, obj)
                self._scan_for_neighbours(obj)
        if not self._engine.tasks:
            message = """Did not find any workflow steps with
            complementary workers. Will scan for single
            object of type %s."""
            logger.info(message, emmo.Calculation)
            self._scan_for_single_calc(buffer)
        else:
            message = """Scan for workflow steps complete.
            Identified the following chain of workers: %s"""
            logger.info(message, self._engine.tasks)

    def _scan_for_neighbours(self, obj: "Cuds", step: str = "first") -> None:
        """Scan the input cuds for neighbour-tasks"""
        neighbour = obj.get(rel=emmo[f"hasSpatial{step.title()}"])
        if not neighbour:
            message = f"""Did not find {step} task in the chain of calculations in {obj}.
            Workflow chain has ended here."""
            logger.info(message)
        else:
            neighbour = neighbour.pop()
            self._get_worker_mapping(neighbour)
            self._scan_for_neighbours(neighbour, step="next")

    def _scan_for_single_calc(self, buffer: "Dict[Any, Cuds]") -> None:
        """Find single calculations to be run in the buffer."""
        for obj in buffer.values():
            if obj.is_a(emmo.Calculation):
                self._get_worker_mapping(obj)
        if not self._engine.tasks:
            message = """Did not find any calculations with
            complementary workers."""
            raise TypeError(message)
        message = """Found additional workers %s in the buffer,
        but will ignored because not part of a workflow chain."""
        logger.info(message, self._engine.tasks)

    def _get_worker_mapping(self, calculation: "Cuds") -> None:
        mapping = self._scan_worker_mapping(calculation)
        if not mapping:
            message = f"""Task in the chain of calculations is not properly
            mapped to an existing worker {calculation}."""
            logger.info(message)
        else:
            self._engine.add_task((calculation, mapping))

    def _scan_worker_mapping(self, calculation: "Cuds") -> "Optional[str]":
        response = []
        for superclass, mapping in self.worker_mapping.items():
            if calculation.is_a(superclass):
                response.append(mapping)
        if len(response) > 1:
            raise ValueError(
                f"More than 1 {calculation.oclass} found in worker mapping!"
            )
        if response:
            response = response.pop()
        return response

    # OVERRIDE
    def _apply_deleted(self, root_obj, buffer) -> None:
        """Apply functions for updated-buffer."""

    def _apply_updated(self, root_obj, buffer) -> None:
        """Apply functions for deleted-buffer."""

    # OVERRIDE
    def _load_from_backend(self, uids, expired=None) -> "Cuds":
        """Load a cuds from backend."""
        for uid in uids:
            if uid in self._registry:
                yield self._registry.get(uid)
            else:
                yield None

    @property
    def settings(cls) -> "BaseSettings":
        """Return the settings from the engine."""
        return cls._engine.settings

    @property
    def result(cls) -> "Dict[str, Any]":
        """Return the final result of the workflow"""
        return cls._engine.result

    @property
    def worker_mapping(cls) -> "Dict[str, Any]":
        """Return the mappings of the ontology class and worker name"""
        return cls._engine.worker_mapping

    @property
    def workers(cls) -> "List[str]":
        """Return the list of workers to pass the knowledge graph in a chain."""
        return cls._engine.workers
