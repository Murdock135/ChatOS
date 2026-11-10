# smriti UI prototype

A standalone, browser-local UI built from the supplied app brief. All 24 conversations, projects, snapshots, paths, and operation results are fictional. The prototype does not use the existing application's workspace or backend.

## Run

```sh
python3 -m http.server 4327 --bind 127.0.0.1 --directory outputs/smriti-ui-demo/dist
```

Open http://127.0.0.1:4327. No installation or build step is needed. Fonts use Google Fonts with local system fallbacks.

## Try

- Search transcript text and local notes; filter sources/projects; change sort and pagination.
- Open conversations, inspect provenance and partial capture gaps, edit local notes/title/project, archive and restore. These changes persist in browser localStorage.
- Explore the fixed-position topic map, pan, zoom, filter topics, select records, export SVG/JSON, and download a Markdown assistant handoff.
- Review/accept/retire sample context, inspect fictional snapshots, and paste a context draft for review.
- Validate JSON/ZIP file structure in the browser. No file is uploaded; no real import occurs.
- Download fictional JSON collections/backups, with separate annotations and optional accepted context.
- Preview sync success/failure, missing model, empty library, and no-result states. Settings exposes the demo scenarios and reset action.

Map positions are predefined. There is no clustering, embedding, indexing, model inference, real source capture, account connection, or background processing. Sync, health, model download, and indexing states are explicitly simulated. Exported JSON includes representative sample excerpts and is not a production capture or integrity-certified bundle.
