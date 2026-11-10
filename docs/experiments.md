# Local embedding and clustering experiments

The experiment CLI turns a frozen dataset and an explicit protocol into an inspectable run bundle. It does not update the search index or production map, download models, generate summaries or call AWS. The user-review interface remains deferred; geometric diagnostics are not semantic accuracy.

## Run a protocol

Install the optional semantic runtime as described in [Semantic setup](semantic-search.md). Copy and edit a [raw](../experiments/configs/raw.json) or [topic/subtopic](../experiments/configs/topics.json) protocol outside the public examples directory. Point `model_path` to a downloaded local Sentence Transformers model and `dataset` to a normalized JSON array of captured conversations. Use the same frozen corpus when comparing settings.

```bash
./scripts/chatos experiment /private/study/protocol.json \
  --output /private/study/runs/run-001 --json
./scripts/chatos experiment-check /private/study/runs/run-001 --json
```

Activate the semantic environment first so `scripts/chatos` finds its Python, or use `PYTHONPATH=src .venv-semantic/bin/python -m chatos` from the repository. Installed users can run `chatos` from any directory. The experiment commands do not require an initialized workspace or open its database. Relative input paths are resolved from the protocol's directory. Output must be a new directory; failed/partial runs are preserved rather than overwritten.

## Inputs and representations

The dataset is a JSON array of source-qualified records with `source`, `id`, `title` and ordered `messages` (`role`, `text`). Raw experiments embed the same title and bounded, evenly spaced user samples used by the application's existing map, with an assistant fallback when user text is unavailable. Sample vectors are normalized and their mean is normalized. Raw passage truncation at `max_length` is counted and reported.

Topic experiments additionally require `responses`, the folder of saved pilot response JSON files, and `summary_model`, the saved response's model key. Records need their existing `pilot_id` and `source_sha256`. Complete, contract-valid, nontruncated responses with matching identities/hashes are used; exclusions and absent responses are recorded. Each `main_subject` and each chronological subtopic `subject` gets a separate vector. Original parent IDs and exchange ranges are retained. There is no fallback to raw vectors and no new label generation. Labels exceeding the token limit fail visibly.

## Controlled settings

| Setting | Meaning |
| --- | --- |
| `schema_version` | Currently 1; unsupported fields/versions are rejected |
| `seed` | UMAP random seed |
| `batch_size`, `max_length` | CPU embedding batch and token cap |
| `clustering` | `none` or `hdbscan`, applied to original cosine distances |
| `min_cluster_size`, `min_samples` | Explicit sklearn HDBSCAN settings; sklearn counts the point itself |
| `projection` | `none` or `umap`; projection is independent of clustering |
| `n_neighbors`, `min_dist` | UMAP settings, with cosine distance, two components and random initialization |

`n_neighbors` must be smaller than the number of points; values are not silently reduced. With clustering disabled, memberships and cluster diagnostics are null rather than incorrectly reporting every point as noise. HDBSCAN noise retains membership -1. The older private pilot adjusted a density parameter of 2 to sklearn's 3; the production map and this runner's explicit example use sklearn 2. Record this distinction when comparing prior results.

## Saved evidence

- `requested-protocol.json`, `protocol.json`: requested settings and effective resolved settings.
- `inputs/`: frozen dataset and selected saved responses, copied before inference.
- `dataset.json`, `points.json`: source hashes, exclusions, coverage and exact embedding texts in vector-row order.
- `embeddings.npy`, `embedding.json`: normalized vectors, dimensions and truncation information.
- `results.json`: memberships and projected coordinates keyed by stable point IDs.
- `metrics.json`, `report.md`: geometric diagnostics with their denominators and interpretation limits.
- `provenance.json`, `source-snapshot.zip`: Python/platform/library versions, local-model file hashes and a frozen source-code artifact. Maintained code stays in the repository.
- `run.json`, `manifest.json`: lifecycle status, timestamps, timings, errors if any, and relative artifact SHA-256 hashes.

`experiment-check` detects changed, missing, extra and symlinked files without loading model libraries. Integrity can pass for a failed/interrupted run; the command returns a nonzero status unless execution completed. An intact manifest verifies the saved bytes, not scientific validity.

Trustworthiness and nearest-neighbor retention measure projection distortion. Silhouette, when defined, describes nonnoise cluster geometry. Semantic accuracy is null until independently reviewed references exist. Compare conversation-level and topic-level representations with care: their points, coverage and evaluation units differ. Seeds do not guarantee identical floating-point outputs across platforms or library versions. Avoid tuning on the same reviewed examples used for final reporting.

## Existing standalone map

`python3 scripts/build_topic_map.py --help` remains available and delegates to `chatos.experiments.topic_map`. Its maintained template is `src/chatos/templates/topic-map.html`, and source validation lives in `chatos.experiments.points`. The earlier map artifact is retained unchanged; this CLI provides a general run/report workflow alongside it.
