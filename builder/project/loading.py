"""Sprint B03-S023 — Project Loading."""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .registration import ProjectRegistration, ProjectRegistrationError, recognise_project


class ProjectLoadingError(RuntimeError):
    """Raised when project metadata cannot be loaded safely."""


@dataclass(frozen=True, slots=True)
class ProjectMetadata:
    """Metadata available from a Builder project registration."""

    root: Path
    name: str
    format_version: int

    def __post_init__(self) -> None:
        root = Path(self.root)
        if not root.is_absolute():
            raise ValueError("Project metadata roots must be absolute paths")
        if not self.name:
            raise ValueError("Project metadata names must not be empty")
        if type(self.format_version) is not int:
            raise TypeError("Project metadata versions must be integers")
        object.__setattr__(self, "root", root)


class LoadProjectJob(Job):
    """Load metadata for one Builder-managed project."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Load Project")
        self.path = Path(path)
        self.metadata: ProjectMetadata | None = None

    def run(self) -> None:
        self.metadata = _load_project_metadata(self.path)


def load_project_metadata(path: str | PathLike[str]) -> ProjectMetadata:
    """Load registered project metadata through the Job framework."""
    job = LoadProjectJob(path)
    job.execute()

    if job.metadata is None:
        raise RuntimeError("Project loading completed without metadata")

    return job.metadata


def _load_project_metadata(path: Path) -> ProjectMetadata:
    try:
        registration = recognise_project(path)
    except ProjectRegistrationError as error:
        raise ProjectLoadingError(
            f"Unable to load project metadata from '{path}': {error}"
        ) from error

    if registration is None:
        raise ProjectLoadingError(
            f"Project path '{path}' is not registered with Locomotion Builder"
        )

    return _metadata_from_registration(registration)


def _metadata_from_registration(registration: ProjectRegistration) -> ProjectMetadata:
    return ProjectMetadata(
        root=registration.root,
        name=registration.root.name or registration.root.anchor,
        format_version=registration.format_version,
    )
