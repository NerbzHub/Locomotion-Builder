from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass(slots=True)
class Workspace:
    """Represents the active engineering workspace.

    Sprint B03-S011 introduces only the domain model.
    Persistence, loading and recovery are implemented in later sprints.
    """
    name: str
    project_name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    active_sprint: Optional[str] = None
    version: str = "0.2.0"
