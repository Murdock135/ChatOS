# Interface design and provenance

Read the [active style guide](STYLEGUIDE.md) before UI work. Its shared CSS tokens and component rules define the current design; historical sources and screenshots remain separate.

- [v2 supplied specification](sources/modern-dark-v2.txt): current authoritative design source.
- [v2 evidence](evidence/v2/README.md): actual-width screenshots, font delivery and validation.
- [v2 archive](archive/v2/manifest.json): current immutable design snapshot.
- [Behance reference observations](REFERENCES.md): inspected sources, access limits, attribution, and concrete adaptations.
- [v1.1 evidence](evidence/v1.1/README.md): prior palette and its validation limits.
- [v1.1 archive](archive/v1.1/manifest.json): immutable refinement snapshot.
- [Change log](CHANGELOG.md): requests, rationale, status, and version transitions.
- [Observed baseline](archive/2026-11-06-pre-unification/README.md): source-only capture of the mixed interface before app-wide unification. No prior style guide is implied.
- [v1 evidence](evidence/v1/README.md): fictional-data screenshots and verification scope.
- [v1 archive](archive/v1/manifest.json): immutable guide, public frontend sources, evidence and file hashes.
- [Design decision](../adr/0011-interface-design-system.md): scope and authority.

Create a new archive after material changes:

```bash
python3 scripts/archive_design.py --version v2.1 --source-ref 'conversation-or-decision-reference' --summary 'Describe the concrete change'
python3 scripts/archive_design.py --check v2.1
```

The tool uses a fixed allowlist of public frontend/design sources and the matching evidence folder. It excludes `workspace/`, secrets, runtime data, dependency folders, and Git internals. Existing snapshot directories are never overwritten. A snapshot records an implementation at a point in time; user review and validation limits are explicit in its guide/evidence.
