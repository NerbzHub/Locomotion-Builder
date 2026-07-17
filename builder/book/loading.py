"""Sprint B03-S032 — Document Loading."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass

from builder.jobs.job import Job

from .recognition import EngineeringBook


class DocumentLoadingError(RuntimeError):
    """Raised when engineering documentation cannot be loaded safely."""


@dataclass(frozen=True, slots=True)
class LoadedBook:
    """The UTF-8 content of one recognised engineering Book."""

    book: EngineeringBook
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.book, EngineeringBook):
            raise TypeError("Loaded Book documents require an EngineeringBook")
        if not isinstance(self.content, str):
            raise TypeError("Loaded Book content must be text")


class LoadBookDocumentJob(Job):
    """Load the documentation for one recognised engineering Book."""

    def __init__(self, book: EngineeringBook):
        super().__init__("Load Engineering Document")
        self.book = book
        self.document: LoadedBook | None = None

    def run(self) -> None:
        self.document = _load_book_document(self.book)


def load_book_document(book: EngineeringBook) -> LoadedBook:
    """Load one engineering Book through the Job framework."""
    job = LoadBookDocumentJob(book)
    job.execute()

    if job.document is None:
        raise RuntimeError("Document loading completed without a result")

    return job.document


def _load_book_document(book: EngineeringBook) -> LoadedBook:
    try:
        descriptor = os.open(
            book.path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        with os.fdopen(descriptor, "r", encoding="utf-8") as document_file:
            if not stat.S_ISREG(os.fstat(document_file.fileno()).st_mode):
                raise DocumentLoadingError(
                    f"Engineering Book '{book.path}' must be a regular file"
                )
            content = document_file.read()
    except DocumentLoadingError:
        raise
    except (OSError, UnicodeDecodeError) as error:
        raise DocumentLoadingError(
            f"Unable to load engineering Book '{book.path}': {error}"
        ) from error

    return LoadedBook(book=book, content=content)
