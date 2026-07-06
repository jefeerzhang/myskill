#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append a local Mem0 memory suggestion without uploading it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ALLOWED_CATEGORIES = {"preference", "project", "decision", "lesson", "identity"}
SECRET_MARKERS = (
    "api key",
    "apikey",
    "token",
    "secret",
    "password",
    "cookie",
    "authorization",
    "密码",
    "密钥",
)
SECRET_PATTERNS = (
    re.compile(r"m0-[A-Za-z0-9_-]{20,}"),
    re.compile(r"mpg-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
)

def configure_output_encoding() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass


def workspace() -> Path:
    return Path(os.environ.get("MEM0_WORKSPACE", os.getcwd())).resolve()


def suggestions_path() -> Path:
    return workspace() / "memory" / "mem0_memory_suggestions.jsonl"


def looks_sensitive(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SECRET_MARKERS) or any(pattern.search(text) for pattern in SECRET_PATTERNS)


def suggestion_id(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def load_records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    records = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def main() -> int:
    configure_output_encoding()
    parser = argparse.ArgumentParser(description="Create a local Mem0 memory suggestion.")
    parser.add_argument("--content", required=True, help="Candidate memory content.")
    parser.add_argument("--category", required=True, choices=sorted(ALLOWED_CATEGORIES))
    parser.add_argument("--reason", required=True, help="Why this memory is worth keeping.")
    parser.add_argument("--source", default="mem0-memory-flow-skill")
    args = parser.parse_args()

    if looks_sensitive(args.content):
        print("拒绝写入候选：内容疑似包含密钥、token、密码等敏感信息。", file=sys.stderr)
        return 2

    path = suggestions_path()
    sid = suggestion_id(args.content)
    records = load_records(path)
    for record in records:
        if record.get("id") == sid:
            print(f"候选已存在：{sid}")
            return 0

    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": sid,
        "content": args.content,
        "category": args.category,
        "reason": args.reason,
        "status": "suggested",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": args.source,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"已创建候选：{sid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


