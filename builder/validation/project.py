"""Sprint B03-S065 — Project Validation."""

from __future__ import annotations

from builder.jobs.job import Job
from builder.workspace.model import Workspace
from builder.workspace.validation import validate_project

from .framework import ValidationFinding, ValidationResult, create_validation_result


class ValidateProjectStructureJob(Job):
    """Validate one Workspace project's registered structure."""

    def __init__(self, workspace: Workspace):
        super().__init__("Validate Project Structure")
        self.workspace = workspace
        self.result: ValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_project_structure(self.workspace)
        self.workspace.validation_status = self.result.status


def validate_project_structure(workspace: Workspace) -> ValidationResult:
    """Validate project structure through the Job framework."""
    job = ValidateProjectStructureJob(workspace)
    job.execute()
    if job.result is None:
        raise RuntimeError("Project structure validation completed without a result")
    return job.result


def _validate_project_structure(workspace: Workspace) -> ValidationResult:
    if not isinstance(workspace, Workspace):
        raise TypeError("Project structure validation requires a Workspace")

    project_validation = validate_project(workspace)
    findings = tuple(
        ValidationFinding("project structure", issue)
        for issue in project_validation.issues
    )
    return create_validation_result("Project", findings)
