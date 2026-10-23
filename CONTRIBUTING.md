# Contributing

Application code and bundled browser assets live in `src/chatos/`. Tests live in `tests/`; documentation, adopted software decisions, and proposals live in `docs/`. `workspace/` is private user data and is excluded from Git and the Python package.

From this checkout, `./scripts/chatos --help` works with Python 3.9+ without installing dependencies. For development with uv:

```bash
uv venv
uv pip install -e .
PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests -v
```

The test suite uses temporary workspaces; browser API tests bind a loopback port. Do not point tests at a personal archive. Core functionality uses the standard library; optional embedding packages are independent of the core installation.

Before submitting code, run the relevant tests, Ruff lint and format checks, and scoped BasedPyright checks. No universal tool installation is implied by this checkout. Preserve source evidence and separate generated files from authored changes. Never include private workspace contents, real exports, credentials, or runtime databases in contributions.
