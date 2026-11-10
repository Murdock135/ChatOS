"""Checkout entrypoint for the conversation metadata utility."""

import sys
from pathlib import Path

repository = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repository / "src"))
from chatos.maintenance.conversation_metadata import main

if __name__ == "__main__":
    main()
