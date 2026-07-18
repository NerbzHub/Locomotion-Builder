"""Sprint B03-S036 — Construction Progress."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from builder.jobs.job import Job

from .sprints import ConstructionSprint


class ConstructionProgressError(ValueError):
    """Raised when completed construction state is inconsistent."""


@dataclass(frozen=True, slots=True)
class ConstructionProgress:
    """Explicit progress through an ordered construction sprint sequence."""

    sprints: tuple[ConstructionSprint, ...]
    completed_identifiers: tuple[str, ...]

    def __post_init__(self) -> None:
        identifiers = tuple(sprint.identifier for sprint in self.sprints)
        if len(set(identifiers)) != len(identifiers):
            raise ValueError("Construction progress requires unique Sprint IDs")
        if len(set(self.completed_identifiers)) != len(self.completed_identifiers):
            raise ValueError("Completed Sprint IDs must be unique")
        if self.completed_identifiers != identifiers[: len(self.completed_identifiers)]:
            raise ValueError("Completed Sprints must form a sequential prefix")

    @property
    def total_count(self) -> int:
        return len(self.sprints)

    @property
    def completed_count(self) -> int:
        return len(self.completed_identifiers)

    @property
    def active_sprint(self) -> ConstructionSprint | None:
        if self.completed_count == self.total_count:
            return None
        return self.sprints[self.completed_count]

    @property
    def is_complete(self) -> bool:
        return self.completed_count == self.total_count

    @property
    def completion_percent(self) -> float:
        if not self.sprints:
            return 100.0
        return self.completed_count / self.total_count * 100


class DetermineConstructionProgressJob(Job):
    """Determine construction progress from explicit completed Sprint IDs."""

    def __init__(
        self,
        sprints: tuple[ConstructionSprint, ...],
        completed_identifiers: Iterable[str] = (),
    ):
        super().__init__("Determine Construction Progress")
        self.sprints = sprints
        self.completed_identifiers = tuple(completed_identifiers)
        self.progress: ConstructionProgress | None = None

    def run(self) -> None:
        self.progress = _determine_construction_progress(
            self.sprints,
            self.completed_identifiers,
        )


def determine_construction_progress(
    sprints: tuple[ConstructionSprint, ...],
    completed_identifiers: Iterable[str] = (),
) -> ConstructionProgress:
    """Determine construction progress through the Job framework."""
    job = DetermineConstructionProgressJob(sprints, completed_identifiers)
    job.execute()

    if job.progress is None:
        raise RuntimeError("Construction progress completed without a result")

    return job.progress


def _determine_construction_progress(
    sprints: tuple[ConstructionSprint, ...],
    completed_identifiers: tuple[str, ...],
) -> ConstructionProgress:
    if any(not isinstance(sprint, ConstructionSprint) for sprint in sprints):
        raise TypeError("Construction progress requires ConstructionSprint values")
    if any(
        not isinstance(identifier, str) for identifier in completed_identifiers
    ):
        raise TypeError("Completed Sprint IDs must be strings")

    try:
        return ConstructionProgress(
            sprints=sprints,
            completed_identifiers=completed_identifiers,
        )
    except ValueError as error:
        raise ConstructionProgressError(str(error)) from error
