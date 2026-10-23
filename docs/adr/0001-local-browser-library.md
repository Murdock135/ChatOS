# 0001 — Local browser library with an Apple-inspired interface

Date: 2026-10-23. Status: adopted for the current installation.

## Context and decision

The user requested a dedicated chat-management interface now, alongside archive/search/assistant continuity, and said: “For the UI, I really like Apple style. you can take inspiration from dribbble or other sites btw”.

Use a local browser app over the existing workspace and Python core. Keep readable records and CLI operations available. The visual direction uses system typography, a light sidebar, blue selections, simple outline symbols, restrained borders, and a list/detail structure. This is inspiration, not a claim that the web app is a native Apple application or implements Apple's platform materials.

## Boundaries and consequences

The server listens on 127.0.0.1 with a temporary token. Import, annotation, assignment, evidence retrieval, snapshot inspection, sync, and database-backup operations share existing core behavior. Local changes preserve captured source messages. The interface has no built-in model reply service. It does not require a frontend framework or runtime dependency.

This choice does not settle public packaging, a hosted service, broad platform support, new-user setup, or source-app writeback. Those remain separate work. The Apple-style preference is recorded for this product; it does not authorize unrelated UI rewrites.

## References

- [Apple: Sidebars](https://developer.apple.com/design/human-interface-guidelines/sidebars)
- [Mari Chubina: Liquid Glass Sidebar UI](https://dribbble.com/shots/26295742-Liquid-Glass-Sidebar-UI) — secondary visual-direction reference, not copied artwork or code.
- [Library guide](../chat-library.md), [implementation](../../chatos/web.py), [checks](../../tests/test_web.py).
