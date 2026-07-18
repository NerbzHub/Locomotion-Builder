"""Sprint B03-S037 — Parsing Reports."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .dependencies import ConceptualDependency
from .progress import ConstructionProgress
from .sprints import ConstructionSprint
from .structure import DocumentStructure


@dataclass(frozen=True, slots=True)
class ParsingReport:
    """A deterministic summary of parsed engineering Book state."""

    structure: DocumentStructure
    sprints: tuple[ConstructionSprint, ...]
    dependencies: tuple[ConceptualDependency, ...]
    progress: ConstructionProgress

    def __post_init__(self) -> None:
        book = self.structure.document.book
        if any(sprint.book != book for sprint in self.sprints):
            raise ValueError("Parsing reports must contain Sprints from one Book")
        if self.progress.sprints != self.sprints:
            raise ValueError("Parsing report progress must use the reported Sprints")
        for dependency in self.dependencies:
            if (
                dependency.sprint not in self.sprints
                or dependency.prerequisite not in self.sprints
            ):
                raise ValueError(
                    "Parsing report dependencies must use the reported Sprints"
                )

    def render(self) -> str:
        """Render the parser summary in a stable human-readable form."""
        active_identifier = (
            self.progress.active_sprint.identifier
            if self.progress.active_sprint is not None
            else "none"
        )
        return (
            f"Book: {self.structure.document.book.identifier}\n"
            f"Sections: {len(self.structure.sections)}\n"
            f"Sprints: {len(self.sprints)}\n"
            f"Dependencies: {len(self.dependencies)}\n"
            f"Completed sprints: {self.progress.completed_count}\n"
            f"Active sprint: {active_identifier}\n"
            f"Progress: {self.progress.completion_percent:.1f}%"
        )


class GenerateParsingReportJob(Job):
    """Generate a summary from parsed engineering Book state."""

    def __init__(
        self,
        structure: DocumentStructure,
        sprints: tuple[ConstructionSprint, ...],
        dependencies: tuple[ConceptualDependency, ...],
        progress: ConstructionProgress,
    ):
        super().__init__("Generate Parsing Report")
        self.structure = structure
        self.sprints = sprints
        self.dependencies = dependencies
        self.progress = progress
        self.report: ParsingReport | None = None

    def run(self) -> None:
        self.report = ParsingReport(
            structure=self.structure,
            sprints=self.sprints,
            dependencies=self.dependencies,
            progress=self.progress,
        )


def generate_parsing_report(
    structure: DocumentStructure,
    sprints: tuple[ConstructionSprint, ...],
    dependencies: tuple[ConceptualDependency, ...],
    progress: ConstructionProgress,
) -> ParsingReport:
    """Generate a parser summary through the Job framework."""
    job = GenerateParsingReportJob(structure, sprints, dependencies, progress)
    job.execute()

    if job.report is None:
        raise RuntimeError("Parsing report generation completed without a result")

    return job.report
