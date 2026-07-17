"""Sprint B03-S058 — Prompt Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .model import EngineeringPrompt


@dataclass(frozen=True, slots=True)
class PromptValidationResult:
    """The observable validity of one generated engineering prompt."""

    prompt: EngineeringPrompt
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, EngineeringPrompt):
            raise TypeError("Prompt validation requires an EngineeringPrompt")
        if any(not isinstance(issue, str) or not issue for issue in self.issues):
            raise ValueError("Prompt validation issues must be non-empty strings")

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def status(self) -> str:
        if self.is_valid:
            return "Prompt validation passed"
        return f"Prompt validation failed: {len(self.issues)} issue(s)"


class ValidatePromptJob(Job):
    """Validate that one prompt identifies and scopes its Sprint."""

    def __init__(self, prompt: EngineeringPrompt):
        super().__init__("Validate Engineering Prompt")
        self.prompt = prompt
        self.result: PromptValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_prompt(self.prompt)


def validate_prompt(prompt: EngineeringPrompt) -> PromptValidationResult:
    """Validate one engineering prompt through the Job framework."""
    job = ValidatePromptJob(prompt)
    job.execute()
    if job.result is None:
        raise RuntimeError("Prompt validation completed without a result")
    return job.result


def _validate_prompt(prompt: EngineeringPrompt) -> PromptValidationResult:
    if not isinstance(prompt, EngineeringPrompt):
        raise TypeError("Prompt validation requires an EngineeringPrompt")

    issues: list[str] = []
    if prompt.sprint_identifier not in prompt.content:
        issues.append("Prompt does not identify its Sprint")
    if prompt.sprint_name not in prompt.content:
        issues.append("Prompt does not include its Sprint name")
    if "Objective:" not in prompt.content:
        issues.append("Prompt does not include a documented Sprint objective")
    if "{engineering_context}" in prompt.content:
        issues.append("Prompt contains an unrendered engineering context field")

    return PromptValidationResult(prompt=prompt, issues=tuple(issues))
