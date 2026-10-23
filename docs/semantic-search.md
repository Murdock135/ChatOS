# Optional semantic search and clustering

The ordinary archive, keyword search, cited lexical retrieval, and browser app work without a downloaded model. The pretrained semantic backend is an optional local inference layer.

| Feature | Additional requirements |
| --- | --- |
| `search --semantic` | A term-co-occurrence representation built from your archive; no pretrained model download |
| `retrieve --hybrid` | Pinned Qwen embedding model, optional Python dependencies, and current passage embeddings |
| Pretrained conversation map | Current embeddings for at least six conversations, scikit-learn HDBSCAN, and UMAP |

The pretrained backend uses **Qwen/Qwen3-Embedding-0.6B**, pinned to revision `d67280f96c9df4c40d7c6986f4a51c54ac950c0f`. It turns passages into numeric vectors for similarity search. HDBSCAN groups conversation vectors; UMAP places them in the 2D map. These steps do not require a separate chat-generation model or an inference API key.

## Install the optional runtime and model

Run from the repository root, with an initialized workspace and `uv` available. These commands use a separate environment. The existing installation was exercised with Python 3.13 on macOS; other environments need validation.

```bash
uv venv --python 3.13 .venv-semantic
uv pip install --python .venv-semantic/bin/python --require-hashes -r requirements-semantic.lock
.venv-semantic/bin/python scripts/download_embedding_model.py --root workspace
```

The last command downloads public model data into `workspace/app_data/cache/models/qwen3-embedding-0.6b/`. It uses the pinned revision, verifies the weight hash and supported module configuration, and writes the manifest expected by the embedding loader. It does not read your conversations or use saved Hugging Face tokens. `--help` only displays usage.

This requires downloading dependencies and model weights. The normal `init`, `sync`, and app-start commands do not perform these installations. After model setup, inference uses local files and disables remote model code.

## Build embeddings, retrieve, and cluster

First import your conversations with ordinary sync. Then embed a bounded batch:

```bash
PYTHONPATH=src .venv-semantic/bin/python -m chatos --root workspace dense-build --limit 64 --batch-size 4
```

Inspect the reported `remaining` count. Repeat this command to process further batches; existing current vectors are reused. A partial build covers only the passages processed so far. To process all remaining passages in one invocation, omit `--limit`.

Once embeddings are available:

```bash
PYTHONPATH=src .venv-semantic/bin/python -m chatos --root workspace retrieve "related discussions" --hybrid
PYTHONPATH=src .venv-semantic/bin/python -m chatos --root workspace dense-map
```

The map requires at least six conversations represented by current embeddings; the one-chat fictional demo cannot satisfy that requirement. Open the app's **Conversation map** after building it. Ordinary sync preserves a dated pretrained map and reports when source changes make it stale; it does not automatically rerun model inference. Refresh affected embeddings and rebuild the map when needed.

## Boundaries and evidence

Embeddings measure similarity, not truth or agreement. A conversation can contain several topics, clusters can be wrong, and some conversations remain unclustered. The first seven-question diagnostic found the exact supporting user message in the top eight for 4/7 questions with both lexical and hybrid retrieval; the pretrained backend did not demonstrate an improvement on that small diagnostic.

See [features and limits](features.md), [source implementation](../src/chatos/dense.py), [clustering and map implementation](../src/chatos/dense_map.py), and [model setup helper](../src/chatos/maintenance/download_embedding_model.py). This guide documents existing optional functionality; it does not claim broad retrieval quality or complete public onboarding.
