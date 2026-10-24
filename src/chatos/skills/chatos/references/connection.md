# Select a ChatOS workspace

This is the unbound copy shipped with the app. Ask the user for the workspace they want to use, or use the explicit CHATOS_WORKSPACE environment value after verifying its chatos.json. Do not assume a home directory, profile, project registry or account.

Use the installed `chatos --root /absolute/workspace` command, or an explicitly identified checkout's `scripts/chatos --root /absolute/workspace`. Check `--help` before invoking an unfamiliar installed version. The host needs local file and terminal access. Without that access, request a deliberately selected portable bundle and disclose that live maintenance is unavailable.

The app's `assistant-skill` command generates a copy with this reference bound to the chosen workspace. It does not activate the skill in an assistant automatically.
