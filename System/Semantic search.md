# Local semantic search and conversation map

This is an optional local inference layer over the standard-library archive. Its implementation is under chatos/dense.py and chatos/dense_map.py. It is being evaluated; the ordinary archive and full-text search do not require it.

## Components

- **Embedding model:** Qwen/Qwen3-Embedding-0.6B, pinned to revision d67280f96c9df4c40d7c6986f4a51c54ac950c0f. The official model card describes a 1024-dimensional embedding model and an Apache-2.0 license. [Official model card](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B).
- **Retrieval:** cosine ranking of passage embeddings plus SQLite FTS5 BM25, combined with reciprocal-rank fusion. Results retain exact archived message IDs, offsets, excerpts and source links. Similarity does not establish factual support.
- **Conversation representation:** mean normalized user-passage vectors; assistant passages are a fallback only when no user passage is available. This can blur conversations with several topics.
- **Clustering:** HDBSCAN on original conversation cosine distances, minimum cluster size 4 and minimum samples 2. Noise stays unclustered. [HDBSCAN documentation](https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html).
- **2D view:** UMAP with 15 neighbors, minimum distance 0.15 and fixed seed 42. Clustering precedes the 2D projection because projected density/distance can be misleading. [UMAP clustering cautions](https://umap-learn.readthedocs.io/en/latest/clustering.html).

No claim is made that this small model or configuration is globally SOTA. It is a modern pretrained baseline, to be judged on this archive's retrieval and browsing needs.

## Local boundaries

The isolated environment is .venv, installed from requirements-semantic.lock with package hashes. The model is about 1.2 GB; its weight SHA-256 is verified against the pinned public file. Only approved model data/configuration files are downloaded. No Python model source, pickle weights, saved credentials or private chat uploads are required. Inference uses offline mode and disables remote model code.

Embedding ranking is capped at 512 tokens per passage. On this 16 GB M1 Pro, GPU inference was verified through an approved local process with a half-budget MPS memory cap. The restricted sandbox reported no GPU access, so it used CPU. No system permission, privacy setting, or security protection was changed. Core commands remain usable when optional inference is unavailable.

## Agent commands

    .venv/bin/python -B -m chatos dense-build --limit 64 --batch-size 4
    .venv/bin/python -B -m chatos retrieve "question" --hybrid
    .venv/bin/python -B -m chatos dense-map

Builds checkpoint each batch in the local database. Changed source passages receive new identities; stale vectors are excluded from retrieval. Results expose current embedding coverage. The map is a dated computation: ordinary sync preserves it and flags changed source records until it is rebuilt. The agent owns refresh, not the user.

Model setup, when needed, uses the reviewed download_embedding_model.py script and the pinned optional dependency lock. Do not auto-download a different model or enable an external inference service as a fallback.

## Evaluation

The first lexical baseline found the exact supporting user message in the top eight for 4 of 7 hand-authored questions (57%). This is a small, non-blind diagnostic, not a representative benchmark. Some derived notes can support an answer even when the exact original message is not retrieved.

The same questions, labels and evaluator are retained under System/Evaluations/ and chatos/evaluation.py. Preserve failed cases and report the neural/hybrid results before calling the new backend validated. Broader work must include paraphrases, hard negatives, conflicting decisions, source gaps and inspection of topic groups.

The initial LSA/PCA map retained about 24% of five-neighbor relationships on the 220-conversation corpus. Its limitations motivated this second representation. Projection retention compares a map with its own original representation; a higher number across two different representations does not establish that the representation itself is semantically better.

## First measured result

The optional hybrid backend also found 4 of 7 exact source messages in the top eight (57%, MRR 0.405), matching the lexical baseline. It has not demonstrated improvement on this set and is not promoted as the default. See [the diagnostic report](Evaluations/Latest.md). The pretrained map represented all 220 Codex conversations, left 52 unclustered, and retained about 38% of its own five-neighbor relationships. This does not establish correct topic labels or visual usability. New desktop captures and source changes require explicit reindexing; regular sync reports stale coverage rather than silently claiming freshness.
