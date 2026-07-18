# Locomotion Builder — Book 04

## Version 1.1 Roadmap

**Version:** 1.1.0
**Status:** Implemented v1.1.0
**Document Type:** Product Delivery Roadmap

---

# 1. Purpose

Version 1.1 makes the Version 1 engineering workflow usable from the installed command-line application.

Version 1.0 established the Builder's deterministic domain services for workspace persistence, project discovery, book parsing, construction control, prompt generation, validation and release review. Version 1.1 connects those services into a coherent, documented workflow that an engineer can run against a real project.

The primary outcome is an engineer who can start with a project and approved engineering documentation, identify the next construction sprint, generate a reviewed implementation prompt, and preserve the resulting state for later recovery.

---

# 2. Product Outcome

At completion, the following workflow shall be available through the `locomotion-builder` command:

```text
create or open workspace
        ↓
associate and inspect project
        ↓
recognise and analyse engineering book
        ↓
identify next eligible sprint
        ↓
generate and review implementation prompt
        ↓
export prompt and checkpoint progress
        ↓
validate and report workspace state
```

Every operation shall be explicit, deterministic, recoverable and suitable for use without an AI provider or network connection.

---

# 3. Scope

Version 1.1 includes:

* a consistent command-line command hierarchy
* project association, inspection and discovery commands
* engineering-book recognition and sprint-analysis commands
* construction status and next-sprint selection commands
* prompt generation, review, export and history commands
* checkpoint, recovery, validation and report commands
* actionable command errors and stable machine-readable output where appropriate
* automated regression tests for the supported user workflows
* end-user documentation with a complete local walkthrough

---

# 4. Non-Goals

Version 1.1 does not introduce:

* automatic source-code implementation
* AI-provider, cloud-service or local-model integration
* a graphical or web user interface
* collaborative or multi-user workflows
* a plugin system
* dependency-graph visualisation or analytics dashboards

These remain candidate directions for later versions. Version 1.1 shall first make the existing deterministic workflow dependable and accessible.

---

# 5. Construction Principles

The Version 1.1 schedule follows the governing principles established by the Constitution and the Version 1 construction schedule.

* One primary objective per sprint.
* Every sprint produces a usable, verifiable increment.
* Commands shall orchestrate existing domain services rather than duplicate their business rules.
* Workspace mutations shall be persisted safely and remain recoverable.
* Human review remains mandatory for generated engineering prompts.
* Command output shall be clear for both interactive engineers and future automation.
* Every completed workflow shall have automated regression coverage.

---

# 6. Construction Schedule

## Phase I — Command Foundation

### Sprint B04-S001 — Command Architecture

Establish a consistent command hierarchy, shared application context, error handling and exit-code conventions for all Version 1.1 commands.

---

### Sprint B04-S002 — Workspace Operations

Extend workspace commands to create, show, save, recover, checkpoint and display workspace history through the public application interface.

---

### Sprint B04-S003 — Project Association

Allow an engineer to associate a workspace with an existing project and persist the association safely.

---

### Sprint B04-S004 — Project Inspection

Expose project metadata, source discovery, documentation discovery and project overview reporting through CLI commands.

---

## Phase II — Engineering Plan Interpretation

### Sprint B04-S005 — Book Analysis

Allow an engineer to recognise and load an approved engineering book, parse its structure and report parsing issues.

---

### Sprint B04-S006 — Sprint Discovery

Expose discovered construction sprints, objectives, dependencies and current progress in a readable command output.

---

### Sprint B04-S007 — Construction Control

Allow an engineer to initialise construction control, view construction status and select the next eligible sprint.

---

### Sprint B04-S008 — Construction Progress

Record completed construction progress, construction history and resumable checkpoints through explicit user commands.

---

## Phase III — Prompt Workflow

### Sprint B04-S009 — Prompt Generation

Generate a deterministic implementation prompt for the selected sprint using the associated project and parsed engineering context.

---

### Sprint B04-S010 — Prompt Review and Export

Allow prompt review, history inspection and safe export to an engineer-selected file.

---

## Phase IV — Operational Confidence

### Sprint B04-S011 — Validation and Reporting

Expose workspace, project, construction and final validation results, together with clear reports suitable for an engineering hand-off.

---

### Sprint B04-S012 — Guided Workflow and Release

Publish an end-to-end getting-started guide, add command-level regression coverage for the complete workflow, and verify Version 1.1 release readiness.

---

# 7. Completion Criteria

Version 1.1 is complete when:

* an engineer can complete the product outcome workflow using documented commands
* all supported commands return consistent output and meaningful exit codes
* workspace state survives interruption and can be recovered
* a selected sprint can produce a reviewed, exportable implementation prompt
* validation reports identify invalid or incomplete workflow state clearly
* the end-to-end workflow is covered by automated regression tests
* the application installs and runs with the declared supported Python version

---

# 8. Future Direction

After Version 1.1 proves the command-line workflow, the recommended next product decision is whether to prioritise a guided local interface or AI-provider integration.

The preferred sequence is a guided local interface first. It can reuse the stable Version 1.1 application services, makes the Builder accessible to non-terminal users, and preserves the deterministic, offline-capable core. AI integration should remain an optional provider layer introduced only after its authority boundaries, privacy model and failure behaviour are explicitly defined.

---

# Closing Statement

Version 1.1 is a productisation release. It does not expand the Builder's engineering authority; it makes the deterministic capabilities already established in Version 1 accessible, testable and useful in real engineering work.
