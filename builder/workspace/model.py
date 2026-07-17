from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from .settings import WorkspaceSettings


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class Workspace:
    """Represents the active engineering workspace.

    Construction progression is explicit and persisted with the Workspace.
    """
    name: str
    project_name: str
    created_at: datetime = field(default_factory=_utc_now)
    active_sprint: Optional[str] = None
    version: str = "0.2.0"
    completed_sprints: list[str] = field(default_factory=list)
    current_job: Optional[str] = None
    validation_status: Optional[str] = None
    settings: WorkspaceSettings = field(default_factory=WorkspaceSettings)
