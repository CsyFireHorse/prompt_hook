from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_payload() -> dict[str, Any]:
    raw_bytes = sys.stdin.buffer.read()
    if not raw_bytes:
        return {}

    try:
        raw_text = raw_bytes.decode("utf-8-sig").strip()
    except UnicodeDecodeError:
        raw_text = raw_bytes.decode("utf-8", errors="replace").strip()

    if not raw_text:
        return {}

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"raw_stdin": raw_text}

    if isinstance(data, dict):
        return data
    return {"payload": data}


def _to_native_path(raw: str) -> Path:
    text = raw.strip()
    if sys.platform == "win32":
        match = re.match(r"^/([a-zA-Z]):/(.*)$", text)
        if match:
            drive = match.group(1).upper()
            tail = match.group(2).replace("/", "\\")
            if tail:
                return Path(f"{drive}:\\{tail}")
            return Path(f"{drive}:\\")
    return Path(text).expanduser()


def _log_dir(payload: dict[str, Any], log_target: str) -> Path:
    if log_target == "user":
        return Path.home() / ".prompt-hook" / "logs"

    roots = payload.get("workspace_roots")
    if isinstance(roots, list) and roots:
        root = roots[0]
        if isinstance(root, str) and root.strip():
            return _to_native_path(root) / "logs"
    return Path.home() / ".prompt-hook" / "logs"


def _append_record(payload: dict[str, Any], log_target: str) -> None:
    log_dir = _log_dir(payload, log_target)
    log_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
    }
    log_path = log_dir / "cursor_prompts.jsonl"
    with log_path.open("a", encoding="utf-8") as fp:
        fp.write(json.dumps(record, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--log", choices=["project", "user"], default="project")
    args, _unknown = parser.parse_known_args()
    try:
        payload = _read_payload()
        _append_record(payload, args.log)
    except Exception as exc:  # noqa: BLE001
        print(f"prompt-hook failed: {exc}", file=sys.stderr)
    finally:
        print(json.dumps({"continue": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

