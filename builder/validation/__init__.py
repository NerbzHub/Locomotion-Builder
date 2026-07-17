"""Structured validation workflows for engineering progression."""

from .framework import (
    CreateValidationResultJob,
    ValidationFinding,
    ValidationResult,
    create_validation_result,
)
from .workspace import ValidateWorkspaceJob, validate_workspace
from .construction import ValidateConstructionJob, validate_construction
from .documentation import ValidateDocumentationJob, validate_documentation
from .project import ValidateProjectStructureJob, validate_project_structure
from .report import (
    GenerateValidationReportJob,
    ValidationReport,
    generate_validation_report,
)
from .history import (
    RecordValidationEventJob,
    ValidationHistory,
    ValidationHistoryEntry,
    record_validation_event,
)
from .dashboard import (
    GenerateValidationDashboardJob,
    ValidationDashboard,
    generate_validation_dashboard,
)
from .final import FinalValidationResult, ValidateBuilderJob, validate_builder

__all__ = [
    "CreateValidationResultJob",
    "FinalValidationResult",
    "GenerateValidationReportJob",
    "GenerateValidationDashboardJob",
    "RecordValidationEventJob",
    "ValidateConstructionJob",
    "ValidateBuilderJob",
    "ValidateDocumentationJob",
    "ValidateProjectStructureJob",
    "ValidationFinding",
    "ValidationDashboard",
    "ValidationHistory",
    "ValidationHistoryEntry",
    "ValidationResult",
    "ValidationReport",
    "ValidateWorkspaceJob",
    "create_validation_result",
    "generate_validation_report",
    "generate_validation_dashboard",
    "record_validation_event",
    "validate_construction",
    "validate_builder",
    "validate_documentation",
    "validate_project_structure",
    "validate_workspace",
]
