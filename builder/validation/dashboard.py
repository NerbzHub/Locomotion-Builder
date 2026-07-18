"""Sprint B03-S068 — Validation Dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from builder.jobs.job import Job

from .history import ValidationHistory
from .report import ValidationReport


@dataclass(frozen=True, slots=True)
class ValidationDashboard:
    """A concise presentation of current validation status and activity."""

    report: ValidationReport
    history_event_count: int
    last_validated_at: datetime | None

    def __post_init__(self) -> None:
        if not isinstance(self.report, ValidationReport):
            raise TypeError("Validation dashboards require a ValidationReport")
        if type(self.history_event_count) is not int or self.history_event_count < 0:
            raise ValueError("Validation history counts must be non-negative integers")
        if self.last_validated_at is not None and not isinstance(
            self.last_validated_at,
            datetime,
        ):
            raise TypeError("Dashboard validation times must be datetime values")

    @property
    def status(self) -> str:
        return "Validation passed" if self.report.is_valid else "Validation failed"

    def render(self) -> str:
        """Render current validation status in a stable human-readable form."""
        last_validated = (
            self.last_validated_at.isoformat()
            if self.last_validated_at is not None
            else "never"
        )
        return (
            f"Status: {self.status}\n"
            f"Scopes: {len(self.report.results)}\n"
            f"Issues: {self.report.issue_count}\n"
            f"Validation events: {self.history_event_count}\n"
            f"Last validated: {last_validated}"
        )


class GenerateValidationDashboardJob(Job):
    """Present one report and validation history as current status."""

    def __init__(
        self,
        report: ValidationReport,
        history: ValidationHistory | None = None,
    ):
        super().__init__("Generate Validation Dashboard")
        self.report = report
        self.history = history
        self.dashboard: ValidationDashboard | None = None

    def run(self) -> None:
        self.dashboard = _generate_validation_dashboard(self.report, self.history)


def generate_validation_dashboard(
    report: ValidationReport,
    history: ValidationHistory | None = None,
) -> ValidationDashboard:
    """Generate a validation dashboard through the Job framework."""
    job = GenerateValidationDashboardJob(report, history)
    job.execute()
    if job.dashboard is None:
        raise RuntimeError("Validation dashboard generation completed without a result")
    return job.dashboard


def _generate_validation_dashboard(
    report: ValidationReport,
    history: ValidationHistory | None,
) -> ValidationDashboard:
    if not isinstance(report, ValidationReport):
        raise TypeError("Validation dashboards require a ValidationReport")
    if history is not None and not isinstance(history, ValidationHistory):
        raise TypeError("Validation dashboards require a ValidationHistory or null")

    latest_entry = history.entries[-1] if history and history.entries else None
    return ValidationDashboard(
        report=report,
        history_event_count=len(history) if history is not None else 0,
        last_validated_at=(
            latest_entry.validated_at if latest_entry is not None else None
        ),
    )
