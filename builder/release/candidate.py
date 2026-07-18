"""Sprint B03-S079 — Release Candidate."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from builder.jobs.job import Job

from .preparation import RELEASE_VERSION
from .verification import FinalVerification


class ReleaseCandidateError(RuntimeError):
    """Raised when a release candidate cannot be produced safely."""


@dataclass(frozen=True, slots=True)
class ReleaseCandidate:
    """One immutable, readiness-verified Version 1 release candidate."""

    verification: FinalVerification
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.verification, FinalVerification):
            raise TypeError("Release candidates require FinalVerification")
        if not self.verification.is_ready:
            raise ValueError("Release candidates require successful final verification")
        if not isinstance(self.created_at, datetime):
            raise TypeError("Release candidate times must be datetime values")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("Release candidate times must be timezone-aware")
        object.__setattr__(
            self,
            "created_at",
            self.created_at.astimezone(timezone.utc),
        )

    @property
    def version(self) -> str:
        return RELEASE_VERSION


class ProduceReleaseCandidateJob(Job):
    """Produce one Version 1 candidate from successful final verification."""

    def __init__(
        self,
        verification: FinalVerification,
        created_at: datetime | None = None,
    ):
        super().__init__("Produce Version 1 Release Candidate")
        self.verification = verification
        self.created_at = created_at
        self.candidate: ReleaseCandidate | None = None

    def run(self) -> None:
        self.candidate = _produce_release_candidate(
            self.verification,
            self.created_at,
        )


def produce_release_candidate(
    verification: FinalVerification,
    created_at: datetime | None = None,
) -> ReleaseCandidate:
    """Produce a release candidate through the Job framework."""
    job = ProduceReleaseCandidateJob(verification, created_at)
    job.execute()
    if job.candidate is None:
        raise RuntimeError("Release candidate production completed without a result")
    return job.candidate


def _produce_release_candidate(
    verification: FinalVerification,
    created_at: datetime | None,
) -> ReleaseCandidate:
    if not isinstance(verification, FinalVerification):
        raise TypeError("Release candidate production requires FinalVerification")
    if not verification.is_ready:
        raise ReleaseCandidateError(
            "Cannot produce a release candidate before successful verification"
        )
    return ReleaseCandidate(
        verification=verification,
        created_at=created_at or datetime.now(timezone.utc),
    )
