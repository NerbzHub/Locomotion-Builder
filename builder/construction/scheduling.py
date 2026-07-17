"""Sprint B03-S043 — Job Scheduling."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job, JobStatus

from .selection import ConstructionTarget


class JobSchedulingError(RuntimeError):
    """Raised when an executable Job cannot be scheduled safely."""


@dataclass(frozen=True, slots=True)
class ScheduledConstructionJob:
    """One pending Job scheduled against an active construction target."""

    target: ConstructionTarget
    job: Job

    def __post_init__(self) -> None:
        if not isinstance(self.target, ConstructionTarget):
            raise TypeError("Scheduled Jobs require a construction target")
        if not isinstance(self.job, Job):
            raise TypeError("Scheduled Jobs require a Job")
        if self.job.status is not JobStatus.PENDING:
            raise ValueError("Only pending Jobs can be scheduled")


class ScheduleConstructionJob(Job):
    """Schedule one pending Job against an active construction target."""

    def __init__(self, target: ConstructionTarget, job: Job):
        super().__init__("Schedule Construction Job")
        self.target = target
        self.job_to_schedule = job
        self.scheduled_job: ScheduledConstructionJob | None = None

    def run(self) -> None:
        self.scheduled_job = _schedule_construction_job(
            self.target,
            self.job_to_schedule,
        )


def schedule_construction_job(
    target: ConstructionTarget,
    job: Job,
) -> ScheduledConstructionJob:
    """Schedule one pending construction Job through the Job framework."""
    scheduling_job = ScheduleConstructionJob(target, job)
    scheduling_job.execute()

    if scheduling_job.scheduled_job is None:
        raise RuntimeError("Job scheduling completed without a result")

    return scheduling_job.scheduled_job


def _schedule_construction_job(
    target: ConstructionTarget,
    job: Job,
) -> ScheduledConstructionJob:
    workspace = target.controller.workspace
    if workspace.current_job is not None:
        raise JobSchedulingError("Cannot schedule a Job while another Job is active")
    if workspace.active_sprint != target.sprint.identifier:
        raise JobSchedulingError(
            "Construction target is no longer the active Workspace Sprint"
        )
    if not isinstance(job, Job):
        raise TypeError("Construction scheduling requires a Job")
    if job.status is not JobStatus.PENDING:
        raise JobSchedulingError("Only pending Jobs can be scheduled")

    return ScheduledConstructionJob(target=target, job=job)
