"""Sprint B03-S026 — Source Discovery."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .loading import ProjectLoadingError, load_project_metadata

_SOURCE_SUFFIXES = frozenset(
    {
        ".c",
        ".cc",
        ".cpp",
        ".cs",
        ".cxx",
        ".go",
        ".h",
        ".hpp",
        ".java",
        ".js",
        ".jsx",
        ".kt",
        ".kts",
        ".m",
        ".mm",
        ".php",
        ".py",
        ".pyi",
        ".rb",
        ".rs",
        ".scala",
        ".sh",
        ".sql",
        ".swift",
        ".ts",
        ".tsx",
        ".vue",
    }
)


class SourceDiscoveryError(RuntimeError):
    """Raised when implementation sources cannot be discovered safely."""


@dataclass(frozen=True, slots=True)
class ImplementationSource:
    """One discoverable implementation source within a project."""

    path: Path

    def __post_init__(self) -> None:
        path = Path(self.path)
        if not path.is_absolute():
            raise ValueError("Implementation source paths must be absolute")
        if path.suffix.casefold() not in _SOURCE_SUFFIXES:
            raise ValueError("Implementation sources must use a supported suffix")
        object.__setattr__(self, "path", path)


class DiscoverSourcesJob(Job):
    """Locate implementation sources for one Builder-managed project."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Discover Sources")
        self.path = Path(path)
        self.sources: tuple[ImplementationSource, ...] = ()

    def run(self) -> None:
        self.sources = _discover_implementation_sources(self.path)


def discover_implementation_sources(
    path: str | PathLike[str],
) -> tuple[ImplementationSource, ...]:
    """Locate project implementation sources through the Job framework."""
    job = DiscoverSourcesJob(path)
    job.execute()
    return job.sources


def _discover_implementation_sources(
    path: Path,
) -> tuple[ImplementationSource, ...]:
    try:
        metadata = load_project_metadata(path)
    except ProjectLoadingError as error:
        raise SourceDiscoveryError(
            f"Unable to discover implementation sources from '{path}': {error}"
        ) from error

    sources: list[ImplementationSource] = []

    def on_error(error: OSError) -> None:
        raise SourceDiscoveryError(
            f"Unable to inspect project sources in '{metadata.root}': {error}"
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
            if candidate.suffix.casefold() not in _SOURCE_SUFFIXES:
                continue

            try:
                mode = candidate.lstat().st_mode
            except OSError as error:
                raise SourceDiscoveryError(
                    f"Unable to inspect implementation source '{candidate}': {error}"
                ) from error

            if stat.S_ISREG(mode):
                sources.append(ImplementationSource(path=candidate))

    return tuple(sources)
