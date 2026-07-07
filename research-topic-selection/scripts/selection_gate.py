#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""research-topic-selection rigid gate (v1.2).

The gate validates phase deliverables and the two independent review nodes
(`scan` and `topics`). It is intentionally stricter than a simple file-exists
check: review verdicts must be tied to the current workdir, current artifacts,
the transcript hash, and closed P0 dispositions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


ENTER_ALIASES = {
    "2": "scan",
    "scan": "scan",
    "4": "scan-review",
    "scan-review": "scan-review",
    "5": "literature",
    "literature": "literature",
    "7": "topics",
    "topics": "topics",
    "final": "final",
}

SCAN_DIMS = [
    "政策扫描",
    "学术文献扫描",
    "现实实践扫描",
    "数据/材料扫描",
    "发表/申报窗口扫描",
]

REVIEW_BINDINGS = {
    "scan": ["03_五维扫描.md", "04_问题域地图.md"],
    "topics": ["07_核心缺口.md", "08_选题推荐.md"],
}

ALWAYS_INDEPENDENT = {"scan", "topics"}
DISPOSITION_STATUSES = {"已修正", "反驳成立", "不适用"}
MAX_REVIEW_ROUNDS = 3


class GateFail(Exception):
    """Expected validation failure."""


class LoopExceeded(Exception):
    """Review loop exceeded the configured maximum."""


def sha256_of(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def normpath(path: str) -> str:
    return os.path.normcase(os.path.abspath(os.path.normpath(path)))


def read_text(workdir: str, rel: str) -> str:
    path = os.path.join(workdir, rel)
    if not os.path.isfile(path):
        raise GateFail(f"缺失文件: {rel}")
    with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
        return f.read()


def load_json(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise GateFail(f"JSON 根对象必须是 object: {path}")
    return data


def require_file(workdir: str, rel: str, min_chars: int = 1) -> str:
    txt = read_text(workdir, rel)
    if len(txt.strip()) < min_chars:
        raise GateFail(f"{rel} 内容过少，至少需要 {min_chars} 个字符")
    return txt


def require_markers(workdir: str, rel: str, markers: list[str]) -> str:
    txt = require_file(workdir, rel)
    missing = [marker for marker in markers if marker not in txt]
    if missing:
        raise GateFail(f"{rel} 缺少必需段落/关键词: {', '.join(missing)}")
    return txt


def require_section_after_marker(txt: str, rel: str, marker: str, min_chars: int = 20) -> None:
    idx = txt.find(marker)
    if idx < 0:
        raise GateFail(f"{rel} 缺少必需段落: {marker}")
    tail = txt[idx + len(marker) :].strip()
    if len(tail) < min_chars:
        raise GateFail(f"{rel} 的「{marker}」段内容过少")


def count_marked_headings(txt: str, marker: str) -> int:
    pattern = re.compile(rf"(?m)^#{{1,6}}\s*{re.escape(marker)}(?:\s*\d+)?(?:\s*[:：].*)?\s*$")
    return len(pattern.findall(txt))


def extract_last_fenced_json(txt: str) -> dict[str, Any] | None:
    blocks = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", txt, flags=re.S | re.I)
    for block in reversed(blocks):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def review_had_p0(rv: dict[str, Any]) -> bool:
    if rv.get("p0"):
        return True
    history = rv.get("history", [])
    if not isinstance(history, list):
        raise GateFail("review.history 必须是数组")
    for item in history:
        if not isinstance(item, dict):
            raise GateFail("review.history 内部元素必须是 object")
        try:
            if int(item.get("p0_found", 0)) > 0 or int(item.get("p0_open", 0)) > 0:
                return True
        except (TypeError, ValueError):
            raise GateFail("review.history 的 p0_found/p0_open 必须是整数")
    return False


def expected_p0_ids(rv: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for item in rv.get("history", []):
        for p0_id in item.get("p0_ids", []) or []:
            ids.add(str(p0_id))
    for item in rv.get("p0", []) or []:
        if isinstance(item, dict) and item.get("id"):
            ids.add(str(item["id"]))
    return ids


def verify_dispositions(workdir: str, node: str, rv: dict[str, Any]) -> None:
    if not review_had_p0(rv):
        return
    disp_rel = os.path.join("review", f"dispositions_{node}.json")
    disp_path = os.path.join(workdir, disp_rel)
    if not os.path.isfile(disp_path):
        raise GateFail(f"审查节点 {node} 曾出现 P0，但缺失处置闭环: {disp_rel}")
    disp = load_json(disp_path)
    findings = disp.get("findings")
    if not isinstance(findings, list) or not findings:
        raise GateFail(f"{disp_rel} 必须包含非空 findings 数组")

    seen: set[str] = set()
    for item in findings:
        if not isinstance(item, dict):
            raise GateFail(f"{disp_rel}.findings 内部元素必须是 object")
        fid = str(item.get("id", "")).strip()
        status = item.get("status")
        decision = item.get("reviewer_decision")
        if not fid:
            raise GateFail(f"{disp_rel} 存在缺少 id 的处置项")
        seen.add(fid)
        if status not in DISPOSITION_STATUSES:
            raise GateFail(f"{disp_rel} 的 {fid} status 非法: {status}")
        if decision != "accepted":
            raise GateFail(f"{disp_rel} 的 {fid} 尚未被原审查者 accepted")
        if not str(item.get("evidence", "")).strip():
            raise GateFail(f"{disp_rel} 的 {fid} 缺少 evidence")

    missing = expected_p0_ids(rv) - seen
    if missing:
        raise GateFail(f"{disp_rel} 未覆盖历史 P0: {', '.join(sorted(missing))}")
    if rv.get("re_reviewed_dispositions") is not True:
        raise GateFail(f"审查节点 {node} 出现过 P0，review.re_reviewed_dispositions 必须为 true")


def verify_review(workdir: str, node: str) -> dict[str, Any]:
    rv_rel = os.path.join("review", f"review_{node}.json")
    rv_path = os.path.join(workdir, rv_rel)
    if not os.path.isfile(rv_path):
        raise GateFail(f"缺失审查 verdict: {rv_rel}")
    rv = load_json(rv_path)

    if rv.get("node") != node:
        raise GateFail(f"{rv_rel} node={rv.get('node')}，期望 {node}")
    if rv.get("workdir") is None:
        raise GateFail(f"{rv_rel} 缺少 workdir")
    if normpath(str(rv["workdir"])) != normpath(workdir):
        raise GateFail(f"{rv_rel} workdir 与当前目录不一致")
    if node in ALWAYS_INDEPENDENT and rv.get("reviewer_kind") != "independent":
        raise GateFail(f"审查节点 {node} 必须 reviewer_kind=independent")
    if rv.get("verdict") != "PASS":
        raise GateFail(f"审查节点 {node} verdict={rv.get('verdict')}，未 PASS")

    try:
        round_no = int(rv.get("round"))
    except (TypeError, ValueError):
        raise GateFail(f"{rv_rel} round 必须是整数")
    if round_no < 1:
        raise GateFail(f"{rv_rel} round 必须 >= 1")
    if round_no > MAX_REVIEW_ROUNDS:
        raise LoopExceeded(f"审查节点 {node} round={round_no} 超界 > {MAX_REVIEW_ROUNDS}")

    try:
        p0_open = int(rv.get("p0_open"))
    except (TypeError, ValueError):
        raise GateFail(f"{rv_rel} p0_open 必须是整数")
    if p0_open != 0:
        raise GateFail(f"审查节点 {node} p0_open={p0_open}，未闭合")
    if rv.get("p0"):
        raise GateFail(f"审查节点 {node} 当前 verdict 仍含 P0 列表，未闭合")

    reviewer = rv.get("reviewer_agent_id")
    producer = rv.get("producer_agent_id")
    if not reviewer or not producer or reviewer == producer:
        raise GateFail(f"审查节点 {node} reviewer/producer 缺失或相等（自审违规）")

    artifact_hashes = rv.get("artifact_hashes")
    if not isinstance(artifact_hashes, dict):
        raise GateFail(f"{rv_rel} artifact_hashes 必须是 object")
    for art in REVIEW_BINDINGS.get(node, []):
        ap = os.path.join(workdir, art)
        if not os.path.isfile(ap):
            raise GateFail(f"审查绑定产物缺失: {art}（node={node}）")
        if art not in artifact_hashes:
            raise GateFail(f"verdict 未绑定: {art}（node={node}）")
        actual = sha256_of(ap)
        if artifact_hashes[art] != actual:
            raise GateFail(f"hash 失配: {art}（node={node}，产物已变更，旧 verdict 失效）")

    transcript_rel = rv.get("transcript_path") or os.path.join("review", "transcripts", f"{node}_r{round_no}.md")
    transcript_path = (
        str(transcript_rel)
        if os.path.isabs(str(transcript_rel))
        else os.path.join(workdir, str(transcript_rel))
    )
    if not os.path.isfile(transcript_path):
        raise GateFail(f"缺失审查 transcript: {transcript_rel}")
    agent_output_sha256 = rv.get("agent_output_sha256")
    if not agent_output_sha256:
        raise GateFail(f"{rv_rel} 缺少 agent_output_sha256")
    if agent_output_sha256 != sha256_of(transcript_path):
        raise GateFail(f"审查 transcript hash 失配: {transcript_rel}")

    with open(transcript_path, "r", encoding="utf-8-sig", errors="ignore") as f:
        transcript_txt = f.read()
    transcript_json = extract_last_fenced_json(transcript_txt)
    if transcript_json is None:
        raise GateFail(f"{transcript_rel} 未找到 fenced JSON verdict")
    rv_without_append = {k: v for k, v in rv.items() if k not in {"agent_output_sha256", "transcript_path"}}
    for key, value in transcript_json.items():
        if rv_without_append.get(key) != value:
            raise GateFail(f"{rv_rel} 与 transcript fenced JSON 字段不一致: {key}")

    verify_dispositions(workdir, node, rv)
    return rv


def check_scan(workdir: str) -> None:
    txt = require_markers(workdir, "03_五维扫描.md", SCAN_DIMS + ["反确认偏差记录"])
    for marker in SCAN_DIMS:
        require_section_after_marker(txt, "03_五维扫描.md", marker, min_chars=20)
    require_section_after_marker(txt, "03_五维扫描.md", "反确认偏差记录", min_chars=40)


def check_map(workdir: str) -> None:
    require_markers(
        workdir,
        "04_问题域地图.md",
        ["核心现实问题", "主要学术分支", "政策/实践变化", "可用数据", "潜在研究切口", "初步风险判断"],
    )
    require_file(workdir, "04_问题域地图.md", min_chars=300)


def check_literature(workdir: str) -> None:
    require_markers(workdir, "05_文献脉络.md", ["前沿方向", "核心争论", "方法谱系"])
    require_file(workdir, "05_文献脉络.md", min_chars=200)


def check_gap(workdir: str) -> None:
    require_markers(workdir, "07_核心缺口.md", ["核心缺口", "既有研究已解释", "仍不足", "为何重要"])
    require_file(workdir, "07_核心缺口.md", min_chars=200)


def check_topics(workdir: str) -> None:
    txt = require_markers(
        workdir,
        "08_选题推荐.md",
        ["主推选题", "备选选题", "推荐判断", "最推荐推进", "主要风险", "下一步"],
    )
    if count_marked_headings(txt, "主推选题") < 3:
        raise GateFail("08_选题推荐.md 至少需要 3 个「主推选题」标题")
    if count_marked_headings(txt, "备选选题") < 2:
        raise GateFail("08_选题推荐.md 至少需要 2 个「备选选题」标题")
    require_file(workdir, "08_选题推荐.md", min_chars=350)


def check_enter(workdir: str, enter: str) -> None:
    target = ENTER_ALIASES.get(enter)
    if target is None:
        raise GateFail(f"未知 enter 目标: {enter}")

    if target == "scan":
        check_scan(workdir)
        return
    if target == "scan-review":
        check_scan(workdir)
        check_map(workdir)
        verify_review(workdir, "scan")
        return
    if target == "literature":
        check_literature(workdir)
        return
    if target == "topics":
        check_gap(workdir)
        check_topics(workdir)
        verify_review(workdir, "topics")
        return
    if target == "final":
        check_gap(workdir)
        check_topics(workdir)
        verify_review(workdir, "topics")
        return


def artifact_hash_template(workdir: str, node: str) -> dict[str, Any]:
    if node not in REVIEW_BINDINGS:
        raise GateFail(f"未知 review node: {node}")
    return {
        "node": node,
        "workdir": normpath(workdir),
        "artifact_hashes": {
            rel: sha256_of(os.path.join(workdir, rel))
            for rel in REVIEW_BINDINGS[node]
            if os.path.isfile(os.path.join(workdir, rel))
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="research-topic-selection 刚性闸门")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--enter", choices=sorted(ENTER_ALIASES.keys()))
    ap.add_argument("--hash-template", choices=sorted(REVIEW_BINDINGS.keys()))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    workdir = os.path.abspath(args.workdir)
    if not os.path.isdir(workdir):
        message = f"workdir 不存在: {workdir}"
        print(json.dumps({"ok": False, "error": message}, ensure_ascii=False) if args.json else f"FAIL: {message}")
        return 2

    try:
        if args.hash_template:
            result = artifact_hash_template(workdir, args.hash_template)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if not args.enter:
            raise GateFail("必须提供 --enter，或使用 --hash-template 生成审查 hash 模板")
        check_enter(workdir, args.enter)
    except LoopExceeded as e:
        print(
            json.dumps({"ok": False, "loop_exceeded": True, "error": str(e)}, ensure_ascii=False)
            if args.json
            else f"LOOP_EXCEEDED: {e}"
        )
        return 3
    except GateFail as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False) if args.json else f"FAIL: {e}")
        return 1
    except Exception as e:  # noqa: BLE001
        message = f"{type(e).__name__}: {e}"
        print(json.dumps({"ok": False, "error": message}, ensure_ascii=False) if args.json else f"ERROR: {message}")
        return 2

    normalized = ENTER_ALIASES[args.enter]
    print(
        json.dumps({"ok": True, "enter": args.enter, "target": normalized}, ensure_ascii=False)
        if args.json
        else f"PASS: 允许进入 {normalized}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
