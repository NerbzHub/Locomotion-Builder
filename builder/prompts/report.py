"""Sprint B03-S059 — Prompt Reporting."""

from __future__ import annotations

from dataclasses import dataclass

from builder.jobs.job import Job

from .history import PromptHistory


@dataclass(frozen=True, slots=True)
class PromptReport:
    """A stable summary of recorded prompt-generation activity."""

    generated_count: int
    reviewed_count: int
    approved_count: int
    template_counts: tuple[tuple[str, int], ...]

    def __post_init__(self) -> None:
        counts = (self.generated_count, self.reviewed_count, self.approved_count)
        if any(type(count) is not int or count < 0 for count in counts):
            raise ValueError("Prompt report counts must be non-negative integers")
        if self.approved_count > self.reviewed_count:
            raise ValueError("Approved prompts cannot exceed reviewed prompts")
        if self.reviewed_count > self.generated_count:
            raise ValueError("Reviewed prompts cannot exceed generated prompts")
        if any(
            not isinstance(name, str) or not name or type(count) is not int or count < 1
            for name, count in self.template_counts
        ):
            raise ValueError("Prompt template counts must be valid name/count pairs")

    def render(self) -> str:
        """Render the prompt activity summary in a stable format."""
        templates = ", ".join(
            f"{name}: {count}" for name, count in self.template_counts
        ) or "none"
        return (
            f"Generated prompts: {self.generated_count}\n"
            f"Reviewed prompts: {self.reviewed_count}\n"
            f"Approved prompts: {self.approved_count}\n"
            f"Templates: {templates}"
        )


class GeneratePromptReportJob(Job):
    """Summarise recorded prompt-generation activity."""

    def __init__(self, history: PromptHistory):
        super().__init__("Generate Prompt Report")
        self.history = history
        self.report: PromptReport | None = None

    def run(self) -> None:
        self.report = _generate_prompt_report(self.history)


def generate_prompt_report(history: PromptHistory) -> PromptReport:
    """Generate a prompt activity report through the Job framework."""
    job = GeneratePromptReportJob(history)
    job.execute()
    if job.report is None:
        raise RuntimeError("Prompt report generation completed without a result")
    return job.report


def _generate_prompt_report(history: PromptHistory) -> PromptReport:
    if not isinstance(history, PromptHistory):
        raise TypeError("Prompt reports require a PromptHistory")

    template_counts: dict[str, int] = {}
    reviewed_count = 0
    approved_count = 0
    for entry in history.entries:
        template_name = entry.prompt.template_name
        template_counts[template_name] = template_counts.get(template_name, 0) + 1
        if entry.review is not None:
            reviewed_count += 1
            if entry.review.approved:
                approved_count += 1

    return PromptReport(
        generated_count=len(history),
        reviewed_count=reviewed_count,
        approved_count=approved_count,
        template_counts=tuple(sorted(template_counts.items())),
    )
