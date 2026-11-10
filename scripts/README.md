# Checkout commands

These files are thin entrypoints; reusable implementations belong in `src/chatos/`.

| Command | Implementation |
| --- | --- |
| `chatos` | `chatos.cli.main` |
| `start`, `status`, `stop`, `app_control.py` | `chatos.maintenance.app_control` |
| `archive_design.py` | `chatos.maintenance.design_archive` |
| `build_topic_map.py` | `chatos.experiments.topic_map` |
| `conversation_metadata.py` | `chatos.maintenance.conversation_metadata` |
| `system_inventory.py`, `system_log.py`, `snapshot_codex_state.py` | corresponding `chatos.maintenance` modules |
| `download_embedding_model.py` | `chatos.maintenance.download_embedding_model` |
| `run_sync.py` | `chatos.automation.runtime` |

Run reproducible studies with `chatos experiment PROTOCOL --output NEW_DIRECTORY`. Protocols and methods: [Experiments](../docs/experiments.md). Package boundaries: [Code layout](../docs/code-layout.md).
