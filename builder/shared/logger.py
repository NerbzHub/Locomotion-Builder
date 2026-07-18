"""
Structured logging for the Locomotion Builder.

Sprint: B03-S004 — Logging Framework
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

class LogLevel(Enum):
    INFO="INFO"
    WARNING="WARNING"
    ERROR="ERROR"

@dataclass(frozen=True)
class LogEntry:
    timestamp:str
    level:LogLevel
    message:str

class Logger:
    def log(self, level:LogLevel, message:str)->None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        entry=LogEntry(timestamp, level, message)
        print(f"[{entry.timestamp}] [{entry.level.value}] {entry.message}")

    def info(self,message:str)->None:
        self.log(LogLevel.INFO,message)

    def warning(self,message:str)->None:
        self.log(LogLevel.WARNING,message)

    def error(self,message:str)->None:
        self.log(LogLevel.ERROR,message)
