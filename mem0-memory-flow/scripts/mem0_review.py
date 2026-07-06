#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Review and approve Mem0 memory suggestions."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parent
SUGGESTIONS = WORKSPACE / "memory" / "mem0_memory_suggestions.jsonl"


def load_records() -> list[dict[str, Any]]:
    if not SUGGESTIONS.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in SUGGESTIONS.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def save_records(records: list[dict[str, Any]]) -> None:
    SUGGESTIONS.parent.mkdir(parents=True, exist_ok=True)
    SUGGESTIONS.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )


def cmd_list(args: argparse.Namespace) -> int:
    records = [
        record for record in load_records()
        if args.all or record.get("status") == "suggested"
    ]
    if not records:
        print("没有待确认的 Mem0 记忆建议。")
        return 0
    for record in records:
        print(f"{record.get('id')} [{record.get('category')}] {record.get('status')}")
        print(f"  内容：{record.get('content')}")
        print(f"  理由：{record.get('reason')}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    records = load_records()
    selected = {item.strip() for item in args.ids if item.strip()}
    if not selected:
        print("请提供要批准的建议 id。")
        return 2

    changed = False
    failed = 0
    for record in records:
        if str(record.get("id")) not in selected:
            continue
        if record.get("status") == "uploaded":
            continue
        command = [
            sys.executable,
            str(WORKSPACE / "mem0_memory.py"),
            "add",
            "--approved",
            "--category",
            str(record.get("category") or "project"),
            "--source",
            "mem0-review-approved",
            "--content",
            str(record.get("content") or ""),
        ]
        result = subprocess.run(command, cwd=str(WORKSPACE), capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            record["status"] = "uploaded"
            record["approved_at"] = datetime.now(timezone.utc).isoformat()
            changed = True
            print(f"已上传：{record.get('id')}")
        else:
            record["status"] = "upload_failed"
            record["error"] = result.stderr or result.stdout
            failed += 1
            changed = True
            print(f"上传失败：{record.get('id')}")

    if changed:
        save_records(records)
    return 1 if failed else 0


def cmd_reject(args: argparse.Namespace) -> int:
    records = load_records()
    selected = {item.strip() for item in args.ids if item.strip()}
    changed = False
    for record in records:
        if str(record.get("id")) in selected and record.get("status") == "suggested":
            record["status"] = "rejected"
            record["rejected_at"] = datetime.now(timezone.utc).isoformat()
            changed = True
            print(f"已拒绝：{record.get('id')}")
    if changed:
        save_records(records)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Review Mem0 memory suggestions.")
    sub = parser.add_subparsers(dest="command", required=True)

    list_parser = sub.add_parser("list", help="List pending suggestions.")
    list_parser.add_argument("--all", action="store_true", help="Include uploaded/rejected records.")
    list_parser.set_defaults(func=cmd_list)

    approve_parser = sub.add_parser("approve", help="Approve and upload suggestions by id.")
    approve_parser.add_argument("ids", nargs="+")
    approve_parser.set_defaults(func=cmd_approve)

    reject_parser = sub.add_parser("reject", help="Reject suggestions by id.")
    reject_parser.add_argument("ids", nargs="+")
    reject_parser.set_defaults(func=cmd_reject)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
