# Semantic map exploration validation

October 25, 2026. This is implementation evidence, not a general clustering benchmark.

## Isolated regression and browser checks

The Python suite passed 119 tests. It includes content search whose relevant terms occur only inside a message, source-qualified selections with colliding IDs, exact preview citations, immutable source records, current local titles/archive state, malformed and stale-generation selection rejection, known-wrapper removal only from derived input, and authenticated, lock-protected semantic rebuilds. Node's browser startup regression checks navigation while the first request is pending. Astro checks and builds the bundled frontend; new Python modules pass scoped type/lint/format checks.

The browser fixture contains 24 fictional conversations: eight each about PostgreSQL optimization, coral reef restoration and Dempster–Shafer evidence. It uses actual downloaded MiniLM embeddings and HDBSCAN/UMAP, not simulated geometry. It produced three groups with all 24 conversations assigned to their expected subject (cluster purity 1.0 for this easy constructed sample) and nearest-five-neighbor retention about 0.71 in 2D. Repetition within the fixture makes it an easy case; this does not establish performance on natural multi-topic archives.

Browser checks exercised concept search, local semantic ranking, topic filtering, source filtering (12 of 24), inclusive single-date filtering (3 of 24), selection and assistant packet creation, original-message navigation, zoom/fit/expand, and separate exports. The query “ocean habitats and reef recovery” ranked all eight reef conversations before the other topics; lower-ranked off-topic candidates remained visible, with the bounded-search limitation disclosed. The keyword “bleaching” narrowed the view to one conversation.

Downloaded results and assistant-selection JSON each contained the eight selected belief-topic conversations. The PNG export had a valid PNG signature and nonzero dimensions. Source IDs remain in these inspectable data exports, not the visible reader. No fixture transcripts or personal records are included in the repository.

## Actual installation check

The selected embedding/reranking models were downloaded locally with resolved revisions and file-hash manifests. Existing derived passage vectors and the semantic map were rebuilt while retaining original conversations, annotations and settings. The final inspected map represented 273 of 273 captured conversations using 1,416 bounded sample vectors, one assistant fallback, 16 clusters and 144 unclustered conversations. Nearest-five-neighbor retention was about 0.41. Freshness matched current captured records at the check; subsequent captures can make the map stale.

The high outlier count and modest 2D neighbor retention remain visible limitations. A bounded inspection identified automatic browser/context and filesystem terms in earlier group names; the derived-input filter addresses that specific contamination. Group correctness across the real archive has not been independently labeled or established. Improved representation hygiene and navigation are verified; a universal clustering-quality improvement is not claimed.

## Remaining limits

The tests do not establish full accessibility conformance or all device/browser combinations. Topic naming uses English source terms and bounded text samples. There is no automatic assistant execution or structured assistant-to-browser view-control bridge. The locally downloaded selection is a preview/evidence packet; full transcripts require a selected portable bundle.
