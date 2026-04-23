# prompt-hook

`prompt-hook` is a standalone package for Cursor hook logging (`beforeSubmitPrompt` and `afterAgentResponse`).

## Install the package first

### Option A: Install as a uv tool (recommended)

From local directory (current repo stage):

```bash
uv tool install --from "c:\Project\tools\prompt_hook" prompt-hook
```

If published later:

```bash
uv tool install prompt-hook
```

### Option B: Run directly from project (no global install)

```bash
uv run --project prompt-hook prompt-hook --help
python -m prompt_hook --help
```

## Then install the hook

After package/tool is available, install Cursor hook.
Recommended: prefer `uv tool run --from prompt-hook prompt-hook ...` so you do not depend on whether the script entrypoint is already on `PATH`.

### Install to current project

Run in your target project root:

```bash
uv tool run --from prompt-hook prompt-hook install --scope project
```

Default installs only `beforeSubmitPrompt`.

Install both hooks:

```bash
uv tool run --from prompt-hook prompt-hook install --scope project --hooks before,after
```

Install only `afterAgentResponse`:

```bash
uv tool run --from prompt-hook prompt-hook install --scope project --hooks after
```

This writes:

- `<project>/.cursor/hooks.json`
- hook commands include explicit marker:
  - `beforeSubmitPrompt` -> `... prompt-hook log --log project --hook before`
  - `afterAgentResponse` -> `... prompt-hook log --log project --hook after`

### Install to user scope

```bash
uv tool run --from prompt-hook prompt-hook install --scope user
```

You can also combine with `--hooks before,after` or `--hooks after`.

Recommended user-scope install for both hooks:

```bash
uv tool run --from prompt-hook prompt-hook install --scope user --hooks before,after
```

This writes:

- `~/.cursor/hooks.json`
- command pattern:
  - `beforeSubmitPrompt` -> `uv tool run --from prompt-hook prompt-hook log --log user --hook before`
  - `afterAgentResponse` -> `uv tool run --from prompt-hook prompt-hook log --log user --hook after`

### Uninstall

```bash
uv tool run --from prompt-hook prompt-hook uninstall --scope project
uv tool run --from prompt-hook prompt-hook uninstall --scope user
```

`--uninstall` always removes both `beforeSubmitPrompt` and `afterAgentResponse` if present.

## Verify

Send a message in Cursor, then check:

- project mode (`--log project`): `<workspace>/logs/cursor_prompts.jsonl`
- user mode (`--log user`): `~/.prompt-hook/logs/cursor_prompts.jsonl`
- each JSONL record now includes `"hook": "before"` or `"hook": "after"`

## Log target parameter

`prompt-hook` supports:

- `--log project`: resolve log path from `workspace_roots[0]` and write to workspace `logs/`
- `--log user`: always write to user path `~/.prompt-hook/logs/`
- `--hook before|after`: write the triggering hook name into each JSONL record

