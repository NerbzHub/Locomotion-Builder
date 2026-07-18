# Changelog

## 1.1.0 — Usable Engineering Workflow

### Added
- Public CLI workflows for project registration and inspection, Workspace association and checkpoints, Book analysis, construction status and progression, prompt generation and reviewed export, and final validation
- Persistent Workspace event history for project, Sprint, and prompt workflow actions
- End-to-end command-line regression coverage for a registered project and engineering Book

### Changed
- Default Workspace and application release versions now report 1.1.0
- Documentation now includes a complete local engineering workflow walkthrough

### Validation
- End-to-end command workflow validation passed

## 0.5.0 — Construction Manager

### Added
- Construction controller, ordered Sprint selection, Job scheduling, and execution
- Progress updates, stable recovery checkpoints, and append-only event history
- Construction state reports and lifecycle validation

### Validation
- Construction Manager v0.5.0 acceptance validation passed

## 0.4.0 — Book Parser

### Added
- Engineering Book recognition and safe document loading
- Document structure parsing and construction Sprint discovery
- Dependency recognition, construction progress, parser reporting, and validation

### Validation
- Book Parser v0.4.0 acceptance validation passed

## 0.3.0 — Project Discovery

### Added
- Builder-managed project registration, discovery, and metadata loading
- Project overview, documentation discovery, and source discovery
- Workspace project association, project validation, and discovery reporting

### Validation
- Project Discovery v0.3.0 acceptance validation passed

## 0.2.0 — Workspace Persistence

### Added
- Workspace model, creation, loading, and atomic saving
- Interrupted-save recovery
- Persistent construction state and Workspace settings
- Append-only engineering history
- Immutable Workspace checkpoint metadata

### Validation
- Workspace persistence and recovery passed

## B03-S009 — Progress Framework

### Added
- ProgressPanel
- Basic progress display

### Changed
- Application updates progress during lifecycle

### Validation
Passed
