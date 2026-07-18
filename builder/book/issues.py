"""Sprint B03-S038 — Error Reporting."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from builder.jobs.job import Job


@dataclass(frozen=True, slots=True)
class ParsingIssue:
    """One transparent issue encountered while parsing engineering Books."""

    stage: str
    message: str
    line_number: int | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.stage, str) or not self.stage.strip():
            raise ValueError("Parsing issue stages must be non-empty strings")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Parsing issue messages must be non-empty strings")
        if self.line_number is not None and self.line_number < 1:
            raise ValueError("Parsing issue line numbers must be positive")


@dataclass(frozen=True, slots=True)
class ParsingIssueReport:
    """An ordered, human-readable report of parsing issues."""

    issues: tuple[ParsingIssue, ...]

    def __post_init__(self) -> None:
        if any(not isinstance(issue, ParsingIssue) for issue in self.issues):
            raise TypeError("Parsing issue reports require ParsingIssue values")

    @property
    def is_clean(self) -> bool:
        return not self.issues

    def render(self) -> str:
        """Render parsing issues in their discovery order."""
        if self.is_clean:
            return "Parsing completed without issues"

        lines = []
        for issue in self.issues:
            location = (
                f" (line {issue.line_number})"
                if issue.line_number is not None
                else ""
            )
            lines.append(f"{issue.stage}: {issue.message}{location}")
        return "\n".join(lines)


class ReportParsingIssuesJob(Job):
    """Report an ordered set of parsing issues."""

    def __init__(self, issues: Iterable[ParsingIssue] = ()):
        super().__init__("Report Parsing Issues")
        self.issues = tuple(issues)
        self.report: ParsingIssueReport | None = None

    def run(self) -> None:
        self.report = ParsingIssueReport(issues=self.issues)


def report_parsing_issues(
    issues: Iterable[ParsingIssue] = (),
) -> ParsingIssueReport:
    """Report parser issues through the Job framework."""
    job = ReportParsingIssuesJob(issues)
    job.execute()

    if job.report is None:
        raise RuntimeError("Parsing issue reporting completed without a result")

    return job.report
