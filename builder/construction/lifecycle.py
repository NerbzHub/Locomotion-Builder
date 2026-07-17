"""Sprint B03-S049 — Lifecycle Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.book.progress import ConstructionProgressError, determine_construction_progress
from builder.jobs.job import Job
from builder.workspace.validation import validate_project

from .controller import ConstructionController


@dataclass(frozen=True, slots=True)
class LifecycleValidationResult:
    """The observable validity of one construction lifecycle state."""

    controller: ConstructionController
    issues: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.controller, ConstructionController):
            raise TypeError("Lifecycle validation requires a ConstructionController")
        if any(not isinstance(issue, str) or not issue for issue in self.issues):
            raise ValueError("Lifecycle validation issues must be non-empty strings")

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def status(self) -> str:
        if self.is_valid:
            return "Construction lifecycle validation passed"
        return f"Construction lifecycle validation failed: {len(self.issues)} issue(s)"


class ValidateConstructionLifecycleJob(Job):
    """Validate recoverable, observable construction lifecycle state."""

    def __init__(self, controller: ConstructionController):
        super().__init__("Validate Construction Lifecycle")
        self.controller = controller
        self.result: LifecycleValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_construction_lifecycle(self.controller)


def validate_construction_lifecycle(
    controller: ConstructionController,
) -> LifecycleValidationResult:
    """Validate construction lifecycle state through the Job framework."""
    job = ValidateConstructionLifecycleJob(controller)
    job.execute()

    if job.result is None:
        raise RuntimeError("Lifecycle validation completed without a result")

    return job.result


def _validate_construction_lifecycle(
    controller: ConstructionController,
) -> LifecycleValidationResult:
    if not isinstance(controller, ConstructionController):
        raise TypeError("Lifecycle validation requires a ConstructionController")

    workspace = controller.workspace
    issues: list[str] = []
    project_validation = validate_project(workspace)
    if not project_validation.is_valid:
        issues.extend(project_validation.issues)
    if not controller.parser_validation.is_valid:
        issues.append("Parsed construction state is not valid")
    if workspace.current_job is not None:
        issues.append("Workspace has an active Job")
    if not workspace.checkpoints.checkpoints:
        issues.append("Workspace has no recovery checkpoint")

    try:
        progress = controller.progress
    except ConstructionProgressError as error:
        issues.append(str(error))
    else:
        expected_active_sprint = (
            progress.active_sprint.identifier
            if progress.active_sprint is not None
            else None
        )
        if (
            workspace.active_sprint is not None
            and workspace.active_sprint != expected_active_sprint
        ):
            issues.append("Workspace active Sprint is inconsistent with progress")

        for checkpoint in workspace.checkpoints.checkpoints:
            try:
                checkpoint_progress = determine_construction_progress(
                    progress.sprints,
                    checkpoint.completed_sprints,
                )
            except ConstructionProgressError as error:
                issues.append(
                    f"Checkpoint '{checkpoint.identifier}' has invalid progress: {error}"
                )
                continue

            checkpoint_active_sprint = (
                checkpoint_progress.active_sprint.identifier
                if checkpoint_progress.active_sprint is not None
                else None
            )
            if (
                checkpoint.active_sprint is not None
                and checkpoint.active_sprint != checkpoint_active_sprint
            ):
                issues.append(
                    f"Checkpoint '{checkpoint.identifier}' has an inconsistent active Sprint"
                )

    result = LifecycleValidationResult(controller=controller, issues=tuple(issues))
    workspace.validation_status = result.status
    return result
