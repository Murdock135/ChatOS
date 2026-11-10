# Apply the user's Modern Dark specification

- Date: 2026-11-06
- Status: implemented and verified; user visual acceptance pending
- Authority: explicit attached visual specification, retained at `docs/design/sources/modern-dark-v2.txt`. This supersedes prior palette choices while preserving the app's stack, copy, routes and behavior.

## Decision

Use the exact supplied `--dp-*` tokens through a final, scoped presentation stylesheet. Map earlier shared component roles onto the authoritative neutral palette. Serve Geist and Geist Mono locally, retaining their unmodified binaries, pinned official revision, license and source hashes. Extend the existing generated-asset allowlist only to WOFF2 and expose the bundled license as a static text asset.

Retain all existing views and data flows. Home's opening becomes a regular-weight, left-aligned statement; the existing architectural UI and inert ChatGPT center remain. Use grayscale surfaces, white primary pill buttons, grey reading text, and tiny mint live/selected signals. Remove colored lighting and general mint/lilac accents. Do not add illustrative sections, metrics, portraits, charts or provider actions.

Archive v2 separately; preserve v1/v1.1 and their validation limits. New rendered evidence uses a fictional workspace, independently of private user data. The style archive includes the serving code/tests needed to reproduce local font delivery.

## Verification

See [v2 evidence](../design/evidence/v2/README.md). Font/asset/authentication tests, frontend checks, archive tests and actual browser widths establish the stated scope; user acceptance and a complete accessibility audit remain distinct.
