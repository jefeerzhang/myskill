#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Post-turn hook that suggests Mem0 memories without uploading them.

This hook never sends data to Mem0. It only appends local candidates to
memory/mem0_memory_suggestions.jsonl. The user must approve candidates before
anything is uploaded.
"""

from __future__ import annotations

import hashlib
import json
import re
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def find_workspace() -> Path:
    configured = os.environ.get("MEM0_WORKSPACE")
    if configured:
        return Path(configured).resolve()
    return Path.cwd().resolve()


WORKSPACE = find_workspace()
SUGGESTIONS = WORKSPACE / "memory" / "mem0_memory_suggestions.jsonl"
LOG_PATH = WORKSPACE / "memory" / "mem0_hook.log"
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

def log(message: str) -> None:
    try:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as handle:
            handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def text_from_content(content: Any) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or item.get("content") or ""))
        return "\n".join(part for part in parts if part)
    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or "")
    return str(content)


def read_payload() -> dict[str, Any]:
    try:
        raw_bytes = sys.stdin.buffer.read()
    except AttributeError:
        raw_bytes = b""
    if raw_bytes:
        raw = raw_bytes.decode("utf-8", errors="replace")
    else:
        raw = sys.stdin.read()
    if not raw.strip() and len(sys.argv) > 1:
        raw = sys.argv[-1]
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
        if isinstance(payload, str):
            nested = json.loads(payload)
            return nested if isinstance(nested, dict) else {"raw": nested}
        if isinstance(payload, dict):
            return payload
        return {"raw": payload}
    except json.JSONDecodeError:
        return {"raw": raw}

def extract_role_and_text(record: dict[str, Any]) -> tuple[str, str]:
    role = str(record.get("role") or record.get("type") or "")
    message = record.get("message")
    if isinstance(message, dict):
        role = str(message.get("role") or role)
        return role, text_from_content(message.get("content"))
    return role, text_from_content(record.get("content") or record.get("text"))


def latest_turn_from_transcript(path: str | None) -> tuple[str, str]:
    if not path:
        return "", ""
    transcript = Path(path)
    if not transcript.exists():
        return "", ""
    last_user = ""
    last_assistant = ""
    pending_user = ""
    for line in transcript.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        role, text = extract_role_and_text(record)
        if not text:
            continue
        if role == "user":
            pending_user = text
        elif role == "assistant":
            last_user = pending_user or last_user
            last_assistant = text
    return last_user, last_assistant


def latest_turn_from_messages(messages: Any) -> tuple[str, str]:
    if not isinstance(messages, list):
        return "", ""
    last_user = ""
    last_assistant = ""
    pending_user = ""
    for message in messages:
        if not isinstance(message, dict):
            continue
        role = str(message.get("role") or message.get("type") or "")
        text = text_from_content(message.get("content") or message.get("text") or message.get("message"))
        if not text:
            continue
        if role == "user":
            pending_user = text
        elif role == "assistant":
            last_user = pending_user or last_user
            last_assistant = text
    return last_user, last_assistant


def turn_from_payload(payload: dict[str, Any]) -> tuple[str, str]:
    user_text = text_from_content(
        payload.get("user")
        or payload.get("user_input")
        or payload.get("prompt")
        or payload.get("input")
        or payload.get("human")
    )
    assistant_text = text_from_content(
        payload.get("assistant")
        or payload.get("assistant_response")
        or payload.get("response")
        or payload.get("output")
        or payload.get("completion")
    )
    if user_text and assistant_text:
        return user_text, assistant_text

    message_user, message_assistant = latest_turn_from_messages(
        payload.get("messages") or payload.get("conversation")
    )
    if message_user and message_assistant:
        return message_user, message_assistant

    return latest_turn_from_transcript(
        payload.get("transcript_path") or payload.get("transcriptPath")
    )


def compact(text: str, limit: int = 260) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "..."


def sensitive(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in SECRET_MARKERS) or any(pattern.search(text) for pattern in SECRET_PATTERNS)


def candidate_from_turn(user_text: str, assistant_text: str) -> tuple[str, str, str] | None:
    combined = f"{user_text}\n{assistant_text}".lower()
    if sensitive(user_text) or sensitive(assistant_text):
        return None

    if "重要记忆" in user_text and ("我来决定" in user_text or "我来选" in user_text):
        return (
            "decision",
            "用户决定：Mem0 hook 只建议可上传的重要记忆，是否上传由用户手动批准。",
            "用户明确限定 Mem0 记忆写入权限。",
        )

    if "召回" in user_text and "手动" in user_text and "hook" in combined:
        return (
            "decision",
            "用户决定：Mem0 记忆召回保持手动，hook 只处理候选记忆建议。",
            "用户明确限定召回机制。",
        )

    explicit = any(marker in user_text for marker in ("记住", "记录", "以后", "偏好", "规则"))
    if explicit and any(marker in user_text for marker in ("必须", "不要", "应该", "偏好", "以后")):
        return (
            "preference",
            f"用户可能希望长期保留：{compact(user_text)}",
            "用户表达了稳定偏好或规则。",
        )

    if any(marker in user_text for marker in ("教训", "下次不要", "避免再次", "以后别")):
        return (
            "lesson",
            f"用户指出一条可能需要保留的教训：{compact(user_text)}",
            "用户表达了避免复发的要求。",
        )

    return None


def suggestion_id(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def existing_ids() -> set[str]:
    if not SUGGESTIONS.exists():
        return set()
    ids: set[str] = set()
    for line in SUGGESTIONS.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("id"):
            ids.add(str(record["id"]))
    return ids


def append_suggestion(category: str, content: str, reason: str) -> None:
    sid = suggestion_id(content)
    if sid in existing_ids():
        log(f"skip duplicate suggestion {sid}")
        return
    SUGGESTIONS.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "id": sid,
        "content": content,
        "category": category,
        "reason": reason,
        "status": "suggested",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": "mem0-suggest-hook",
    }
    with SUGGESTIONS.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    log(f"suggested {sid}: {content}")


def main() -> int:
    try:
        payload = read_payload()
        user_text, assistant_text = turn_from_payload(payload)
        log(f"parsed turn user_len={len(user_text)} assistant_len={len(assistant_text)}")
        candidate = candidate_from_turn(user_text, assistant_text)
        if candidate:
            append_suggestion(*candidate)
        else:
            log(f"no memory suggestion; payload_keys={','.join(sorted(payload.keys()))}")
    except Exception as exc:
        log(f"hook error: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())









