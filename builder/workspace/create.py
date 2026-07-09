
from __future__ import annotations

from .model import Workspace

def create_workspace(name:str, project_name:str)->Workspace:
    """Create a new in-memory Workspace.

    Introduced in Sprint B03-S012. Persistence is intentionally deferred
    to later sprints.
    """
    return Workspace(name=name, project_name=project_name)
