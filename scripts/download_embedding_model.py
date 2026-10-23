"""Run the optional model setup from a source checkout."""

from pathlib import Path
import sys

repository = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repository / "src"))
from chatos.maintenance.download_embedding_model import main  # noqa: E402

if __name__ == "__main__":
    main()
