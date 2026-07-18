"""Command-line application workflow for Locomotion Builder."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from builder.book import (
    discover_construction_sprints,
    determine_construction_progress,
    generate_parsing_report,
    load_book_document,
    parse_document_structure,
    recognise_conceptual_dependencies,
    recognise_engineering_books,
    report_parsing_issues,
    validate_parsed_construction_state,
)
from builder.construction import (
    create_construction_checkpoint,
    create_construction_controller,
    execute_scheduled_job,
    generate_construction_report,
    schedule_construction_job,
    select_construction_target,
    update_construction_progress,
)
from builder.jobs.job import Job
from builder.project import (
    discover_engineering_documents,
    discover_implementation_sources,
    generate_project_overview,
    register_project,
)
from builder.prompts import (
    assemble_prompt_context,
    export_prompt,
    generate_sprint_prompt,
    review_prompt,
)
from builder.shared.config import ApplicationSettings
from builder.shared.logger import Logger
from builder.ui.console import ConsoleUI
from builder.ui.progress import ProgressPanel
from builder.ui.status import StatusPanel
from builder.validation import validate_builder
from builder.workspace import (
    Workspace,
    associate_project,
    create_workspace,
    load_workspace,
    record_history,
    recover_workspace,
    save_workspace,
)


class Application:
    """Expose Builder Workspace workflows through a command-line interface."""

    def __init__(self) -> None:
        self.settings = ApplicationSettings()
        self.logger = Logger()
        self.ui = ConsoleUI()
        self.status = StatusPanel()
        self.progress = ProgressPanel()

    def launch(self) -> None:
        self.status.set_status("Launching")
        self.progress.update(10)
        self.logger.info("Launching application")

    def initialise(self) -> None:
        self.status.set_status("Initialising")
        self.progress.update(50)
        self.logger.info("Initialising application")

    def shutdown(self) -> None:
        self.status.set_status("Shutdown")
        self.progress.update(100)
        self.logger.info("Shutting down application")

    def run(self, arguments: Sequence[str] | None = None) -> int:
        """Run one requested Builder workflow and return an exit status."""
        parser = self._build_parser()
        namespace = parser.parse_args(arguments)
        if namespace.command is None:
            parser.print_help()
            return 0

        self.launch()
        try:
            self.initialise()
            if namespace.command == "status":
                self._render_status()
            elif namespace.command == "workspace":
                self._run_workspace_command(namespace)
            elif namespace.command == "project":
                self._run_project_command(namespace)
            elif namespace.command == "book":
                self._run_book_command(namespace)
            elif namespace.command == "construction":
                self._run_construction_command(namespace)
            elif namespace.command == "prompt":
                self._run_prompt_command(namespace)
            elif namespace.command == "validate":
                self._run_validation_command(namespace)
            else:
                parser.error(f"Unsupported command: {namespace.command}")
            return 0
        except (OSError, RuntimeError, ValueError) as error:
            print(f"Error: {error}", file=sys.stderr)
            return 1
        finally:
            self.shutdown()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="locomotion-builder",
            description="Deterministic engineering orchestration.",
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {self.settings.version}",
        )
        commands = parser.add_subparsers(dest="command", title="commands")
        commands.add_parser("status", help="show application status")

        workspace = commands.add_parser("workspace", help="manage Workspaces")
        workspace_commands = workspace.add_subparsers(
            dest="workspace_command",
            required=True,
            title="workspace commands",
        )
        create = workspace_commands.add_parser(
            "create",
            help="create and save a Workspace",
        )
        create.add_argument("name", help="Workspace name")
        create.add_argument("project_name", help="Project name")
        create.add_argument("path", type=Path, help="Destination JSON file")

        for command_name, help_text in (
            ("show", "load and show a Workspace"),
            ("recover", "recover an interrupted Workspace save"),
        ):
            command = workspace_commands.add_parser(command_name, help=help_text)
            command.add_argument("path", type=Path, help="Workspace JSON file")

        associate = workspace_commands.add_parser(
            "associate", help="associate a registered project with a Workspace"
        )
        associate.add_argument("workspace", type=Path, help="Workspace JSON file")
        associate.add_argument("project", type=Path, help="Registered project root")

        checkpoint = workspace_commands.add_parser(
            "checkpoint", help="create and save a construction checkpoint"
        )
        checkpoint.add_argument("workspace", type=Path, help="Workspace JSON file")
        checkpoint.add_argument("identifier", help="Unique checkpoint identifier")

        history = workspace_commands.add_parser(
            "history", help="show recorded Workspace history"
        )
        history.add_argument("workspace", type=Path, help="Workspace JSON file")

        project = commands.add_parser("project", help="register and inspect projects")
        project_commands = project.add_subparsers(
            dest="project_command", required=True, title="project commands"
        )
        for command_name, help_text in (
            ("register", "register an existing project directory"),
            ("inspect", "inspect a registered project"),
        ):
            command = project_commands.add_parser(command_name, help=help_text)
            command.add_argument("path", type=Path, help="Project root")

        book = commands.add_parser("book", help="analyse engineering documentation")
        book_commands = book.add_subparsers(
            dest="book_command", required=True, title="book commands"
        )
        books = book_commands.add_parser("list", help="list recognised engineering Books")
        books.add_argument("project", type=Path, help="Registered project root")
        analyse = book_commands.add_parser("analyse", help="analyse a construction Book")
        analyse.add_argument("workspace", type=Path, help="Workspace JSON file")
        analyse.add_argument("book", type=Path, help="Recognised engineering Book")

        construction = commands.add_parser(
            "construction", help="manage construction progression"
        )
        construction_commands = construction.add_subparsers(
            dest="construction_command", required=True, title="construction commands"
        )
        for command_name, help_text in (
            ("status", "show construction status"),
            ("next", "select the next eligible Sprint"),
        ):
            command = construction_commands.add_parser(command_name, help=help_text)
            command.add_argument("workspace", type=Path, help="Workspace JSON file")
            command.add_argument("book", type=Path, help="Recognised engineering Book")
        complete = construction_commands.add_parser(
            "complete", help="record human-confirmed completion of the active Sprint"
        )
        complete.add_argument("workspace", type=Path, help="Workspace JSON file")
        complete.add_argument("book", type=Path, help="Recognised engineering Book")
        complete.add_argument(
            "--confirm", action="store_true", help="confirm that implementation was completed outside Builder"
        )

        prompt = commands.add_parser("prompt", help="generate and export Sprint prompts")
        prompt_commands = prompt.add_subparsers(
            dest="prompt_command", required=True, title="prompt commands"
        )
        generate = prompt_commands.add_parser("generate", help="generate the next Sprint prompt")
        generate.add_argument("workspace", type=Path, help="Workspace JSON file")
        generate.add_argument("book", type=Path, help="Recognised engineering Book")
        export = prompt_commands.add_parser(
            "export", help="review and export the next Sprint prompt"
        )
        export.add_argument("workspace", type=Path, help="Workspace JSON file")
        export.add_argument("book", type=Path, help="Recognised engineering Book")
        export.add_argument("path", type=Path, help="Destination prompt file")
        export.add_argument("--reviewer", required=True, help="Human reviewer name")
        export.add_argument("--approve", action="store_true", help="approve the prompt for export")
        export.add_argument(
            "--observation", action="append", default=[], help="Optional review observation; repeat as needed"
        )
        prompt_history = prompt_commands.add_parser(
            "history", help="show exported prompt history"
        )
        prompt_history.add_argument("workspace", type=Path, help="Workspace JSON file")

        validate = commands.add_parser("validate", help="validate a complete workflow")
        validate.add_argument("workspace", type=Path, help="Workspace JSON file")
        validate.add_argument("book", type=Path, help="Recognised engineering Book")
        return parser

    def _run_workspace_command(self, namespace: argparse.Namespace) -> None:
        if namespace.workspace_command == "create":
            workspace = create_workspace(namespace.name, namespace.project_name)
            save_workspace(workspace, namespace.path)
            print(f"Workspace saved: {namespace.path}")
            self._render_workspace(workspace)
            return
        if namespace.workspace_command == "show":
            self._render_workspace(load_workspace(namespace.path))
            return
        if namespace.workspace_command == "recover":
            workspace = recover_workspace(namespace.path)
            print(f"Workspace recovered: {namespace.path}")
            self._render_workspace(workspace)
            return
        if namespace.workspace_command == "associate":
            workspace = load_workspace(namespace.workspace)
            metadata = associate_project(workspace, namespace.project)
            record_history(workspace.history, f"Associated project: {metadata.root}")
            save_workspace(workspace, namespace.workspace)
            print(f"Project associated: {metadata.root}")
            self._render_workspace(workspace)
            return
        if namespace.workspace_command == "checkpoint":
            workspace = load_workspace(namespace.workspace)
            checkpoint = create_construction_checkpoint(workspace, namespace.identifier)
            record_history(workspace.history, f"Created checkpoint: {checkpoint.identifier}")
            save_workspace(workspace, namespace.workspace)
            print(f"Checkpoint saved: {checkpoint.identifier}")
            return
        if namespace.workspace_command == "history":
            workspace = load_workspace(namespace.workspace)
            if not workspace.history.entries:
                print("Workspace history: none")
                return
            for entry in workspace.history.entries:
                print(f"{entry.timestamp.isoformat()} {entry.description}")
            return
        raise ValueError(f"Unsupported Workspace command: {namespace.workspace_command}")

    def _run_project_command(self, namespace: argparse.Namespace) -> None:
        if namespace.project_command == "register":
            registration = register_project(namespace.path)
            print(f"Project registered: {registration.root}")
            return
        if namespace.project_command == "inspect":
            overview = generate_project_overview(namespace.path)
            documents = discover_engineering_documents(namespace.path)
            sources = discover_implementation_sources(namespace.path)
            print(overview.render())
            print(f"Engineering documents: {len(documents)}")
            print(f"Implementation sources: {len(sources)}")
            return
        raise ValueError(f"Unsupported project command: {namespace.project_command}")

    def _run_book_command(self, namespace: argparse.Namespace) -> None:
        if namespace.book_command == "list":
            books = recognise_engineering_books(namespace.project)
            if not books:
                print("Engineering Books: none")
                return
            for book in books:
                print(f"{book.identifier}: {book.path}")
            return
        if namespace.book_command == "analyse":
            workspace = load_workspace(namespace.workspace)
            parser_validation = self._parse_book(workspace, namespace.book)
            print(parser_validation.report.render())
            print(parser_validation.status)
            return
        raise ValueError(f"Unsupported book command: {namespace.book_command}")

    def _run_construction_command(self, namespace: argparse.Namespace) -> None:
        workspace = load_workspace(namespace.workspace)
        controller = self._create_controller(workspace, namespace.book)
        if namespace.construction_command == "status":
            print(generate_construction_report(controller).render())
            return
        target = select_construction_target(controller)
        if namespace.construction_command == "next":
            record_history(workspace.history, f"Selected Sprint: {target.sprint.identifier}")
            save_workspace(workspace, namespace.workspace)
            print(f"Next Sprint: {target.sprint.identifier} — {target.sprint.name}")
            return
        if namespace.construction_command == "complete":
            if not namespace.confirm:
                raise ValueError("Use --confirm after completing implementation outside Builder")
            execution = execute_scheduled_job(
                schedule_construction_job(target, _CompletionConfirmationJob())
            )
            progress = update_construction_progress(execution)
            record_history(workspace.history, f"Completed Sprint: {target.sprint.identifier}")
            save_workspace(workspace, namespace.workspace)
            print(f"Sprint completed: {target.sprint.identifier}")
            print(f"Progress: {progress.completion_percent:.1f}%")
            return
        raise ValueError(f"Unsupported construction command: {namespace.construction_command}")

    def _run_prompt_command(self, namespace: argparse.Namespace) -> None:
        if namespace.prompt_command == "history":
            workspace = load_workspace(namespace.workspace)
            entries = tuple(
                entry for entry in workspace.history.entries if "prompt:" in entry.description.lower()
            )
            if not entries:
                print("Prompt history: none")
                return
            for entry in entries:
                print(f"{entry.timestamp.isoformat()} {entry.description}")
            return
        workspace = load_workspace(namespace.workspace)
        controller = self._create_controller(workspace, namespace.book)
        target = select_construction_target(controller)
        prompt = generate_sprint_prompt(assemble_prompt_context(target))
        if namespace.prompt_command == "generate":
            record_history(workspace.history, f"Generated prompt: {prompt.sprint_identifier}")
            save_workspace(workspace, namespace.workspace)
            print(prompt.content)
            return
        if namespace.prompt_command == "export":
            review = review_prompt(
                prompt,
                namespace.reviewer,
                namespace.approve,
                tuple(namespace.observation),
            )
            if not review.approved:
                raise ValueError("Prompt export requires --approve after human review")
            export_prompt(prompt, namespace.path)
            record_history(
                workspace.history,
                f"Exported approved prompt: {prompt.sprint_identifier} ({review.reviewer})",
            )
            save_workspace(workspace, namespace.workspace)
            print(f"Prompt exported: {namespace.path}")
            return
        raise ValueError(f"Unsupported prompt command: {namespace.prompt_command}")

    def _run_validation_command(self, namespace: argparse.Namespace) -> None:
        workspace = load_workspace(namespace.workspace)
        controller = self._create_controller(workspace, namespace.book)
        from builder.prompts import PromptHistory

        result = validate_builder(controller, PromptHistory())
        save_workspace(workspace, namespace.workspace)
        print(result.report.render())
        if not result.is_valid:
            raise ValueError(result.status)

    def _create_controller(self, workspace: Workspace, book_path: Path):
        return create_construction_controller(workspace, self._parse_book(workspace, book_path))

    def _parse_book(self, workspace: Workspace, book_path: Path):
        if workspace.project_root is None:
            raise ValueError("Workspace must be associated with a project first")
        resolved_path = book_path.resolve()
        books = recognise_engineering_books(workspace.project_root)
        book = next((item for item in books if item.path == resolved_path), None)
        if book is None:
            raise ValueError(f"Engineering Book is not recognised: {resolved_path}")
        structure = parse_document_structure(load_book_document(book))
        sprints = discover_construction_sprints(structure)
        report = generate_parsing_report(
            structure,
            sprints,
            recognise_conceptual_dependencies(sprints),
            determine_construction_progress(sprints, workspace.completed_sprints),
        )
        return validate_parsed_construction_state(report, report_parsing_issues())

    def _render_status(self) -> None:
        self.ui.render()
        print(f"Application: {self.settings.application_name}")
        print(f"Version: {self.settings.version}")
        self.status.render()
        self.progress.render()

    def _render_workspace(self, workspace: Workspace) -> None:
        active_sprint = workspace.active_sprint or "none"
        project_root = str(workspace.project_root) if workspace.project_root else "none"
        print(f"Workspace: {workspace.name}")
        print(f"Project: {workspace.project_name}")
        print(f"Project root: {project_root}")
        print(f"Active sprint: {active_sprint}")
        print(f"Completed sprints: {len(workspace.completed_sprints)}")
        print(f"Checkpoints: {len(workspace.checkpoints)}")


class _CompletionConfirmationJob(Job):
    """Record that an engineer confirmed external implementation completion."""

    def __init__(self) -> None:
        super().__init__("Confirm Sprint Completion")

    def run(self) -> None:
        return None
