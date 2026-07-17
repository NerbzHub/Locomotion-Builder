"""Sprint B03-S076 — Reliability Review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from builder.jobs.job import Job
from builder.workspace.model import Workspace
from builder.workspace.recover import recover_workspace
from builder.workspace.save import save_workspace

from .engineering import ReviewFinding, ReviewResult


@dataclass(frozen=True, slots=True)
class ReliabilityReview:
    """An isolated save-and-recovery review for one Workspace state."""

    result: ReviewResult

    def __post_init__(self) -> None:
        if not isinstance(self.result, ReviewResult):
            raise TypeError("Reliability reviews require a ReviewResult")
        if self.result.name != "Reliability":
            raise ValueError("Reliability reviews require a Reliability result")


class ReviewReliabilityJob(Job):
    """Exercise Workspace save and interrupted-state recovery safely."""

    def __init__(self, workspace: Workspace):
        super().__init__("Review Recovery Reliability")
        self.workspace = workspace
        self.review: ReliabilityReview | None = None

    def run(self) -> None:
        self.review = _review_reliability(self.workspace)


def review_reliability(workspace: Workspace) -> ReliabilityReview:
    """Review recovery behaviour through the Job framework."""
    job = ReviewReliabilityJob(workspace)
    job.execute()
    if job.review is None:
        raise RuntimeError("Reliability review completed without a result")
    return job.review


def _review_reliability(workspace: Workspace) -> ReliabilityReview:
    if not isinstance(workspace, Workspace):
        raise TypeError("Reliability reviews require a Workspace")

    findings: list[ReviewFinding] = []
    with TemporaryDirectory() as directory:
        primary_path = Path(directory) / "workspace.json"
        recovery_path = primary_path.with_name(".workspace.json.recovery.tmp")
        save_workspace(workspace, primary_path)
        primary_path.replace(recovery_path)
        primary_path.write_text("interrupted write", encoding="utf-8")
        recovered = recover_workspace(primary_path)

    if not _matches_workspace_state(workspace, recovered):
        findings.append(
            ReviewFinding(
                "recovery state",
                "Recovered Workspace does not match the saved state",
            )
        )

    return ReliabilityReview(
        result=ReviewResult(name="Reliability", findings=tuple(findings))
    )


def _matches_workspace_state(expected: Workspace, actual: Workspace) -> bool:
    return (
        expected.name == actual.name
        and expected.project_name == actual.project_name
        and expected.project_root == actual.project_root
        and expected.created_at == actual.created_at
        and expected.active_sprint == actual.active_sprint
        and expected.version == actual.version
        and expected.completed_sprints == actual.completed_sprints
        and expected.current_job == actual.current_job
        and expected.validation_status == actual.validation_status
        and expected.settings == actual.settings
        and expected.history == actual.history
        and expected.checkpoints == actual.checkpoints
    )
