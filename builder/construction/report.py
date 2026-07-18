"""Sprint B03-S048 — Construction Reports."""

from __future__ import annotations

from dataclasses import dataclass

from builder.book.progress import ConstructionProgress
from builder.jobs.job import Job

from .controller import ConstructionController


@dataclass(frozen=True, slots=True)
class ConstructionReport:
    """A stable summary of the current engineering construction state."""

    workspace_name: str
    project_name: str
    progress: ConstructionProgress
    active_sprint: str | None
    current_job: str | None
    validation_status: str | None
    checkpoint_count: int
    history_event_count: int

    def render(self) -> str:
        """Render the construction summary in a stable human-readable form."""
        active_sprint = self.active_sprint or "none"
        current_job = self.current_job or "none"
        validation_status = self.validation_status or "not validated"
        return (
            f"Workspace: {self.workspace_name}\n"
            f"Project: {self.project_name}\n"
            f"Completed sprints: {self.progress.completed_count}/"
            f"{self.progress.total_count}\n"
            f"Active sprint: {active_sprint}\n"
            f"Current job: {current_job}\n"
            f"Validation: {validation_status}\n"
            f"Checkpoints: {self.checkpoint_count}\n"
            f"History events: {self.history_event_count}\n"
            f"Progress: {self.progress.completion_percent:.1f}%"
        )


class GenerateConstructionReportJob(Job):
    """Generate one observable summary of construction state."""

    def __init__(self, controller: ConstructionController):
        super().__init__("Generate Construction Report")
        self.controller = controller
        self.report: ConstructionReport | None = None

    def run(self) -> None:
        self.report = _generate_construction_report(self.controller)


def generate_construction_report(
    controller: ConstructionController,
) -> ConstructionReport:
    """Generate a construction report through the Job framework."""
    job = GenerateConstructionReportJob(controller)
    job.execute()

    if job.report is None:
        raise RuntimeError("Construction report generation completed without a result")

    return job.report


def _generate_construction_report(
    controller: ConstructionController,
) -> ConstructionReport:
    if not isinstance(controller, ConstructionController):
        raise TypeError("Construction reports require a ConstructionController")

    workspace = controller.workspace
    return ConstructionReport(
        workspace_name=workspace.name,
        project_name=workspace.project_name,
        progress=controller.progress,
        active_sprint=workspace.active_sprint,
        current_job=workspace.current_job,
        validation_status=workspace.validation_status,
        checkpoint_count=len(workspace.checkpoints),
        history_event_count=len(workspace.history),
    )
