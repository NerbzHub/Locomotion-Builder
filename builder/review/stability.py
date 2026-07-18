"""Sprint B03-S074 — Stability Review."""

from __future__ import annotations

from dataclasses import dataclass

from builder.construction.controller import ConstructionController
from builder.construction.lifecycle import (
    LifecycleValidationResult,
    validate_construction_lifecycle,
)
from builder.jobs.job import Job

from .engineering import ReviewFinding, ReviewResult


@dataclass(frozen=True, slots=True)
class StabilityReview:
    """An operational stability review grounded in lifecycle validation."""

    lifecycle_validation: LifecycleValidationResult
    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.lifecycle_validation, LifecycleValidationResult):
            raise TypeError("Stability reviews require LifecycleValidationResult")
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Stability reviews require a ReviewResult")
        if self.result.name != "Stability":
            raise ValueError("Stability reviews require a Stability result")


class ReviewStabilityJob(Job):
    """Review operational stability for one construction controller."""

    def __init__(self, controller: ConstructionController):
        super().__init__("Review Operational Stability")
        self.controller = controller
        self.review: StabilityReview | None = None

    def run(self) -> None:
        self.review = _review_stability(self.controller)


def review_stability(controller: ConstructionController) -> StabilityReview:
    """Review operational stability through the Job framework."""
    job = ReviewStabilityJob(controller)
    job.execute()
    if job.review is None:
        raise RuntimeError("Stability review completed without a result")
    return job.review


def _review_stability(controller: ConstructionController) -> StabilityReview:
    if not isinstance(controller, ConstructionController):
        raise TypeError("Stability reviews require a ConstructionController")

    lifecycle_validation = validate_construction_lifecycle(controller)
    return StabilityReview(
        lifecycle_validation=lifecycle_validation,
        result=ReviewResult(
            name="Stability",
            findings=tuple(
                ReviewFinding("construction lifecycle", issue)
                for issue in lifecycle_validation.issues
            ),
        ),
    )
