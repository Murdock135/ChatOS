# v1.1 Behance-informed palette refinement

Date: 2026-11-06. Status: implemented; user visual review pending.

[Selected palette](palette.svg) · [Contrast measurements](contrast.json) · [Reference image identity receipts](reference-receipts.json) · [Observed sources and adaptations](../../REFERENCES.md)

## What changed

The shared tokens now use graphite surfaces and softened mint interaction states, with lilac secondary identity and restrained warm status colors. Panel edge highlights and selected rows follow the same visual direction. Home's architectural structure, application workflows, source data and all destinations are retained. The chosen hex values are implementation decisions, not claimed samples from Behance.

## Verification and limits

- Three source images were downloaded from Behance's public CDN and inspected directly using the image viewer. Gallery page opens returned HTTP 403; the browser access host was unavailable. Native Chrome observation then failed screen capture. Search descriptions were used only for metadata.
- Astro check/build and the existing Node browser regression passed. One existing `beforeunload.returnValue` hint remains.
- Current token pairs were measured using the standard sRGB luminance contrast calculation; see the JSON. These selected pair measurements are not a full accessibility audit.
- The earlier v1 screenshots remain available in their original evidence directory and immutable archive. They depict v1, not this new palette. No refreshed app screenshots or responsive-browser pass are claimed for v1.1 because the available visual automation failed. This refinement changes tokens, color/edge treatments and a small corner-radius adjustment, not layouts or actions. The current palette is retained as a code-native SVG instead of presenting old screenshots as current evidence.
- Prior v1 archive integrity is checked separately and must remain unchanged. The new v1.1 snapshot retains this guide revision, public sources, reference observations/receipts, palette, and contrast measurements. It contains no reference artwork, personal workspace data or account credentials.
