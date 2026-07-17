"""Sprint B03-S066 — Report Generation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .framework import ValidationResult


@dataclass(frozen=True, slots=True)
class ValidationReport:
    """A stable summary of validation outcomes across engineering scopes."""

    results: tuple[ValidationResult, ...]

    def __post_init__(self) -> None:
        if any(not isinstance(result, ValidationResult) for result in self.results):
            raise TypeError("Validation reports require ValidationResult values")
        scopes = tuple(result.scope for result in self.results)
        if len(set(scopes)) != len(scopes):
            raise ValueError("Validation reports require unique scopes")

    @property
    def is_valid(self) -> bool:
        return all(result.is_valid for result in self.results)

    @property
    def issue_count(self) -> int:
        return sum(len(result.findings) for result in self.results)

    def render(self) -> str:
        """Render a stable, human-readable validation summary."""
        lines = [
            f"Validation scopes: {len(self.results)}",
            f"Validation issues: {self.issue_count}",
            f"Validation: {'passed' if self.is_valid else 'failed'}",
        ]
        lines.extend(f"{result.scope}: {result.status}" for result in self.results)
        return "\n".join(lines)


class GenerateValidationReportJob(Job):
    """Generate one report from explicit validation results."""

    def __init__(self, results: tuple[ValidationResult, ...]):
        super().__init__("Generate Validation Report")
        self.results = results
        self.report: ValidationReport | None = None

    def run(self) -> None:
        self.report = ValidationReport(results=self.results)


def generate_validation_report(
    results: tuple[ValidationResult, ...],
) -> ValidationReport:
    """Generate a validation report through the Job framework."""
    job = GenerateValidationReportJob(results)
    job.execute()
    if job.report is None:
        raise RuntimeError("Validation report generation completed without a result")
    return job.report
