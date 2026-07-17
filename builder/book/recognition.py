"""Sprint B03-S031 — Book Recognition."""

from __future__ import annotations

import re
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job
from builder.project.documentation import (
    DocumentationDiscoveryError,
    discover_engineering_documents,
)

_BOOK_FILENAME = re.compile(
    r"(?:^|\s)Book\s+(?P<number>\d{2})(?=$|\s|[-—])"
)


class BookRecognitionError(RuntimeError):
    """Raised when engineering Books cannot be recognised safely."""


@dataclass(frozen=True, slots=True)
class EngineeringBook:
    """One recognised engineering Book identified by its filename."""

    number: int
    path: Path

    def __post_init__(self) -> None:
        path = Path(self.path)
        if not 0 <= self.number <= 99:
            raise ValueError("Engineering Book numbers must be between 00 and 99")
        if not path.is_absolute():
            raise ValueError("Engineering Book paths must be absolute")
        object.__setattr__(self, "path", path)

    @property
    def identifier(self) -> str:
        return f"Book {self.number:02d}"


class RecogniseBooksJob(Job):
    """Recognise engineering Books for one Builder-managed project."""

    def __init__(self, project_path: str | PathLike[str]):
        super().__init__("Recognise Engineering Books")
        self.project_path = Path(project_path)
        self.books: tuple[EngineeringBook, ...] = ()

    def run(self) -> None:
        self.books = _recognise_engineering_books(self.project_path)


def recognise_engineering_books(
    project_path: str | PathLike[str],
) -> tuple[EngineeringBook, ...]:
    """Recognise project engineering Books through the Job framework."""
    job = RecogniseBooksJob(project_path)
    job.execute()
    return job.books


def _recognise_engineering_books(
    project_path: Path,
) -> tuple[EngineeringBook, ...]:
    try:
        documents = discover_engineering_documents(project_path)
    except DocumentationDiscoveryError as error:
        raise BookRecognitionError(
            f"Unable to recognise engineering Books from '{project_path}': {error}"
        ) from error

    books: list[EngineeringBook] = []
    book_numbers: set[int] = set()
    for document in documents:
        match = _BOOK_FILENAME.search(document.path.stem)
        if match is None:
            continue

        number = int(match.group("number"))
        if number in book_numbers:
            raise BookRecognitionError(
                f"Multiple engineering Books use identifier 'Book {number:02d}'"
            )
        book_numbers.add(number)
        books.append(EngineeringBook(number=number, path=document.path))

    return tuple(sorted(books, key=lambda book: (book.number, book.path)))
