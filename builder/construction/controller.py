"""Sprint B03-S041 — Construction Controller."""

from __future__ import annotations

from dataclasses import dataclass

from builder.book.progress import (
    ConstructionProgress,
    ConstructionProgressError,
    determine_construction_progress,
)
from builder.book.validation import ParserValidationResult
from builder.jobs.job import Job
from builder.workspace.model import Workspace
from builder.workspace.validation import validate_project


class ConstructionControllerError(RuntimeError):
    """Raised when a Workspace cannot coordinate parsed construction state."""


@dataclass(frozen=True, slots=True)
class ConstructionController:
    """Coordinates one Workspace with one validated construction schedule."""

    workspace: Workspace
    parser_validation: ParserValidationResult

    def __post_init__(self) -> None:
        if not isinstance(self.workspace, Workspace):
            raise TypeError("Construction controllers require a Workspace")
        if not isinstance(self.parser_validation, ParserValidationResult):
            raise TypeError(
                "Construction controllers require parser validation"
            )
        if not self.parser_validation.is_valid:
            raise ValueError("Construction controllers require valid parser state")

    @property
    def progress(self) -> ConstructionProgress:
        return determine_construction_progress(
            self.parser_validation.report.sprints,
            self.workspace.completed_sprints,
        )


class CreateConstructionControllerJob(Job):
    """Create a controller for one Workspace and parsed construction state."""

    def __init__(
        self,
        workspace: Workspace,
        parser_validation: ParserValidationResult,
    ):
        super().__init__("Create Construction Controller")
        self.workspace = workspace
        self.parser_validation = parser_validation
        self.controller: ConstructionController | None = None

    def run(self) -> None:
        self.controller = _create_construction_controller(
            self.workspace,
            self.parser_validation,
        )


def create_construction_controller(
    workspace: Workspace,
    parser_validation: ParserValidationResult,
) -> ConstructionController:
    """Create a construction controller through the Job framework."""
    job = CreateConstructionControllerJob(workspace, parser_validation)
    job.execute()

    if job.controller is None:
        raise RuntimeError("Construction controller creation completed without a result")

    return job.controller


def _create_construction_controller(
    workspace: Workspace,
    parser_validation: ParserValidationResult,
) -> ConstructionController:
    if not parser_validation.is_valid:
        raise ConstructionControllerError(parser_validation.status)

    project_validation = validate_project(workspace)
    if not project_validation.is_valid:
        raise ConstructionControllerError(project_validation.status)
    if project_validation.metadata is None:
        raise RuntimeError("Valid project validation completed without metadata")

    book_path = parser_validation.report.structure.document.book.path
    if not book_path.is_relative_to(project_validation.metadata.root):
        raise ConstructionControllerError(
            "Parsed engineering Book does not belong to the Workspace project"
        )

    controller = ConstructionController(
        workspace=workspace,
        parser_validation=parser_validation,
    )
    try:
        controller.progress
    except ConstructionProgressError as error:
        raise ConstructionControllerError(
            f"Workspace construction state is invalid: {error}"
        ) from error

    return controller
