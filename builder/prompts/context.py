"""Sprint B03-S052 — Context Assembly."""

from __future__ import annotations

from dataclasses import dataclass

from builder.construction.selection import ConstructionTarget
from builder.jobs.job import Job


@dataclass(frozen=True, slots=True)
class PromptContext:
    """Approved engineering context used to generate one Sprint prompt."""

    target: ConstructionTarget
    book_identifier: str
    sprint_objective: str
    completed_sprints: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.target, ConstructionTarget):
            raise TypeError("Prompt contexts require a construction target")
        if not isinstance(self.book_identifier, str) or not self.book_identifier:
            raise ValueError("Prompt contexts require a Book identifier")
        if not isinstance(self.sprint_objective, str) or not self.sprint_objective:
            raise ValueError("Prompt contexts require a Sprint objective")
        if any(not isinstance(item, str) or not item for item in self.completed_sprints):
            raise ValueError("Completed Sprint identifiers must be non-empty strings")

    def render(self) -> str:
        """Render stable, human-readable engineering context."""
        completed_sprints = ", ".join(self.completed_sprints) or "none"
        return (
            f"Engineering Book: {self.book_identifier}\n"
            f"Sprint: {self.target.sprint.identifier} — {self.target.sprint.name}\n"
            f"Objective: {self.sprint_objective}\n"
            f"Completed sprints: {completed_sprints}"
        )


class AssemblePromptContextJob(Job):
    """Assemble approved engineering context for one active Sprint."""

    def __init__(self, target: ConstructionTarget):
        super().__init__("Assemble Prompt Context")
        self.target = target
        self.context: PromptContext | None = None

    def run(self) -> None:
        self.context = _assemble_prompt_context(self.target)


def assemble_prompt_context(target: ConstructionTarget) -> PromptContext:
    """Assemble prompt context through the Job framework."""
    job = AssemblePromptContextJob(target)
    job.execute()
    if job.context is None:
        raise RuntimeError("Prompt context assembly completed without a result")
    return job.context


def _assemble_prompt_context(target: ConstructionTarget) -> PromptContext:
    if not isinstance(target, ConstructionTarget):
        raise TypeError("Prompt context assembly requires a construction target")

    controller = target.controller
    if not controller.parser_validation.is_valid:
        raise ValueError("Prompt context requires valid parsed construction state")
    if controller.progress.active_sprint != target.sprint:
        raise ValueError("Prompt context requires the next incomplete Sprint")

    document = controller.parser_validation.report.structure.document
    objective = _extract_sprint_objective(document.content, target.sprint.line_number)
    return PromptContext(
        target=target,
        book_identifier=document.book.identifier,
        sprint_objective=objective,
        completed_sprints=tuple(controller.workspace.completed_sprints),
    )


def _extract_sprint_objective(content: str, sprint_line_number: int) -> str:
    lines = content.splitlines()
    objective_lines: list[str] = []
    for line in lines[sprint_line_number:]:
        if line.startswith("## "):
            break
        stripped = line.strip()
        if stripped and stripped != "---":
            objective_lines.append(stripped)

    objective = " ".join(objective_lines)
    if not objective:
        raise ValueError("Prompt context requires a documented Sprint objective")
    return objective
