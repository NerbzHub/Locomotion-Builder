from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from builder.jobs.job import Job


@dataclass(frozen=True, slots=True)
class HistoryEntry:
    """An immutable record of one significant engineering event."""

    timestamp: datetime
    description: str

    def __post_init__(self) -> None:
        if not isinstance(self.timestamp, datetime):
            raise TypeError("History entry timestamps must be datetime values")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("History entry timestamps must be timezone-aware")
        if not isinstance(self.description, str) or not self.description.strip():
            raise ValueError("History entry descriptions must be non-empty strings")

        object.__setattr__(
            self,
            "timestamp",
            self.timestamp.astimezone(timezone.utc),
        )


class WorkspaceHistory:
    """Maintains chronological, append-only engineering history."""

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[HistoryEntry] | None = None):
        self._entries: list[HistoryEntry] = []
        for entry in entries or ():
            self._append(entry)

    @property
    def entries(self) -> tuple[HistoryEntry, ...]:
        return tuple(self._entries)

    def _record(self, description: str, timestamp: datetime) -> HistoryEntry:
        entry = HistoryEntry(timestamp=timestamp, description=description)
        self._append(entry)
        return entry

    def _append(self, entry: HistoryEntry) -> None:
        if not isinstance(entry, HistoryEntry):
            raise TypeError("Workspace history accepts only HistoryEntry records")
        if self._entries and entry.timestamp < self._entries[-1].timestamp:
            raise ValueError("Workspace history entries must be chronological")
        self._entries.append(entry)

    def __len__(self) -> int:
        return len(self._entries)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkspaceHistory):
            return NotImplemented
        return self._entries == other._entries

    def __repr__(self) -> str:
        return f"WorkspaceHistory(entries={self._entries!r})"


class RecordHistoryJob(Job):
    """Append one engineering event to Workspace history."""

    def __init__(
        self,
        history: WorkspaceHistory,
        description: str,
        timestamp: datetime | None = None,
    ):
        super().__init__("Record Workspace History")
        self.history = history
        self.description = description
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.entry: HistoryEntry | None = None

    def run(self) -> None:
        self.entry = self.history._record(self.description, self.timestamp)


def record_history(
    history: WorkspaceHistory,
    description: str,
    timestamp: datetime | None = None,
) -> HistoryEntry:
    """Record one engineering event through the Job framework."""
    job = RecordHistoryJob(history, description, timestamp)
    job.execute()

    if job.entry is None:
        raise RuntimeError("History recording completed without an entry")

    return job.entry
