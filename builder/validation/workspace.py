"""Sprint B03-S062 — Workspace Validation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from builder.jobs.job import Job
from builder.workspace.checkpoint import WorkspaceCheckpoints
from builder.workspace.history import WorkspaceHistory
from builder.workspace.model import Workspace
from builder.workspace.settings import WorkspaceSettings

from .framework import ValidationFinding, ValidationResult, create_validation_result


class ValidateWorkspaceJob(Job):
    """Validate recoverable Workspace state without checking its project."""

    def __init__(self, workspace: Workspace):
        super().__init__("Validate Workspace")
        self.workspace = workspace
        self.result: ValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_workspace(self.workspace)
        self.workspace.validation_status = self.result.status


def validate_workspace(workspace: Workspace) -> ValidationResult:
    """Validate Workspace integrity through the Job framework."""
    job = ValidateWorkspaceJob(workspace)
    job.execute()
    if job.result is None:
        raise RuntimeError("Workspace validation completed without a result")
    return job.result


def _validate_workspace(workspace: Workspace) -> ValidationResult:
    if not isinstance(workspace, Workspace):
        raise TypeError("Workspace validation requires a Workspace")

    findings: list[ValidationFinding] = []
    _require_non_empty_string(findings, "workspace name", workspace.name)
    _require_non_empty_string(findings, "project name", workspace.project_name)
    _require_aware_datetime(findings, "creation time", workspace.created_at)
    _require_optional_string(findings, "active Sprint", workspace.active_sprint)
    _require_non_empty_string(findings, "version", workspace.version)
    _require_unique_strings(findings, "completed Sprints", workspace.completed_sprints)
    _require_optional_string(findings, "current Job", workspace.current_job)
    _require_optional_string(
        findings,
        "validation status",
        workspace.validation_status,
    )

    if workspace.project_root is not None and (
        not isinstance(workspace.project_root, Path)
        or not workspace.project_root.is_absolute()
    ):
        findings.append(
            ValidationFinding(
                "project root",
                "Workspace project root must be an absolute path or null",
            )
        )
    if not isinstance(workspace.settings, WorkspaceSettings):
        findings.append(ValidationFinding("settings", "Workspace settings are invalid"))
    if not isinstance(workspace.history, WorkspaceHistory):
        findings.append(ValidationFinding("history", "Workspace history is invalid"))
    if not isinstance(workspace.checkpoints, WorkspaceCheckpoints):
        findings.append(
            ValidationFinding("checkpoints", "Workspace checkpoints are invalid")
        )

    return create_validation_result("Workspace", tuple(findings))


def _require_non_empty_string(
    findings: list[ValidationFinding],
    check: str,
    value: object,
) -> None:
    if not isinstance(value, str) or not value.strip():
        findings.append(ValidationFinding(check, f"Workspace {check} must be text"))


def _require_optional_string(
    findings: list[ValidationFinding],
    check: str,
    value: object,
) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        findings.append(
            ValidationFinding(check, f"Workspace {check} must be text or null")
        )


def _require_aware_datetime(
    findings: list[ValidationFinding],
    check: str,
    value: object,
) -> None:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        findings.append(
            ValidationFinding(check, f"Workspace {check} must be timezone-aware")
        )


def _require_unique_strings(
    findings: list[ValidationFinding],
    check: str,
    values: object,
) -> None:
    if not isinstance(values, list) or any(
        not isinstance(value, str) or not value.strip() for value in values
    ):
        findings.append(
            ValidationFinding(check, f"Workspace {check} must be non-empty text")
        )
    elif len(set(values)) != len(values):
        findings.append(ValidationFinding(check, f"Workspace {check} must be unique"))
