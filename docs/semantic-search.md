# Local hybrid search and model setup

Keyword search and Chief of Staff review work without model downloads. Local hybrid search uses a user-selected Sentence Transformers embedding model and scalar CrossEncoder reranker.

Install the optional runtime and start the app in it:

```bash
uv venv --python 3.13 .venv-semantic
uv pip install --python .venv-semantic/bin/python --require-hashes -r requirements-semantic.lock
PYTHONPATH=src .venv-semantic/bin/python -m chatos --root workspace serve --open
```

In **Settings → Search models → Local search models**, enter model IDs and save. The compact examples are `sentence-transformers/all-MiniLM-L6-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`; these are editable choices, not an allowlist. Models must work with the installed libraries, use safetensors weights and require no custom executable model code. Consult each model's documentation for its license, languages and prompts. Incompatible architectures report an error.

Download each saved model using its button. Downloads record the resolved commit and file hashes. Inference loads these files locally; ordinary search and sync do not download models. Advanced settings expose revisions, query/document prefixes, token limits, candidate count and an optional minimum relevance score. Scores are model-specific, not calibrated probabilities.

Use **Index next 64 passages** until none remain. Alternatively, `dense-build` processes remaining passages. Changing the embedding model, prompts or token limit requires rebuilding. Source changes invalidate affected passages. Partial indexing can miss semantic-only matches.

Select **Local hybrid + reranker** in Conversations. Keyword and meaning-based candidates are combined and reranked into the same list with matching messages. Source/project/archive filters constrain candidates. The current passage-return cap is 30 before conversation grouping; this is bounded retrieval, not exhaustive recall.

## Chief of Staff review

Enter a query and choose **Ask Chief of Staff**. Give the displayed request to an assistant with local file/terminal access. Its local packet preserves query, filters, inventory and keyword candidates. The assistant inspects original messages, broadens within that scope, excludes incidental mentions and writes ordered results with exact excerpts and relevance explanations. Select **Load Chief of Staff results** to show them in the same list. An empty array means none qualified.

The app validates current message IDs and exact excerpts. Citation integrity does not establish the assistant's relevance judgment. Changing query or filters requires a new request. Preparing a request does not launch an assistant or transmit chats. Assistants without local access need a separately authorized portable handoff.

## Explore the conversation map

Open **Conversation map** and enter a concept, then choose **Explore**. **Text in conversations** searches captured messages and local notes as well as titles. **Local semantic search** uses the configured embedding model and reranker; it needs downloaded models and a current passage index. Its candidates remain bounded to 30 passages before conversation grouping, so the visible results are not exhaustive recall. A failed semantic query shows an error instead of presenting the previous query's results.

**Filters & sort** contains source, project, inclusive date bounds, and relevance/newest/title order. Click a topic in the color-matched legend to filter both the map and the list; **All topics** resets that topic filter. Additional topics appear behind **more topics**. Topic labels can be hidden, unclustered conversations can be omitted, and the display control changes point size (Compact/Balanced/Comfortable). These visual controls do not change clustering parameters. Drag to pan, scroll or use the zoom buttons, choose **Fit map**, or expand the map; Escape collapses it.

Select a point to select and highlight its conversation in the results, or use a result checkbox. Click a result's title to open its original captured messages. Filtering removes selections that are no longer visible. **Select visible** and **Clear selection** make the scope explicit. **Export results JSON** downloads selected results, or all visible results when nothing is selected, including source-qualified identities, exact preview evidence where available, filters, method and freshness. It is metadata and excerpts, not full transcripts. **Download map PNG** exports the current visual view and visible labels separately.

### Ask your existing assistant

Select 1–200 conversations and choose **Explore with my assistant**. The app saves a validated JSON snapshot under the workspace's state directory (`map-explorations/`), then shows a request to copy into your existing assistant. The snapshot contains query/filters, map generation/method/freshness, selected source-qualified records, record fingerprints, topic labels, source paths, exact original-message preview citations, and capture limits. The server checks current map membership and archive state; a rebuilt map invalidates a handoff from an old generation.

An assistant with local file access can read that selection and inspect the original records. **Download selection JSON** supports deliberately supplying the snapshot to an assistant without local access; full selected transcripts can be exported separately through Setup & handoff. Nothing is transmitted and no assistant is launched automatically. The handoff requests source-grounded explanations, keeps captured text separate from instructions, and does not grant edit authority. Structured assistant-driven changes to browser view state are not implemented.

### Build and understand the semantic map

After downloading the embedding model in **Setup & handoff**, choose **Rebuild semantic map**, or run `dense-map`. The operation respects the workspace maintenance lock. It requires the optional clustering runtime and at least six conversations with usable topic text. The map can be built independently of the passage index; semantic *querying* still needs `dense-build`. Ordinary sync preserves a saved pretrained map and reports when captured records have changed; it does not automatically rebuild it or download models. A fresh workspace can use sync's provisional local LSA map without model downloads.

The current pretrained representation encodes a title plus up to twelve evenly spaced user-text samples per conversation, with a bounded assistant fallback when no user text exists. Recognized imported context wrappers, attachment-only auto-titles and filesystem paths are excluded from derived topic input; original messages, retrieval citations and source files are unchanged. Each sample is capped at 900 characters and the model's configured token limit. Normalized sample embeddings are averaged per conversation. HDBSCAN clusters original cosine distances; UMAP only determines the 2D layout. Corpus-weighted shared source phrases label groups, rather than treating frequent words or titles as verified summaries.

Sampling and averaging can miss or blur multiple topics. English phrase labels, outliers, ambiguous groups and 2D distortions still require review. The map displays neighbor retention as a projection diagnostic, not semantic accuracy. Similarity does not establish truth, agreement, ownership or accepted decisions. Legacy saved maps remain readable. See [the exploration design decision](adr/0006-semantic-map-exploration.md) and [validation evidence](verification/semantic-map-exploration.md).
