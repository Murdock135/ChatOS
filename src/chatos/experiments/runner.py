"""Run local, source-frozen experiments without modifying the application index."""

import json
import os
import platform
import shutil
import sys
import time
import zipfile
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any, cast

from .artifacts import file_hash, seal, write_json
from .config import ExperimentConfig, load_config
from .dataset import prepare


def embed(points: list[dict[str, Any]], config: ExperimentConfig) -> tuple[Any, dict]:
    """Embed exact input pieces, retaining the raw baseline's normalized mean."""
    import numpy as np
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(config.model_path, local_files_only=True, device="cpu")
    model.max_seq_length = config.max_length
    pieces = []
    spans = []
    truncated = 0
    for point in points:
        texts = point["embedding_texts"]
        spans.append((len(pieces), len(pieces) + len(texts)))
        for text in texts:
            length = len(model.tokenizer.encode(text, verbose=False))
            if length > config.max_length:
                if config.representation == "topic-subtopic":
                    raise ValueError(
                        "Topic label exceeds max_length; no silent truncation"
                    )
                truncated += 1
        pieces.extend(texts)
    encoded = np.asarray(
        model.encode(
            pieces,
            batch_size=config.batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        ),
        dtype=np.float64,
    )
    vectors = np.stack([encoded[start:end].mean(axis=0) for start, end in spans])
    norms = np.linalg.norm(vectors, axis=1)
    if not np.isfinite(vectors).all() or np.any(norms < 1e-10):
        raise ValueError("Nonfinite or empty embedding vectors")
    return vectors / norms[:, None], {
        "input_pieces": len(pieces),
        "truncated_raw_pieces": truncated,
    }


def analyze(vectors: Any, config: ExperimentConfig) -> tuple[Any, Any, dict[str, Any]]:
    """Cluster original cosine distances; independently project and measure geometry."""
    import numpy as np
    from sklearn.cluster import HDBSCAN
    from sklearn.manifold import trustworthiness
    from sklearn.metrics import silhouette_score

    count = len(vectors)
    distance = np.clip(1 - vectors @ vectors.T, 0, 2)
    np.fill_diagonal(distance, 0)
    labels = np.full(count, -1, dtype=int)
    if config.clustering == "hdbscan":
        if config.min_samples > count or config.min_cluster_size > count:
            raise ValueError("HDBSCAN minimum settings exceed the number of points")
        labels = HDBSCAN(
            min_cluster_size=config.min_cluster_size,
            min_samples=config.min_samples,
            metric="precomputed",
            n_jobs=1,
            # sklearn's temporary "warn" default is inferred as str; bool is supported.
            copy=cast(Any, True),
        ).fit_predict(distance.copy())
    metrics: dict[str, Any] = {
        "points": count,
        "clustering_applied": config.clustering != "none",
        "clusters": len({int(i) for i in labels if i >= 0})
        if config.clustering != "none"
        else None,
        "unclustered": int((labels < 0).sum()) if config.clustering != "none" else None,
        "semantic_accuracy": None,
        "semantic_accuracy_reason": "No independently reviewed reference labels supplied",
    }
    mask = labels >= 0
    if 1 < len(set(labels[mask])) < int(mask.sum()):
        metrics["silhouette_nonnoise_cosine"] = float(
            silhouette_score(
                distance[np.ix_(mask, mask)], labels[mask], metric="precomputed"
            )
        )
    plane = None
    if config.projection == "umap":
        if not 2 <= config.n_neighbors < count:
            raise ValueError(
                "UMAP n_neighbors must be smaller than the number of points"
            )
        from umap import UMAP

        plane = np.asarray(
            UMAP(
                n_neighbors=config.n_neighbors,
                n_components=2,
                min_dist=config.min_dist,
                metric="cosine",
                random_state=config.seed,
                n_jobs=1,
                init="random",
            ).fit_transform(vectors),
            dtype=np.float64,
        )
        if not np.isfinite(plane).all():
            raise ValueError("Nonfinite projected coordinates")
        k = min(5, (count - 1) // 2)
        metrics["diagnostic_k"] = k
        if k:
            metrics["trustworthiness"] = float(
                trustworthiness(distance, plane, n_neighbors=k, metric="precomputed")
            )
            original = np.argsort(distance, axis=1, kind="stable")
            projected = ((plane[:, None, :] - plane[None, :, :]) ** 2).sum(axis=2)
            reduced = np.argsort(projected, axis=1, kind="stable")
            retention = []
            for i in range(count):
                left = [int(j) for j in original[i] if j != i][:k]
                right = [int(j) for j in reduced[i] if j != i][:k]
                retention.append(len(set(left) & set(right)) / k)
            metrics["neighbor_retention"] = float(np.mean(retention))
    return labels, plane, metrics


def provenance(config: ExperimentConfig, output: Path) -> dict[str, Any]:
    """Snapshot experiment/source modules and identify exact downloaded model files."""
    package = Path(__file__).resolve().parents[1]
    with zipfile.ZipFile(
        output / "source-snapshot.zip", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for source in sorted(package.rglob("*.py")):
            archive.write(source, source.relative_to(package).as_posix())
    model_files = {
        str(path.relative_to(Path(config.model_path))): file_hash(path)
        for path in sorted(Path(config.model_path).rglob("*"))
        if path.is_file()
    }
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "device": "cpu",
        "packages": {
            name: version(name)
            for name in (
                "numpy",
                "scikit-learn",
                "sentence-transformers",
                "torch",
                "umap-learn",
            )
        },
        "model_files": model_files,
        "min_samples_convention": "sklearn HDBSCAN includes the point itself; production uses 2, older pilot adjusted 2 to sklearn 3",
        "determinism_limit": "Seeds and inputs are recorded; bitwise reproducibility across platforms/library versions is not guaranteed",
    }


def run(protocol: Path, output: Path) -> dict[str, Any]:
    """Run a new immutable bundle; record failures without publishing partial success."""
    config = load_config(protocol)
    if not Path(config.model_path).is_dir():
        raise ValueError("model_path must identify a previously downloaded local model")
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    state: dict[str, Any] = {
        "schema_version": 1,
        "status": "running",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "timings_seconds": {},
        "additional_api_calls": 0,
        "directory": str(output),
    }
    write_json(output / "protocol.json", config.as_dict())
    (output / "requested-protocol.json").write_bytes(protocol.read_bytes())
    write_json(output / "run.json", state)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["NUMBA_CACHE_DIR"] = str(output / ".numba-cache")
    os.environ["NUMBA_NUM_THREADS"] = "4"
    try:
        state["stage"] = "prepare"
        write_json(output / "run.json", state)
        mark = time.perf_counter()
        points, dataset = prepare(config, output)
        write_json(output / "dataset.json", dataset)
        write_json(output / "points.json", points)
        state["timings_seconds"]["prepare"] = time.perf_counter() - mark
        state["stage"] = "provenance"
        write_json(output / "run.json", state)
        write_json(output / "provenance.json", provenance(config, output))
        mark = time.perf_counter()
        state["stage"] = "embedding"
        write_json(output / "run.json", state)
        vectors, embedding = embed(points, config)
        import numpy as np

        np.save(output / "embeddings.npy", vectors)
        write_json(
            output / "embedding.json",
            {**embedding, "dimensions": int(vectors.shape[1])},
        )
        state["timings_seconds"]["embedding"] = time.perf_counter() - mark
        mark = time.perf_counter()
        state["stage"] = "analysis"
        write_json(output / "run.json", state)
        labels, plane, metrics = analyze(vectors, config)
        state["timings_seconds"]["analysis"] = time.perf_counter() - mark
        write_json(output / "metrics.json", metrics)
        results = []
        for i, point in enumerate(points):
            results.append(
                {
                    "point_id": point["id"],
                    "cluster": int(labels[i]) if config.clustering != "none" else None,
                    "coordinates": [float(v) for v in plane[i]]
                    if plane is not None
                    else None,
                }
            )
        write_json(output / "results.json", results)
        state.update(
            status="complete",
            stage="complete",
            points=len(points),
            represented_conversations=len(
                {(p["source"], p["conversation_id"]) for p in points}
            ),
        )
        report = [
            "# Local representation experiment",
            "",
            f"Representation: {config.representation}. Points: {len(points)}.",
            f"Clustering: {config.clustering}. Projection: {config.projection}. Seed: {config.seed}.",
            "",
            "Exact embedding inputs and IDs: points.json. Frozen records/responses: inputs/.",
            "Vectors: embeddings.npy. Memberships and coordinates: results.json.",
            "Protocol, model hashes, package versions, source snapshot, exclusions and timings accompany the results.",
            "",
            "## Geometric diagnostics",
            "",
            "```json",
            json.dumps(metrics, indent=2),
            "```",
            "",
            "Geometry is not semantic accuracy. No independently reviewed ground truth was supplied.",
            "Raw representations average sampled passage vectors; topic/subtopic labels remain separate points.",
            "Topic hierarchy records source structure and does not force spatial containment.",
            "Raw conversations and topic points have different evaluation units; compare coverage and denominators explicitly.",
            "No model download, remote inference or production-index replacement was performed.",
        ]
        (output / "report.md").write_text("\n".join(report) + "\n")
    except BaseException as error:
        state.update(
            status="interrupted" if isinstance(error, KeyboardInterrupt) else "failed",
            error_type=type(error).__name__,
            error=str(error),
        )
        raise
    finally:
        state["finished_at"] = datetime.now(timezone.utc).isoformat()
        state["timings_seconds"]["total"] = time.perf_counter() - started
        write_json(output / "run.json", state)
        # Compiler caches are not scientific artifacts and vary by process/platform.
        cache = output / ".numba-cache"
        if cache.is_dir():
            shutil.rmtree(cache)
        seal(output)
    return state
