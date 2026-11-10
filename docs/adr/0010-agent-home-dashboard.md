# Live workspace dashboard with a ChatGPT interface visualization

- Date: 2026-11-06
- Status: implemented
- Authority: Zayan requested a new homepage, supplied a dark architectural reference, and specified: “that is just for visualizing chatgpt's interfacing behavior. clicking it should not trigger any action”.

## Decision

Make Home the default entry point, retaining the conversation library and existing destinations. The Directive registry header opens/closes its file browser, with independently collapsible categories and live file readers. The Conversation pool card opens the existing conversation clustering/map view. Follow the supplied dark grid reference: a categorized directive registry on the left, a ChatGPT visualization in the center, and grounded knowledge sources plus active connectors on the right. Collapse into a single column on phones.

The ChatGPT center is a non-interactive architectural visualization. It has no click handler, task submission, execution backend, live processing claim, or model call. “Workspace online” describes the local app API, not a ChatGPT runtime connection.

Replace placeholder filenames and source descriptions with real workspace operations:

- List available instruction, memory, and skill/script source files from the known inventory and workspace-owned paths. Open the current file on selection, displaying its source, read time, and SHA-256. Do not activate or execute its contents.
- Discover registered Git repositories and Obsidian vault directories. Mount an explicitly chosen local directory after validating its `.git` or `.obsidian` marker, persist the mount in the private workspace, and browse visible text files within that root. Reject traversal and escaping symlinks; exclude hidden paths and limit previews to 2 MiB.
- Show the authenticated archive's actual conversation count and navigate to its existing searchable library.
- Run the existing workspace health check from Home.
- Connect Gmail using an explicitly supplied Google OAuth access token. Verify the account through the Gmail profile endpoint, then support inbox metadata/snippet reads and Gmail queries. Keep the token only in server memory; disconnect clears it. No sending or account changes are exposed.

Mounting a local source registers it for this app's browser; it does not grant a hosted ChatGPT session filesystem access. Gmail is shown disconnected until successful authorization. The app does not inherit the Codex/ChatGPT host's connector credentials. Tokens expire according to Google's authorization and must be supplied again after expiry or server restart; refresh-token persistence and a packaged OAuth client are outside this change.

Keep all new API operations behind the existing loopback, token, host, and origin checks. Render file and mail content as text. Emit the dashboard script as an external build asset for the server's self-only CSP.

## Verification

See [dashboard verification](../verification/agent-home-2026-11-06.md). Source and compiled browser assets are included; unrelated working-tree changes are retained.
