#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""selection_gate.py —— research-topic-selection 刚性推进闸门（v1.1）。

进入关键 Phase（含断点续写跳入）前必须过本闸：校验全部前置必要产物存在、非空、
schema 合法、审查 verdict 为 PASS 且经 hash 绑定（防重放 / 审后改 / 跨目录搬运）。

用法：
    python3 scripts/selection_gate.py --workdir DIR --enter {2,4,5,7,final} [--json]

退出码：
    0 = PASS（允许进入该 Phase）
    1 = FAIL（打印缺失 / 失配清单，拒绝进入）
    2 = 用法 / IO / JSON 错误
    3 = 回环越界（某审查节点 round > 3）—— 升级人类裁决，不许再自动重试

设计原则：
- 审查 verdict（review/review_<node>.json）必须绑定被审 artifact 的 sha256、
  匹配当前 workdir 与 node、与 transcript 中 fenced JSON 一致。
- reviewer 档位：选题技能 critical 节点（scan / topics）一律 independent；
  其余 subagent 即可。
- 信任边界（如实声明）：本脚本只校验字段与 hash 绑定，不提供密码学身份保证；
  蓄意编排者仍可整体伪造自洽 transcript+verdict（v1.1 级残留）。
"""
import argparse
import hashlib
import json
import os
import re
import sys

PHASES = ["2", "4", "5", "7", "final"]

# deliverable_type -> (expected_stakes, min_topics)
DELIVERABLE_MAP = {
    "期刊论文": ("high", 3),
    "课题申报": ("high", 3),
    "政策报告": ("standard", 2),
    "案例研究": ("standard", 2),
    "快速选题梳理": ("standard", 2),
}

# 五维扫描维度（schema 校验用）
SCAN_DIMS = ["政策扫描", "学术文献扫描", "现实实践扫描", "数据/材料扫描", "发表/申报窗口扫描"]

# node -> 必须绑定的 artifact 相对路径（verdict.artifact_hashes 必须含且 hash 一致）
REVIEW_BINDINGS = {
    "scan": ["03_五维扫描.md", "04_问题域地图.md"],
    "topics": ["07_核心缺口.md", "08_选题推荐.md"],
}

# critical 节点一律走 independent 审查（选题仅 scan / topics 两道硬闸）
ALWAYS_INDEPENDENT = {"scan", "topics"}

DISPOSITION_STATUSES = {"已修正", "反驳成立", "不适用"}
MAX_REVIEW_ROUNDS = 3

SAFE_SLUG = re.compile(r"^[A-Za-z0-9_-]+$")


class GateFail(Exception):
    pass


class LoopExceeded(Exception):
    pass


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def require_file(workdir, rel, must_nonempty=True):
    p = os.path.join(workdir, rel)
    if not os.path.isfile(p):
        raise GateFail(f"缺失文件: {rel}")
    if must_nonempty and os.path.getsize(p) == 0:
        raise GateFail(f"空文件: {rel}")


def require_heading(workdir, rel, marker):
    """校验产物 md 含某关键字（避免只有标题无内容）。文件缺失仍归为 GateFail（缺文件）。"""
    p = os.path.join(workdir, rel)
    if not os.path.isfile(p):
        raise GateFail(f"缺失文件: {rel}")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        txt = f.read()
    if marker not in txt:
        raise GateFail(f"{rel} 缺少必需段落: {marker}")


def verify_review(workdir, node):
    """校验 review/review_<node>.json：verdict=PASS、hash 绑定、reviewer≠producer、回合≤3。"""
    rv_path = os.path.join(workdir, "review", f"review_{node}.json")
    if not os.path.isfile(rv_path):
        raise GateFail(f"缺失审查 verdict: review/review_{node}.json")
    rv = load_json(rv_path)
    if rv.get("verdict") != "PASS":
        raise GateFail(f"审查节点 {node} verdict={rv.get('verdict')}，未 PASS")
    if rv.get("round", 1) > MAX_REVIEW_ROUNDS:
        raise LoopExceeded(f"审查节点 {node} round={rv.get('round')} 超界 >3")
    reviewer = rv.get("reviewer_agent_id")
    producer = rv.get("producer_agent_id")
    if not reviewer or not producer or reviewer == producer:
        raise GateFail(f"审查节点 {node} reviewer/producer 缺失或相等（自审违规）")
    # hash 绑定校验
    bindings = REVIEW_BINDINGS.get(node, [])
    artifact_hashes = rv.get("artifact_hashes", {})
    for art in bindings:
        ap = os.path.join(workdir, art)
        if not os.path.isfile(ap):
            raise GateFail(f"审查绑定产物缺失: {art}（node={node}）")
        if art not in artifact_hashes:
            raise GateFail(f"verdict 未绑定: {art}（node={node}）")
        if artifact_hashes[art] != sha256_of(ap):
            raise GateFail(f"hash 失配: {art}（node={node}，产物已变更，旧 verdict 失效）")
    return rv


def check_enter(workdir, phase):
    # Phase 1（三问与澄清）为起点，无需前置闸；以下为关键 BLOCKING 点
    if phase == "2":
        # 进入「初步问题域假设」需三问与澄清非空
        require_heading(workdir, "01_三问与澄清.md", "关心的问题")
        return
    if phase == "4":
        # 进入「问题域地图」需五维扫描已完成且 scan 审查 PASS
        require_file(workdir, "03_五维扫描.md")
        for d in SCAN_DIMS:
            require_heading(workdir, "03_五维扫描.md", d)
        verify_review(workdir, "scan")
        return
    if phase == "5":
        # 进入「中等深度文献脉络」需问题域地图非空
        require_file(workdir, "04_问题域地图.md")
        return
    if phase == "7":
        # 进入「核心缺口 + 选题推荐」需文献脉络非空 + topics 审查 PASS（基于地图+脉络）
        require_file(workdir, "05_文献脉络.md")
        verify_review(workdir, "topics")
        return
    if phase == "final":
        # 交付前：缺口 1-3 个 + 3+2 推荐齐全 + 信任边界声明
        require_heading(workdir, "07_核心缺口.md", "核心缺口")
        require_heading(workdir, "08_选题推荐.md", "主推选题")
        require_heading(workdir, "08_选题推荐.md", "备选选题")
        return
    raise GateFail(f"未知 enter 目标: {phase}")


def main():
    ap = argparse.ArgumentParser(description="research-topic-selection 刚性闸门")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--enter", required=True, choices=PHASES)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    workdir = os.path.abspath(args.workdir)
    if not os.path.isdir(workdir):
        print(json.dumps({"ok": False, "error": f"workdir 不存在: {workdir}"}) if args.json
              else f"FAIL: workdir 不存在: {workdir}")
        return 2

    try:
        check_enter(workdir, args.enter)
    except LoopExceeded as e:
        msg = f"LOOP_EXCEEDED: {e}"
        print(json.dumps({"ok": False, "loop_exceeded": True, "error": str(e)}) if args.json else msg)
        return 3
    except GateFail as e:
        msg = f"FAIL: {e}"
        print(json.dumps({"ok": False, "error": str(e)}) if args.json else msg)
        return 1
    except Exception as e:  # noqa
        msg = f"ERROR: {type(e).__name__}: {e}"
        print(json.dumps({"ok": False, "error": msg}) if args.json else msg)
        return 2

    print(json.dumps({"ok": True, "enter": args.enter}) if args.json
          else f"PASS: 允许进入 Phase {args.enter}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
