"""Optional offline embeddings, reranking, and hybrid passage retrieval."""

import json
import time
from pathlib import Path

from .core import digest, now
from .retrieval import refresh as refresh_passages
from .retrieval import retrieve as lexical_retrieve
from .search_models import fingerprint, model, settings

VERSION = "dense-passages-v1-max512"
# Compatibility labels for older map/status readers. Active searches report the
# configured model and its manifest fingerprint instead.
MODEL = "Qwen/Qwen3-Embedding-0.6B"
REVISION = "d67280f96c9df4c40d7c6986f4a51c54ac950c0f"


def passages(store):
    store.db.execute("""CREATE TABLE IF NOT EXISTS dense_vectors (
                       identity TEXT PRIMARY KEY,revision TEXT NOT NULL,vector BLOB NOT NULL)""")
    refresh_passages(store)
    result = []
    for row in store.db.execute("SELECT title,body,metadata FROM passage_index"):
        metadata = json.loads(row["metadata"])
        key = digest(
            [
                VERSION,
                metadata["key"],
                metadata.get("message_id"),
                metadata.get("message_index"),
                metadata["start"],
                metadata["end"],
                row["title"],
                row["body"],
            ]
        )
        result.append(
            {
                "identity": key,
                "text": row["title"] + "\n" + row["body"],
                "excerpt": row["body"],
                **metadata,
            }
        )
    return result


def build(store, limit=None, batch_size=4):
    import numpy as np

    items = passages(store)
    config = settings(Path(store.root))
    revision = fingerprint(Path(store.root), config["embedding"])
    existing = {
        r[0]
        for r in store.db.execute(
            "SELECT identity FROM dense_vectors WHERE revision=?", (revision,)
        )
    }
    todo = [item for item in items if item["identity"] not in existing]
    selected = todo[:limit] if limit is not None else todo
    started = time.monotonic()
    if selected:
        encoder = model(Path(store.root), "embedding", config)
        for start in range(0, len(selected), batch_size):
            batch = selected[start : start + batch_size]
            vectors = encoder.encode(
                [
                    config["embedding"]["document_prompt"] + item["text"]
                    for item in batch
                ],
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            with store.db:
                for item, vector in zip(batch, vectors):
                    vector = np.asarray(vector, dtype="<f4")
                    if vector.ndim != 1 or not np.isfinite(vector).all():
                        raise ValueError("Invalid embedding vector")
                    store.db.execute(
                        "INSERT OR REPLACE INTO dense_vectors VALUES(?,?,?)",
                        (item["identity"], revision, vector.tobytes()),
                    )
            if start % 128 == 0:
                print(
                    json.dumps(
                        {
                            "embedded": min(start + len(batch), len(selected)),
                            "requested": len(selected),
                        }
                    ),
                    flush=True,
                )
    from .core import write_json

    result = {
        "checked_at": now(),
        "model": config["embedding"]["model_id"],
        "revision": revision,
        "device": "local",
        "added": len(selected),
        "current_passages": len(items),
        "current_vectors": len(items) - len(todo) + len(selected),
        "remaining": len(todo) - len(selected),
        "seconds": round(time.monotonic() - started, 2),
        "limits": "Local inference; 512-token embedding cap per passage. Dense scores are similarity, not truth or decision status.",
    }
    write_json(store.state / "dense-status.json", result)
    return result


def retrieve(store, query, project=None, limit=8, allowed=None):
    import numpy as np

    if not 1 <= limit <= 30:
        raise ValueError("Retrieval limit must be between 1 and 30")
    if project and project not in {p["id"] for p in store.registry()}:
        raise ValueError("Unknown project filter")
    items = passages(store)
    config = settings(Path(store.root))
    revision = fingerprint(Path(store.root), config["embedding"])
    cached = {
        r[0]: np.frombuffer(r[1], dtype="<f4")
        for r in store.db.execute(
            "SELECT identity,vector FROM dense_vectors WHERE revision=?", (revision,)
        )
    }
    active = [item for item in items if item["identity"] in cached]
    if not active:
        raise ValueError("No current passage embeddings; run dense-build first")
    eligible = [
        item
        for item in active
        if (not project or project in item["projects"])
        and (allowed is None or (item["source"], item["id"]) in allowed)
    ]
    encoder = model(Path(store.root), "embedding", config)
    query_vector = encoder.encode(
        [config["embedding"]["query_prompt"] + query],
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )[0]
    candidate_limit = config["candidate_limit"]
    dense = sorted(
        (
            (float(np.dot(query_vector, cached[item["identity"]])), item)
            for item in eligible
        ),
        key=lambda pair: pair[0],
        reverse=True,
    )[:candidate_limit]
    lexical = lexical_retrieve(store, query, project, min(30, max(limit, 20)))
    by_locator = {
        (item["key"], item.get("message_index"), item["start"]): item for item in items
    }
    scores = {}
    selected = {}
    for rank, (similarity, item) in enumerate(dense, 1):
        key = item["identity"]
        scores[key] = 1 / (60 + rank)
        selected[key] = {**item, "dense_similarity": similarity}
    for rank, hit in enumerate(lexical["passages"], 1):
        item = by_locator[(hit["key"], hit.get("message_index"), hit["start"])]
        if allowed is not None and (item["source"], item["id"]) not in allowed:
            continue
        key = item["identity"]
        scores[key] = scores.get(key, 0) + 1 / (60 + rank)
        selected.setdefault(key, item)
    reranker = model(Path(store.root), "reranker", config)
    candidates = sorted(selected, key=lambda key: scores[key], reverse=True)[
        :candidate_limit
    ]
    rerank_pairs = [
        (query, selected[key]["title"] + "\n" + selected[key]["excerpt"])
        for key in candidates
    ]
    rerank_scores = (
        reranker.predict(rerank_pairs, show_progress_bar=False) if candidates else []
    )
    scores = {key: float(score) for key, score in zip(candidates, rerank_scores)}
    if any(not np.isfinite(score) for score in scores.values()):
        raise ValueError("Reranker returned invalid scores")
    result = {
        "query": query,
        "checked_at": now(),
        "project": project,
        "method": "Hybrid embedding retrieval plus local cross-encoder reranking and FTS5 BM25",
        "model_revision": revision,
        "embedding_model": config["embedding"]["model_id"],
        "reranker_model": config["reranker"]["model_id"],
        "device": "local",
        "coverage": {"current_vectors": len(active), "current_passages": len(items)},
        "limits": lexical["limits"][1:]
        + [
            "User-selected local models; passage text is capped by the embedding model settings.",
            "Partial embedding coverage can omit semantic-only matches; exact-source citations remain authoritative.",
        ],
        "passages": [],
    }
    per_doc = {}
    per_message = {}
    for key in sorted(scores, key=lambda key: scores[key], reverse=True):
        if (
            config["minimum_score"] is not None
            and scores[key] < config["minimum_score"]
        ):
            continue
        item = selected[key]
        identity = item["key"]
        message = (identity, item.get("message_index"))
        if per_doc.get(identity, 0) >= 3 or per_message.get(message, 0) >= 2:
            continue
        item = {k: v for k, v in item.items() if k not in ["text", "identity"]}
        item.update(
            {"rank": scores[key], "citation": "E" + str(len(result["passages"]) + 1)}
        )
        result["passages"].append(item)
        per_doc[identity] = per_doc.get(identity, 0) + 1
        per_message[message] = per_message.get(message, 0) + 1
        if len(result["passages"]) >= limit:
            break
    return result
