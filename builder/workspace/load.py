from __future__ import annotations

import json
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Any

from builder.jobs.job import Job

from .model import Workspace


class WorkspaceLoadError(ValueError):
    """Raised when a workspace cannot be reconstructed from disk."""


class LoadWorkspaceJob(Job):
    """Load an existing Workspace from a JSON document."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Load Workspace")
        self.path = Path(path)
        self.workspace: Workspace | None = None

    def run(self) -> None:
        self.workspace = _read_workspace(self.path)


def load_workspace(path: str | PathLike[str]) -> Workspace:
    """Load an existing Workspace through the Job framework."""
    job = LoadWorkspaceJob(path)
    job.execute()

    if job.workspace is None:
        raise RuntimeError("Workspace loading completed without a result")

    return job.workspace


def _read_workspace(path: Path) -> Workspace:
    try:
        with path.open("r", encoding="utf-8") as workspace_file:
            document = json.load(workspace_file)
    except (OSError, json.JSONDecodeError) as error:
        raise WorkspaceLoadError(
            f"Unable to load workspace '{path}': {error}"
        ) from error

    if not isinstance(document, dict):
        raise WorkspaceLoadError("Workspace document must contain a JSON object")

    expected_fields = {
        "name",
        "project_name",
        "created_at",
        "active_sprint",
        "version",
    }
    actual_fields = set(document)
    missing_fields = expected_fields - actual_fields
    unexpected_fields = actual_fields - expected_fields

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise WorkspaceLoadError(f"Workspace document is missing fields: {missing}")

    if unexpected_fields:
        unexpected = ", ".join(sorted(unexpected_fields))
        raise WorkspaceLoadError(
            f"Workspace document contains unexpected fields: {unexpected}"
        )

    name = _require_string(document, "name")
    project_name = _require_string(document, "project_name")
    created_at_value = _require_string(document, "created_at")
    active_sprint = document["active_sprint"]
    version = _require_string(document, "version")

    if active_sprint is not None and not isinstance(active_sprint, str):
        raise WorkspaceLoadError(
            "Workspace field 'active_sprint' must be a string or null"
        )

    try:
        created_at = datetime.fromisoformat(created_at_value)
    except ValueError as error:
        raise WorkspaceLoadError(
            "Workspace field 'created_at' must be an ISO 8601 datetime"
        ) from error

    return Workspace(
        name=name,
        project_name=project_name,
        created_at=created_at,
        active_sprint=active_sprint,
        version=version,
    )


def _require_string(document: dict[str, Any], field_name: str) -> str:
    value = document[field_name]
    if not isinstance(value, str):
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be a string"
        )
    return value
