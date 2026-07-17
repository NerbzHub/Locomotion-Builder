"""Sprint B03-S025 — Documentation Discovery."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .loading import ProjectLoadingError, load_project_metadata

_MARKDOWN_SUFFIX = ".md"


class DocumentationDiscoveryError(RuntimeError):
    """Raised when engineering documentation cannot be discovered safely."""


@dataclass(frozen=True, slots=True)
class EngineeringDocument:
    """One discoverable engineering document within a project."""

    path: Path

    def __post_init__(self) -> None:
        path = Path(self.path)
        if not path.is_absolute():
            raise ValueError("Engineering document paths must be absolute")
        if path.suffix.casefold() != _MARKDOWN_SUFFIX:
            raise ValueError("Engineering documents must be Markdown files")
        object.__setattr__(self, "path", path)


class DiscoverDocumentationJob(Job):
    """Locate Markdown engineering documentation for one project."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Discover Documentation")
        self.path = Path(path)
        self.documents: tuple[EngineeringDocument, ...] = ()

    def run(self) -> None:
        self.documents = _discover_engineering_documents(self.path)


def discover_engineering_documents(
    path: str | PathLike[str],
) -> tuple[EngineeringDocument, ...]:
    """Locate project Markdown documentation through the Job framework."""
    job = DiscoverDocumentationJob(path)
    job.execute()
    return job.documents


def _discover_engineering_documents(
    path: Path,
) -> tuple[EngineeringDocument, ...]:
    try:
        metadata = load_project_metadata(path)
    except ProjectLoadingError as error:
        raise DocumentationDiscoveryError(
            f"Unable to discover documentation from '{path}': {error}"
        ) from error

    documents: list[EngineeringDocument] = []

    def on_error(error: OSError) -> None:
        raise DocumentationDiscoveryError(
            f"Unable to inspect project documentation in '{metadata.root}': {error}"
        ) from error

    for directory, directories, filenames in os.walk(
        metadata.root,
        topdown=True,
        followlinks=False,
        onerror=on_error,
    ):
        directories.sort()
        filenames.sort()

        for filename in filenames:
            candidate = Path(directory) / filename
            if candidate.suffix.casefold() != _MARKDOWN_SUFFIX:
                continue

            try:
                mode = candidate.lstat().st_mode
            except OSError as error:
                raise DocumentationDiscoveryError(
                    f"Unable to inspect engineering document '{candidate}': {error}"
                ) from error

            if stat.S_ISREG(mode):
                documents.append(EngineeringDocument(path=candidate))

    return tuple(documents)
