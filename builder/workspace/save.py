from __future__ import annotations

import json
import os
import tempfile
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .model import Workspace


class WorkspaceSaveError(OSError):
    """Raised when a workspace cannot be persisted to disk."""


class SaveWorkspaceJob(Job):
    """Persist a Workspace as a JSON document."""

    def __init__(self, workspace: Workspace, path: str | PathLike[str]):
        super().__init__("Save Workspace")
        self.workspace = workspace
        self.path = Path(path)

    def run(self) -> None:
        _write_workspace(self.workspace, self.path)


def save_workspace(workspace: Workspace, path: str | PathLike[str]) -> None:
    """Persist a Workspace through the Job framework."""
    job = SaveWorkspaceJob(workspace, path)
    job.execute()


def _write_workspace(workspace: Workspace, path: Path) -> None:
    document = {
        "name": workspace.name,
        "project_name": workspace.project_name,
        "created_at": workspace.created_at.isoformat(),
        "active_sprint": workspace.active_sprint,
        "version": workspace.version,
    }
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(document, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise WorkspaceSaveError(
            f"Unable to save workspace '{path}': {error}"
        ) from error
