"""Sprint B03-S070 — Validation Version Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.shared.config import ApplicationSettings

from .final import FinalValidationResult


VALIDATION_VERSION = "0.7.0"


@dataclass(frozen=True, slots=True)
class ValidationVersionValidationResult:
    """The release-readiness outcome for the v0.7.0 validation capability."""

    final_validation: FinalValidationResult
    issues: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.final_validation, FinalValidationResult):
            raise TypeError("Version validation requires FinalValidationResult")
        if any(not isinstance(issue, str) or not issue for issue in self.issues):
            raise ValueError("Version validation issues must be non-empty strings")

    @property
    def is_valid(self) -> bool:
        return not self.issues

    @property
    def status(self) -> str:
        if self.is_valid:
            return f"Validation v{VALIDATION_VERSION} release check passed"
        return (
            f"Validation v{VALIDATION_VERSION} release check failed: "
            f"{len(self.issues)} issue(s)"
        )


class ValidateValidationVersionJob(Job):
    """Validate final Builder functionality against the v0.7.0 release."""

    def __init__(
        self,
        settings: ApplicationSettings,
        final_validation: FinalValidationResult,
    ):
        super().__init__("Validate Validation Version")
        self.settings = settings
        self.final_validation = final_validation
        self.result: ValidationVersionValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_validation_version(
            self.settings,
            self.final_validation,
        )


def validate_validation_version(
    settings: ApplicationSettings,
    final_validation: FinalValidationResult,
) -> ValidationVersionValidationResult:
    """Validate the v0.7.0 release through the Job framework."""
    job = ValidateValidationVersionJob(settings, final_validation)
    job.execute()
    if job.result is None:
        raise RuntimeError("Validation version check completed without a result")
    return job.result


def _validate_validation_version(
    settings: ApplicationSettings,
    final_validation: FinalValidationResult,
) -> ValidationVersionValidationResult:
    if not isinstance(settings, ApplicationSettings):
        raise TypeError("Validation version checks require ApplicationSettings")
    if not isinstance(final_validation, FinalValidationResult):
        raise TypeError("Validation version checks require FinalValidationResult")

    issues: list[str] = []
    if settings.version != VALIDATION_VERSION:
        issues.append(f"Application version must be {VALIDATION_VERSION}")
    if not final_validation.is_valid:
        issues.append("Final Builder validation must pass before release")

    return ValidationVersionValidationResult(
        final_validation=final_validation,
        issues=tuple(issues),
    )
