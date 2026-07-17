"""Sprint B03-S051 — Prompt Model."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


class PromptGenerationError(RuntimeError):
    """Raised when an engineering prompt cannot be produced safely."""


@dataclass(frozen=True, slots=True)
class EngineeringPrompt:
    """One immutable prompt prepared for a specific construction Sprint."""

    sprint_identifier: str
    sprint_name: str
    content: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.sprint_identifier, str) or not self.sprint_identifier:
            raise ValueError("Prompt Sprint identifiers must be non-empty strings")
        if not isinstance(self.sprint_name, str) or not self.sprint_name.strip():
            raise ValueError("Prompt Sprint names must be non-empty strings")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Prompt content must be non-empty text")
        if not isinstance(self.created_at, datetime):
            raise TypeError("Prompt creation times must be datetime values")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise ValueError("Prompt creation times must be timezone-aware")
        object.__setattr__(
            self,
            "created_at",
            self.created_at.astimezone(timezone.utc),
        )
