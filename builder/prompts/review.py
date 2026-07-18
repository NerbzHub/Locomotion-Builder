"""Sprint B03-S054 — Prompt Review."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from builder.jobs.job import Job

from .model import EngineeringPrompt


@dataclass(frozen=True, slots=True)
class PromptReview:
    """An explicit human review decision for one engineering prompt."""

    prompt: EngineeringPrompt
    reviewer: str
    approved: bool
    observations: tuple[str, ...]
    reviewed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, EngineeringPrompt):
            raise TypeError("Prompt reviews require an EngineeringPrompt")
        if not isinstance(self.reviewer, str) or not self.reviewer.strip():
            raise ValueError("Prompt reviewers must be non-empty strings")
        if type(self.approved) is not bool:
            raise TypeError("Prompt review approval must be boolean")
        if any(
            not isinstance(observation, str) or not observation.strip()
            for observation in self.observations
        ):
            raise ValueError("Prompt review observations must be non-empty strings")
        if not isinstance(self.reviewed_at, datetime):
            raise TypeError("Prompt review times must be datetime values")
        if self.reviewed_at.tzinfo is None or self.reviewed_at.utcoffset() is None:
            raise ValueError("Prompt review times must be timezone-aware")
        object.__setattr__(
            self,
            "reviewed_at",
            self.reviewed_at.astimezone(timezone.utc),
        )


class ReviewPromptJob(Job):
    """Record an explicit engineering review of a generated prompt."""

    def __init__(
        self,
        prompt: EngineeringPrompt,
        reviewer: str,
        approved: bool,
        observations: tuple[str, ...] = (),
        reviewed_at: datetime | None = None,
    ):
        super().__init__("Review Engineering Prompt")
        self.prompt = prompt
        self.reviewer = reviewer
        self.approved = approved
        self.observations = observations
        self.reviewed_at = reviewed_at
        self.review: PromptReview | None = None

    def run(self) -> None:
        self.review = PromptReview(
            prompt=self.prompt,
            reviewer=self.reviewer,
            approved=self.approved,
            observations=self.observations,
            reviewed_at=self.reviewed_at or datetime.now(timezone.utc),
        )


def review_prompt(
    prompt: EngineeringPrompt,
    reviewer: str,
    approved: bool,
    observations: tuple[str, ...] = (),
    reviewed_at: datetime | None = None,
) -> PromptReview:
    """Record one human prompt review through the Job framework."""
    job = ReviewPromptJob(
        prompt,
        reviewer,
        approved,
        observations,
        reviewed_at,
    )
    job.execute()
    if job.review is None:
        raise RuntimeError("Prompt review completed without a result")
    return job.review
