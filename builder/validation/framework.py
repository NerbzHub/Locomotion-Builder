"""Sprint B03-S061 — Validation Framework."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One transparent finding from a named validation check."""

    check: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.check, str) or not self.check.strip():
            raise ValueError("Validation finding checks must be non-empty strings")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Validation finding messages must be non-empty strings")


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """The stable outcome of validation for one engineering scope."""

    scope: str
    findings: tuple[ValidationFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.scope, str) or not self.scope.strip():
            raise ValueError("Validation scopes must be non-empty strings")
        if any(not isinstance(finding, ValidationFinding) for finding in self.findings):
            raise TypeError("Validation results require ValidationFinding values")

    @property
    def is_valid(self) -> bool:
        return not self.findings

    @property
    def status(self) -> str:
        if self.is_valid:
            return f"{self.scope} validation passed"
        return f"{self.scope} validation failed: {len(self.findings)} issue(s)"


class CreateValidationResultJob(Job):
    """Create a standard validation result through the Job framework."""

    def __init__(
        self,
        scope: str,
        findings: tuple[ValidationFinding, ...] = (),
    ):
        super().__init__("Create Validation Result")
        self.scope = scope
        self.findings = findings
        self.result: ValidationResult | None = None

    def run(self) -> None:
        self.result = ValidationResult(scope=self.scope, findings=self.findings)


def create_validation_result(
    scope: str,
    findings: tuple[ValidationFinding, ...] = (),
) -> ValidationResult:
    """Create one validation result through the Job framework."""
    job = CreateValidationResultJob(scope, findings)
    job.execute()
    if job.result is None:
        raise RuntimeError("Validation result creation completed without a result")
    return job.result
