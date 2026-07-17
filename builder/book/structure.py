"""Sprint B03-S033 — Structure Parsing."""

from __future__ import annotations

import re
from dataclasses import dataclass

from builder.jobs.job import Job

from .loading import LoadedBook

_FENCE = re.compile(r"^(?: {0,3})(?P<marker>`{3,}|~{3,})")
_HEADING = re.compile(
    r"^(?: {0,3})(?P<markers>#{1,6})[ \t]+(?P<title>.*?)(?:[ \t]+#+[ \t]*)?$"
)


class StructureParsingError(ValueError):
    """Raised when an engineering Book has invalid heading structure."""


@dataclass(frozen=True, slots=True)
class DocumentSection:
    """One ATX heading in an engineering Book."""

    level: int
    title: str
    line_number: int

    def __post_init__(self) -> None:
        if not 1 <= self.level <= 6:
            raise ValueError("Document section levels must be between 1 and 6")
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("Document section titles must be non-empty strings")
        if self.line_number < 1:
            raise ValueError("Document section line numbers must be positive")


@dataclass(frozen=True, slots=True)
class DocumentStructure:
    """The heading structure parsed from one loaded engineering Book."""

    document: LoadedBook
    sections: tuple[DocumentSection, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.document, LoadedBook):
            raise TypeError("Document structures require a loaded Book")
        if any(
            not isinstance(section, DocumentSection) for section in self.sections
        ):
            raise TypeError("Document structures require DocumentSection values")


class ParseDocumentStructureJob(Job):
    """Parse ATX heading structure from one loaded engineering Book."""

    def __init__(self, document: LoadedBook):
        super().__init__("Parse Document Structure")
        self.document = document
        self.structure: DocumentStructure | None = None

    def run(self) -> None:
        self.structure = _parse_document_structure(self.document)


def parse_document_structure(document: LoadedBook) -> DocumentStructure:
    """Parse engineering Book headings through the Job framework."""
    job = ParseDocumentStructureJob(document)
    job.execute()

    if job.structure is None:
        raise RuntimeError("Structure parsing completed without a result")

    return job.structure


def _parse_document_structure(document: LoadedBook) -> DocumentStructure:
    sections: list[DocumentSection] = []
    fence_marker: str | None = None

    for line_number, line in enumerate(document.content.splitlines(), start=1):
        fence_match = _FENCE.match(line)
        if fence_match is not None:
            marker = fence_match.group("marker")
            if fence_marker is None:
                fence_marker = marker
            elif marker[0] == fence_marker[0] and len(marker) >= len(fence_marker):
                fence_marker = None
            continue

        if fence_marker is not None:
            continue

        heading_match = _HEADING.match(line)
        if heading_match is None:
            continue

        title = heading_match.group("title").strip()
        if not title:
            raise StructureParsingError(
                f"Engineering Book '{document.book.path}' has an empty heading "
                f"on line {line_number}"
            )

        sections.append(
            DocumentSection(
                level=len(heading_match.group("markers")),
                title=title,
                line_number=line_number,
            )
        )

    return DocumentStructure(document=document, sections=tuple(sections))
