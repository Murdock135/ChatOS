"""Optional pretrained conversation map; cluster before the two-dimensional projection."""

import os

from .core import digest, now, write_json
from .workspace import workspace_path


def build(store):
    os.environ["NUMBA_CACHE_DIR"] = str(store.state / "numba-cache")
    os.environ["NUMBA_NUM_THREADS"] = "4"
    import numpy as np
    from sklearn.cluster import HDBSCAN
    from sklearn.metrics.pairwise import cosine_distances
    from umap import UMAP

    from .explorer import neighbor_retention, write_page
    from .map_topics import LABEL_VERSION, label_groups, semantic_samples
    from .search_models import fingerprint, model, settings

    config = settings(store.root)
    revision = fingerprint(store.root, config["embedding"])
    records = store.records()
    represented = []
    vectors = []
    samples = []
    spans = []
    assistant_fallback = 0
    for record in records:
        selected, fallback = semantic_samples(record)
        if not selected:
            continue
        assistant_fallback += int(fallback)
        spans.append((len(samples), len(samples) + len(selected)))
        samples.extend(selected)
        represented.append(record)
    if len(represented) < 6:
        raise ValueError(
            "At least six conversations with visible topic text are required"
        )
    encoder = model(store.root, "embedding", config)
    encoded = encoder.encode(
        [config["embedding"]["document_prompt"] + sample for sample in samples],
        batch_size=16,
        normalize_embeddings=True,
        show_progress_bar=False,
        convert_to_numpy=True,
    )
    encoded = np.asarray(encoded, dtype=np.float64)
    if (
        encoded.ndim != 2
        or len(encoded) != len(samples)
        or not np.isfinite(encoded).all()
    ):
        raise ValueError("Invalid topic sample embeddings")
    usable = []
    for record, (start, end) in zip(represented, spans):
        vector = np.mean(encoded[start:end], axis=0)
        norm = np.linalg.norm(vector)
        if norm < 1e-10:
            continue
        usable.append(record)
        vectors.append(vector / norm)
    represented = usable
    if len(vectors) < 6:
        raise ValueError(
            "At least six conversations with current embeddings are required"
        )
    matrix = np.asarray(vectors, dtype=np.float64)
    distances = np.maximum(cosine_distances(matrix), 0)
    np.fill_diagonal(distances, 0)
    labels = HDBSCAN(
        min_cluster_size=4, min_samples=2, metric="precomputed", n_jobs=1
    ).fit_predict(distances.copy())
    plane = np.asarray(
        UMAP(
            n_neighbors=min(15, len(vectors) - 1),
            n_components=2,
            min_dist=0.15,
            metric="cosine",
            random_state=42,
            n_jobs=1,
        ).fit_transform(matrix),
        dtype=np.float64,
    )
    group_for = {}
    for label in sorted(set(labels)):
        indices = [i for i, value in enumerate(labels) if value == label]
        identity = (
            "unclustered"
            if label < 0
            else digest(
                sorted(
                    represented[i]["source"] + ":" + represented[i]["id"]
                    for i in indices
                )
            )[:10]
        )
        for i in indices:
            group_for[i] = identity
    group_labels = label_groups(
        represented, [group_for[i] for i in range(len(represented))]
    )
    documents = []
    for i, record in enumerate(represented):
        neighbors = np.argsort(distances[i]).tolist()
        neighbors = [j for j in neighbors if j != i][:5]
        documents.append(
            {
                "source": record["source"],
                "id": record["id"],
                "title": record["title"],
                "path": record["file_path"],
                "url": (store.root / record["file_path"]).as_uri(),
                "projects": record.get("projects", []),
                "date": (record.get("updated_at") or record.get("created_at") or "")[
                    :10
                ],
                "x": float(plane[i, 0]),
                "y": float(plane[i, 1]),
                "group": group_for[i],
                "neighbors": neighbors,
            }
        )
    data = {
        "checked_at": now(),
        "backend": "configured-topic-umap-hdbscan-v2",
        "model": config["embedding"]["model_id"],
        "revision": revision,
        "input_fingerprint": digest(records),
        "documents": documents,
        "groups": group_labels,
        "label_method": LABEL_VERSION,
        "variance_2d": None,
        "neighbor_retention_5": neighbor_retention(matrix.tolist(), plane.tolist()),
        "coverage": {
            "represented_conversations": len(represented),
            "total_conversations": len(records),
            "sample_vectors": len(samples),
            "sample_limit_per_conversation": 13,
            "assistant_fallback": assistant_fallback,
        },
        "method": "Mean normalized embeddings of title and up to 12 evenly spaced user samples; capture wrappers and filesystem paths excluded from derived topic input; HDBSCAN on original cosine distances (min cluster 4, min samples 2); UMAP 2D (15 neighbors, min distance 0.15, seed 42). Topic labels use corpus-weighted distinctive source phrases sampled across user messages.",
        "limits": "Experimental local pretrained representation. HDBSCAN may leave conversations unclustered; labels and clusters need human/agent review. UMAP can distort distance and density. Groups and map proximity do not establish ownership, truth, or accepted decisions. Bounded samples and averaging can blur multi-topic conversations; assistant passages are used only if no user passage is available. Embedding text uses the configured token cap per passage.",
    }
    write_json(store.state / "dense-map.json", data)
    write_page(store, data)
    return {
        "checked_at": data["checked_at"],
        "coverage": data["coverage"],
        "clusters": len([k for k in group_labels if k != "unclustered"]),
        "unclustered": int(sum(label < 0 for label in labels)),
        "neighbor_retention_5": data["neighbor_retention_5"],
        "path": str(workspace_path(store.root, "Humans/explorer.html")),
    }
