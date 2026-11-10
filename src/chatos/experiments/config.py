"""Explicit, versioned settings for local embedding and map experiments."""

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ExperimentConfig:
    dataset: str
    model_path: str
    representation: str = "raw"
    responses: str = ""
    summary_model: str = ""
    seed: int = 42
    batch_size: int = 16
    max_length: int = 256
    clustering: str = "none"
    min_cluster_size: int = 4
    min_samples: int = 2
    projection: str = "umap"
    n_neighbors: int = 15
    min_dist: float = 0.15
    schema_version: int = 1

    def validate(self) -> None:
        """Reject unsupported settings before loading optional model libraries."""
        if type(self.schema_version) is not int or self.schema_version != 1:
            raise ValueError("Unsupported experiment schema_version")
        for name in ("dataset", "model_path", "responses", "summary_model"):
            if not isinstance(getattr(self, name), str):
                raise ValueError(name + " must be a string")  # noqa: TRY004 -- CLI protocol validation contract
        for name in ("dataset", "model_path"):
            if not isinstance(getattr(self, name), str) or not getattr(self, name):
                raise ValueError(name + " must be a nonempty path")
        if self.representation not in ("raw", "topic-subtopic"):
            raise ValueError("representation must be raw or topic-subtopic")
        if self.representation == "topic-subtopic" and (
            not self.responses or not self.summary_model
        ):
            raise ValueError("Topic experiments require responses and summary_model")
        if self.clustering not in ("none", "hdbscan"):
            raise ValueError("clustering must be none or hdbscan")
        if self.projection not in ("none", "umap"):
            raise ValueError("projection must be none or umap")
        for name, low, high in (
            ("seed", 0, 2**32 - 1),
            ("batch_size", 1, 256),
            ("max_length", 32, 8192),
            ("min_cluster_size", 2, 100000),
            ("min_samples", 1, 100000),
            ("n_neighbors", 2, 100000),
        ):
            value = getattr(self, name)
            if type(value) is not int or not low <= value <= high:
                raise ValueError(f"{name} must be an integer between {low} and {high}")
        if (
            type(self.min_dist) not in (int, float)
            or not math.isfinite(self.min_dist)
            or not 0 <= self.min_dist <= 1
        ):
            raise ValueError("min_dist must be finite and between 0 and 1")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: Path) -> ExperimentConfig:
    """Resolve input paths relative to the supplied protocol, not the shell cwd."""
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError("An experiment protocol must be a JSON object")  # noqa: TRY004 -- CLI protocol validation contract
    try:
        config = ExperimentConfig(**value)
    except TypeError as error:
        raise ValueError(
            "Unknown or missing experiment settings: " + str(error)
        ) from error
    config.validate()
    resolved = config.as_dict()
    for name in ("dataset", "model_path", "responses"):
        if resolved[name]:
            candidate = Path(resolved[name]).expanduser()
            if not candidate.is_absolute():
                candidate = path.resolve().parent / candidate
            resolved[name] = str(candidate.resolve())
    return ExperimentConfig(**resolved)
