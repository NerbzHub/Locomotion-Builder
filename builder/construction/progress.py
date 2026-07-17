"""Sprint B03-S045 — Progress Updating."""

from __future__ import annotations

from builder.book.progress import ConstructionProgress, ConstructionProgressError
from builder.jobs.job import Job

from .execution import JobExecutionResult


class ConstructionProgressUpdateError(RuntimeError):
    """Raised when completed Job execution cannot update construction state."""


class UpdateConstructionProgressJob(Job):
    """Apply one successful Job execution to Workspace construction progress."""

    def __init__(self, execution_result: JobExecutionResult):
        super().__init__("Update Construction Progress")
        self.execution_result = execution_result
        self.progress: ConstructionProgress | None = None

    def run(self) -> None:
        self.progress = _update_construction_progress(self.execution_result)


def update_construction_progress(
    execution_result: JobExecutionResult,
) -> ConstructionProgress:
    """Update Workspace progress after one successful scheduled Job execution."""
    job = UpdateConstructionProgressJob(execution_result)
    job.execute()

    if job.progress is None:
        raise RuntimeError("Construction progress update completed without a result")

    return job.progress


def _update_construction_progress(
    execution_result: JobExecutionResult,
) -> ConstructionProgress:
    if not isinstance(execution_result, JobExecutionResult):
        raise TypeError("Construction progress updates require an execution result")

    scheduled_job = execution_result.scheduled_job
    target = scheduled_job.target
    workspace = target.controller.workspace
    current_progress = target.controller.progress

    if workspace.current_job is not None:
        raise ConstructionProgressUpdateError(
            "Cannot update construction progress while a Job is active"
        )
    if workspace.active_sprint != target.sprint.identifier:
        raise ConstructionProgressUpdateError(
            "Executed Job target is no longer the active Workspace Sprint"
        )
    if current_progress.active_sprint != target.sprint:
        raise ConstructionProgressUpdateError(
            "Executed Job target is not the next incomplete Sprint"
        )

    completed_identifiers = (*workspace.completed_sprints, target.sprint.identifier)
    try:
        updated_progress = ConstructionProgress(
            sprints=current_progress.sprints,
            completed_identifiers=completed_identifiers,
        )
    except ValueError as error:
        raise ConstructionProgressUpdateError(str(error)) from error

    workspace.completed_sprints.append(target.sprint.identifier)
    workspace.active_sprint = (
        updated_progress.active_sprint.identifier
        if updated_progress.active_sprint is not None
        else None
    )
    return updated_progress
