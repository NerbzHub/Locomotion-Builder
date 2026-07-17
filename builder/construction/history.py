"""Sprint B03-S047 — History Updates."""

from __future__ import annotations

from datetime import datetime, timezone

from builder.jobs.job import Job
from builder.workspace.history import HistoryEntry
from builder.workspace.model import Workspace


class ConstructionHistoryError(RuntimeError):
    """Raised when a construction event cannot be recorded safely."""


class RecordConstructionEventJob(Job):
    """Record one append-only construction event in Workspace history."""

    def __init__(
        self,
        workspace: Workspace,
        description: str,
        timestamp: datetime | None = None,
    ):
        super().__init__("Record Construction Event")
        self.workspace = workspace
        self.description = description
        self.timestamp = timestamp
        self.entry: HistoryEntry | None = None

    def run(self) -> None:
        self.entry = _record_construction_event(
            self.workspace,
            self.description,
            self.timestamp,
        )


def record_construction_event(
    workspace: Workspace,
    description: str,
    timestamp: datetime | None = None,
) -> HistoryEntry:
    """Record an observable construction event through the Job framework."""
    job = RecordConstructionEventJob(workspace, description, timestamp)
    job.execute()

    if job.entry is None:
        raise RuntimeError("Construction event recording completed without an entry")

    return job.entry


def _record_construction_event(
    workspace: Workspace,
    description: str,
    timestamp: datetime | None,
) -> HistoryEntry:
    if not isinstance(workspace, Workspace):
        raise TypeError("Construction events require a Workspace")

    try:
        return workspace.history._record(
            description,
            timestamp or datetime.now(timezone.utc),
        )
    except ValueError as error:
        raise ConstructionHistoryError(str(error)) from error
