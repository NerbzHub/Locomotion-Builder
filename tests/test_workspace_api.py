"""Regression coverage for the public Workspace API."""

from __future__ import annotations

import unittest

from builder.workspace import Workspace, create_workspace


class WorkspaceApiTests(unittest.TestCase):
    def test_create_workspace_is_public(self) -> None:
        workspace = create_workspace("Demo", "Project")

        self.assertIsInstance(workspace, Workspace)
        self.assertEqual(workspace.name, "Demo")
        self.assertEqual(workspace.project_name, "Project")
