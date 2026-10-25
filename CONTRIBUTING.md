# Contributing

Python application code and compiled browser assets live in `src/chatos/`. The frontend source is in `frontend/`, using Astro components and Tailwind CSS. Tests live in `tests/`; documentation, adopted software decisions, and proposals live in `docs/`. `workspace/` is private user data and is excluded from Git and the Python package.

Build the frontend after editing its components, styles or `frontend/public/app.js`:

```bash
cd frontend
npm ci
npm run check
npm run build
```

Commit the compiled `src/chatos/static/` output with its source changes. The Python server serves that output directly; end users do not need Node. Do not edit generated browser files directly. Component-specific styles can use Tailwind utilities; shared compatibility rules remain in `frontend/src/styles/` while they are consolidated. Runtime JavaScript remains framework-independent and uses the existing authenticated Python API.

From this checkout, `./scripts/chatos --help` works with Python 3.9+ without installing dependencies. For development with uv:

```bash
uv venv
uv pip install -e .
PYTHONPATH=src uv run --no-sync python -m unittest discover -s tests -v
```

For browser startup logic, use Node.js 18+ with its built-in test runner (no npm dependencies):

```bash
node --test tests/browser_startup.test.cjs
```

The test suite uses temporary workspaces; browser API tests bind a loopback port. Do not point tests at a personal archive. Core functionality uses the standard library; optional embedding packages are independent of the core installation.

Before submitting code, run the relevant tests, Ruff lint and format checks, and scoped BasedPyright checks. No universal tool installation is implied by this checkout. Preserve source evidence and separate generated files from authored changes. Never include private workspace contents, real exports, credentials, or runtime databases in contributions.
