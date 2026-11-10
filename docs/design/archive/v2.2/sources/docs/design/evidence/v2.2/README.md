# v2.2 — Transparent vector branding

Date: 2026-11-06. Source: user request to replace the bitmap logo with a vector figure that does not interfere with the background. Status: implemented; user review pending.

## Assets and provenance

The old icon SVG contained a base64-encoded PNG rather than vector geometry. Expanded navigation used the PNG directly. The new `smriti-icon.svg` contains five paths (8,638 bytes); `smriti-brand.svg` contains thirteen paths (20,569 bytes). Both use a transparent canvas and a monochrome bright foreground. There are no image elements, embedded bitmap payloads, external assets or background rectangles.

The supplied PNG remains unchanged. These are traced derivatives, not claimed original vector masters. [Receipt](vector-receipt.json) records source hash, crop/bounds, output view boxes, path counts and output hashes. The one-time conversion used foreground luminance threshold 128, tight bounds plus six pixels of transparent padding, and VTracer 0.6.15 spline tracing in a temporary environment. The reference [VTracer documentation](https://github.com/visioncortex/vtracer/blob/master/README.md) was read; the temporary tool is not an app dependency. The wordmark's existing letter shapes were traced rather than replaced by a font.

## Verification

- Astro check/build, existing Node startup/browser regression and scoped type checking passed. One existing beforeunload deprecation hint remains.
- Focused HTTP/XML tests passed for both SVG routes: vector/path elements only, no embedded raster or rectangle, valid viewBox, and the compiled page uses the SVG wordmark. Existing compiled asset tests passed.
- Real-server browser checks with a fictional workspace passed compact/expanded branding, Settings, 390px phone rendering, image loading and no script errors. Both SVGs were rendered onto a transparent canvas; all four corners had zero alpha and the artwork contained visible pixels. See [alpha results](alpha-check.json).
- Screenshots were inspected: [compact navigation](compact-navigation.png), [expanded navigation](expanded-navigation.png), [Settings](settings.png), [phone Settings](mobile-settings.png). Fictional data only; no private archive data was copied.

The original raster asset/route is retained for compatibility but is no longer the active wordmark. This change concerns branding assets and containers; no source records, navigation destinations or provider behavior changed.
