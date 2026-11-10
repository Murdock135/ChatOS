"""Freeze source data and derive inspectable experiment embedding inputs."""

import json
from pathlib import Path
from typing import Any

from chatos.mapping.map_topics import semantic_samples

from .artifacts import file_hash
from .config import ExperimentConfig
from .points import topic_points


def prepare(
    config: ExperimentConfig, output: Path
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Use one frozen corpus; retain source text, exact inputs and exclusion reasons."""
    inputs = output / "inputs"
    inputs.mkdir()
    dataset = Path(config.dataset)
    raw = dataset.read_bytes()
    (inputs / "sample.json").write_bytes(raw)
    records = json.loads(raw)
    if not isinstance(records, list) or not records:
        raise ValueError("dataset must contain a nonempty JSON array of conversations")
    identities = set()
    for record in records:
        identity = (record["source"], record["id"])
        if identity in identities:
            raise ValueError("Duplicate source-qualified conversation in dataset")
        identities.add(identity)
    points = []
    excluded = []
    sources: dict[str, Any] = {
        "dataset": {"path": str(dataset), "sha256": file_hash(inputs / "sample.json")}
    }
    if config.representation == "raw":
        for record in records:
            samples, fallback = semantic_samples(record)
            if not samples:
                excluded.append(
                    {
                        "source": record["source"],
                        "id": record["id"],
                        "reason": "No usable source samples",
                    }
                )
                continue
            points.append(
                {
                    "id": record["source"] + ":" + record["id"],
                    "source": record["source"],
                    "conversation_id": record["id"],
                    "kind": "conversation",
                    "label": record.get("title", ""),
                    "embedding_texts": samples,
                    "assistant_fallback": fallback,
                }
            )
    else:
        by_id = {record["pilot_id"]: record for record in records}
        if len(by_id) != len(records):
            raise ValueError("Duplicate pilot IDs")
        response_dir = inputs / "responses"
        response_dir.mkdir()
        seen = set()
        sources["responses"] = []
        for path in sorted(Path(config.responses).glob("*.json")):
            payload = path.read_bytes()
            response = json.loads(payload)
            if response.get("model") != config.summary_model:
                continue
            identity = response.get("pilot_id")
            if identity in seen:
                raise ValueError("Duplicate summary response for " + str(identity))
            seen.add(identity)
            snapshot = response_dir / path.name
            snapshot.write_bytes(payload)
            sources["responses"].append(
                {"path": str(path), "sha256": file_hash(snapshot)}
            )
            try:
                derived = topic_points(by_id[identity], response)
            except (KeyError, ValueError, TypeError) as error:
                excluded.append({"response": path.name, "reason": str(error)})
                continue
            for point in derived:
                point["embedding_texts"] = [point["embedding_text"]]
            points.extend(derived)
        for identity in sorted(set(by_id) - seen):
            excluded.append(
                {"pilot_id": identity, "reason": "No saved response for selected model"}
            )
    if not points:
        raise ValueError("No usable embedding inputs")
    return points, {
        "input_conversations": len(records),
        "sources": sources,
        "excluded": excluded,
    }
