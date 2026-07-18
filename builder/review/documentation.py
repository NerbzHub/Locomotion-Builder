"""Sprint B03-S072 — Documentation Review."""

from __future__ import annotations

from dataclasses import dataclass

from builder.book.validation import ParserValidationResult
from builder.jobs.job import Job
from builder.validation.documentation import validate_documentation

from .engineering import ReviewFinding, ReviewResult


@dataclass(frozen=True, slots=True)
class DocumentationReview:
    """A documentation readiness review grounded in parser validation."""

    parser_validation: ParserValidationResult
    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.parser_validation, ParserValidationResult):
            raise TypeError("Documentation reviews require ParserValidationResult")
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Documentation reviews require a ReviewResult")
        if self.result.name != "Documentation":
            raise ValueError("Documentation reviews require a Documentation result")


class ReviewDocumentationJob(Job):
    """Review parsed engineering documentation for construction readiness."""

    def __init__(self, parser_validation: ParserValidationResult):
        super().__init__("Review Documentation")
        self.parser_validation = parser_validation
        self.review: DocumentationReview | None = None

    def run(self) -> None:
        self.review = _review_documentation(self.parser_validation)


def review_documentation(
    parser_validation: ParserValidationResult,
) -> DocumentationReview:
    """Conduct a documentation review through the Job framework."""
    job = ReviewDocumentationJob(parser_validation)
    job.execute()
    if job.review is None:
        raise RuntimeError("Documentation review completed without a result")
    return job.review


def _review_documentation(
    parser_validation: ParserValidationResult,
) -> DocumentationReview:
    if not isinstance(parser_validation, ParserValidationResult):
        raise TypeError("Documentation reviews require ParserValidationResult")

    validation = validate_documentation(parser_validation)
    result = ReviewResult(
        name="Documentation",
        findings=tuple(
            ReviewFinding(finding.check, finding.message)
            for finding in validation.findings
        ),
    )
    return DocumentationReview(parser_validation=parser_validation, result=result)
