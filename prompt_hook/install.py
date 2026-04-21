from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _hooks_path(scope: str, cwd: Path) -> Path:
    if scope == "project":
        return cwd / ".cursor" / "hooks.json"
    return Path.home() / ".cursor" / "hooks.json"


def _project_command(project_dir: Path) -> str:
    return f'uv run --project "{project_dir}" prompt-hook --log project'


def _user_command() -> str:
    return "uv tool run --from prompt-hook prompt-hook --log user"


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


def _install(scope: str, cwd: Path, project_dir: Path) -> tuple[Path, str]:
    hooks_path = _hooks_path(scope, cwd)
    data = _load_hooks_json(hooks_path)
    hooks = data.setdefault("hooks", {})
    if scope == "project":
        # When installer runs from uv tool site-packages, there is no project file.
        # Fallback to uv tool runner to avoid broken hooks command.
        command = _project_command(project_dir) if _has_pyproject(project_dir) else _user_command()
    else:
        command = _user_command()
    hooks["beforeSubmitPrompt"] = [{"command": command}]
    _write_hooks_json(hooks_path, data)
    return hooks_path, command


def _uninstall(scope: str, cwd: Path) -> tuple[Path, bool]:
    hooks_path = _hooks_path(scope, cwd)
    data = _load_hooks_json(hooks_path)
    hooks = data.setdefault("hooks", {})
    removed = "beforeSubmitPrompt" in hooks
    if removed:
        hooks.pop("beforeSubmitPrompt", None)
        _write_hooks_json(hooks_path, data)
    return hooks_path, removed


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install or uninstall prompt-hook in Cursor hooks.json")
    parser.add_argument("--scope", choices=["project", "user"], default="project")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument(
        "--project-dir",
        default=None,
        help="Absolute path to logInstaller project. Defaults to this package root.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    cwd = Path.cwd()
    default_project_dir = Path(__file__).resolve().parents[1]
    project_dir = Path(args.project_dir).expanduser().resolve() if args.project_dir else default_project_dir

    if args.uninstall:
        hooks_path, removed = _uninstall(args.scope, cwd)
        print(f"scope={args.scope}")
        print(f"hooks_json={hooks_path}")
        print(f"removed_beforeSubmitPrompt={str(removed).lower()}")
        return 0

    hooks_path, command = _install(args.scope, cwd, project_dir)
    print(f"scope={args.scope}")
    print(f"hooks_json={hooks_path}")
    print(f"command={command}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

