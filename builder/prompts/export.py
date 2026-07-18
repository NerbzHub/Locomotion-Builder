"""Sprint B03-S056 — Prompt Export."""

from __future__ import annotations

import os
import tempfile
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

from .model import EngineeringPrompt


class PromptExportError(OSError):
    """Raised when a prompt cannot be exported safely."""


class ExportPromptJob(Job):
    """Export one prompt atomically as UTF-8 text."""

    def __init__(self, prompt: EngineeringPrompt, path: str | PathLike[str]):
        super().__init__("Export Engineering Prompt")
        self.prompt = prompt
        self.path = Path(path)

    def run(self) -> None:
        _export_prompt(self.prompt, self.path)


def export_prompt(prompt: EngineeringPrompt, path: str | PathLike[str]) -> None:
    """Export one engineering prompt through the Job framework."""
    job = ExportPromptJob(prompt, path)
    job.execute()


def _export_prompt(prompt: EngineeringPrompt, path: Path) -> None:
    if not isinstance(prompt, EngineeringPrompt):
        raise TypeError("Prompt export requires an EngineeringPrompt")
    if not path.name:
        raise PromptExportError("Prompt export requires a file path")

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as export_file:
            temporary_path = Path(export_file.name)
            export_file.write(prompt.content)
            export_file.write("\n")
            export_file.flush()
            os.fsync(export_file.fileno())
        os.replace(temporary_path, path)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise PromptExportError(
            f"Unable to export prompt to '{path}': {error}"
        ) from error
