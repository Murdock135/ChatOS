"""Build an offline topic/subtopic map from a saved structured-summary pilot.

Usage: PYTHONPATH=src .venv/bin/python scripts/build_topic_map.py --help
"""

import argparse
import json
import os
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Any

from chatos.experiments.points import embedded_json, load_points, sha256


def build(pilot: Path, output: Path, model_path: Path) -> dict[str, Any]:
    """Embed labels separately and project each model's points without clustering."""
    if output.exists():
        raise ValueError(
            "Choose a new output directory; existing experiments are retained"
        )
    if not model_path.is_dir():
        raise ValueError("A previously downloaded local embedding model is required")
    grouped, excluded = load_points(pilot)
    output.mkdir(parents=True)
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["NUMBA_CACHE_DIR"] = str(output / "numba-cache")
    os.environ["NUMBA_NUM_THREADS"] = "4"
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from umap import UMAP

    model = SentenceTransformer(str(model_path), local_files_only=True, device="cpu")
    token_limit = model.max_seq_length
    if token_limit is None:
        raise ValueError("The local embedding model must declare a token limit")
    datasets = {}
    for key, points in grouped.items():
        workspace = pilot.resolve().parents[3]
        for point in points:
            relative = Path(point.get("file_path") or "")
            source = (workspace / relative).resolve()
            if source.is_relative_to(workspace) and source.is_file():
                point["source_url"] = source.as_uri()
        print(
            f"Embedding {key}: {len(points)} separate topic/subtopic points", flush=True
        )
        texts = [point["embedding_text"] for point in points]
        # Fail visibly rather than silently truncating an unexpectedly long label.
        lengths = [len(model.tokenizer.encode(text)) for text in texts]
        if max(lengths) > token_limit:
            raise ValueError(f"{key}: a topic label exceeds the embedding token limit")
        vectors = np.asarray(
            model.encode(texts, normalize_embeddings=True, show_progress_bar=False),
            dtype=np.float64,
        )
        if not np.isfinite(vectors).all() or np.any(
            np.linalg.norm(vectors, axis=1) < 1e-8
        ):
            raise ValueError("Invalid or empty topic embeddings")
        plane = np.asarray(
            UMAP(
                n_components=2,
                n_neighbors=min(15, len(points) - 1),
                min_dist=0.15,
                metric="cosine",
                random_state=42,
                n_jobs=1,
            ).fit_transform(vectors),
            dtype=np.float64,
        )
        if not np.isfinite(plane).all():
            raise ValueError("Invalid projected coordinates")
        distances = np.clip(1 - vectors @ vectors.T, 0, 2)
        for index, point in enumerate(points):
            point["x"], point["y"] = map(float, plane[index])
            neighbors = [
                int(i)
                for i in np.argsort(distances[index], kind="stable")
                if points[i]["pilot_id"] != point["pilot_id"]
            ][:5]
            point["neighbors"] = [
                {"id": points[i]["id"], "cosine_distance": float(distances[index, i])}
                for i in neighbors
            ]
        np.save(output / (key + "-vectors.npy"), vectors)
        datasets[key] = {
            "points": points,
            "conversations": sum(p["kind"] == "main" for p in points),
            "subtopics": sum(p["kind"] == "subtopic" for p in points),
            "max_label_tokens": max(lengths),
        }
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "input": str(pilot.resolve()),
        "sample_sha256": sha256(pilot / "sample.json"),
        "embedding_model": str(model_path.resolve()),
        "embedding_max_tokens": model.max_seq_length,
        "embedding_dimensions": int(vectors.shape[1]),
        "packages": {
            name: version(name)
            for name in (
                "numpy",
                "scikit-learn",
                "umap-learn",
                "sentence-transformers",
                "torch",
            )
        },
        "representation": "Main subject and subtopic subject separately; no averaging, weighting, objective or summary prose",
        "label_origin": "Existing pilot fields from the older prompt; no compact-label regeneration",
        "projection": {
            "method": "UMAP",
            "metric": "cosine",
            "n_neighbors": 15,
            "min_dist": 0.15,
            "seed": 42,
        },
        "clustering": None,
        "additional_paid_calls": 0,
        "excluded": excluded,
        "counts": {
            key: {k: v for k, v in dataset.items() if k != "points"}
            for key, dataset in datasets.items()
        },
        "limits": [
            "Derived summaries were not independently validated for semantic faithfulness.",
            "Only complete, source-matched, contract-valid responses are included; no raw-text fallback.",
            "Each model has an independent layout; coordinates cannot be compared across models.",
            "Parent links record source hierarchy, not embedding similarity or spatial containment.",
            "UMAP distorts distances and density; islands are not validated categories.",
            "Nearest-topic suggestions use original embedding cosine distances and exclude the same conversation.",
            "This experiment does not replace the production map.",
        ],
    }
    data = {"metadata": metadata, "datasets": datasets}
    (output / "topics.json").write_text(json.dumps(data, indent=2) + "\n")
    template = (
        Path(__file__).resolve().parents[1] / "templates/topic-map.html"
    ).read_text()
    (output / "map.html").write_text(
        template.replace("__TOPIC_DATA__", embedded_json(data))
    )
    inputs = [pilot / "sample.json", *sorted((pilot / "responses").glob("*.json"))]
    manifest = {
        "inputs": {str(p.resolve()): sha256(p) for p in inputs},
        "embedding_files": {
            str(p.resolve()): sha256(p)
            for p in sorted(model_path.rglob("*"))
            if p.is_file()
        },
        "code": {
            str(p.resolve()): sha256(p)
            for p in [
                Path(__file__),
                Path(__file__).resolve().parents[1] / "templates/topic-map.html",
                Path(__file__).with_name("points.py"),
            ]
        },
        "artifacts": {
            p.name: sha256(p) for p in sorted(output.iterdir()) if p.is_file()
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(metadata["counts"], indent=2), flush=True)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--model-path", type=Path, required=True)
    args = parser.parse_args()
    build(args.pilot_dir, args.output_dir, args.model_path)


if __name__ == "__main__":
    main()
