# Map sharpness — 2026-10-27

User requested sharper map text and dots, with black labels, and supplied two visual references. Source: Codex `01a17e0f-cff6-7b61-84a8-849228ab4546`.

Updated only `drawMap` and rebuilt bundled assets. Labels use black 13px semibold system text, opaque white backing, whole CSS-pixel placement and measured ellipsis rather than horizontal font compression. Dots retain topic colors and gain a subtle 0.75px outline. Canvas backing resolution is at least 2×, uses rounded physical dimensions and scales to the precise CSS bounds. Existing pan, zoom, selection and export code remains in place.

Verification: Astro check (zero errors/warnings, existing returnValue deprecation hint), frontend build, Node syntax check, browser startup regression, scoped renderer Prettier formatting check and Git whitespace check passed. Headless Chrome used a fictional 384-conversation/eight-topic fixture at device scales 1, 1.25 and 2. All eight labels rendered black at the expected font size, with a 2× backing store. Label focus, all-topics reset, zoom, point selection, expand/Escape, PNG download and 390px layout overflow checks passed at all three scales. No page errors observed. The DPR-1 screenshot was visually inspected. Screenshots contain fictional data only; no clustering computation or semantic-quality claim is made.

Browser setup recovery: bundled Playwright had no downloaded browser; sandboxed installed Chrome could not launch. Installed Chrome ran with approved escalation. The initial point-selection check clicked under a topic label; moving the test click outside labels passed. No application change was needed for that fixture correction.

The existing working tree contained unrelated app, branding, documentation and map-refinement edits. They were preserved. No commit or external publication was requested or performed.

## Follow-up — translucent dots

User requested “use fading/muting like the reference picture.” This supersedes the dot-outline treatment above: removed outlines from ordinary points and used 65% topic opacity, 30% unclustered opacity, and 18% opacity for other points when a selection exists. Selected points stay opaque with their existing white ring. Opacity resets before drawing the sharp black labels. Overlapping translucent dots naturally show denser areas more strongly. Frontend check/build, renderer formatting, Node syntax and browser startup regression pass.

## Correction — fade by measured membership strength

User clarified that translucency should vary with membership degree/confidence. This supersedes the uniform translucency and selection muting above. The dense-map builder now preserves scikit-learn HDBSCAN `probabilities_` as each point's `membership_strength`. Dot opacity maps strength 0–1 linearly onto 0.2–1; the floor keeps noise visible. Selection adds a ring and does not modify strength-driven fill opacity. Black text stays opaque. Hover shows the numeric strength and results JSON exports it. Missing legacy/LSA scores remain absent and use neutral 0.65 opacity, with a rebuild explanation in About. These scores measure cluster persistence, not calibrated confidence in a topic label. Source documentation read: HDBSCAN Attributes/probabilities_, https://scikit-learn.org/stable/modules/generated/sklearn.cluster.HDBSCAN.html.

Rebuilt the existing local semantic map offline using the already-downloaded embedding model: 307 points, 16 clusters, 166 noise points, 40 distinct strengths including 57 clustered points strictly between zero and one. Checked all scores finite/in-range, noise scores zero, and unchanged source-qualified scores through API enrichment. Current records were used, so groups/layout can differ from the prior saved map.

Verification: 11 map-exploration tests (including score preservation and absence for legacy maps), browser startup regression, Node syntax, Astro check/build, scoped Ruff lint/format, BasedPyright on dense_map.py (zero errors/warnings), scoped JS formatting and whitespace checks pass. Fictional browser fixture now has varying strengths: fill opacity increases with strength, zero-strength dots stay visible, absent/null scores use the legacy fallback, and selecting a point preserves every fill opacity. Existing interaction/export/390px checks pass at DPR 1, 1.25 and 2; screenshots refreshed and DPR-1 inspected.

Verification recovery: uv could not fetch tooling with restricted DNS; existing cached Ruff/BasedPyright executables worked. An ad hoc API check incorrectly used Store as a context manager; corrected to explicit close. No application fix was needed for that check.
