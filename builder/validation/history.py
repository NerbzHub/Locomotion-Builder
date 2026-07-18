"""Sprint B03-S067 — Validation History."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from builder.jobs.job import Job

from .report import ValidationReport


@dataclass(frozen=True, slots=True)
class ValidationHistoryEntry:
    """An immutable record of one completed validation event."""

    report: ValidationReport
    validated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.report, ValidationReport):
            raise TypeError("Validation history entries require a ValidationReport")
        if not isinstance(self.validated_at, datetime):
            raise TypeError("Validation history times must be datetime values")
        if self.validated_at.tzinfo is None or self.validated_at.utcoffset() is None:
            raise ValueError("Validation history times must be timezone-aware")
        object.__setattr__(
            self,
            "validated_at",
            self.validated_at.astimezone(timezone.utc),
        )


class ValidationHistory:
    """Maintains chronological, append-only validation event history."""

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[ValidationHistoryEntry] | None = None):
        self._entries: list[ValidationHistoryEntry] = []
        for entry in entries or ():
            self._append(entry)

    @property
    def entries(self) -> tuple[ValidationHistoryEntry, ...]:
        return tuple(self._entries)

    def _append(self, entry: ValidationHistoryEntry) -> None:
        if not isinstance(entry, ValidationHistoryEntry):
            raise TypeError(
                "Validation history accepts only ValidationHistoryEntry records"
            )
        if self._entries and entry.validated_at < self._entries[-1].validated_at:
            raise ValueError("Validation history entries must be chronological")
        self._entries.append(entry)

    def __len__(self) -> int:
        return len(self._entries)


class RecordValidationEventJob(Job):
    """Record one completed validation report in append-only history."""

    def __init__(
        self,
        history: ValidationHistory,
        report: ValidationReport,
        validated_at: datetime | None = None,
    ):
        super().__init__("Record Validation Event")
        self.history = history
        self.report = report
        self.validated_at = validated_at
        self.entry: ValidationHistoryEntry | None = None

    def run(self) -> None:
        entry = ValidationHistoryEntry(
            report=self.report,
            validated_at=self.validated_at or datetime.now(timezone.utc),
        )
        self.history._append(entry)
        self.entry = entry


def record_validation_event(
    history: ValidationHistory,
    report: ValidationReport,
    validated_at: datetime | None = None,
) -> ValidationHistoryEntry:
    """Record one validation event through the Job framework."""
    job = RecordValidationEventJob(history, report, validated_at)
    job.execute()
    if job.entry is None:
        raise RuntimeError("Validation event recording completed without an entry")
    return job.entry
