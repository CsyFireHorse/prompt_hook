from __future__ import annotations

import argparse

from prompt_hook.hook import add_log_arguments, run_log
from prompt_hook.install import add_install_arguments, add_uninstall_arguments, run_install, run_uninstall


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="prompt-hook CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("log", help="Write a hook payload record to JSONL")
    add_log_arguments(log_parser)
    log_parser.set_defaults(handler=run_log)

    install_parser = subparsers.add_parser("install", help="Install Cursor hooks")
    add_install_arguments(install_parser)
    install_parser.set_defaults(handler=run_install)

    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall Cursor hooks")
    add_uninstall_arguments(uninstall_parser)
    uninstall_parser.set_defaults(handler=run_uninstall)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
