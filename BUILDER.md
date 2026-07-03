# BUILDER.md

Version: 1.0.0  
Status: Governing Directive  
Applies To: All Locomotion Builder engineering sessions

---

# Purpose

This document defines the engineering workflow used to develop the Locomotion Builder.

Unlike the Builder Books, which define the Builder itself, this document defines how engineering work shall be performed.

Every Builder development session shall begin by following this directive.

The objective is to ensure deterministic, consistent and professional engineering throughout the lifetime of the project.

---

# Builder Mission

The Locomotion Builder exists to orchestrate deterministic software construction.

It coordinates engineering work.

It does not replace engineering judgement.

Every engineering decision should strengthen the Builder's ability to remain:

- deterministic
- recoverable
- modular
- understandable
- maintainable

---

# Governing Documents

The Builder shall always be engineered according to the following hierarchy.

1. Book 01 — Constitution
2. Book 02 — Conceptual Architecture
3. Book 03 — Construction Schedule
4. Book 00 — Roadmap

Where conflict exists, higher documents take precedence.

Implementation must never contradict the governing Books.

---

# Engineering Philosophy

The Builder is a permanent engineering application.

Temporary solutions should be avoided.

Engineering quality takes precedence over development speed.

Simple architecture is preferred over clever architecture.

The Builder should become easier to extend over time rather than more difficult.

---

# Operating Modes

The Builder project operates in two modes.

## Architect Mode

Architect Mode is responsible for engineering decisions.

Typical activities include:

- architecture
- planning
- design
- documentation
- reviewing
- refactoring proposals

Architect Mode does not produce production implementation unless explicitly requested.

---

## Engineer Mode

Engineer Mode implements approved engineering work.

Engineer Mode follows the Construction Schedule.

Engineer Mode does not redesign completed architecture.

---

# Construction Workflow

Implementation shall always follow the Construction Schedule.

Every engineering session should execute the following workflow.

```
Load Books

↓

Identify Current Sprint

↓

Review Sprint Objective

↓

Implement Sprint

↓

Validate Sprint

↓

Create Checkpoint

↓

Summarise Progress

↓

Recommend Next Sprint
```

Future sprint objectives should not be implemented early.

---

# Sprint Rules

Every sprint has exactly one primary objective.

A sprint should:

- remain focused
- remain understandable
- remain independently verifiable

Implementation should satisfy the sprint objective completely before progressing.

---

# Definition of Done

A sprint is complete only when:

- sprint objective is satisfied
- implementation is internally consistent
- project compiles or executes where applicable
- validation has been completed
- checkpoint can be created
- summary has been produced

---

# Job-First Development

The Builder is fundamentally Job-driven.

Whenever new functionality is introduced, the following question should be asked first.

> Should this be represented as a Job?

Where practical, the answer should be yes.

Special-case workflows should be avoided.

The Job system is the operational core of the Builder.

---

# Documentation Authority

Documentation defines engineering intent.

Implementation realises documentation.

Documentation should not be modified to justify implementation shortcuts.

If implementation reveals a genuine architectural issue, the documentation should be formally reviewed before implementation changes proceed.

---

# Workspace Integrity

Workspace integrity is considered critical.

Engineering should never compromise the ability to:

- save
- recover
- resume
- validate

Recoverability always takes priority over convenience.

---

# Checkpoint Policy

Checkpoints should be created after meaningful engineering progress.

Every checkpoint should represent a stable construction state.

Checkpoint creation should never leave the Workspace inconsistent.

---

# Validation Policy

Every sprint concludes with validation.

Validation should confirm:

- sprint objective achieved
- no regression introduced
- architecture remains consistent
- documentation remains respected

Validation is mandatory.

---

# Engineering Standards

Implementation should emphasise:

- readability
- determinism
- modularity
- consistency
- maintainability

Avoid:

- unnecessary abstraction
- hidden behaviour
- duplicated logic
- speculative implementation
- tightly coupled systems

---

# Repository Principles

The repository should remain organised.

Files should have clear responsibilities.

Directory structures should communicate architecture naturally.

Naming should remain consistent throughout the project.

---

# Versioning

Version progression follows Book 03.

Versions should only advance after completing their scheduled validation sprint.

Version numbers represent engineering milestones rather than implementation size.

---

# Session Start Procedure

Every implementation session should begin by answering:

1. Which sprint is active?
2. What is its objective?
3. What Books govern this work?
4. What dependencies exist?
5. What constitutes completion?

Only then should implementation begin.

---

# Session End Procedure

Every engineering session should conclude by documenting:

Completed Sprint

Completed Objectives

Validation Results

Checkpoint Recommendation

Next Sprint

Known Issues (if any)

Future implementation should begin from this summary.

---

# AI Usage

Artificial Intelligence is an engineering assistant.

It is not the engineering authority.

AI-generated implementation should always conform to:

- Constitution
- Conceptual Architecture
- Construction Schedule

Human review remains mandatory.

---

# Long-Term Vision

The Builder is expected to evolve for many years.

Engineering decisions should prioritise long-term maintainability over short-term convenience.

Future capabilities should extend the existing architecture rather than replace it.

The Builder should become increasingly capable while preserving a small, understandable and dependable operational core.

---

# Directive Statement

Every Builder engineering session shall begin with this directive.

The Builder shall be engineered through deterministic, sequential construction.

Architecture precedes implementation.

Documentation governs engineering.

Jobs govern execution.

Workspaces preserve construction.

Checkpoints preserve progress.

Engineering quality always takes precedence over development speed.