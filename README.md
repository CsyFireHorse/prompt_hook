# prompt-hook

`prompt-hook` is a standalone package for Cursor `beforeSubmitPrompt` logging.

## Install the package first

### Option A: Install as a uv tool (recommended)

From local directory (current repo stage):

```bash
uv tool install --from "c:\Project\tools\toybakup\logInstaller" prompt-hook
```

If published later:

```bash
uv tool install prompt-hook
```

### Option B: Run directly from project (no global install)

```bash
uv run --project logInstaller prompt-hook --help
uv run --project logInstaller prompt-hook-install --help
```

## Then install the hook

After package/tool is available, install Cursor hook:

### Install to current project

Run in your target project root:

```bash
prompt-hook-install --scope project
```

This writes:

- `<project>/.cursor/hooks.json`
- command:
  - preferred: `uv run --project "<logInstaller_absolute_path>" prompt-hook --log project`
  - fallback (when installer is executed from uv tool): `uv tool run --from prompt-hook prompt-hook --log user`

### Install to user scope

```bash
prompt-hook-install --scope user
```

This writes:

- `~/.cursor/hooks.json`
- command: `uv tool run --from prompt-hook prompt-hook --log user`

### Uninstall

```bash
prompt-hook-install --scope project --uninstall
prompt-hook-install --scope user --uninstall
```

## Verify

Send a message in Cursor, then check:

- project mode (`--log project`): `<workspace>/logs/cursor_prompts.jsonl`
- user mode (`--log user`): `~/.prompt-hook/logs/cursor_prompts.jsonl`

## Log target parameter

`prompt-hook` supports:

- `--log project`: resolve log path from `workspace_roots[0]` and write to workspace `logs/`
- `--log user`: always write to user path `~/.prompt-hook/logs/`

