"""Sprint B03-S046 — Checkpoint Creation."""

from __future__ import annotations

from datetime import datetime, timezone

from builder.jobs.job import Job
from builder.workspace.checkpoint import WorkspaceCheckpoint
from builder.workspace.model import Workspace


class ConstructionCheckpointError(RuntimeError):
    """Raised when construction state cannot be captured safely."""


class CreateConstructionCheckpointJob(Job):
    """Capture one stable immutable Workspace recovery checkpoint."""

    def __init__(
        self,
        workspace: Workspace,
        identifier: str,
        created_at: datetime | None = None,
    ):
        super().__init__("Create Construction Checkpoint")
        self.workspace = workspace
        self.identifier = identifier
        self.created_at = created_at
        self.checkpoint: WorkspaceCheckpoint | None = None

    def run(self) -> None:
        self.checkpoint = _create_construction_checkpoint(
            self.workspace,
            self.identifier,
            self.created_at,
        )


def create_construction_checkpoint(
    workspace: Workspace,
    identifier: str,
    created_at: datetime | None = None,
) -> WorkspaceCheckpoint:
    """Create a stable construction checkpoint through the Job framework."""
    job = CreateConstructionCheckpointJob(workspace, identifier, created_at)
    job.execute()

    if job.checkpoint is None:
        raise RuntimeError("Construction checkpoint creation completed without a result")

    return job.checkpoint


def _create_construction_checkpoint(
    workspace: Workspace,
    identifier: str,
    created_at: datetime | None,
) -> WorkspaceCheckpoint:
    if not isinstance(workspace, Workspace):
        raise TypeError("Construction checkpoints require a Workspace")
    if workspace.current_job is not None:
        raise ConstructionCheckpointError(
            "Cannot create a checkpoint while a Job is active"
        )

    checkpoint = WorkspaceCheckpoint(
        identifier=identifier,
        created_at=created_at or datetime.now(timezone.utc),
        active_sprint=workspace.active_sprint,
        completed_sprints=tuple(workspace.completed_sprints),
        validation_status=workspace.validation_status,
    )
    try:
        workspace.checkpoints._append(checkpoint)
    except ValueError as error:
        raise ConstructionCheckpointError(str(error)) from error

    return checkpoint
