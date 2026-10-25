# White conversation library with aligned metadata

- Date: 2026-10-25
- Status: accepted and implemented
- Authority: Zayan requested the white theme and conversation-list layout from the supplied [Behance recruiter-dashboard reference](https://www.behance.net/gallery/256334515/dashbord-rekrutera), allowing date/time and model columns.

## Decision

Use a warm off-white canvas, white panels, restrained borders and compact conversation rows. Align conversation identity, last-updated date/time and observed model information into columns. Keep each entire row a keyboard-accessible button opening the existing reader. At narrow widths, stack metadata beneath the conversation rather than forcing the desktop columns.

Model metadata comes from captured record/message fields. Show a blue tag for a captured model and a red Unknown tag when none was captured. Multiple distinct captured models have a count and full-name tooltip; do not infer missing models from a source app or current workspace default. The date column explicitly represents the existing updated timestamp, rendered in local browser time.

Keep original source records, local annotations, search/filter behavior, incomplete-capture tooltips, reader model tags, compact sync status and existing assistant handoff. The reference informs presentation; no external artwork or recruiter-specific behavior is incorporated. This replaces the previous graphite visual treatment, not compatibility command or storage identities.

## Verification

See [white-theme checks](../verification/white-conversation-library.md).

## User refinements — October 25

Zayan subsequently requested no outer list card, less vertical row spacing, pure black conversation titles and no circled source initials. The current list is unboxed with compact rows (58px minimum, 9px vertical padding), black titles including hover/selection, and source names retained only in secondary text. Metadata columns and responsive stacking remain.

## Orange accent refinement — October 25

Zayan rejected the green cast and supplied an orange reference. The current palette uses neutral white/gray surfaces with the reference's sampled orange (#ec6631) for brand and active accents, with a darker orange for readable text. Green sync/local-status dots, red errors/unknown models and blue captured-model tags retain their previously requested semantic meanings. Pure-black conversation titles remain unchanged.

## Main font selection — October 25 (implementation deferred)

Zayan explicitly selected **IBM Plex Sans** as ChatGrep’s main font and instructed: “don't implement it now.” This supersedes the earlier Aeonik request. The current font stack remains unchanged; do not download fonts, change CSS or rebuild assets solely from this recorded selection. Resume font integration only when requested. Source: Codex `01a17120-0b72-7073-9847-ae25e24d509f`.

## App icon selection — October 25 (subsequently implemented)

Zayan selected the supplied black lowercase “g” mark, whose upper counter contains a speech-bubble shape, as the future ChatGrep icon. The exact original reference is preserved privately at `workspace/chief_of_staff/reference/Design/2026-10-25-chatgrep-icon-reference.png`. This replaces the current icon direction only when implementation is resumed. Explicit instruction: later, just note it; do not change icons, generate variants or rebuild assets now. Source: Codex `01a17120-0b72-7073-9847-ae25e24d509f`.

Zayan subsequently instructed “change the icon to this now”, authorizing implementation. The sidebar now uses the exact supplied raster mark, framed with CSS to remove its large surrounding canvas from the visible icon area. The original reference remains preserved. The IBM Plex Sans change remains deferred.

## Reduced label clutter — October 25

Zayan requested removal of the subtitle beneath ChatGrep, the conversation-page header tagline and the Library navigation eyebrow. App-controlled labels no longer use uppercase text transforms, and the empty-reader eyebrow uses sentence case. Captured message text, source/model names and literal filenames retain their original spelling.
