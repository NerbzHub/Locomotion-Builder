"""Sprint B03-S035 — Dependency Recognition."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .sprints import ConstructionSprint


class DependencyRecognitionError(ValueError):
    """Raised when conceptual sprint dependencies are ambiguous."""


@dataclass(frozen=True, slots=True)
class ConceptualDependency:
    """One ordering dependency between two construction sprints."""

    sprint: ConstructionSprint
    prerequisite: ConstructionSprint

    def __post_init__(self) -> None:
        if not isinstance(self.sprint, ConstructionSprint):
            raise TypeError("Dependencies require a construction sprint")
        if not isinstance(self.prerequisite, ConstructionSprint):
            raise TypeError("Dependencies require a prerequisite sprint")
        if self.sprint.identifier == self.prerequisite.identifier:
            raise ValueError("Construction sprints cannot depend on themselves")


class RecogniseDependenciesJob(Job):
    """Identify conceptual dependencies from construction sprint order."""

    def __init__(self, sprints: tuple[ConstructionSprint, ...]):
        super().__init__("Recognise Conceptual Dependencies")
        self.sprints = sprints
        self.dependencies: tuple[ConceptualDependency, ...] = ()

    def run(self) -> None:
        self.dependencies = _recognise_conceptual_dependencies(self.sprints)


def recognise_conceptual_dependencies(
    sprints: tuple[ConstructionSprint, ...],
) -> tuple[ConceptualDependency, ...]:
    """Identify ordered sprint dependencies through the Job framework."""
    job = RecogniseDependenciesJob(sprints)
    job.execute()
    return job.dependencies


def _recognise_conceptual_dependencies(
    sprints: tuple[ConstructionSprint, ...],
) -> tuple[ConceptualDependency, ...]:
    identifiers: set[str] = set()
    for sprint in sprints:
        if not isinstance(sprint, ConstructionSprint):
            raise TypeError("Dependencies require ConstructionSprint values")
        if sprint.identifier in identifiers:
            raise DependencyRecognitionError(
                f"Construction Sprint '{sprint.identifier}' is ambiguous"
            )
        identifiers.add(sprint.identifier)

    return tuple(
        ConceptualDependency(sprint=sprint, prerequisite=prerequisite)
        for prerequisite, sprint in zip(sprints, sprints[1:])
    )
