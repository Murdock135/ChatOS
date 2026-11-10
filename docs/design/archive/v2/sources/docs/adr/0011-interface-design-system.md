# App-wide interface design system and immutable design archives

- Date: 2026-11-06
- Status: implemented; user visual review pending
- Authority: explicit request for a modern interface across the app, an assistant-maintained style guide, and archival provenance. Individual visual choices are delegated implementation decisions.

## Decision

Use the dark architectural dashboard as the starting identity and extend a consistent Midnight workspace palette, readable typography, spacing, controls and surfaces across all seven destinations. Preserve the supplied lowercase smriti branding. Centralize visual values in `frontend/src/styles/design-tokens.css` and presentation in `design-system.css`; retain legacy structural rules for compatibility rather than rewriting application behavior.

The central ChatGPT visualization remains inert. Files, source mounts, archive navigation, setup and health actions continue to use existing operations. The canvas reads its surface, label and topic palette from the same design tokens; clustering coordinates and source data do not change.

Maintain an active guide, a design changelog, fictional-data screenshot evidence and immutable version snapshots under `docs/design/`. Record the source request, implementation authority, review status, time, Git working-tree context, and SHA-256 hashes. Preserve an observed baseline without pretending an earlier style guide existed. Use a fixed public-source allowlist; never archive the private workspace or account credentials. Refuse to overwrite an archived version, and verify archive integrity separately from visual correctness.

Add a project instruction to consult and maintain the guide during future UI changes. Git commits are not implied by this workflow; snapshots can accurately record an uncommitted working tree.

## Verification

See [v1 evidence](../design/evidence/v1/README.md). Archive integrity checks establish retained file identity, not design quality or user acceptance.
