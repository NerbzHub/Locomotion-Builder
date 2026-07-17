"""Sprint B03-S034 — Sprint Discovery."""

from __future__ import annotations

import re
from dataclasses import dataclass

from builder.jobs.job import Job

from .recognition import EngineeringBook
from .structure import DocumentStructure

_SPRINT_IDENTIFIER = re.compile(r"B\d{2}-S\d{3}")
_SPRINT_TITLE = re.compile(
    r"^Sprint\s+(?P<identifier>B\d{2}-S\d{3})\s+[—-]\s+(?P<name>.+)$"
)


class SprintDiscoveryError(ValueError):
    """Raised when construction sprints cannot be identified safely."""


@dataclass(frozen=True, slots=True)
class ConstructionSprint:
    """One construction sprint identified from an engineering Book."""

    book: EngineeringBook
    identifier: str
    name: str
    line_number: int

    def __post_init__(self) -> None:
        if not isinstance(self.book, EngineeringBook):
            raise TypeError("Construction sprints require an EngineeringBook")
        if _SPRINT_IDENTIFIER.fullmatch(self.identifier) is None:
            raise ValueError("Construction sprint identifiers must use BNN-SNNN")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Construction sprint names must be non-empty strings")
        if self.line_number < 1:
            raise ValueError("Construction sprint line numbers must be positive")


class DiscoverSprintsJob(Job):
    """Identify construction sprints from parsed Book structure."""

    def __init__(self, structure: DocumentStructure):
        super().__init__("Discover Construction Sprints")
        self.structure = structure
        self.sprints: tuple[ConstructionSprint, ...] = ()

    def run(self) -> None:
        self.sprints = _discover_construction_sprints(self.structure)


def discover_construction_sprints(
    structure: DocumentStructure,
) -> tuple[ConstructionSprint, ...]:
    """Identify Book construction sprints through the Job framework."""
    job = DiscoverSprintsJob(structure)
    job.execute()
    return job.sprints


def _discover_construction_sprints(
    structure: DocumentStructure,
) -> tuple[ConstructionSprint, ...]:
    sprints: list[ConstructionSprint] = []
    identifiers: set[str] = set()
    book = structure.document.book

    for section in structure.sections:
        if section.level != 2 or not section.title.startswith("Sprint"):
            continue

        match = _SPRINT_TITLE.fullmatch(section.title)
        if match is None:
            raise SprintDiscoveryError(
                f"Engineering Book '{book.path}' has an invalid Sprint heading "
                f"on line {section.line_number}"
            )

        identifier = match.group("identifier")
        if identifier in identifiers:
            raise SprintDiscoveryError(
                f"Engineering Book '{book.path}' defines Sprint '{identifier}' "
                "more than once"
            )
        identifiers.add(identifier)
        sprints.append(
            ConstructionSprint(
                book=book,
                identifier=identifier,
                name=match.group("name").strip(),
                line_number=section.line_number,
            )
        )

    return tuple(sprints)
