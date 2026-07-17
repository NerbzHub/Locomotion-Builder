from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

from builder.jobs.job import Job

PROJECT_REGISTRATION_FILENAME = ".locomotion-builder.json"
_PROJECT_REGISTRATION_FORMAT = "locomotion-builder-project"
_PROJECT_REGISTRATION_VERSION = 1


class ProjectRegistrationError(RuntimeError):
    """Raised when project registration cannot be read or written safely."""


@dataclass(frozen=True, slots=True)
class ProjectRegistration:
    """Identifies one Builder-managed project root."""

    root: Path
    format_version: int = _PROJECT_REGISTRATION_VERSION

    def __post_init__(self) -> None:
        root = Path(self.root)
        if not root.is_absolute():
            raise ValueError("Project registration roots must be absolute paths")
        object.__setattr__(self, "root", root)
        if type(self.format_version) is not int:
            raise TypeError("Project registration version must be an integer")
        if self.format_version != _PROJECT_REGISTRATION_VERSION:
            raise ValueError("Unsupported project registration version")

    @property
    def marker_path(self) -> Path:
        return self.root / PROJECT_REGISTRATION_FILENAME


class RegisterProjectJob(Job):
    """Register one existing directory as a Builder-managed project."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Register Project")
        self.path = Path(path)
        self.registration: ProjectRegistration | None = None

    def run(self) -> None:
        self.registration = _register_project(self.path)


class RecogniseProjectJob(Job):
    """Recognise a Builder-managed project from its registration marker."""

    def __init__(self, path: str | PathLike[str]):
        super().__init__("Recognise Project")
        self.path = Path(path)
        self.registration: ProjectRegistration | None = None

    def run(self) -> None:
        self.registration = _recognise_project(self.path)


def register_project(path: str | PathLike[str]) -> ProjectRegistration:
    """Register an existing project directory through the Job framework."""
    job = RegisterProjectJob(path)
    job.execute()

    if job.registration is None:
        raise RuntimeError("Project registration completed without a result")

    return job.registration


def recognise_project(
    path: str | PathLike[str],
) -> ProjectRegistration | None:
    """Recognise a project directory through the Job framework."""
    job = RecogniseProjectJob(path)
    job.execute()
    return job.registration


def _register_project(path: Path) -> ProjectRegistration:
    root = _require_project_root(path)
    marker_path = root / PROJECT_REGISTRATION_FILENAME

    if marker_path.exists():
        return _read_registration(root, marker_path)

    document = {
        "format": _PROJECT_REGISTRATION_FORMAT,
        "version": _PROJECT_REGISTRATION_VERSION,
    }
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=root,
            prefix=f"{PROJECT_REGISTRATION_FILENAME}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(document, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, marker_path)
    except OSError as error:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise ProjectRegistrationError(
            f"Unable to register project '{root}': {error}"
        ) from error

    return ProjectRegistration(root=root)


def _recognise_project(path: Path) -> ProjectRegistration | None:
    root = _require_project_root(path)
    marker_path = root / PROJECT_REGISTRATION_FILENAME

    if not marker_path.exists():
        return None

    return _read_registration(root, marker_path)


def _read_registration(root: Path, marker_path: Path) -> ProjectRegistration:
    try:
        descriptor = os.open(
            marker_path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        )
        with os.fdopen(descriptor, "r", encoding="utf-8") as marker_file:
            if not stat.S_ISREG(os.fstat(marker_file.fileno()).st_mode):
                raise ProjectRegistrationError(
                    f"Project registration '{marker_path}' must be a regular file"
                )
            document = json.load(marker_file)
    except ProjectRegistrationError:
        raise
    except (OSError, json.JSONDecodeError) as error:
        raise ProjectRegistrationError(
            f"Unable to read project registration '{marker_path}': {error}"
        ) from error

    expected_fields = {"format", "version"}
    if not isinstance(document, dict) or set(document) != expected_fields:
        raise ProjectRegistrationError(
            f"Project registration '{marker_path}' has invalid fields"
        )
    if document["format"] != _PROJECT_REGISTRATION_FORMAT:
        raise ProjectRegistrationError(
            f"Project registration '{marker_path}' has an invalid format"
        )
    if (
        type(document["version"]) is not int
        or document["version"] != _PROJECT_REGISTRATION_VERSION
    ):
        raise ProjectRegistrationError(
            f"Project registration '{marker_path}' has an unsupported version"
        )

    return ProjectRegistration(
        root=root,
        format_version=document["version"],
    )


def _require_project_root(path: Path) -> Path:
    try:
        root = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise ProjectRegistrationError(
            f"Project path '{path}' is not accessible: {error}"
        ) from error

    if not root.is_dir():
        raise ProjectRegistrationError(
            f"Project path '{root}' must be a directory"
        )

    return root
