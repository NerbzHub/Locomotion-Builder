"""Sprint B03-S064 — Documentation Validation."""

from __future__ import annotations

from builder.book.validation import ParserValidationResult
from builder.jobs.job import Job

from .framework import ValidationFinding, ValidationResult, create_validation_result


class ValidateDocumentationJob(Job):
    """Validate parsed engineering documentation for construction use."""

    def __init__(self, parser_validation: ParserValidationResult):
        super().__init__("Validate Engineering Documentation")
        self.parser_validation = parser_validation
        self.result: ValidationResult | None = None

    def run(self) -> None:
        self.result = _validate_documentation(self.parser_validation)


def validate_documentation(
    parser_validation: ParserValidationResult,
) -> ValidationResult:
    """Validate engineering documentation through the Job framework."""
    job = ValidateDocumentationJob(parser_validation)
    job.execute()
    if job.result is None:
        raise RuntimeError("Documentation validation completed without a result")
    return job.result


def _validate_documentation(
    parser_validation: ParserValidationResult,
) -> ValidationResult:
    if not isinstance(parser_validation, ParserValidationResult):
        raise TypeError("Documentation validation requires ParserValidationResult")

    report = parser_validation.report
    document = report.structure.document
    findings: list[ValidationFinding] = []
    for issue in parser_validation.issue_report.issues:
        findings.append(ValidationFinding(issue.stage, issue.message))
    if not document.content.strip():
        findings.append(
            ValidationFinding("document content", "Engineering documentation is empty")
        )
    if not report.structure.sections:
        findings.append(
            ValidationFinding("document structure", "No documentation sections found")
        )
    if not report.sprints:
        findings.append(
            ValidationFinding("construction Sprints", "No construction Sprints found")
        )
    if not document.book.path.is_absolute():
        findings.append(
            ValidationFinding("document path", "Engineering Book path must be absolute")
        )

    return create_validation_result("Documentation", tuple(findings))
