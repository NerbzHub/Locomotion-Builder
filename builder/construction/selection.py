"""Sprint B03-S042 — Sprint Selection."""

from __future__ import annotations

from dataclasses import dataclass

from builder.book.progress import ConstructionProgressError
from builder.book.sprints import ConstructionSprint
from builder.jobs.job import Job

from .controller import ConstructionController


class SprintSelectionError(RuntimeError):
    """Raised when a construction target cannot be selected safely."""


@dataclass(frozen=True, slots=True)
class ConstructionTarget:
    """One explicitly selected, dependency-ready construction Sprint."""

    controller: ConstructionController
    sprint: ConstructionSprint

    def __post_init__(self) -> None:
        if not isinstance(self.controller, ConstructionController):
            raise TypeError("Construction targets require a controller")
        if self.sprint not in self.controller.parser_validation.report.sprints:
            raise ValueError("Construction targets must belong to the controller")


class SelectConstructionTargetJob(Job):
    """Select the next eligible Sprint for construction."""

    def __init__(
        self,
        controller: ConstructionController,
        sprint_identifier: str | None = None,
    ):
        super().__init__("Select Construction Target")
        self.controller = controller
        self.sprint_identifier = sprint_identifier
        self.target: ConstructionTarget | None = None

    def run(self) -> None:
        self.target = _select_construction_target(
            self.controller,
            self.sprint_identifier,
        )


def select_construction_target(
    controller: ConstructionController,
    sprint_identifier: str | None = None,
) -> ConstructionTarget:
    """Select one construction target through the Job framework."""
    job = SelectConstructionTargetJob(controller, sprint_identifier)
    job.execute()

    if job.target is None:
        raise RuntimeError("Construction target selection completed without a result")

    return job.target


def _select_construction_target(
    controller: ConstructionController,
    sprint_identifier: str | None,
) -> ConstructionTarget:
    if controller.workspace.current_job is not None:
        raise SprintSelectionError(
            "Cannot select a construction target while a Job is active"
        )

    try:
        progress = controller.progress
    except ConstructionProgressError as error:
        raise SprintSelectionError(
            f"Workspace construction state is invalid: {error}"
        ) from error

    active_sprint = progress.active_sprint
    if active_sprint is None:
        raise SprintSelectionError("Construction is already complete")

    if sprint_identifier is not None and not isinstance(sprint_identifier, str):
        raise TypeError("Construction Sprint identifiers must be strings or null")
    if sprint_identifier is not None and sprint_identifier != active_sprint.identifier:
        raise SprintSelectionError(
            f"Construction Sprint '{sprint_identifier}' is not dependency-ready"
        )

    controller.workspace.active_sprint = active_sprint.identifier
    return ConstructionTarget(controller=controller, sprint=active_sprint)
