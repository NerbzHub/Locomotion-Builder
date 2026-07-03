# Locomotion Builder — Book 02

## Conceptual Architecture

**Version:** 1.0.0
**Status:** Governing Document
**Document Type:** Conceptual Architecture

---

# Preface

This document defines the conceptual architecture of the Locomotion Builder.

It describes how the Builder is organised at a systems level without prescribing implementation details.

The purpose of this document is to establish stable architectural boundaries that guide implementation while allowing the software to evolve over time.

Implementation technologies, programming languages and internal algorithms are intentionally excluded.

---

# Part I — Architectural Overview

## 1.1 Purpose

The Builder is an engineering orchestration platform.

Its architecture is designed around coordinating engineering work rather than performing engineering work.

The Builder manages construction by maintaining engineering state, executing Jobs and preserving Workspace integrity.

---

## 1.2 Architectural Philosophy

The architecture is founded upon several principles:

* deterministic execution
* explicit state management
* modular responsibilities
* recoverable workflows
* observable operations
* long-term maintainability

Every architectural decision should reinforce these principles.

---

## 1.3 High-Level Structure

At a conceptual level, the Builder consists of the following layers.

```text
┌───────────────────────────────┐
│          User Interface        │
├───────────────────────────────┤
│         Application Layer      │
├───────────────────────────────┤
│         Job Execution          │
├───────────────────────────────┤
│      Domain Services           │
├───────────────────────────────┤
│      Workspace Model           │
├───────────────────────────────┤
│         Persistence            │
└───────────────────────────────┘
```

Each layer has clearly defined responsibilities.

Communication should occur through adjacent layers only.

---

# Part II — Core Concepts

## 2.1 Workspace

The Workspace represents the complete engineering environment.

It contains all information required to continue construction.

The Workspace is the primary unit of persistence.

---

## 2.2 Project

A Project represents the software system being constructed.

The Builder manages one Project within a Workspace.

Future versions may support multiple Projects through multiple Workspaces.

---

## 2.3 Construction State

Construction State records engineering progression.

Examples include:

* active sprint
* completed sprints
* current Job
* validation status
* checkpoint references

Construction State should always be recoverable.

---

## 2.4 History

History records significant engineering events.

History provides traceability rather than decision making.

It should be append-only.

---

## 2.5 Settings

Settings define Builder behaviour.

Settings shall never modify engineering specifications.

---

# Part III — Job Architecture

## 3.1 Job-Centred Design

The Job is the fundamental architectural unit.

Every Builder operation shall be represented as a Job.

There are no exceptions.

---

## 3.2 Job Responsibilities

A Job performs one engineering operation.

Examples include:

* opening a Workspace
* parsing documentation
* validating progress
* generating reports
* creating checkpoints

Jobs should remain narrowly focused.

---

## 3.3 Job Lifecycle

Every Job follows a common lifecycle.

```text
Queued
    │
    ▼
Running
    │
    ▼
Completed
```

Alternative outcomes include:

```text
Running
    │
 ┌──┴──┐
 ▼     ▼
Failed Cancelled
```

Job execution should always produce an observable outcome.

---

## 3.4 Job Composition

Complex engineering workflows should be constructed by sequencing multiple Jobs.

Large procedural workflows should be avoided.

---

# Part IV — Application Layer

## 4.1 Responsibility

The Application Layer coordinates Builder behaviour.

It is responsible for:

* workflow orchestration
* navigation
* state coordination
* lifecycle management

It is not responsible for engineering logic.

---

## 4.2 Coordination

The Application Layer coordinates communication between architectural subsystems.

It should avoid direct ownership of operational behaviour.

---

# Part V — Domain Services

## 5.1 Purpose

Services encapsulate reusable operational capabilities.

Services provide behaviour.

They do not own construction state.

---

## 5.2 Characteristics

Services should be:

* modular
* reusable
* deterministic
* independently testable

---

## 5.3 Examples

Typical services include:

* Workspace Service
* History Service
* Persistence Service
* Checkpoint Service
* Reporting Service
* Validation Service
* Project Discovery Service

These names describe architectural intent rather than implementation.

---

# Part VI — Persistence

## 6.1 Responsibility

Persistence preserves engineering state.

It enables interruption without loss of progress.

---

## 6.2 Architectural Goals

Persistence should provide:

* durability
* integrity
* consistency
* recoverability

---

## 6.3 Save Operations

Saving should preserve:

* Workspace
* Construction State
* History
* Checkpoints
* Settings

The Builder should never rely upon transient memory for engineering progress.

---

# Part VII — User Interface

## 7.1 Philosophy

The User Interface presents engineering information.

It should not contain engineering behaviour.

---

## 7.2 Primary Information

The interface should continuously communicate:

* active Workspace
* current Project
* active Sprint
* active Job
* construction progress
* validation status
* recent activity

---

## 7.3 Visual Hierarchy

Information should be organised according to engineering importance.

Critical operational state should always remain visible.

---

# Part VIII — Workspace Lifecycle

The conceptual Workspace lifecycle is illustrated below.

```text
Create Workspace
        │
        ▼
Open Workspace
        │
        ▼
Load Project
        │
        ▼
Resume Construction
        │
        ▼
Execute Jobs
        │
        ▼
Create Checkpoint
        │
        ▼
Update History
        │
        ▼
Save Workspace
        │
        ▼
Close Workspace
```

Every stage should preserve Workspace integrity.

---

# Part IX — Construction Flow

The Builder manages engineering progression through a structured construction flow.

```text
Engineering Documentation
            │
            ▼
      Construction State
            │
            ▼
      Job Selection
            │
            ▼
      Job Execution
            │
            ▼
         Validation
            │
            ▼
        Checkpoint
            │
            ▼
     Workspace Save
            │
            ▼
     Construction Continues
```

This flow defines the operational rhythm of the Builder.

Future capabilities should integrate into this flow rather than replace it.

---

# Part X — Future Extension Points

The architecture intentionally reserves extension points for future capabilities.

Potential areas include:

* Prompt Generation
* AI Providers
* Local LLM Integration
* Validation Engines
* Plugin Framework
* Dependency Graphs
* Project Dashboards
* Analytics
* Multi-Project Coordination

These extensions should interact with the existing architecture through clearly defined interfaces.

The core architecture should remain stable regardless of future expansion.

---

# Architectural Principles

The architecture of the Locomotion Builder is governed by the following principles:

* Work is represented as Jobs.
* Progress is represented by Construction State.
* Construction occurs within a Workspace.
* Recovery occurs through Checkpoints.
* History records engineering progression.
* Services provide reusable behaviour.
* The Application Layer coordinates workflows.
* The User Interface presents engineering state.
* Persistence protects engineering integrity.

Every architectural decision should reinforce these principles.

---

# Closing Statement

The conceptual architecture establishes a stable foundation upon which the Locomotion Builder can evolve over many years.

Its purpose is not to constrain implementation, but to preserve clarity, modularity and long-term maintainability.

Future versions may expand the Builder's capabilities substantially, yet the underlying architectural model should remain consistent: deterministic engineering orchestration centred upon Jobs, Workspaces and recoverable construction state.
