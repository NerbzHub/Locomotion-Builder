from __future__ import annotations

import json
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Any

from builder.jobs.job import Job

from .checkpoint import WorkspaceCheckpoint, WorkspaceCheckpoints
from .history import HistoryEntry, WorkspaceHistory
from .model import Workspace
from .settings import WorkspaceSettings


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

    required_fields = {
        "name",
        "project_name",
        "created_at",
        "active_sprint",
        "version",
    }
    optional_fields = {
        "checkpoints",
        "completed_sprints",
        "current_job",
        "history",
        "project_root",
        "settings",
        "validation_status",
    }
    actual_fields = set(document)
    missing_fields = required_fields - actual_fields
    unexpected_fields = actual_fields - required_fields - optional_fields

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
    project_root = _require_optional_path(document, "project_root")
    created_at_value = _require_string(document, "created_at")
    active_sprint = _require_optional_string(document, "active_sprint")
    checkpoints = _require_checkpoints(document)
    completed_sprints = _require_string_list(document, "completed_sprints")
    current_job = _require_optional_string(document, "current_job")
    history = _require_history(document)
    settings = _require_settings(document)
    validation_status = _require_optional_string(document, "validation_status")
    version = _require_string(document, "version")

    try:
        created_at = datetime.fromisoformat(created_at_value)
    except ValueError as error:
        raise WorkspaceLoadError(
            "Workspace field 'created_at' must be an ISO 8601 datetime"
        ) from error

    return Workspace(
        name=name,
        project_name=project_name,
        project_root=project_root,
        created_at=created_at,
        active_sprint=active_sprint,
        checkpoints=checkpoints,
        completed_sprints=completed_sprints,
        current_job=current_job,
        history=history,
        settings=settings,
        validation_status=validation_status,
        version=version,
    )


def _require_string(document: dict[str, Any], field_name: str) -> str:
    value = document[field_name]
    if not isinstance(value, str):
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be a string"
        )
    return value


def _require_optional_string(
    document: dict[str, Any],
    field_name: str,
) -> str | None:
    value = document.get(field_name)
    if value is not None and not isinstance(value, str):
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be a string or null"
        )
    return value


def _require_optional_path(
    document: dict[str, Any],
    field_name: str,
) -> Path | None:
    value = document.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be a string or null"
        )

    path = Path(value)
    if not path.is_absolute():
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be an absolute path"
        )
    return path


def _require_string_list(
    document: dict[str, Any],
    field_name: str,
) -> list[str]:
    value = document.get(field_name, [])
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise WorkspaceLoadError(
            f"Workspace field '{field_name}' must be a list of strings"
        )
    return value


def _require_settings(document: dict[str, Any]) -> WorkspaceSettings:
    value = document.get("settings", {})
    if not isinstance(value, dict):
        raise WorkspaceLoadError("Workspace field 'settings' must be an object")

    try:
        return WorkspaceSettings(value)
    except (TypeError, ValueError) as error:
        raise WorkspaceLoadError(f"Invalid Workspace settings: {error}") from error


def _require_history(document: dict[str, Any]) -> WorkspaceHistory:
    value = document.get("history", [])
    if not isinstance(value, list):
        raise WorkspaceLoadError("Workspace field 'history' must be a list")

    entries: list[HistoryEntry] = []
    expected_fields = {"timestamp", "description"}
    for index, entry_document in enumerate(value):
        if not isinstance(entry_document, dict):
            raise WorkspaceLoadError(
                f"Workspace history entry {index} must be an object"
            )
        if set(entry_document) != expected_fields:
            raise WorkspaceLoadError(
                f"Workspace history entry {index} must contain "
                "timestamp and description"
            )

        timestamp_value = entry_document["timestamp"]
        description = entry_document["description"]
        if not isinstance(timestamp_value, str):
            raise WorkspaceLoadError(
                f"Workspace history entry {index} timestamp must be a string"
            )

        try:
            timestamp = datetime.fromisoformat(timestamp_value)
            entries.append(HistoryEntry(timestamp, description))
        except (TypeError, ValueError) as error:
            raise WorkspaceLoadError(
                f"Invalid Workspace history entry {index}: {error}"
            ) from error

    try:
        return WorkspaceHistory(entries)
    except (TypeError, ValueError) as error:
        raise WorkspaceLoadError(f"Invalid Workspace history: {error}") from error


def _require_checkpoints(document: dict[str, Any]) -> WorkspaceCheckpoints:
    value = document.get("checkpoints", [])
    if not isinstance(value, list):
        raise WorkspaceLoadError("Workspace field 'checkpoints' must be a list")

    checkpoints: list[WorkspaceCheckpoint] = []
    expected_fields = {
        "identifier",
        "created_at",
        "active_sprint",
        "completed_sprints",
        "validation_status",
    }
    for index, checkpoint_document in enumerate(value):
        if not isinstance(checkpoint_document, dict):
            raise WorkspaceLoadError(
                f"Workspace checkpoint {index} must be an object"
            )
        if set(checkpoint_document) != expected_fields:
            raise WorkspaceLoadError(
                f"Workspace checkpoint {index} has invalid fields"
            )

        try:
            created_at = datetime.fromisoformat(
                checkpoint_document["created_at"]
            )
            checkpoints.append(
                WorkspaceCheckpoint(
                    identifier=checkpoint_document["identifier"],
                    created_at=created_at,
                    active_sprint=checkpoint_document["active_sprint"],
                    completed_sprints=checkpoint_document["completed_sprints"],
                    validation_status=checkpoint_document["validation_status"],
                )
            )
        except (TypeError, ValueError) as error:
            raise WorkspaceLoadError(
                f"Invalid Workspace checkpoint {index}: {error}"
            ) from error

    try:
        return WorkspaceCheckpoints(checkpoints)
    except (TypeError, ValueError) as error:
        raise WorkspaceLoadError(
            f"Invalid Workspace checkpoints: {error}"
        ) from error
