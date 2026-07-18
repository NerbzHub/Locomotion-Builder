"""Sprint B03-S057 — Prompt Templates."""

from __future__ import annotations

from dataclasses import dataclass
from string import Formatter


_CONTEXT_FIELD = "engineering_context"


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """A reusable, deterministic prompt template."""

    name: str
    content: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Prompt template names must be non-empty strings")
        if not isinstance(self.content, str) or not self.content.strip():
            raise ValueError("Prompt template content must be non-empty text")

        fields = set()
        for _, field_name, format_spec, conversion in Formatter().parse(self.content):
            if field_name is not None:
                fields.add(field_name)
            if format_spec or conversion:
                raise ValueError("Prompt templates cannot use formats or conversions")
        if fields != {_CONTEXT_FIELD}:
            raise ValueError(
                "Prompt templates must contain only the engineering_context field"
            )

    def render(self, engineering_context: str) -> str:
        """Render one prompt from approved engineering context."""
        if not isinstance(engineering_context, str) or not engineering_context.strip():
            raise ValueError("Prompt templates require non-empty engineering context")
        return self.content.format(engineering_context=engineering_context)


DEFAULT_PROMPT_TEMPLATE = PromptTemplate(
    name="default",
    content=(
        "Implement the approved engineering Sprint below.\n\n"
        "{engineering_context}\n\n"
        "Work within the existing architecture. Keep the change focused, "
        "deterministic, recoverable, and independently verifiable. Review "
        "the implementation before treating the Sprint as complete."
    ),
)
