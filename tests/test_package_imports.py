"""Package entrypoints must work in a fresh process and any import order."""

import os
import subprocess
import sys
import unittest
from pathlib import Path


class PackageImportTests(unittest.TestCase):
    def test_resource_services_and_initialization_import_independently(self):
        source = Path(__file__).resolve().parents[1] / "src"
        environment = {**os.environ, "PYTHONPATH": str(source)}
        for module in (
            "chatos.assistant.assistant_skill",
            "chatos.setup.onboarding",
            "chatos.setup.initialization",
            "chatos.web.server",
        ):
            with self.subTest(module=module):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        "import importlib; importlib.import_module("
                        + repr(module)
                        + ")",
                    ],
                    env=environment,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
