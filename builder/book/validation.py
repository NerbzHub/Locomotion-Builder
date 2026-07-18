"""Sprint B03-S039 — Parser Validation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .issues import ParsingIssue, ParsingIssueReport
from .report import ParsingReport


@dataclass(frozen=True, slots=True)
class ParserValidationResult:
    """The validity of one parsed construction state."""

    report: ParsingReport
    issue_report: ParsingIssueReport

    def __post_init__(self) -> None:
        if not isinstance(self.report, ParsingReport):
            raise TypeError("Parser validation requires a ParsingReport")
        if not isinstance(self.issue_report, ParsingIssueReport):
            raise TypeError("Parser validation requires a ParsingIssueReport")

    @property
    def is_valid(self) -> bool:
        return self.issue_report.is_clean

    @property
    def status(self) -> str:
        if self.is_valid:
            return "Parser validation passed"
        return f"Parser validation failed: {len(self.issue_report.issues)} issue(s)"


class ValidateParsedConstructionStateJob(Job):
    """Validate one parsed construction state."""

    def __init__(self, report: ParsingReport, issue_report: ParsingIssueReport):
        super().__init__("Validate Parsed Construction State")
        self.report = report
        self.issue_report = issue_report
        self.result: ParserValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_parsed_construction_state(
            self.report,
            self.issue_report,
        )


def validate_parsed_construction_state(
    report: ParsingReport,
    issue_report: ParsingIssueReport,
) -> ParserValidationResult:
    """Validate parsed construction state through the Job framework."""
    job = ValidateParsedConstructionStateJob(report, issue_report)
    job.execute()

    if job.result is None:
        raise RuntimeError("Parser validation completed without a result")

    return job.result


def _validate_parsed_construction_state(
    report: ParsingReport,
    issue_report: ParsingIssueReport,
) -> ParserValidationResult:
    issues = list(issue_report.issues)
    if not report.structure.sections:
        issues.append(
            ParsingIssue(
                stage="Parser validation",
                message="no document sections were identified",
            )
        )
    if not report.sprints:
        issues.append(
            ParsingIssue(
                stage="Parser validation",
                message="no construction Sprints were identified",
            )
        )

    expected_dependencies = tuple(
        (sprint.identifier, prerequisite.identifier)
        for prerequisite, sprint in zip(report.sprints, report.sprints[1:])
    )
    actual_dependencies = tuple(
        (dependency.sprint.identifier, dependency.prerequisite.identifier)
        for dependency in report.dependencies
    )
    if actual_dependencies != expected_dependencies:
        issues.append(
            ParsingIssue(
                stage="Parser validation",
                message="conceptual dependencies do not match Sprint order",
            )
        )

    return ParserValidationResult(
        report=report,
        issue_report=ParsingIssueReport(issues=tuple(issues)),
    )
