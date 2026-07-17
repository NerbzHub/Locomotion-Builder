"""Sprint B03-S027 — Workspace Association."""

from __future__ import annotations

from os import PathLike
from pathlib import Path

from builder.jobs.job import Job
from builder.project.loading import (
    ProjectLoadingError,
    ProjectMetadata,
    load_project_metadata,
)

from .model import Workspace


class WorkspaceAssociationError(RuntimeError):
    """Raised when a project cannot be associated with a Workspace."""


class AssociateProjectJob(Job):
    """Associate one registered project with one Workspace."""

    def __init__(self, workspace: Workspace, project_path: str | PathLike[str]):
        super().__init__("Associate Project")
        self.workspace = workspace
        self.project_path = Path(project_path)
        self.metadata: ProjectMetadata | None = None

    def run(self) -> None:
        self.metadata = _associate_project(self.workspace, self.project_path)


def associate_project(
    workspace: Workspace,
    project_path: str | PathLike[str],
) -> ProjectMetadata:
    """Associate a registered project with a Workspace through a Job."""
    job = AssociateProjectJob(workspace, project_path)
    job.execute()

    if job.metadata is None:
        raise RuntimeError("Project association completed without metadata")

    return job.metadata


def _associate_project(workspace: Workspace, project_path: Path) -> ProjectMetadata:
    try:
        metadata = load_project_metadata(project_path)
    except ProjectLoadingError as error:
        raise WorkspaceAssociationError(
            f"Unable to associate project '{project_path}': {error}"
        ) from error

    workspace.project_name = metadata.name
    workspace.project_root = metadata.root
    return metadata
