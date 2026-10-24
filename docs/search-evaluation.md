# Evaluate search and clustering

Search results are evidence candidates, and a map is an exploratory view. Measure whether they help before treating similarity as reliable memory.

## Evaluate returned passages

After importing the fictional demo in Getting started:

```bash
./scripts/chatos --root Demo evaluate docs/examples/evaluation-cases.json --json
```

A labeled positive case supplies a source, conversation ID and exact known wording. A negative case uses `expected: null`. Optional `project` restricts the query; the evaluator rejects an expected source outside that project. Duplicate case IDs and nonexistent source labels are rejected.

For your own cases, copy the example format and label messages you actually inspected. Include exact wording, paraphrases, later corrections, project-scoped questions, and queries without relevant evidence. Do not invent expected evidence to make a test pass. Test user and assistant statements separately with optional expected `role` (default `user`). Optional `passage_contains` can specify the shorter excerpt that must be returned.

The report includes:

- **Passage recall at k:** positive queries returning the labeled wording from the correct source message.
- **Message hit rate:** correct source/message found, even if the returned chunk misses the relevant wording. This is weaker evidence.
- **Mean reciprocal rank:** how early the first correct passage appears.
- **Negative queries with results:** retrieval noise on your labeled no-evidence cases; this is not an answer-hallucination score.
- **Scope violations:** returned passages outside a requested project.
- Corpus/case fingerprints, backend method and optional embedding coverage for repeatable comparison.

Use `--output /private/result.json` to retain a report, `--limit 8` to set k, or `--hybrid` with the installed optional runtime. Run the same cases against the same corpus and current vectors when comparing methods. Labeled sources are not necessarily the only useful evidence; unlabeled relevant results can exist. This is a diagnostic, not a general model benchmark or guarantee that an assistant will interpret a result correctly.

## Inspect the map separately

```bash
./scripts/chatos --root workspace map-diagnostics --json
```

This reads the saved pretrained map without starting inference. It reports freshness, represented/missing chats, duplicate or nonfinite points, cluster sizes, unclustered points and saved neighbor retention. No saved map produces an explicit unavailable result.

Neighbor retention describes projection distortion, not semantic topic quality. A fresh map with every chat represented can still group them poorly. To inspect topic quality, supply independently reviewed labels:

```json
{"labels": [
  {"source": "chatgpt", "id": "REAL_ID_A", "topics": ["reading"]},
  {"source": "chatgpt", "id": "REAL_ID_B", "topics": ["reading"]},
  {"source": "codex", "id": "REAL_ID_C", "topics": ["cooking"]}
]}
```

```bash
./scripts/chatos --root workspace map-diagnostics --labels /private/topic-labels.json --json
```

The diagnostic compares labeled pairs: shared topic means related, shared non-unclustered group means predicted together. It reports positive pairs found, false merges, missed related pairs and pair precision/recall. Multiple topics can overlap. Unlabeled chats are excluded; missing labeled points and stale geometry limit interpretation. Project ownership is not automatically a topic label. Keep label provenance and sample selection with the results.

## Current installation observation

A seven-question source-labeled convenience set returned expected passages for 3/7 lexical queries and 4/7 hybrid queries at k=8 in this pass. Hybrid was rerun with 5,253/5,253 current vectors and still found 4/7. This does not establish superiority or a general recall estimate. It exposes remaining misses.

The refreshed map represented 264 chats, left 12 unclustered, and retained about 38.8% of its five-neighbor relationships in the 2D projection. Its semantic groups still need review; the label-evaluation mechanism does not manufacture independent ground truth. These are dated observations, and later imports can make the map or embedding coverage stale again.

A five-record assistant-labeled convenience sample produced two related pairs found and eight false merges (pair precision 0.2, recall 1.0). The sample was chosen from existing source-verified diagnostic cases and is not independently reviewed or representative. It demonstrates why cluster coverage and visually plausible geometry should not be treated as validated semantic organization.
