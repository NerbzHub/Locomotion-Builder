"""Sprint B03-S029 — Discovery Reporting."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.workspace.model import Workspace
from builder.workspace.validation import ProjectValidationResult, validate_project

from .documentation import EngineeringDocument, discover_engineering_documents
from .overview import ProjectOverview, generate_project_overview
from .source import ImplementationSource, discover_implementation_sources


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    """A deterministic summary of project discovery results."""

    validation: ProjectValidationResult
    overview: ProjectOverview | None = None
    documents: tuple[EngineeringDocument, ...] = ()
    sources: tuple[ImplementationSource, ...] = ()

    def __post_init__(self) -> None:
        if self.validation.is_valid != (self.overview is not None):
            raise ValueError("Discovery reports must agree with project validation")
        if not self.validation.is_valid and (self.documents or self.sources):
            raise ValueError("Invalid projects cannot report discovered artifacts")

    def render(self) -> str:
        """Render the discovery summary in a stable human-readable form."""
        if not self.validation.is_valid:
            return self.validation.status

        if self.overview is None:
            raise RuntimeError("Valid discovery reports require project information")

        return (
            f"Project: {self.overview.name}\n"
            f"Root: {self.overview.root}\n"
            f"Registration format version: {self.overview.format_version}\n"
            f"Engineering documents: {len(self.documents)}\n"
            f"Implementation sources: {len(self.sources)}\n"
            f"Validation: {self.validation.status}"
        )


class GenerateDiscoveryReportJob(Job):
    """Summarise discovery results for one Workspace project."""

    def __init__(self, workspace: Workspace):
        super().__init__("Generate Discovery Report")
        self.workspace = workspace
        self.report: DiscoveryReport | None = None

    def run(self) -> None:
        self.report = _generate_discovery_report(self.workspace)


def generate_discovery_report(workspace: Workspace) -> DiscoveryReport:
    """Summarise project discovery through the Job framework."""
    job = GenerateDiscoveryReportJob(workspace)
    job.execute()

    if job.report is None:
        raise RuntimeError("Discovery reporting completed without a result")

    return job.report


def _generate_discovery_report(workspace: Workspace) -> DiscoveryReport:
    validation = validate_project(workspace)
    if not validation.is_valid:
        return DiscoveryReport(validation=validation)

    if validation.metadata is None:
        raise RuntimeError("Valid project validation completed without metadata")

    project_root = validation.metadata.root
    return DiscoveryReport(
        validation=validation,
        overview=generate_project_overview(project_root),
        documents=discover_engineering_documents(project_root),
        sources=discover_implementation_sources(project_root),
    )
