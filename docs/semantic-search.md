# Local hybrid search and model setup

Keyword search and Chief of Staff review work without model downloads. Local hybrid search uses a user-selected Sentence Transformers embedding model and scalar CrossEncoder reranker.

Install the optional runtime and start the app in it:

```bash
uv venv --python 3.13 .venv-semantic
uv pip install --python .venv-semantic/bin/python --require-hashes -r requirements-semantic.lock
PYTHONPATH=src .venv-semantic/bin/python -m chatos --root workspace serve --open
```

In **Setup & handoff → Local search models**, enter model IDs and save. The compact examples are `sentence-transformers/all-MiniLM-L6-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`; these are editable choices, not an allowlist. Models must work with the installed libraries, use safetensors weights and require no custom executable model code. Consult each model's documentation for its license, languages and prompts. Incompatible architectures report an error.

Download each saved model using its button. Downloads record the resolved commit and file hashes. Inference loads these files locally; ordinary search and sync do not download models. Advanced settings expose revisions, query/document prefixes, token limits, candidate count and an optional minimum relevance score. Scores are model-specific, not calibrated probabilities.

Use **Index next 64 passages** until none remain. Alternatively, `dense-build` processes remaining passages. Changing the embedding model, prompts or token limit requires rebuilding. Source changes invalidate affected passages. Partial indexing can miss semantic-only matches.

Select **Local hybrid + reranker** in Conversations. Keyword and meaning-based candidates are combined and reranked into the same list with matching messages. Source/project/archive filters constrain candidates. The current passage-return cap is 30 before conversation grouping; this is bounded retrieval, not exhaustive recall.

## Chief of Staff review

Enter a query and choose **Ask Chief of Staff**. Give the displayed request to an assistant with local file/terminal access. Its local packet preserves query, filters, inventory and keyword candidates. The assistant inspects original messages, broadens within that scope, excludes incidental mentions and writes ordered results with exact excerpts and relevance explanations. Select **Load Chief of Staff results** to show them in the same list. An empty array means none qualified.

The app validates current message IDs and exact excerpts. Citation integrity does not establish the assistant's relevance judgment. Changing query or filters requires a new request. Preparing a request does not launch an assistant or transmit chats. Assistants without local access need a separately authorized portable handoff.

## Map and limits

`dense-map` uses the selected embedding cache, requires six represented conversations and the optional clustering dependencies. HDBSCAN/UMAP remain experimental. Similarity does not establish truth, agreement or ownership. The older pinned-Qwen downloader remains a legacy utility; configurable search uses the model controls above.
