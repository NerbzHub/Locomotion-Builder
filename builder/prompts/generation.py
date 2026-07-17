"""Sprint B03-S053 — Sprint Prompt Generation."""

from __future__ import annotations

from datetime import datetime, timezone

from builder.jobs.job import Job

from .context import PromptContext
from .model import EngineeringPrompt


class GenerateSprintPromptJob(Job):
    """Generate a deterministic implementation prompt for one Sprint."""

    def __init__(
        self,
        context: PromptContext,
        created_at: datetime | None = None,
    ):
        super().__init__("Generate Sprint Prompt")
        self.context = context
        self.created_at = created_at
        self.prompt: EngineeringPrompt | None = None

    def run(self) -> None:
        self.prompt = _generate_sprint_prompt(self.context, self.created_at)


def generate_sprint_prompt(
    context: PromptContext,
    created_at: datetime | None = None,
) -> EngineeringPrompt:
    """Generate one Sprint prompt through the Job framework."""
    job = GenerateSprintPromptJob(context, created_at)
    job.execute()
    if job.prompt is None:
        raise RuntimeError("Sprint prompt generation completed without a result")
    return job.prompt


def _generate_sprint_prompt(
    context: PromptContext,
    created_at: datetime | None,
) -> EngineeringPrompt:
    if not isinstance(context, PromptContext):
        raise TypeError("Sprint prompt generation requires a PromptContext")

    sprint = context.target.sprint
    content = (
        "Implement the approved engineering Sprint below.\n\n"
        f"{context.render()}\n\n"
        "Work within the existing architecture. Keep the change focused, "
        "deterministic, recoverable, and independently verifiable. Review "
        "the implementation before treating the Sprint as complete."
    )
    return EngineeringPrompt(
        sprint_identifier=sprint.identifier,
        sprint_name=sprint.name,
        content=content,
        created_at=created_at or datetime.now(timezone.utc),
    )
