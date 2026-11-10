# Reproducible experiments

Reusable experiment code lives in `src/chatos/experiments/`. This directory holds reviewable example protocols and explains where run artifacts belong.

Run through the normal app CLI:

```bash
chatos experiment /path/to/protocol.json --output /path/to/new-run
chatos experiment-check /path/to/new-run
```

From a checkout, use `./scripts/chatos` with the optional semantic environment activated, or `PYTHONPATH=src .venv-semantic/bin/python -m chatos`. No provider calls or model downloads are performed by these commands. Choose an already downloaded model and supply a frozen normalized dataset.

Copy a protocol from `configs/` into your study directory and edit its paths. Relative paths are resolved from the protocol file. A run refuses an existing output directory, snapshots inputs and source-code evidence, records local-model hashes and library versions, and saves vectors, memberships, coordinates, exclusions, timings, diagnostics and a report. Failed and interrupted runs retain their status and partial evidence. A manifest verifies the saved bundle without loading an embedding model.

See [experiment methods and limits](../docs/experiments.md) and [code layout](../docs/code-layout.md).

## Source and data boundaries

- `src/chatos/experiments/`: maintained, reusable implementation.
- `experiments/configs/`: fictional/template protocols without personal paths or data.
- `experiments/runs/`: optional local output location, ignored by Git.
- `workspace/`: private datasets, protocols, reviewed labels, generated visualizations and run artifacts. Active Python implementations do not belong here.
- `experiments/archive/`: ignored private historical source evidence relocated from the former workspace script folders. These exact scripts preserve the original studies' provenance; they are not supported entrypoints and may contain old personal paths or side effects. The relocation receipt remains with the private study records. Use the maintained CLI for new local runs.

Frozen snapshots and downloaded third-party environments in the workspace remain historical/runtime artifacts, not application source. Generated HTML maps contain their rendering code as an artifact; their maintained template lives in the package. Do not copy private datasets, old study scripts or credentials into public fixtures or packages.
