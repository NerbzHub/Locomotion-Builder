"""Sprint B03-S069 — Final Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.construction.controller import ConstructionController
from builder.jobs.job import Job
from builder.prompts.history import PromptHistory
from builder.prompts.validation import validate_prompt

from .construction import validate_construction
from .documentation import validate_documentation
from .framework import ValidationFinding, ValidationResult, create_validation_result
from .project import validate_project_structure
from .report import ValidationReport, generate_validation_report
from .workspace import validate_workspace


@dataclass(frozen=True, slots=True)
class FinalValidationResult:
    """The combined validation outcome for complete Builder functionality."""

    report: ValidationReport

    def __post_init__(self) -> None:
        if not isinstance(self.report, ValidationReport):
            raise TypeError("Final validation requires a ValidationReport")

    @property
    def is_valid(self) -> bool:
        return self.report.is_valid

    @property
    def status(self) -> str:
        if self.is_valid:
            return "Final Builder validation passed"
        return f"Final Builder validation failed: {self.report.issue_count} issue(s)"


class ValidateBuilderJob(Job):
    """Validate coordinated Workspace, construction, documentation, and prompts."""

    def __init__(
        self,
        controller: ConstructionController,
        prompt_history: PromptHistory,
    ):
        super().__init__("Validate Complete Builder")
        self.controller = controller
        self.prompt_history = prompt_history
        self.result: FinalValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_builder(self.controller, self.prompt_history)
        self.controller.workspace.validation_status = self.result.status


def validate_builder(
    controller: ConstructionController,
    prompt_history: PromptHistory,
) -> FinalValidationResult:
    """Validate complete Builder functionality through the Job framework."""
    job = ValidateBuilderJob(controller, prompt_history)
    job.execute()
    if job.result is None:
        raise RuntimeError("Final Builder validation completed without a result")
    return job.result


def _validate_builder(
    controller: ConstructionController,
    prompt_history: PromptHistory,
) -> FinalValidationResult:
    if not isinstance(controller, ConstructionController):
        raise TypeError("Final validation requires a ConstructionController")
    if not isinstance(prompt_history, PromptHistory):
        raise TypeError("Final validation requires a PromptHistory")

    workspace = controller.workspace
    results = (
        validate_workspace(workspace),
        validate_construction(controller),
        validate_documentation(controller.parser_validation),
        validate_project_structure(workspace),
        _validate_prompt_history(prompt_history),
    )
    return FinalValidationResult(report=generate_validation_report(results))


def _validate_prompt_history(history: PromptHistory) -> ValidationResult:
    findings: list[ValidationFinding] = []
    for entry in history.entries:
        validation = validate_prompt(entry.prompt)
        for issue in validation.issues:
            findings.append(
                ValidationFinding(
                    f"prompt {entry.prompt.sprint_identifier}",
                    issue,
                )
            )
    return create_validation_result("Prompt Generation", tuple(findings))
