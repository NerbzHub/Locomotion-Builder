"""Sprint B03-S022 — Project Discovery."""

from __future__ import annotations

import os
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .registration import (
    PROJECT_REGISTRATION_FILENAME,
    ProjectRegistration,
    ProjectRegistrationError,
    recognise_project,
)


class ProjectDiscoveryError(RuntimeError):
    """Raised when project discovery cannot inspect a search root safely."""


class DiscoverProjectsJob(Job):
    """Locate Builder-managed projects beneath one directory tree."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Discover Projects")
        self.path = Path(path)
        self.projects: tuple[ProjectRegistration, ...] = ()

    def run(self) -> None:
        self.projects = _discover_projects(self.path)


def discover_projects(
    path: str | PathLike[str],
) -> tuple[ProjectRegistration, ...]:
    """Locate registered projects beneath a directory through the Job framework."""
    job = DiscoverProjectsJob(path)
    job.execute()
    return job.projects


def _discover_projects(path: Path) -> tuple[ProjectRegistration, ...]:
    root = _require_search_root(path)
    projects: list[ProjectRegistration] = []

    def on_error(error: OSError) -> None:
        raise ProjectDiscoveryError(
            f"Unable to inspect project search root '{root}': {error}"
        ) from error

    for directory, directories, filenames in os.walk(
        root,
        topdown=True,
        followlinks=False,
        onerror=on_error,
    ):
        directories.sort()
        filenames.sort()
        if PROJECT_REGISTRATION_FILENAME not in filenames:
            continue

        try:
            registration = recognise_project(Path(directory))
        except ProjectRegistrationError as error:
            raise ProjectDiscoveryError(
                f"Unable to recognise project in '{directory}': {error}"
            ) from error

        if registration is not None:
            projects.append(registration)

    return tuple(projects)


def _require_search_root(path: Path) -> Path:
    try:
        root = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ProjectDiscoveryError(
            f"Project search root '{path}' is not accessible: {error}"
        ) from error

    if not root.is_dir():
        raise ProjectDiscoveryError(
            f"Project search root '{root}' must be a directory"
        )

    return root
