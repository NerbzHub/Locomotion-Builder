"""Sprint B03-S060 — Prompt Generator Version Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.shared.config import ApplicationSettings

from .history import PromptHistory
from .validation import PromptValidationResult, validate_prompt


PROMPT_GENERATOR_VERSION = "0.6.0"


@dataclass(frozen=True, slots=True)
class PromptVersionValidationResult:
    """The compatibility result for the v0.6.0 prompt-generation release."""

    prompt_validations: tuple[PromptValidationResult, ...]
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if any(
            not isinstance(validation, PromptValidationResult)
            for validation in self.prompt_validations
        ):
            raise TypeError("Version validation requires prompt validation results")
        if any(not isinstance(issue, str) or not issue for issue in self.issues):
            raise ValueError("Version validation issues must be non-empty strings")

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def status(self) -> str:
        if self.is_valid:
            return f"Prompt Generator v{PROMPT_GENERATOR_VERSION} validation passed"
        return (
            f"Prompt Generator v{PROMPT_GENERATOR_VERSION} validation failed: "
            f"{len(self.issues)} issue(s)"
        )


class ValidatePromptGeneratorVersionJob(Job):
    """Validate prompt-generation behaviour for the current release version."""

    def __init__(self, settings: ApplicationSettings, history: PromptHistory):
        super().__init__("Validate Prompt Generator Version")
        self.settings = settings
        self.history = history
        self.result: PromptVersionValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_prompt_generator_version(self.settings, self.history)


def validate_prompt_generator_version(
    settings: ApplicationSettings,
    history: PromptHistory,
) -> PromptVersionValidationResult:
    """Validate v0.6.0 prompt generation through the Job framework."""
    job = ValidatePromptGeneratorVersionJob(settings, history)
    job.execute()
    if job.result is None:
        raise RuntimeError("Prompt version validation completed without a result")
    return job.result


def _validate_prompt_generator_version(
    settings: ApplicationSettings,
    history: PromptHistory,
) -> PromptVersionValidationResult:
    if not isinstance(settings, ApplicationSettings):
        raise TypeError("Prompt version validation requires ApplicationSettings")
    if not isinstance(history, PromptHistory):
        raise TypeError("Prompt version validation requires a PromptHistory")

    validations = tuple(validate_prompt(entry.prompt) for entry in history.entries)
    issues: list[str] = []
    if settings.version != PROMPT_GENERATOR_VERSION:
        issues.append(
            f"Application version must be {PROMPT_GENERATOR_VERSION}"
        )
    for validation in validations:
        if not validation.is_valid:
            issues.extend(validation.issues)

    return PromptVersionValidationResult(
        prompt_validations=validations,
        issues=tuple(issues),
    )
