from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True, slots=True)
class WorkspaceCheckpoint:
    """An immutable snapshot of stable construction progression."""

    identifier: str
    created_at: datetime
    active_sprint: Optional[str] = None
    completed_sprints: tuple[str, ...] = ()
    validation_status: Optional[str] = None

    def __post_init__(self) -> None:
        if not isinstance(self.identifier, str) or not self.identifier.strip():
            raise ValueError("Checkpoint identifiers must be non-empty strings")
        if not isinstance(self.created_at, datetime):
            raise TypeError("Checkpoint creation times must be datetime values")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("Checkpoint creation times must be timezone-aware")
        if self.active_sprint is not None and not isinstance(
            self.active_sprint,
            str,
        ):
            raise TypeError("Checkpoint active sprint must be a string or null")
        if isinstance(self.active_sprint, str) and not self.active_sprint.strip():
            raise ValueError("Checkpoint active sprint cannot be empty")
        if not isinstance(self.completed_sprints, (list, tuple)):
            raise TypeError("Checkpoint completed sprints must be a sequence")

        completed_sprints = tuple(self.completed_sprints)
        if not all(
            isinstance(sprint, str) and sprint.strip()
            for sprint in completed_sprints
        ):
            raise ValueError(
                "Checkpoint completed sprints must be non-empty strings"
            )
        if len(set(completed_sprints)) != len(completed_sprints):
            raise ValueError("Checkpoint completed sprints must be unique")
        if self.validation_status is not None and not isinstance(
            self.validation_status,
            str,
        ):
            raise TypeError(
                "Checkpoint validation status must be a string or null"
            )
        if (
            isinstance(self.validation_status, str)
            and not self.validation_status.strip()
        ):
            raise ValueError("Checkpoint validation status cannot be empty")

        object.__setattr__(
            self,
            "created_at",
            self.created_at.astimezone(timezone.utc),
        )
        object.__setattr__(self, "completed_sprints", completed_sprints)


class WorkspaceCheckpoints:
    """Maintains chronological Workspace checkpoint metadata."""

    __slots__ = ("_checkpoints",)

    def __init__(
        self,
        checkpoints: Iterable[WorkspaceCheckpoint] | None = None,
    ):
        self._checkpoints: list[WorkspaceCheckpoint] = []
        for checkpoint in checkpoints or ():
            self._append(checkpoint)

    @property
    def checkpoints(self) -> tuple[WorkspaceCheckpoint, ...]:
        return tuple(self._checkpoints)

    def get(self, identifier: str) -> WorkspaceCheckpoint | None:
        for checkpoint in self._checkpoints:
            if checkpoint.identifier == identifier:
                return checkpoint
        return None

    def _append(self, checkpoint: WorkspaceCheckpoint) -> None:
        if not isinstance(checkpoint, WorkspaceCheckpoint):
            raise TypeError(
                "Workspace checkpoints accept only WorkspaceCheckpoint records"
            )
        if self.get(checkpoint.identifier) is not None:
            raise ValueError("Workspace checkpoint identifiers must be unique")
        if (
            self._checkpoints
            and checkpoint.created_at < self._checkpoints[-1].created_at
        ):
            raise ValueError("Workspace checkpoints must be chronological")
        self._checkpoints.append(checkpoint)

    def __len__(self) -> int:
        return len(self._checkpoints)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkspaceCheckpoints):
            return NotImplemented
        return self._checkpoints == other._checkpoints

    def __repr__(self) -> str:
        return f"WorkspaceCheckpoints(checkpoints={self._checkpoints!r})"
