"""
Sprint B03-S005 — Job Framework
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum, auto

class JobStatus(Enum):
    PENDING=auto()
    RUNNING=auto()
    COMPLETED=auto()
    FAILED=auto()

class Job(ABC):
    def __init__(self,name:str):
        self.name=name
        self.status=JobStatus.PENDING

    def execute(self)->None:
        self.status=JobStatus.RUNNING
        try:
            self.run()
            self.status=JobStatus.COMPLETED
        except Exception:
            self.status=JobStatus.FAILED
            raise

    @abstractmethod
    def run(self)->None:
        ...
