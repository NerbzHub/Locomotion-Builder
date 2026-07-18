"""Sprint B03-S024 — Project Overview."""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .loading import ProjectMetadata, load_project_metadata


@dataclass(frozen=True, slots=True)
class ProjectOverview:
    """A concise presentation of Builder project metadata."""

    name: str
    root: Path
    format_version: int

    def __post_init__(self) -> None:
        root = Path(self.root)
        if not root.is_absolute():
            raise ValueError("Project overview roots must be absolute paths")
        if not self.name:
            raise ValueError("Project overview names must not be empty")
        if type(self.format_version) is not int:
            raise TypeError("Project overview versions must be integers")
        object.__setattr__(self, "root", root)

    def render(self) -> str:
        """Render the project information in a stable human-readable form."""
        return (
            f"Project: {self.name}\n"
            f"Root: {self.root}\n"
            f"Registration format version: {self.format_version}"
        )


class GenerateProjectOverviewJob(Job):
    """Present metadata for one Builder-managed project."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Generate Project Overview")
        self.path = Path(path)
        self.overview: ProjectOverview | None = None

    def run(self) -> None:
        self.overview = _generate_project_overview(self.path)


def generate_project_overview(path: str | PathLike[str]) -> ProjectOverview:
    """Present project information through the Job framework."""
    job = GenerateProjectOverviewJob(path)
    job.execute()

    if job.overview is None:
        raise RuntimeError("Project overview generation completed without a result")

    return job.overview


def _generate_project_overview(path: Path) -> ProjectOverview:
    return _overview_from_metadata(load_project_metadata(path))


def _overview_from_metadata(metadata: ProjectMetadata) -> ProjectOverview:
    return ProjectOverview(
        name=metadata.name,
        root=metadata.root,
        format_version=metadata.format_version,
    )
