"""Sprint B03-S063 — Construction Validation."""

from __future__ import annotations

from builder.book.progress import ConstructionProgressError
from builder.construction.controller import ConstructionController
from builder.jobs.job import Job

from .framework import ValidationFinding, ValidationResult, create_validation_result


class ValidateConstructionJob(Job):
    """Validate explicit construction progression for one controller."""

    def __init__(self, controller: ConstructionController):
        super().__init__("Validate Construction")
        self.controller = controller
        self.result: ValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_construction(self.controller)
        self.controller.workspace.validation_status = self.result.status


def validate_construction(controller: ConstructionController) -> ValidationResult:
    """Validate construction progression through the Job framework."""
    job = ValidateConstructionJob(controller)
    job.execute()
    if job.result is None:
        raise RuntimeError("Construction validation completed without a result")
    return job.result


def _validate_construction(controller: ConstructionController) -> ValidationResult:
    if not isinstance(controller, ConstructionController):
        raise TypeError("Construction validation requires a ConstructionController")

    findings: list[ValidationFinding] = []
    workspace = controller.workspace
    if not controller.parser_validation.is_valid:
        findings.append(
            ValidationFinding(
                "parsed construction state",
                "Construction requires valid parsed engineering documentation",
            )
        )

    try:
        progress = controller.progress
    except ConstructionProgressError as error:
        findings.append(ValidationFinding("progress", str(error)))
    else:
        expected_active_sprint = (
            progress.active_sprint.identifier
            if progress.active_sprint is not None
            else None
        )
        if workspace.active_sprint != expected_active_sprint:
            findings.append(
                ValidationFinding(
                    "active Sprint",
                    "Workspace active Sprint is inconsistent with progression",
                )
            )
        if (
            workspace.active_sprint is not None
            and workspace.active_sprint in workspace.completed_sprints
        ):
            findings.append(
                ValidationFinding(
                    "active Sprint",
                    "Workspace active Sprint cannot already be completed",
                )
            )

    return create_validation_result("Construction", tuple(findings))
