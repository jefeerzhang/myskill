#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mem0 memory CLI for Codex agents.

Subcommands:
  add           Upload one important memory.
  search        Search relevant memories for the current task.
  list          List stored memories.
  retry-outbox  Retry local pending/failed outbox records.
"""

from __future__ import annotations

import argparse
import json
import re
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


WORKSPACE = Path(__file__).resolve().parent
OUTBOX = WORKSPACE / "memory" / "mem0_important_outbox.jsonl"
DEFAULT_MEM0_BASE_URL = "https://api.mem0.ai/v3"
ALLOWED_CATEGORIES = {"preference", "project", "decision", "lesson", "identity"}

def configure_output_encoding() -> None:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

SECRET_MARKERS = (
    "api key",
    "apikey",
    "token",
    "secret",
    "password",
    "cookie",
    "authorization",
)
SECRET_PATTERNS = (
    re.compile(r"m0-[A-Za-z0-9_-]{20,}"),
    re.compile(r"mpg-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
)

def load_env() -> None:
    load_dotenv(WORKSPACE / ".env")
    load_dotenv(WORKSPACE / ".env.local")


def looks_sensitive(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SECRET_MARKERS) or any(pattern.search(text) for pattern in SECRET_PATTERNS)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Mem0Client:
    def __init__(self, api_key: str, base_url: str = DEFAULT_MEM0_BASE_URL, timeout: int = 30):
        if not api_key:
            raise ValueError("缺少 MEM0_API_KEY。")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json",
            }
        )

    def _post(self, path: str, payload: dict[str, Any], *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        response = self.session.post(
            f"{self.base_url}/{path.lstrip('/')}",
            json=payload,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        if not response.text.strip():
            return {}
        return response.json()

    def add(
        self,
        *,
        content: str,
        user_id: str,
        category: str,
        source: str,
        agent_id: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "messages": [{"role": "assistant", "content": content}],
            "user_id": user_id,
            "metadata": {
                "category": category,
                "source": source,
                "captured_by": "mem0_memory_cli",
            },
        }
        if agent_id:
            payload["agent_id"] = agent_id
        if run_id:
            payload["run_id"] = run_id
        return self._post("/memories/add/", payload)

    def search(
        self,
        *,
        query: str,
        user_id: str,
        top_k: int = 8,
        threshold: float = 0.1,
        agent_id: str | None = None,
        run_id: str | None = None,
        rerank: bool = False,
    ) -> dict[str, Any]:
        filters: dict[str, Any]
        parts: list[dict[str, Any]] = [{"user_id": user_id}]
        if agent_id:
            parts.append({"agent_id": agent_id})
        if run_id:
            parts.append({"run_id": run_id})
        filters = {"AND": parts} if len(parts) > 1 else parts[0]
        payload = {
            "query": query,
            "filters": filters,
            "top_k": top_k,
            "threshold": threshold,
            "rerank": rerank,
        }
        return self._post("/memories/search/", payload)

    def list_memories(
        self,
        *,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        agent_id: str | None = None,
    ) -> dict[str, Any]:
        parts: list[dict[str, Any]] = [{"user_id": user_id}]
        if agent_id:
            parts.append({"agent_id": agent_id})
        filters: dict[str, Any] = {"AND": parts} if len(parts) > 1 else parts[0]
        return self._post(
            "/memories/",
            {"filters": filters},
            params={"page": page, "page_size": page_size},
        )


def append_outbox(record: dict[str, Any]) -> Path:
    OUTBOX.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOX.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return OUTBOX


def outbox_record(
    *,
    content: str,
    category: str,
    source: str,
    remote_status: str,
    approved: bool = False,
    remote_error: str | None = None,
) -> dict[str, Any]:
    record = {
        "content": content.strip(),
        "category": category,
        "source": source,
        "created_at": now_iso(),
        "remote_status": remote_status,
        "remote_provider": "mem0",
        "approved": approved,
    }
    if remote_error:
        record["remote_error"] = remote_error
    return record


def load_client(args: argparse.Namespace) -> Mem0Client:
    load_env()
    api_key = os.environ.get("MEM0_API_KEY", "")
    return Mem0Client(api_key=api_key, base_url=args.base_url, timeout=args.timeout)


def print_search_results(data: dict[str, Any]) -> None:
    results = data.get("results", []) or []
    if not results:
        print("未召回相关 Mem0 记忆。")
        return
    for idx, item in enumerate(results, 1):
        memory = item.get("memory") or item.get("content") or ""
        score = item.get("score")
        score_text = f" score={score:.3f}" if isinstance(score, (int, float)) else ""
        print(f"{idx}. {memory}{score_text}")


def cmd_add(args: argparse.Namespace) -> int:
    content = args.content.strip()
    if not content:
        print("错误：content 不能为空。")
        return 2
    if looks_sensitive(content) and not args.allow_sensitive:
        print("已拒绝：内容疑似包含密钥、token、cookie 或密码。")
        return 3
    if not args.local_only and not args.approved:
        print("已拒绝：远程上传必须显式传入 --approved，表示用户已经批准。")
        return 4
    if args.local_only:
        append_outbox(
            outbox_record(
                content=content,
                category=args.category,
                source=args.source,
                remote_status="pending",
                approved=args.approved,
            )
        )
        print("已写入本地 Mem0 重要记忆队列；本次跳过远程上传。")
        return 0
    try:
        client = load_client(args)
        client.add(
            content=content,
            user_id=args.user_id,
            category=args.category,
            source=args.source,
            agent_id=args.agent_id,
            run_id=args.run_id,
        )
    except Exception as exc:
        status = "pending" if str(exc) == "local-only" else "failed"
        append_outbox(
            outbox_record(
                content=content,
                category=args.category,
                source=args.source,
                remote_status=status,
                approved=args.approved,
                remote_error=None if status == "pending" else str(exc),
            )
        )
        print("Mem0 远程上传失败，已写入本地重试队列。")
        return 1
    append_outbox(
        outbox_record(
            content=content,
            category=args.category,
            source=args.source,
            remote_status="uploaded",
            approved=args.approved,
        )
    )
    print("已上传到 Mem0，并记录本地审计队列。")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    client = load_client(args)
    data = client.search(
        query=args.query,
        user_id=args.user_id,
        top_k=args.top_k,
        threshold=args.threshold,
        agent_id=args.agent_id,
        run_id=args.run_id,
        rerank=args.rerank,
    )
    print_search_results(data)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    client = load_client(args)
    data = client.list_memories(
        user_id=args.user_id,
        page=args.page,
        page_size=args.page_size,
        agent_id=args.agent_id,
    )
    for idx, item in enumerate(data.get("results", []) or [], 1):
        memory = item.get("memory") or item.get("content") or ""
        print(f"{idx}. {memory}")
    return 0


def cmd_retry_outbox(args: argparse.Namespace) -> int:
    if not OUTBOX.exists():
        print("没有本地 Mem0 outbox。")
        return 0
    client = load_client(args)
    records: list[dict[str, Any]] = []
    for line in OUTBOX.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))

    retried = 0
    failed = 0
    for record in records:
        if record.get("remote_status") == "uploaded":
            continue
        content = record.get("content", "")
        if not content or looks_sensitive(content):
            continue
        if not record.get("approved"):
            continue
        try:
            client.add(
                content=content,
                user_id=args.user_id,
                category=record.get("category", "project"),
                source=record.get("source", "codex-main-agent"),
                agent_id=args.agent_id,
                run_id=args.run_id,
            )
            record["remote_status"] = "uploaded"
            record["retried_at"] = now_iso()
            record.pop("remote_error", None)
            retried += 1
        except Exception as exc:
            record["remote_status"] = "failed"
            record["remote_error"] = str(exc)
            record["retried_at"] = now_iso()
            failed += 1

    OUTBOX.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    print(f"重试完成：成功 {retried} 条，失败 {failed} 条。")
    return 0 if failed == 0 else 1


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--user-id", default=os.environ.get("MEM0_USER_ID", "jefeer"))
    parser.add_argument("--agent-id", default=os.environ.get("MEM0_AGENT_ID"))
    parser.add_argument("--run-id", default=os.environ.get("MEM0_RUN_ID"))
    parser.add_argument("--base-url", default=os.environ.get("MEM0_BASE_URL", DEFAULT_MEM0_BASE_URL))
    parser.add_argument("--timeout", type=int, default=30)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Mem0 memory CLI for Codex agents.")
    sub = parser.add_subparsers(dest="command", required=True)

    add_parser = sub.add_parser("add", help="Upload one important memory.")
    add_common(add_parser)
    add_parser.add_argument("--content", required=True)
    add_parser.add_argument("--category", default="project", choices=sorted(ALLOWED_CATEGORIES))
    add_parser.add_argument("--source", default="codex-main-agent")
    add_parser.add_argument("--local-only", action="store_true")
    add_parser.add_argument("--approved", action="store_true")
    add_parser.add_argument("--allow-sensitive", action="store_true")
    add_parser.set_defaults(func=cmd_add)

    search_parser = sub.add_parser("search", help="Search relevant memories.")
    add_common(search_parser)
    search_parser.add_argument("--query", required=True)
    search_parser.add_argument("--top-k", type=int, default=8)
    search_parser.add_argument("--threshold", type=float, default=0.1)
    search_parser.add_argument("--rerank", action="store_true")
    search_parser.set_defaults(func=cmd_search)

    list_parser = sub.add_parser("list", help="List memories.")
    add_common(list_parser)
    list_parser.add_argument("--page", type=int, default=1)
    list_parser.add_argument("--page-size", type=int, default=20)
    list_parser.set_defaults(func=cmd_list)

    retry_parser = sub.add_parser("retry-outbox", help="Retry pending/failed outbox memories.")
    add_common(retry_parser)
    retry_parser.set_defaults(func=cmd_retry_outbox)

    return parser


def main() -> int:
    configure_output_encoding()
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())




