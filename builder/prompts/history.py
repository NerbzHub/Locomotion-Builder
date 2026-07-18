"""Sprint B03-S055 — Prompt History."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from builder.jobs.job import Job

from .model import EngineeringPrompt
from .review import PromptReview


@dataclass(frozen=True, slots=True)
class PromptHistoryEntry:
    """An immutable record of one generated prompt and optional review."""

    prompt: EngineeringPrompt
    review: PromptReview | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, EngineeringPrompt):
            raise TypeError("Prompt history entries require an EngineeringPrompt")
        if self.review is not None:
            if not isinstance(self.review, PromptReview):
                raise TypeError("Prompt history reviews must be PromptReview values")
            if self.review.prompt != self.prompt:
                raise ValueError("Prompt history reviews must belong to their prompt")


class PromptHistory:
    """Maintains chronological, append-only prompt generation history."""

    __slots__ = ("_entries",)

    def __init__(self, entries: Iterable[PromptHistoryEntry] | None = None):
        self._entries: list[PromptHistoryEntry] = []
        for entry in entries or ():
            self._append(entry)

    @property
    def entries(self) -> tuple[PromptHistoryEntry, ...]:
        return tuple(self._entries)

    def _append(self, entry: PromptHistoryEntry) -> None:
        if not isinstance(entry, PromptHistoryEntry):
            raise TypeError("Prompt history accepts only PromptHistoryEntry records")
        if self._entries and entry.prompt.created_at < self._entries[-1].prompt.created_at:
            raise ValueError("Prompt history entries must be chronological")
        self._entries.append(entry)

    def __len__(self) -> int:
        return len(self._entries)


class RecordPromptHistoryJob(Job):
    """Record one generated prompt in append-only prompt history."""

    def __init__(
        self,
        history: PromptHistory,
        prompt: EngineeringPrompt,
        review: PromptReview | None = None,
    ):
        super().__init__("Record Prompt History")
        self.history = history
        self.prompt = prompt
        self.review = review
        self.entry: PromptHistoryEntry | None = None

    def run(self) -> None:
        entry = PromptHistoryEntry(prompt=self.prompt, review=self.review)
        self.history._append(entry)
        self.entry = entry


def record_prompt_history(
    history: PromptHistory,
    prompt: EngineeringPrompt,
    review: PromptReview | None = None,
) -> PromptHistoryEntry:
    """Record prompt generation through the Job framework."""
    job = RecordPromptHistoryJob(history, prompt, review)
    job.execute()
    if job.entry is None:
        raise RuntimeError("Prompt history recording completed without an entry")
    return job.entry
