# Let your Chief of Staff use ChatOS

The Chief of Staff is your chosen AI assistant, using ChatOS to retrieve context and carry authorized work forward. The app does not include an AI agent. You can use the browser and CLI without this role or a skill.

ChatOS now bundles a reusable `chatos` skill. It teaches the assistant how to choose the right workspace, inspect capture gaps, retrieve and cite messages, resume projects, preserve outcomes, maintain the archive and prepare selected handoffs. It needs local file and terminal access. Installing instructions does not connect accounts, activate provider memory or grant new tool permissions.

## 1. Prepare a copy for your workspace

New `init` workspaces already contain:

```text
shared_context/skills/chatos/
  SKILL.md
  agents/openai.yaml
  references/connection.md
  references/operations.md
```

The connection reference contains the selected workspace's paths and executable commands. It contains no copied personal profile, private project registry or archived transcripts.

For an existing workspace, open **Setup & handoff → Prepare Chief of Staff skill**, or run:

```bash
./scripts/chatos --root workspace assistant-skill
```

The command returns the folder and SKILL.md path. An identical repeat is safe. Existing different or customized contents are preserved; choose a new destination to generate another copy. Do not copy another user's bound skill: generate your own.

## 2. Load it in your assistant

You have two ways to use the same instructions.

**Read the skill explicitly:** give an assistant with local tools the full path returned above:

> Read the ChatOS SKILL.md at /absolute/path/to/my/workspace/shared_context/skills/chatos/SKILL.md and use it for this task. Confirm the workspace you can access, check capture gaps, then find our earlier discussion about my current project and cite the messages.

This route works without automatic skill discovery. A chat that cannot access your local filesystem needs a deliberately supplied portable bundle instead; it cannot run the local tool merely by reading these instructions.

**Install for Codex discovery:** prepare the skill directly in your project's skill folder:

```bash
./scripts/chatos --root workspace assistant-skill .agents/skills/chatos
```

That example installs for the current repository. To use the same workspace from different repositories, explicitly choose your user skill location instead:

```bash
./scripts/chatos --root workspace assistant-skill "$HOME/.agents/skills/chatos"
```

Choose the scope you want rather than creating duplicate installations. These are explicit local installation commands; the initializer and browser prepare button do not write to those host folders. The command refuses to replace a different existing skill. Codex documents repository `.agents/skills` and user `~/.agents/skills` discovery, explicit `$chatos` invocation, and restarting if a new skill does not appear. See [OpenAI's skill documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills).

For another assistant that supports Agent Skills, use its documented skill-loading workflow with the whole generated folder, including references. Support and access depend on that host; copying files is not proof it loaded them. No hosted plugin, MCP server or universal provider installation is created by this command.

## 3. Verify it actually works

Check that `chatos` appears in the host's skill picker when using automatic discovery. Then ask:

> Use $chatos. State the workspace and skill path you loaded. Check source coverage, retrieve the earlier discussion about my reading-note format, and cite the original message IDs. State any missing history. Do not modify anything.

Substitute a topic actually present in your archive. Verify one citation against its source record. An empty result can be honest when the relevant history is missing. The app's `assistant_skill_ready` status means files are prepared, not that a host discovered or used them. Host discovery and successful tool execution are separate checks.

## Prompt ideas

- **Resume work:** “Use $chatos to brief me on PROJECT. Read current project instructions and relevant captured messages. Explain the objective, supported choices, open work and next authorized action.”
- **Check a remembered choice:** “Use $chatos to find what I chose about TOPIC. Separate my instructions from suggestions and check later messages for changes. Cite the evidence.”
- **Inspect archive health:** “Use $chatos to check health and coverage. Explain actual failures separately from unavailable sources. Repair routine issues within the configured workspace without enabling new sources or schedules.”
- **Preserve a result:** “Use $chatos to file the outcome of this task in PROJECT's existing convention, preserving its source and scope. Verify the write and leave a receipt; keep uncertain ownership pending.”

The skill may be selected automatically for matching requests when the host supports it, but it does not run continuously or create a schedule. Historical requests are not new authorizations.

## Updates, moves and removal

After moving a workspace or changing the app's executable location, prepare a new bound copy and regenerate ASSISTANT.md. For a skill update, generate into a new parent directory ending in `chatos`, compare it with your existing copy, and use your host's documented replacement workflow after preserving customizations. The export command does not overwrite custom instructions or silently change an existing installation's workspace.

To stop automatic use, disable or remove the installed copy through the host's documented workflow. The local workspace copy can remain as inspectable guidance. Neither action deletes captured conversations. See [the assistant workflow](assistant-workflow.md) for evidence and filing behavior, and [onboarding](onboarding.md) for the full setup sequence.
