"""Sprint B03-S044 — Job Execution."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job, JobStatus

from .scheduling import ScheduledConstructionJob


class JobExecutionError(RuntimeError):
    """Raised when a scheduled Job cannot be executed safely."""


@dataclass(frozen=True, slots=True)
class JobExecutionResult:
    """The observable successful outcome of one scheduled Job execution."""

    scheduled_job: ScheduledConstructionJob
    status: JobStatus

    def __post_init__(self) -> None:
        if not isinstance(self.scheduled_job, ScheduledConstructionJob):
            raise TypeError("Execution results require a scheduled Job")
        if self.status is not JobStatus.COMPLETED:
            raise ValueError("Successful execution results must be completed")


class ExecuteScheduledJobJob(Job):
    """Execute one scheduled Job while preserving observable Workspace state."""

    def __init__(self, scheduled_job: ScheduledConstructionJob):
        super().__init__("Execute Scheduled Job")
        self.scheduled_job = scheduled_job
        self.result: JobExecutionResult | None = None

    def run(self) -> None:
        self.result = _execute_scheduled_job(self.scheduled_job)


def execute_scheduled_job(
    scheduled_job: ScheduledConstructionJob,
) -> JobExecutionResult:
    """Execute one scheduled construction Job through the Job framework."""
    execution_job = ExecuteScheduledJobJob(scheduled_job)
    execution_job.execute()

    if execution_job.result is None:
        raise RuntimeError("Job execution completed without a result")

    return execution_job.result


def _execute_scheduled_job(
    scheduled_job: ScheduledConstructionJob,
) -> JobExecutionResult:
    if not isinstance(scheduled_job, ScheduledConstructionJob):
        raise TypeError("Construction execution requires a scheduled Job")

    workspace = scheduled_job.target.controller.workspace
    if workspace.current_job is not None:
        raise JobExecutionError("Cannot execute a Job while another Job is active")
    if workspace.active_sprint != scheduled_job.target.sprint.identifier:
        raise JobExecutionError(
            "Scheduled Job target is no longer the active Workspace Sprint"
        )
    if scheduled_job.job.status is not JobStatus.PENDING:
        raise JobExecutionError("Only pending scheduled Jobs can be executed")

    workspace.current_job = scheduled_job.job.name
    try:
        scheduled_job.job.execute()
    finally:
        workspace.current_job = None

    return JobExecutionResult(
        scheduled_job=scheduled_job,
        status=scheduled_job.job.status,
    )
