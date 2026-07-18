"""Regression coverage for the public command-line workflows."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from builder.application.app import Application


class ApplicationCliTests(unittest.TestCase):
    def test_no_command_shows_help_without_running_lifecycle(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_status = Application().run(())

        self.assertEqual(exit_status, 0)
        self.assertIn("workspace", output.getvalue())
        self.assertNotIn("Shutting down application", output.getvalue())

    def test_workspace_create_and_show_are_accessible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace_path = Path(directory) / "workspace.json"
            output = io.StringIO()
            with redirect_stdout(output):
                create_status = Application().run(
                    ("workspace", "create", "Demo", "Project", str(workspace_path))
                )
                show_status = Application().run(
                    ("workspace", "show", str(workspace_path))
                )

        self.assertEqual(create_status, 0)
        self.assertEqual(show_status, 0)
        self.assertIn("Workspace saved:", output.getvalue())
        self.assertIn("Workspace: Demo", output.getvalue())

    def test_workspace_recover_is_accessible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace_path = Path(directory) / "workspace.json"
            output = io.StringIO()
            with redirect_stdout(output):
                Application().run(
                    ("workspace", "create", "Demo", "Project", str(workspace_path))
                )
                recover_status = Application().run(
                    ("workspace", "recover", str(workspace_path))
                )

        self.assertEqual(recover_status, 0)
        self.assertIn("Workspace recovered:", output.getvalue())

    def test_v1_1_end_to_end_workflow_is_accessible(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project_path = root / "project"
            documentation_path = project_path / "docs" / "Book 03 Plan.md"
            workspace_path = root / "workspace.json"
            prompt_path = root / "next-sprint.md"
            documentation_path.parent.mkdir(parents=True)
            (project_path / "main.py").write_text("", encoding="utf-8")
            documentation_path.write_text(
                "# Plan\n\n"
                "## Sprint B04-S001 — Command Foundation\n"
                "Establish the command foundation.\n\n"
                "## Sprint B04-S002 — Workspace Operations\n"
                "Expose workspace operations.\n",
                encoding="utf-8",
            )
            commands = (
                ("project", "register", str(project_path)),
                ("workspace", "create", "Demo", "Project", str(workspace_path)),
                ("workspace", "associate", str(workspace_path), str(project_path)),
                ("book", "analyse", str(workspace_path), str(documentation_path)),
                ("construction", "next", str(workspace_path), str(documentation_path)),
                (
                    "prompt", "export", str(workspace_path), str(documentation_path),
                    str(prompt_path), "--reviewer", "Engineer", "--approve",
                ),
                (
                    "construction", "complete", str(workspace_path),
                    str(documentation_path), "--confirm",
                ),
                ("validate", str(workspace_path), str(documentation_path)),
            )
            output = io.StringIO()
            with redirect_stdout(output):
                exit_statuses = [Application().run(command) for command in commands]
            prompt_was_exported = prompt_path.exists()

        self.assertEqual(exit_statuses, [0] * len(commands))
        self.assertTrue(prompt_was_exported)
        self.assertIn("Validation: passed", output.getvalue())
