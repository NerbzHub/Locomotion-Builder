"""Sprint B03-S028 — Project Validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from builder.jobs.job import Job
from builder.project.loading import (
    ProjectLoadingError,
    ProjectMetadata,
    load_project_metadata,
)

from .model import Workspace


@dataclass(frozen=True, slots=True)
class ProjectValidationResult:
    """The integrity result for one Workspace project association."""

    metadata: ProjectMetadata | None
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all(isinstance(issue, str) and issue.strip() for issue in self.issues):
            raise ValueError("Project validation issues must be non-empty strings")
        if self.metadata is not None and self.issues:
            raise ValueError("Valid project metadata cannot have validation issues")
        if self.metadata is None and not self.issues:
            raise ValueError("Valid project validation requires metadata")

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def status(self) -> str:
        if self.is_valid:
            return "Project validation passed"
        return f"Project validation failed: {'; '.join(self.issues)}"


class ValidateProjectJob(Job):
    """Validate the project associated with one Workspace."""

    def __init__(self, workspace: Workspace):
        super().__init__("Validate Project")
        self.workspace = workspace
        self.result: ProjectValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_project(self.workspace)
        self.workspace.validation_status = self.result.status


def validate_project(workspace: Workspace) -> ProjectValidationResult:
    """Validate a Workspace project association through the Job framework."""
    job = ValidateProjectJob(workspace)
    job.execute()

    if job.result is None:
        raise RuntimeError("Project validation completed without a result")

    return job.result


def _validate_project(workspace: Workspace) -> ProjectValidationResult:
    project_root = workspace.project_root
    if project_root is None:
        return ProjectValidationResult(
            metadata=None,
            issues=("workspace has no associated project root",),
        )
    if not isinstance(project_root, Path) or not project_root.is_absolute():
        return ProjectValidationResult(
            metadata=None,
            issues=("workspace project root must be an absolute path",),
        )

    try:
        metadata = load_project_metadata(project_root)
    except ProjectLoadingError as error:
        return ProjectValidationResult(metadata=None, issues=(str(error),))

    issues: list[str] = []
    if metadata.root != project_root:
        issues.append("workspace project root is not canonical")
    if metadata.name != workspace.project_name:
        issues.append("workspace project name does not match the registered project")

    if issues:
        return ProjectValidationResult(metadata=None, issues=tuple(issues))

    return ProjectValidationResult(metadata=metadata)
