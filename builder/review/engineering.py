"""Sprint B03-S071 — Engineering Review."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.validation.final import FinalValidationResult


@dataclass(frozen=True, slots=True)
class ReviewFinding:
    """One transparent finding from a named readiness review."""

    area: str
    message: str

    def __post_init__(self) -> None:
        if not isinstance(self.area, str) or not self.area.strip():
            raise ValueError("Review finding areas must be non-empty strings")
        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("Review finding messages must be non-empty strings")


@dataclass(frozen=True, slots=True)
class ReviewResult:
    """The outcome of one evidence-based readiness review."""

    name: str
    findings: tuple[ReviewFinding, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Review names must be non-empty strings")
        if any(not isinstance(finding, ReviewFinding) for finding in self.findings):
            raise TypeError("Review results require ReviewFinding values")

    @property
    def is_ready(self) -> bool:
        return not self.findings

    @property
    def status(self) -> str:
        if self.is_ready:
            return f"{self.name} review passed"
        return f"{self.name} review found {len(self.findings)} issue(s)"


@dataclass(frozen=True, slots=True)
class EngineeringReview:
    """A complete engineering review grounded in final validation evidence."""

    final_validation: FinalValidationResult
    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.final_validation, FinalValidationResult):
            raise TypeError("Engineering reviews require FinalValidationResult")
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Engineering reviews require a ReviewResult")
        if self.result.name != "Engineering":
            raise ValueError("Engineering reviews require an Engineering result")


class ReviewEngineeringJob(Job):
    """Review complete Builder validation evidence for engineering readiness."""

    def __init__(self, final_validation: FinalValidationResult):
        super().__init__("Review Engineering")
        self.final_validation = final_validation
        self.review: EngineeringReview | None = None

    def run(self) -> None:
        self.review = _review_engineering(self.final_validation)


def review_engineering(final_validation: FinalValidationResult) -> EngineeringReview:
    """Conduct an engineering review through the Job framework."""
    job = ReviewEngineeringJob(final_validation)
    job.execute()
    if job.review is None:
        raise RuntimeError("Engineering review completed without a result")
    return job.review


def _review_engineering(final_validation: FinalValidationResult) -> EngineeringReview:
    if not isinstance(final_validation, FinalValidationResult):
        raise TypeError("Engineering reviews require FinalValidationResult")

    findings = tuple(
        ReviewFinding(result.scope, finding.message)
        for result in final_validation.report.results
        for finding in result.findings
    )
    return EngineeringReview(
        final_validation=final_validation,
        result=ReviewResult(name="Engineering", findings=findings),
    )
