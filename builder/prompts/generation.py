"""Sprint B03-S053 — Sprint Prompt Generation."""

from __future__ import annotations

from datetime import datetime, timezone

from builder.jobs.job import Job

from .context import PromptContext
from .model import EngineeringPrompt
from .templates import DEFAULT_PROMPT_TEMPLATE, PromptTemplate


class GenerateSprintPromptJob(Job):
    """Generate a deterministic implementation prompt for one Sprint."""

    def __init__(
        self,
        context: PromptContext,
        created_at: datetime | None = None,
        template: PromptTemplate = DEFAULT_PROMPT_TEMPLATE,
    ):
        super().__init__("Generate Sprint Prompt")
        self.context = context
        self.created_at = created_at
        self.template = template
        self.prompt: EngineeringPrompt | None = None

    def run(self) -> None:
        self.prompt = _generate_sprint_prompt(
            self.context,
            self.created_at,
            self.template,
        )


def generate_sprint_prompt(
    context: PromptContext,
    created_at: datetime | None = None,
    template: PromptTemplate = DEFAULT_PROMPT_TEMPLATE,
) -> EngineeringPrompt:
    """Generate one Sprint prompt through the Job framework."""
    job = GenerateSprintPromptJob(context, created_at, template)
    job.execute()
    if job.prompt is None:
        raise RuntimeError("Sprint prompt generation completed without a result")
    return job.prompt


def _generate_sprint_prompt(
    context: PromptContext,
    created_at: datetime | None,
    template: PromptTemplate,
) -> EngineeringPrompt:
    if not isinstance(context, PromptContext):
        raise TypeError("Sprint prompt generation requires a PromptContext")

    sprint = context.target.sprint
    if not isinstance(template, PromptTemplate):
        raise TypeError("Sprint prompt generation requires a PromptTemplate")
    content = template.render(context.render())
    return EngineeringPrompt(
        sprint_identifier=sprint.identifier,
        sprint_name=sprint.name,
        content=content,
        created_at=created_at or datetime.now(timezone.utc),
        template_name=template.name,
    )
