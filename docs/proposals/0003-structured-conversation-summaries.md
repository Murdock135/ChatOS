# Structured conversation summaries for semantic clustering

**Status:** proposal; implementation deferred. **Recorded:** October 25, 2026.

Zayan requested this document to preserve the discussion, implementation plan and cost analysis for later work. The preferred first experiment is one strong-model structured summary of each entire available conversation, followed by local embedding and clustering. Five-exchange weighted representations remain a later alternative. Two authorized Bedrock pilot calls are complete; a full-library API run and production integration have not been authorized by this proposal.

This extends [clustering and exploration](0002-clustering-exploration.md). That proposal's coordinated map controls have already been implemented; the work here concerns representation quality, optional user corrections and their integration with that experience. It is not an adopted software ADR or a claim of improved accuracy.

## Problem and intended behavior

Averaging embeddings of a long, mixed-topic conversation can blur its subjects. The current topic pipeline takes up to twelve distributed user-text samples, each capped at 900 characters, plus a usable title; it falls back to assistant text when user text is unavailable. Samples are embedded and combined rather than first being interpreted as a whole conversation. See `src/chatos/map_topics.py` and `src/chatos/search_models.py`; embedding length limits depend on the configured model. Clustering uses semantic distances; the two-dimensional map is a separate projection, not a quality score.

A prior 273-record model comparison found default MiniLM pairwise F1 of 49.5% on a small assistant-labeled diagnostic, with no convincing improvement from the tested alternative pretrained models. This is F1, not literal classification accuracy or evidence that every assignment is a coin flip. The labels were not independently reviewed or representative. Moreover, the user's subsequent clarification changes the target: debugging conversations from different projects may appropriately share a debugging cluster. Old labels that penalize such merges must be revised before evaluating this design.

The intended experience is:

- Preserve raw conversations and their provenance while deriving a concise, grounded description of intent, subject, operations and topic changes.
- Permit broad operation clusters across projects. Project membership remains an independent filter: selecting a project narrows visible conversations within clusters.
- Let the user optionally identify or correct uncertain groups after clustering, whenever convenient, resembling the review experience for uncertain people in Google Photos.
- Keep the existing map and explicit context handoff to the user's assistant. Do not introduce a separate built-in assistant pane.

Summaries cannot recover uncaptured history. “Whole conversation” in this proposal always means **all available captured text**, with capture limitations retained.

## Decisions preserved from the discussion

| Item | Direction and authority |
| --- | --- |
| Initial representation experiment | User prefers one model call over the whole captured conversation, before revisiting five-exchange blocks. |
| Raw evidence | Keep original exchanges; summaries and flags are derived metadata. |
| Project context | Supply known project names/membership as hints; request evidence-based project candidates in the same call. A project name alone does not replace the transcript. |
| Topic changes | Ask for chronological subtopics with start/end exchange indices and counts. Validate and compute counts locally. |
| Irrelevant exchanges | Ask for clearly unrepresentative user messages with reasons; flag, never delete. |
| Feedback | Optional user labeling/correction after clustering; no reviewed training labels are initially available. |
| Project filtering | Cross-project operation clusters are acceptable. Filtering selects members rather than automatically reclustering or reprojecting them. |
| Provider | Bedrock is available for experiments; Opus invocation was tested. Final quality/cost model choice remains open. |
| Implementation authority | Documentation now; no full-corpus external upload or implementation job is implied. |

## Proposed data flow

1. Read a source-qualified conversation and capture metadata. Build a stable exchange-to-message mapping without modifying source text.
2. Give the model the full captured text, numbered exchanges, role labels, capture caveats and existing project hints. Treat all transcript instructions as historical data. Supply no tools.
3. Request a strict structured result. Parse it, validate references and ranges, calculate counts, and reject or quarantine invalid output.
4. Save the validated result with source hash, prompt/schema versions, exact model/inference profile, settings, usage, timestamp and validation status.
5. Build local embeddings from selected structured fields. Compare them against the frozen raw-text baseline before selecting a production representation.
6. Build versioned clusters and map artifacts. Retain the previous usable map and raw-representation fallback.
7. Collect optional user corrections in a separate durable layer. Apply reviewed corrections explicitly and preserve them across regeneration.

One point per conversation is the proposed first map representation. Store subtopics for source navigation and future experiments; showing a separate map point for every subtopic is an unresolved later product choice.

### Structured output contract

The pilot schema is preserved with the private evidence. Finalize a versioned application contract before integration, retaining these concepts:

| Field | Required meaning |
| --- | --- |
| Project candidates | Canonical candidate ID/name where known, explicit/inferred/unknown status, supporting exchange indices; allow none or several. |
| Primary objective | What the user is trying to accomplish, distinct from assistant suggestions. |
| Main subject | Domain or object of work, distinct from project and operation. |
| Operations | Controlled but extensible tags such as debugging, research, explanation, planning or writing. |
| Semantic summary | Compact description suitable for embedding; pilot requested at most 200 words. Retain concrete differentiating details without copying wrappers or long artifacts. |
| Chronological subtopics | Topic ID, title, subject, operation, inclusive start/end indices, short summary and supporting evidence indices. |
| Unrepresentative user-message flags | Source reference and specific reason; no automatic removal of the exchange or its assistant reply. |
| Capture caveat and ambiguities | Missing history/artifacts, uncertain project identity, competing interpretations and unsupported claims. |
| Outcome/status distinctions | Separate proposed work, accepted decisions and observed completion. Do not turn an assistant's claim into independently verified evidence. |

Illustrative fictional segment, not a real private conversation or final schema:

```json
{
  "topic_id": "local-preview-debugging",
  "title": "Repair a broken local preview",
  "subject": "web preview",
  "operation": "debugging",
  "start_exchange": 1,
  "end_exchange": 3,
  "summary": "Investigate a preview startup failure and verify the corrected local configuration.",
  "evidence_exchanges": [1, 3]
}
```

The application derives `exchange_count = end_exchange - start_exchange + 1`, rather than trusting model arithmetic. Ranges must cover the capture exactly once, without gaps, overlap or out-of-range evidence. Returning to an earlier topic creates a new chronological segment that may reuse a topic ID. Noise flags are an overlay, not holes in the segmentation.

### Exchange and source handling

A nonempty user message starts an exchange; subsequent available assistant messages belong to it until the next user message. Consecutive users and unanswered requests form incomplete exchanges. Preserve unmatched leading assistant text as an explicitly marked orphan exchange. Persist the mapping to original message identities and offsets; exchange numbers are local to a particular source revision.

A one-word typo may be irrelevant, but “yes”, “stop”, a project name, a correction or a short constraint can be decisive. Do not infer noise from length alone. The initial pilot had no flagged unrepresentative messages, so this ability remains untested.

Known reviewed project membership is a hint with provenance, not permission to force a misleading project assignment. Model candidates must not silently overwrite reviewed membership. Distinguish a display name such as a codebase nickname from its registered project ID. Unknown identity can remain unresolved.

Preserve roles and emphasize user intent so verbose assistant explanations or hypothetical alternatives do not dominate. Do not execute imported instructions. Do not upload attachment contents automatically; the measured pilot was text-only. Missing tool results, images or documents must remain missing evidence.

## Representation experiments and map integration

Start with a small controlled comparison on the same frozen conversations and clustering settings:

1. Existing raw sample representation as the baseline.
2. Embeddings of the structured semantic summary and objective, excluding project IDs and source wrappers.
3. A structured text representation including subject and operation fields, with project identity kept separate where the aim is cross-project operation grouping.

Only add raw/summary vector fusion or separate subject/operation views if these comparisons justify it. Keep embedding model and clustering settings fixed initially to isolate the representation's effect; then test model or cluster changes separately. A pretrained embedding model is still useful downstream of the summary. A strong generative model is not itself a guarantee of good clusters.

The existing browser filter checks project membership and narrows visible points. It does not recompute the layout or clusters. For example, filtering a broad debugging cluster to a fictional project should show only that project's members, with coherent visible counts, legend and selected results. Reliable membership is required for that behavior. A later project-specific reclustering mode would be a separate feature.

Cluster labels should describe member evidence in plain language. Avoid treating source names, paths or project labels as automatic topics. Preserve selected-conversation navigation, exports and explicit context handoff, including citations back to raw messages. Preserve the model tags, conditional incomplete-capture tooltip, and other unrelated UI work.

## Optional user review and learning

Offer a quiet review entry point for uncertain cases, without mandatory onboarding labels. Useful actions include naming a group, confirming or moving a member, and proposing merges or splits. A name change alone is not a membership correction. A split suggestion needs a reviewable member allocation rather than a destructive automatic repartition.

Uncertainty signals can include weak density membership, small distance margins, instability under modest parameter changes, or disagreement between raw and summary representations. These are heuristics; do not present them as calibrated probabilities or model-reported certainty as measured accuracy.

Store corrections separately with source-qualified identities, cluster/version context, action, user-review status, timestamp and undo history. Cluster IDs may change after rebuilding; retain the reviewed member relationships and migration evidence rather than assuming IDs remain stable. Assistant suggestions are not accepted user labels. Do not overwrite original conversations, notes, settings or project assignments.

Initially there are no reviewed labels for optimization. Gather voluntary corrections first. Later tune a small number of parameters using one reviewed set and evaluate on other reviewed conversations whose labels were not used for tuning.

**Hold out entire conversations**, and shared fork ancestry where appropriate. Neighboring blocks share vocabulary and context, so putting one block in training and another from the same conversation in validation can inflate performance. This leakage concern is separate from topic drift. Include genuine topic changes in evaluation rather than assuming neighboring blocks always share a label.

## Phased implementation plan for later approval

| Phase | Work | Completion evidence |
| --- | --- | --- |
| 0 — Freeze scope and baseline | Recheck source coverage, current code, prices, model access, intended grouping and a fixed evaluation sample. Confirm allowed provider uploads and explicit run limits. | Recorded manifest, revised evaluation rubric and bounded run plan. No incidental bulk API run. |
| 1 — Summary adapter | Implement typed schema, exchange mapping, prompt, Bedrock adapter, local validation and versioned cache. Keep provider optional and use fictional fixtures. | Tests for boundaries, orphans, missing history, instruction-like text, invalid JSON, truncation, project ambiguity and flags. Cache invalidation/resume verified without extra calls. |
| 2 — Bounded quality study | Select additional authorized examples spanning projects, lengths, operations, drift, incomplete captures and short meaningful responses. Compare candidate models/representations. | Source-grounded review, token/cost ledger and comparable baseline metrics; report failures as well as improvements. |
| 3 — Optional derived index | Add summary-based local embeddings/clusters behind an explicit experimental selection. Preserve old artifacts and source data. | Incremental rebuild, unchanged-record reuse, invalid-result fallback, deterministic provenance and rollback verified. |
| 4 — Review experience | Integrate summary provenance, optional uncertainty review, durable corrections and existing map filters/navigation/exports/handoff. | Essential rendered browser flows tested with fictional data, including filtering, correction, undo and rebuild persistence. |
| 5 — Evaluate and decide | Assess semantic utility and correction burden before promotion; retain baseline if gain is absent. | Published scoped results and limitations, focused tests plus applicable lint/format/type checks, rebuilt browser assets. Adopted choices may then become an ADR. |

Do not require a particular numerical quality threshold chosen after seeing results. Before comparative testing, agree on practical acceptance criteria for representative neighbors/groups and acceptable false merges. In the absence of reviewed labels, structural validity and assistant review support feasibility, not a production accuracy claim.

### Runtime and cost controls

Use source content hash plus prompt/schema/model/settings and project-hint versions as cache identity. A changed capture invalidates its old exchange mapping. Resume completed work and refresh only changed inputs. Keep earlier validated summaries available for comparison; do not silently present stale ones as current.

Persist a manifest of planned calls and attempt limits. Begin with automatic SDK retries disabled, as in the pilot; any repair call or retry is an additional paid attempt requiring room in the authorized plan. Reject oversized inputs visibly rather than silently truncating. Make any chunking fallback an explicit later choice.

Record usage and estimated cost per call. Stop before new calls when the configured allowance would be exceeded, using provider token counts when supported or a documented conservative estimate otherwise. A local estimate is not an AWS billing guarantee; maintain a reserve and disclose residual uncertainty. Recheck prices, reasoning/output accounting, context limits and regional routing at execution time. Do not log credentials. Credits and billing alarms do not replace bounded application behavior.

No background paid service should be required for core archive/search use. Summary failure must leave the raw source and existing local experience usable.

## Evaluation plan and current evidence

Evaluate these separately:

- Summary faithfulness: intent, project candidates, operations, status distinctions and evidence support.
- Segmentation: coverage, arithmetic, boundary placement and genuine topic changes. Structural checks alone do not establish semantic boundary quality.
- Grouping: reviewed pair relationships, neighborhood relevance, false merges, missed relationships and unclustered coverage. Allow legitimate cross-project operation groups and multiple subjects.
- Product usefulness: project filtering, useful labels, source navigation and the amount of correction required.
- Reliability and expense: malformed/truncated responses, reproducibility, cache behavior, latency, input/output usage and cost.

The previous MiniLM comparison is a diagnostic baseline, not an independently reviewed test set. Two successful summaries do not establish clustering gains. Do not optimize only cluster compactness, a two-dimensional map's appearance, or agreement with an unreviewed model-generated answer key.

## Measured corpus and cost analysis

These are historical measurements from October 25, 2026, not live quotes or complete account-history lengths. The private [study report](../../workspace/chief_of_staff/reference/Evaluations/2026-10-25-bedrock-summary-study/report.md) retains exact requests, usage and reproducible calculations. Fresh clones do not include those private files.

### Captured conversation lengths

Read-only local measurement covered **275 conversations: 238 Codex and 37 ChatGPT**. Of these, 142 were partial history projections, 37 partial desktop captures and 96 available-visible-message captures. None establishes complete original history. Images, audio and attachment contents were excluded; this was the ChatGrep archive, not a new account-wide ChatGPT export.

| Measure | Average | Median | Minimum | Maximum | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw words | 1,418.4 | 560 | 3 | 29,863 | 390,064 |
| Raw characters | 10,918.3 | 4,240 | 20 | 217,973 | 3,002,530 |
| Estimated raw text tokens | 2,426.4 | 939 | 3 | 47,191 | 667,247 |
| Estimated tokens with exchange/role markers | 2,513.5 | 993 | 10 | 47,977 | 691,217 |
| Exchanges | 6.1 | 3 | 1 | 95 | 1,664 |
| Visible messages | 17.2 | 7 | 1 | 254 | 4,729 |

Token estimates used local `o200k_base`, not Claude's tokenizer or a Bedrock billable input count. The 95th percentile was 7,929 raw tokens / 8,188 formatted tokens. Including instructions, schema and metadata, the whole-library input proxy was **879,856 tokens**, with a maximum individual request proxy of 48,671.

### Actual two-conversation pilot

The user explicitly authorized two conversations to be sent. Both were selected from the same technical project; one was the longest captured conversation by local formatted-token estimate. Each received one inference, without automatic SDK retries, using **`us.anthropic.claude-opus-5-5`**, US geographic inference, an 8,192-token generation cap and no tools. The model used its default adaptive reasoning configuration. Reasoning blocks were not retained; usage accounting was retained.

| Pilot | Exchanges | Local formatted tokens | Actual input tokens | Actual output tokens | Subtopics | Time | Published-price cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Short technical refactor discussion | 10 | 1,880 | 4,073 | 1,422 | 4 | 15.0 s | $0.0492 |
| Long technical case-study discussion | 66 | 47,977 | 73,484 | 2,763 | 11 | 25.2 s | $0.3841 |
| Total | 76 | 49,857 | 77,557 | 4,185 | 15 | 40.2 s | **$0.4333** |

Both ended normally, parsed as JSON, covered all exchanges without overlapping/gapped ranges, and satisfied count/evidence-bound checks. Their semantic summaries contained 185 and 194 words. Neither flagged an unrepresentative user exchange.

Review scope: the short transcript was read fully; review of the long conversation sampled up to 260 characters of each user request after wrapper removal, rather than fully rereading all assistant text or referenced artifacts. Semantic faithfulness, noise detection and boundaries have not been exhaustively audited. No summary embeddings or clusters were built. These results demonstrate feasibility and observed usage, not representative accuracy.

### Model availability and prices

SPARQ's `utils/bedrock_utils.py` was used read-only after SSO refresh. The helper listed 123 foundation-model catalog entries in `us-east-1`. Access metadata listed Opus 5.5, Sonnet 5.5, Haiku 5.5, GPT-6 Astra and GPT-6.1 Sol as authorized; only Opus invocation was actually verified. Other agreement states were not all available. No subscription, model agreement or account setting was changed.

Rates below came from the [official AWS regional pricing offer](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonBedrockFoundationModels/current/us-east-1/index.json), saved with the evidence. They are **US geographic/in-region Standard USD per million tokens**, before credits or tax, rather than global-route prices. Recheck before execution. Lower cost does not establish adequate summary quality.

| Model | Input / million | Output / million | A: pilot-scaled, 275 calls | B: 2× input proxy, full output cap | C: byte-based input allowance, full output cap |
| --- | ---: | ---: | ---: | ---: | ---: |
| Claude Opus 5.5 | $4.40 | $22.00 | $18.85 | $57.30 | $68.67 |
| Claude Sonnet 5.5 | $2.20 | $11.00 | $9.42 | $28.65 | $34.33 |
| Claude Haiku 5.5 | $0.11 | $0.55 | $0.47 | $1.43 | $1.72 |
| OpenAI GPT-6 Astra | $11.00 | $55.00 | $47.11 | $143.26 | $171.67 |

For input total I, per-call output allowance O, N calls and rates Ri/Ro per million:

`cost_USD = (I × Ri + N × O × Ro) / 1,000,000`

- **A:** I = 879,856 × 1.597881522, the largest observed actual/proxy input ratio; O = 2,092.5, the pilot mean billable output. This is a two-example extrapolation, not a measured archive cost.
- **B:** I = 2 × 879,856; O = 8,192 for every call.
- **C:** I = 4,341,957, assuming one input token per UTF-8 byte of full requests plus 1,024 framing tokens per request; O = 8,192. This deliberately pessimistic allowance is **not a provider-guaranteed tokenization bound**.

All scenarios assume one attempt per conversation, no batch/cache discounts, and no other paid services. Other models reuse hypothetical Opus-derived workload assumptions; their tokenization, output usage and quality were not measured. Long-context price tiers must be checked against actual inputs; the saved Astra rate changes above 272K input tokens, beyond the measured byte allowances. Reasoning usage may be chargeable and must not be assumed free.

Scaling Opus to **300 conversations at the same average lengths** gives A **$20.56**, B **$62.51**, C **$74.91**. Thus roughly **$75 is a planning allocation**, not an enforced cap or unconditional maximum. Actual Bedrock token counts for the remaining 273 records are unknown. Retries, reruns, growing conversations, higher caps and optional services increase expense. Credit balance and applicability were not verified; do not promise that credits make the run free.

## Research basis and uncertainties

These sources informed the discussion; none establishes a best method for ChatGrep. The linked private reading ledgers preserve exact reading scope and doubts. Distinguish dialogue segmentation, summarization, retrieval and archive-wide clustering when interpreting metrics.

| Source | What was read | Relevant idea and limits |
| --- | --- | --- |
| [HILTON, WWW Companion 2026](https://vbn.aau.dk/ws/files/841550451/3774905.3794645.pdf) | Main sections 1–6 and limitations, PDF pp. 2–9, extracted algorithms/tables and repository README; not code/prompts/appendices or visual plots. | Closest task-discovery example: context-aware per-exchange summaries using previous four exchanges, then embedding/clustering, hierarchy and human review. This is not disjoint five-exchange blocks. Curated classification F1 is not our pairwise clustering F1; large-corpus defaults do not transfer directly. |
| [HiSum, Expert Systems 2025](https://doi.org/10.1111/exsy.70043) | Main pp. 1–14, methods/experiments/results/limitations, tables 1–5; visual inspection pp. 4, 5, 13, 14; not code/checkpoints. | Learned latent topic grouping and role-aware summarization support topic-aware representations. Not demonstrated archive clustering or contiguous boundary extraction. Training/domain transfer, label construction and reporting inconsistencies remain concerns. |
| [SeCom, ICLR 2025](https://arxiv.org/html/2502.05589v3) | Introduction, section 2.2, main results/discussion, Appendix A.1 prose and selected A.5/A.6, repository README; not code or prompt figures. | Indexed turns and contiguous topic segments, raw evidence retention and denoising. Retrieval/QA gains do not prove cross-conversation clustering quality. |
| [Def-DTS, ACL Findings 2025](https://aclanthology.org/2025.findings-acl.1066.pdf) | Section 3, datasets/results, selected ablations/errors/limits and Appendix D; not an implementation reproduction. | Context and dialogue intent can inform boundaries. Short/synthetic benchmarks, filtered malformed outputs and reproduction differences limit transfer. |
| [SumSeg, NAACL Findings 2024](https://aclanthology.org/2024.findings-naacl.291.pdf) | Sections 3–5 and limitations; not code. | Summary-guided sentence representations and segmentation; not evidence for summary-only archive clustering. |
| [Threader, September 2026 preprint](https://arxiv.org/html/2609.33226v1) | Partial introduction, sections 3.1–3.3, selected results/limits and A.1–A.2; not code/checkpoints. | Incremental boundaries, preserved raw views and role separation; trained-model transfer remains unverified. |
| [CGS, September 2026 preprint](https://arxiv.org/html/2609.34425v1) | Partial introduction, sections 2–4, dataset/metric/ablation discussion; not code. | Explicit transition cues plus semantic fallback. Speech/meeting boundary results and tolerance metrics do not establish chat clustering accuracy. |

The present whole-conversation approach is a simpler experiment motivated by these ideas and the small library size. It does not reproduce any paper's pipeline. Summary compression may omit minority topics, introduce unsupported interpretations or overemphasize an early framing; evidence-indexed subtopics and source review mitigate these risks but do not eliminate them.

## Deferred alternatives and open choices

The user's earlier five-exchange idea remains documented for later: preserve raw blocks, emphasize the first exchange and progressively increase the next four weights, generate a summary of the same block, and combine raw and summary representations. An illustrative assistant-suggested weight vector `[0.40, 0.06, 0.12, 0.18, 0.24]` was not adopted or optimized. A block-opening acknowledgment is not equivalent to the conversation's initial topic anchor.

Later experiments could use adaptive boundaries, overlapping context and adjacent-segment merging, while avoiding transitive similarity chains that merge gradual topic drift. Tune a few constrained weights against reviewed examples before considering a neural optimizer. There is no trained weight optimizer in this proposal.

Other open choices are the production summarizer, final schema and vocabulary, summary-only versus multi-field embeddings, multiple map views, practical quality thresholds and uncertainty ranking. The terminal-style live sync output idea is separate deferred work.

## Resume instructions and evidence

Before implementation, re-read this proposal, current project instructions, [semantic setup](../semantic-search.md), [evaluation guide](../search-evaluation.md), and actual code. Recheck the working tree and preserve unrelated changes. Inspect `src/chatos/map_topics.py`, `src/chatos/search_models.py`, the current map/API code and authored frontend sources before selecting extension points; generated assets are not the editing source.

Private installation evidence, absent from fresh clones:

- [Bedrock study and reproducibility bundle](../../workspace/chief_of_staff/reference/Evaluations/2026-10-25-bedrock-summary-study/report.md): requests, parsed outputs, usage, measured lengths, catalog/access snapshots, price snapshot, scripts and SHA-256 manifest. The saved prompts and two outputs are the starting contract; do not rerun them incidentally.
- [Earlier model comparison](../../workspace/chief_of_staff/reference/Evaluations/2026-10-25-model-comparison/report.md): frozen corpus, diagnostic labels, vectors and limitations.
- [Initial research reading ledger](../../workspace/chief_of_staff/reference/Evaluations/2026-10-25-topic-segmentation-research.md).
- [User-supplied paper reading ledger](../../workspace/chief_of_staff/reference/Evaluations/2026-10-25-user-supplied-topic-papers.md).

Keep private transcript payloads and account-specific details in the private workspace, not public examples or packages. Source discussion: Codex conversation `01a17120-0b72-7073-9847-ae25e24d509f`, October 25, 2026. This document preserves design direction and measured evidence; it grants no new external-upload, paid-execution, publication or scheduling authority.
