"""Sprint B03-S073 — UX Review."""

from __future__ import annotations

from dataclasses import dataclass

from builder.application.app import Application
from builder.jobs.job import Job

from .engineering import ReviewFinding, ReviewResult


@dataclass(frozen=True, slots=True)
class WorkflowReview:
    """A review of the available engineering console workflow."""

    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Workflow reviews require a ReviewResult")
        if self.result.name != "Workflow UX":
            raise ValueError("Workflow reviews require a Workflow UX result")


class ReviewWorkflowJob(Job):
    """Review the visible application workflow without changing its state."""

    def __init__(self, application: Application):
        super().__init__("Review Engineering Workflow")
        self.application = application
        self.review: WorkflowReview | None = None

    def run(self) -> None:
        self.review = _review_workflow(self.application)


def review_workflow(application: Application) -> WorkflowReview:
    """Review the engineering workflow through the Job framework."""
    job = ReviewWorkflowJob(application)
    job.execute()
    if job.review is None:
        raise RuntimeError("Workflow review completed without a result")
    return job.review


def _review_workflow(application: Application) -> WorkflowReview:
    if not isinstance(application, Application):
        raise TypeError("Workflow reviews require an Application")

    findings: list[ReviewFinding] = []
    for action in ("launch", "initialise", "shutdown", "run"):
        if not callable(getattr(application, action, None)):
            findings.append(
                ReviewFinding("application lifecycle", f"Missing '{action}' action")
            )
    if not application.settings.application_name.strip():
        findings.append(ReviewFinding("application identity", "Name is unavailable"))
    if not application.settings.version.strip():
        findings.append(ReviewFinding("application identity", "Version is unavailable"))
    if not callable(getattr(application.ui, "render", None)):
        findings.append(ReviewFinding("console", "Console rendering is unavailable"))
    if not isinstance(application.status.status, str) or not application.status.status:
        findings.append(ReviewFinding("status", "Visible status is unavailable"))
    if (
        not isinstance(application.progress.total, int)
        or application.progress.total <= 0
        or not isinstance(application.progress.current, int)
        or not 0 <= application.progress.current <= application.progress.total
    ):
        findings.append(
            ReviewFinding("progress", "Visible progress must remain within bounds")
        )

    return WorkflowReview(
        result=ReviewResult(name="Workflow UX", findings=tuple(findings))
    )
