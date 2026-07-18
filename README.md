# Locomotion Builder

Deterministic engineering orchestration for recoverable software construction.

Current version: 1.1.0

Construction Manager lifecycle coordination is available, including Sprint
selection, Job execution, progress updates, checkpoints, history, reporting,
and lifecycle validation.

Prompt Generator workflows are available, including approved-context assembly,
deterministic Sprint prompt generation, human review, history, safe export,
templates, validation, and reporting.

Validation workflows are available for Workspace, construction, documentation,
project structure, prompt history, reporting, audit history, dashboards, and
complete Builder release checks.

Version 1.1.0 exposes the deterministic workflow through an installable
command-line application: project registration, Workspace association, Book
analysis, Sprint selection, reviewed prompt export, progress recording,
checkpointing, recovery, and validation.

## Run it

Locomotion Builder requires Python 3.10 or newer. Create a supported local
environment, then install the command-line application:

```sh
python3.12 -m venv .venv
.venv/bin/pip install -e .

locomotion-builder status
```

Use any Python 3.10+ executable in place of `python3.12`.

## First workflow

Register the project you want Builder to manage, then create and associate a
Workspace. The project must contain a Markdown engineering Book with Sprint
headings such as `## Sprint B04-S001 — Command Foundation`.

```sh
locomotion-builder project register /path/to/project
locomotion-builder workspace create "Demo" "Demo Project" demo-workspace.json
locomotion-builder workspace associate demo-workspace.json /path/to/project

locomotion-builder project inspect /path/to/project
locomotion-builder book list /path/to/project
locomotion-builder book analyse demo-workspace.json \
  "/path/to/project/docs/Book 03 Construction Schedule.md"

locomotion-builder construction next demo-workspace.json \
  "/path/to/project/docs/Book 03 Construction Schedule.md"
locomotion-builder prompt export demo-workspace.json \
  "/path/to/project/docs/Book 03 Construction Schedule.md" \
  next-sprint.md --reviewer "Your Name" --approve
```

After implementing the exported prompt outside Builder, explicitly confirm the
work, save a checkpoint, and run the final validation:

```sh
locomotion-builder construction complete demo-workspace.json \
  "/path/to/project/docs/Book 03 Construction Schedule.md" --confirm
locomotion-builder workspace checkpoint demo-workspace.json after-sprint-001
locomotion-builder validate demo-workspace.json \
  "/path/to/project/docs/Book 03 Construction Schedule.md"
```

Run `locomotion-builder --help` to see all available commands.
