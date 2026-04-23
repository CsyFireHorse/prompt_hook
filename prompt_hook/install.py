from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

HOOK_ALIAS_TO_KEY = {
    "before": "beforeSubmitPrompt",
    "after": "afterAgentResponse",
}
UNINSTALL_HOOK_KEYS = ("beforeSubmitPrompt", "afterAgentResponse")


def _hooks_path(scope: str, cwd: Path) -> Path:
    if scope == "project":
        return cwd / ".cursor" / "hooks.json"
    return Path.home() / ".cursor" / "hooks.json"


def _project_command(project_dir: Path, hook_name: str) -> str:
    return f'uv run --project "{project_dir}" prompt-hook log --log project --hook {hook_name}'


def _user_command(hook_name: str) -> str:
    return f"uv tool run --from prompt-hook prompt-hook log --log user --hook {hook_name}"


def _has_pyproject(project_dir: Path) -> bool:
    return (project_dir / "pyproject.toml").exists()


def _load_hooks_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"version": 1, "hooks": {}}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError(f"Expected object in {path}")
    data.setdefault("version", 1)
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        data["hooks"] = {}
    return data


def _write_hooks_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _parse_hooks(raw: str) -> list[str]:
    tokens = [part.strip().lower() for part in raw.split(",")]
    cleaned = [token for token in tokens if token]
    if not cleaned:
        raise argparse.ArgumentTypeError(
            "Invalid --hooks value: expected a comma-separated list from 'before,after'"
        )

    invalid = [token for token in cleaned if token not in HOOK_ALIAS_TO_KEY]
    if invalid:
        allowed = ",".join(HOOK_ALIAS_TO_KEY.keys())
        bad = ",".join(invalid)
        raise argparse.ArgumentTypeError(f"Invalid --hooks token(s): {bad}. Allowed: {allowed}")

    # Keep order but de-duplicate.
    return list(dict.fromkeys(cleaned))


def _command_for_hook(scope: str, project_dir: Path, hook_name: str) -> str:
    if scope == "project":
        # When installer runs from uv tool site-packages, there is no project file.
        # Fallback to uv tool runner to avoid broken hooks command.
        return _project_command(project_dir, hook_name) if _has_pyproject(project_dir) else _user_command(hook_name)
    return _user_command(hook_name)


def _install(
    scope: str, cwd: Path, project_dir: Path, selected_hooks: list[str]
) -> tuple[Path, dict[str, str], list[str]]:
    hooks_path = _hooks_path(scope, cwd)
    data = _load_hooks_json(hooks_path)
    hooks = data.setdefault("hooks", {})

    selected_hook_keys = [HOOK_ALIAS_TO_KEY[name] for name in selected_hooks]
    installed_commands: dict[str, str] = {}
    for hook_name, hook_key in zip(selected_hooks, selected_hook_keys, strict=True):
        command = _command_for_hook(scope, project_dir, hook_name)
        hooks[hook_key] = [{"command": command}]
        installed_commands[hook_key] = command

    _write_hooks_json(hooks_path, data)
    return hooks_path, installed_commands, selected_hook_keys


def _uninstall(scope: str, cwd: Path) -> tuple[Path, dict[str, bool]]:
    hooks_path = _hooks_path(scope, cwd)
    data = _load_hooks_json(hooks_path)
    hooks = data.setdefault("hooks", {})

    removed = {hook_key: hook_key in hooks for hook_key in UNINSTALL_HOOK_KEYS}
    if any(removed.values()):
        for hook_key in UNINSTALL_HOOK_KEYS:
            hooks.pop(hook_key, None)
        _write_hooks_json(hooks_path, data)
    return hooks_path, removed


def add_install_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument(
        "--hooks",
        type=_parse_hooks,
        default=["before"],
        help="Comma-separated hook aliases to install. Supported: before,after. Default: before",
    )
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Absolute path to prompt-hook project. Defaults to this package root.",
    )


def add_uninstall_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--scope", choices=["project", "user"], default="project")


def run_install(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    default_project_dir = Path(__file__).resolve().parents[1]
    project_dir = Path(args.project_dir).expanduser().resolve() if args.project_dir else default_project_dir

    hooks_path, installed_commands, installed_hook_keys = _install(args.scope, cwd, project_dir, args.hooks)
    print(f"scope={args.scope}")
    print(f"hooks_json={hooks_path}")
    print(f"selected_hooks={','.join(args.hooks)}")
    print(f"installed_hook_keys={','.join(installed_hook_keys)}")
    for hook_key in installed_hook_keys:
        print(f"command_{hook_key}={installed_commands[hook_key]}")
    return 0


def run_uninstall(args: argparse.Namespace) -> int:
    cwd = Path.cwd()
    hooks_path, removed = _uninstall(args.scope, cwd)
    print(f"scope={args.scope}")
    print(f"hooks_json={hooks_path}")
    print(f"removed_beforeSubmitPrompt={str(removed['beforeSubmitPrompt']).lower()}")
    print(f"removed_afterAgentResponse={str(removed['afterAgentResponse']).lower()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Install or uninstall prompt-hook in Cursor hooks.json")
    parser.add_argument("--uninstall", action="store_true")
    add_install_arguments(parser)
    args = parser.parse_args()
    if args.uninstall:
        return run_uninstall(args)
    return run_install(args)


if __name__ == "__main__":
    raise SystemExit(main())

