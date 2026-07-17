from __future__ import annotations

from collections.abc import Mapping
from math import isfinite
from types import MappingProxyType

from builder.jobs.job import Job

SettingValue = str | int | float | bool | None


class WorkspaceSettings:
    """Stores Builder configuration associated with a Workspace."""

    __slots__ = ("_values",)

    def __init__(
        self,
        values: Mapping[str, SettingValue] | None = None,
    ):
        self._values: dict[str, SettingValue] = {}
        for key, value in (values or {}).items():
            self._set(key, value)

    @property
    def values(self) -> Mapping[str, SettingValue]:
        return MappingProxyType(self._values)

    def get(
        self,
        key: str,
        default: SettingValue = None,
    ) -> SettingValue:
        return self._values.get(key, default)

    def as_dict(self) -> dict[str, SettingValue]:
        return dict(self._values)

    def _set(self, key: str, value: SettingValue) -> None:
        _validate_key(key)
        _validate_value(value)
        self._values[key] = value

    def _remove(self, key: str) -> bool:
        _validate_key(key)
        return self._values.pop(key, _MISSING) is not _MISSING

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, WorkspaceSettings):
            return NotImplemented
        return self._values == other._values

    def __repr__(self) -> str:
        return f"WorkspaceSettings(values={self._values!r})"


class SetWorkspaceSettingJob(Job):
    """Set one Workspace configuration value."""

    def __init__(
        self,
        settings: WorkspaceSettings,
        key: str,
        value: SettingValue,
    ):
        super().__init__("Set Workspace Setting")
        self.settings = settings
        self.key = key
        self.value = value

    def run(self) -> None:
        self.settings._set(self.key, self.value)


class RemoveWorkspaceSettingJob(Job):
    """Remove one Workspace configuration value."""

    def __init__(self, settings: WorkspaceSettings, key: str):
        super().__init__("Remove Workspace Setting")
        self.settings = settings
        self.key = key
        self.removed = False

    def run(self) -> None:
        self.removed = self.settings._remove(self.key)


def set_workspace_setting(
    settings: WorkspaceSettings,
    key: str,
    value: SettingValue,
) -> None:
    """Set a Workspace setting through the Job framework."""
    job = SetWorkspaceSettingJob(settings, key, value)
    job.execute()


def remove_workspace_setting(settings: WorkspaceSettings, key: str) -> bool:
    """Remove a Workspace setting through the Job framework."""
    job = RemoveWorkspaceSettingJob(settings, key)
    job.execute()
    return job.removed


def _validate_key(key: str) -> None:
    if not isinstance(key, str) or not key:
        raise ValueError("Workspace setting keys must be non-empty strings")


def _validate_value(value: SettingValue) -> None:
    if value is not None and not isinstance(value, (str, int, float, bool)):
        raise TypeError("Workspace setting values must be JSON scalar values")

    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Workspace setting float values must be finite")


_MISSING = object()
