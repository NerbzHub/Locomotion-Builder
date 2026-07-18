from __future__ import annotations

import os
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .load import WorkspaceLoadError, load_workspace
from .model import Workspace


class WorkspaceRecoveryError(RuntimeError):
    """Raised when no valid persisted Workspace state can be recovered."""


class RecoverWorkspaceJob(Job):
    """Recover the newest valid Workspace state after an interruption."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Recover Workspace")
        self.path = Path(path)
        self.workspace: Workspace | None = None
        self.source_path: Path | None = None

    def run(self) -> None:
        self.workspace, self.source_path = _recover_workspace(self.path)


def recover_workspace(path: str | PathLike[str]) -> Workspace:
    """Recover an interrupted Workspace through the Job framework."""
    job = RecoverWorkspaceJob(path)
    job.execute()

    if job.workspace is None:
        raise RuntimeError("Workspace recovery completed without a result")

    return job.workspace


def _recover_workspace(path: Path) -> tuple[Workspace, Path]:
    for candidate in _recovery_candidates(path):
        try:
            workspace = load_workspace(candidate)
        except WorkspaceLoadError:
            continue

        if candidate != path:
            try:
                os.replace(candidate, path)
            except OSError as error:
                raise WorkspaceRecoveryError(
                    f"Unable to restore workspace '{path}': {error}"
                ) from error

        return workspace, candidate

    raise WorkspaceRecoveryError(
        f"No recoverable workspace state found for '{path}'"
    )


def _recovery_candidates(path: Path) -> list[Path]:
    temporary_pattern = f".{path.name}.*.tmp"

    try:
        candidates = [path, *path.parent.glob(temporary_pattern)]
    except OSError as error:
        raise WorkspaceRecoveryError(
            f"Unable to inspect workspace recovery state for '{path}': {error}"
        ) from error

    candidate_details: list[tuple[int, bool, str, Path]] = []
    for candidate in candidates:
        try:
            modified_at = candidate.stat().st_mtime_ns
        except OSError:
            continue

        candidate_details.append(
            (modified_at, candidate == path, candidate.name, candidate)
        )

    candidate_details.sort(key=lambda details: details[:3], reverse=True)
    return [details[-1] for details in candidate_details]
