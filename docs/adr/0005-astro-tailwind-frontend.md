# 0005 — Astro and Tailwind frontend

Date: 2026-10-24. Status: adopted by explicit user request.

The user requested Astro with Tailwind CSS after reviewing the interface revisions. Build the app from Astro layout and page components with Tailwind's Vite integration. Keep static deployment and the existing authenticated Python API. Node is a development/build dependency, not a runtime requirement for users.

Navigation, search composer, conversations, map, context, health and setup have separate source components. The search composer includes its options inside the rounded bar and a sentence above it. Native disclosure and dialog behavior remains available. Shared CSS is retained in a component layer, with Tailwind utilities available for component styling. This migration does not claim every legacy rule has been replaced by a utility.

Compile into a separate frontend/dist directory, then publish only generated public files into src/chatos/static. Private workspace files are never build inputs. The server exposes generated CSS/JS only through a constrained asset path; the Python wheel bundles those files. Existing source/message preservation and access checks remain required.
