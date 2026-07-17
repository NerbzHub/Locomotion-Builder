"""Sprint B03-S075 — Performance Review."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from time import perf_counter

from builder.application.app import Application
from builder.jobs.job import Job

from .engineering import ReviewFinding, ReviewResult


@dataclass(frozen=True, slots=True)
class PerformanceReview:
    """An observed application run time for human performance assessment."""

    duration_seconds: float
    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.duration_seconds, float) or not isfinite(
            self.duration_seconds
        ):
            raise ValueError("Performance durations must be finite floats")
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Performance reviews require a ReviewResult")
        if self.result.name != "Performance":
            raise ValueError("Performance reviews require a Performance result")


class ReviewPerformanceJob(Job):
    """Measure one complete application run for performance review."""

    def __init__(
        self,
        application: Application,
        clock: Callable[[], float] = perf_counter,
    ):
        super().__init__("Review Application Performance")
        self.application = application
        self.clock = clock
        self.review: PerformanceReview | None = None

    def run(self) -> None:
        self.review = _review_performance(self.application, self.clock)


def review_performance(
    application: Application,
    clock: Callable[[], float] = perf_counter,
) -> PerformanceReview:
    """Measure application performance through the Job framework."""
    job = ReviewPerformanceJob(application, clock)
    job.execute()
    if job.review is None:
        raise RuntimeError("Performance review completed without a result")
    return job.review


def _review_performance(
    application: Application,
    clock: Callable[[], float],
) -> PerformanceReview:
    if not isinstance(application, Application):
        raise TypeError("Performance reviews require an Application")
    if not callable(clock):
        raise TypeError("Performance reviews require a clock callable")

    started_at = clock()
    application.run()
    duration_seconds = float(clock() - started_at)
    findings: tuple[ReviewFinding, ...] = ()
    if duration_seconds < 0:
        findings = (
            ReviewFinding(
                "measurement",
                "Performance clock produced a negative duration",
            ),
        )
    return PerformanceReview(
        duration_seconds=duration_seconds,
        result=ReviewResult(name="Performance", findings=findings),
    )
