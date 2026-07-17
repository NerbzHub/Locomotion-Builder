"""Sprint B03-S077 — Release Preparation."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.review.engineering import ReviewFinding, ReviewResult


RELEASE_VERSION = "1.0.0"
_REQUIRED_REVIEW_NAMES = frozenset(
    {
        "Engineering",
        "Documentation",
        "Workflow UX",
        "Stability",
        "Performance",
        "Reliability",
    }
)


@dataclass(frozen=True, slots=True)
class ReleasePreparation:
    """The explicit readiness evidence assembled for the Version 1 release."""

    reviews: tuple[ReviewResult, ...]
    findings: tuple[ReviewFinding, ...] = ()

    def __post_init__(self) -> None:
        if any(not isinstance(review, ReviewResult) for review in self.reviews):
            raise TypeError("Release preparation requires ReviewResult values")
        if any(not isinstance(finding, ReviewFinding) for finding in self.findings):
            raise TypeError("Release preparation findings must be ReviewFinding values")

    @property
    def is_ready(self) -> bool:
        return not self.findings

    @property
    def status(self) -> str:
        if self.is_ready:
            return f"Version {RELEASE_VERSION} release preparation passed"
        return (
            f"Version {RELEASE_VERSION} release preparation found "
            f"{len(self.findings)} issue(s)"
        )


class PrepareReleaseJob(Job):
    """Prepare explicit Version 1 release evidence from completed reviews."""

    def __init__(self, reviews: tuple[ReviewResult, ...]):
        super().__init__("Prepare Version 1 Release")
        self.reviews = reviews
        self.preparation: ReleasePreparation | None = None

    def run(self) -> None:
        self.preparation = _prepare_release(self.reviews)


def prepare_release(reviews: tuple[ReviewResult, ...]) -> ReleasePreparation:
    """Prepare Version 1 release evidence through the Job framework."""
    job = PrepareReleaseJob(reviews)
    job.execute()
    if job.preparation is None:
        raise RuntimeError("Release preparation completed without a result")
    return job.preparation


def _prepare_release(reviews: tuple[ReviewResult, ...]) -> ReleasePreparation:
    if not isinstance(reviews, tuple):
        raise TypeError("Release preparation requires a tuple of reviews")
    if any(not isinstance(review, ReviewResult) for review in reviews):
        raise TypeError("Release preparation requires ReviewResult values")

    findings: list[ReviewFinding] = []
    review_names = tuple(review.name for review in reviews)
    if len(set(review_names)) != len(review_names):
        findings.append(
            ReviewFinding("release evidence", "Release reviews must be unique")
        )
    missing_reviews = _REQUIRED_REVIEW_NAMES - set(review_names)
    for review_name in sorted(missing_reviews):
        findings.append(
            ReviewFinding("release evidence", f"Missing {review_name} review")
        )
    for review in reviews:
        for finding in review.findings:
            findings.append(
                ReviewFinding(f"{review.name}: {finding.area}", finding.message)
            )

    return ReleasePreparation(reviews=reviews, findings=tuple(findings))
