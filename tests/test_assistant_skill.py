"""Portable skill binding, real command execution and non-destructive preparation."""

import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from chatos.assistant_skill import export_skill
from chatos.onboarding import setup_status
from chatos.runtime import sync
from chatos.setup import initialize

ROOT = Path(__file__).resolve().parents[1]


class AssistantSkillTests(unittest.TestCase):
    def test_two_bound_skills_run_against_only_their_own_workspace(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            for name, choice in [("Ada", "Markdown"), ("Bryn", "org-mode")]:
                root = parent / (name + "'s chat library")
                home = parent / (name + " home")
                home.mkdir()
                initialize(root)
                self.assertTrue(setup_status(root)["assistant_skill_ready"])
                payload = (
                    (ROOT / "docs/examples/conversations.json")
                    .read_text()
                    .replace("Markdown", choice)
                )
                (root / "your_ais/chatgpt/imports/conversations.json").write_text(
                    payload
                )
                self.assertEqual(sync(root)["changes"]["chats"]["new"], 1)
                prepared = export_skill(root)
                self.assertEqual(prepared["status"], "unchanged")
                installed = parent / (name + " skills") / "chatos"
                export_skill(root, installed)
                connection = (installed / "references/connection.md").read_text()
                commands = (
                    connection.split("```bash\n", 1)[1]
                    .split("```", 1)[0]
                    .strip()
                    .splitlines()
                )
                environment = dict(
                    os.environ,
                    HOME=str(home),
                    PYTHONPATH="",
                    CHATOS_WORKSPACE=str(parent / "wrong workspace"),
                )
                reports = []
                for command in commands:
                    result = subprocess.run(
                        shlex.split(command),
                        cwd=parent,
                        env=environment,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(
                        result.returncode, 0, result.stderr + result.stdout
                    )
                    reports.append(json.loads(result.stdout))
                coverage, evidence, health = reports
                self.assertEqual(coverage["sources"]["chatgpt"]["records"], 1)
                self.assertEqual(coverage["sources"]["codex"]["records"], 0)
                self.assertTrue(
                    any(
                        item["role"] == "user" and choice in item["excerpt"]
                        for item in evidence["passages"]
                    )
                )
                self.assertTrue(
                    all(
                        str(root.resolve()) in item["path"]
                        for item in evidence["passages"]
                    )
                )
                self.assertTrue(health["ok"])
                self.assertFalse((home / ".agents").exists())
                self.assertFalse((home / ".codex").exists())
                self.assertFalse(prepared["host_activation_verified"])

    def test_customizations_moved_bindings_and_symlinks_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "workspace"
            initialize(root)
            source = Path(export_skill(root)["path"])
            moved = parent / "moved"
            shutil.copytree(root, moved)
            with self.assertRaises(ValueError):
                export_skill(moved)
            destination = parent / "custom" / "chatos"
            export_skill(moved, destination)
            self.assertIn(
                str(moved), (destination / "references/connection.md").read_text()
            )
            operations = source / "references/operations.md"
            operations.write_text("My custom operating instructions")
            with self.assertRaises(ValueError):
                export_skill(root)
            self.assertEqual(operations.read_text(), "My custom operating instructions")
            linked = parent / "linked"
            linked.symlink_to(source, target_is_directory=True)
            with self.assertRaises(ValueError):
                export_skill(root, linked)

    def test_interrupted_export_publishes_no_partial_discoverable_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "workspace"
            initialize(root)
            destination = parent / "host skills" / "chatos"
            with patch(
                "chatos.assistant_skill.Path.write_text",
                side_effect=OSError("Interrupted export"),
            ):
                with self.assertRaises(OSError):
                    export_skill(root, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(list(destination.parent.iterdir()), [])
