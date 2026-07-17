"""Sprint B03-S080 — Version 1.0.0."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job
from builder.shared.config import ApplicationSettings

from .candidate import ReleaseCandidate
from .preparation import RELEASE_VERSION


class ReleaseVersionError(RuntimeError):
    """Raised when the Version 1 release cannot be activated safely."""


@dataclass(frozen=True, slots=True)
class VersionOneRelease:
    """The active production release backed by a verified candidate."""

    candidate: ReleaseCandidate
    settings: ApplicationSettings

    def __post_init__(self) -> None:
        if not isinstance(self.candidate, ReleaseCandidate):
            raise TypeError("Version 1 releases require a ReleaseCandidate")
        if not isinstance(self.settings, ApplicationSettings):
            raise TypeError("Version 1 releases require ApplicationSettings")
        if self.candidate.version != RELEASE_VERSION:
            raise ValueError("Release candidate has an unsupported version")
        if self.settings.version != RELEASE_VERSION:
            raise ValueError("Application settings must use the release version")


class ReleaseVersionOneJob(Job):
    """Activate Version 1 from one readiness-verified release candidate."""

    def __init__(
        self,
        candidate: ReleaseCandidate,
        settings: ApplicationSettings,
    ):
        super().__init__("Release Locomotion Builder Version 1")
        self.candidate = candidate
        self.settings = settings
        self.release: VersionOneRelease | None = None

    def run(self) -> None:
        self.release = _release_version_one(self.candidate, self.settings)


def release_version_one(
    candidate: ReleaseCandidate,
    settings: ApplicationSettings,
) -> VersionOneRelease:
    """Activate Version 1 through the Job framework."""
    job = ReleaseVersionOneJob(candidate, settings)
    job.execute()
    if job.release is None:
        raise RuntimeError("Version 1 release completed without a result")
    return job.release


def _release_version_one(
    candidate: ReleaseCandidate,
    settings: ApplicationSettings,
) -> VersionOneRelease:
    if not isinstance(candidate, ReleaseCandidate):
        raise TypeError("Version 1 release requires a ReleaseCandidate")
    if not isinstance(settings, ApplicationSettings):
        raise TypeError("Version 1 release requires ApplicationSettings")
    if not candidate.verification.is_ready:
        raise ReleaseVersionError("Version 1 release requires final verification")
    if settings.version != RELEASE_VERSION:
        raise ReleaseVersionError(
            f"Application version must be {RELEASE_VERSION} for release"
        )
    return VersionOneRelease(candidate=candidate, settings=settings)
