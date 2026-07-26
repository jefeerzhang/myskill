#!/usr/bin/env python3
"""
score.py — natural-chinese 自动打分器

按 references/self-check.md 的 28 条判据，对一段中文文本打分。
覆盖：机器味残留（10 条）+ 反向机械化（5 条）+ 基础阅读呼吸感（4 条）。

用法：
    python score.py <text_file>
    python score.py --string "一段中文"
    python score.py --json <text_file>

输出：Markdown 报告（默认）或 JSON。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# ========== 机器味残留词典（10 组警戒词）==========

MACHINE_TASTE_PATTERNS = {
    "1_宏大叙事": [
        r"标志着.{0,15}(新|新的)",
        r"开启了.{0,15}新篇章",
        r"深度赋能",
        r"里程碑",
        r"重塑了.{0,15}闭环",
        r"指明了方向",
        r"谱写.{0,8}新篇章",
        r"深刻反映",
        r"深度重构",
        r"悄然重塑",
        r"深刻改变",
        r"重塑(我们的|我们的)?思维方式",
        r"重塑.{0,15}(认知|知识工作)",
        r"认知生态",
        r"认知外包的深层风险",
        r"大规模.{0,6}能力下降",
    ],
    "2_确信感": [
        r"无疑", r"毫无疑问", r"毋庸置疑",
        r"绝对地", r"绝对能", r"绝对会",
        r"完全展现", r"完全证明",
        r"必然导致", r"必将",
        r"唯有.{0,4}才能",
    ],
    "3_显性衔接": [
        r"值得注意的是", r"需要指出的是", r"需要强调的是",
        r"不可否认的是", r"综上所述", r"正如前文所述",
        r"在这个.{0,8}(飞速发展的|快速发展的|高速发展的)",
    ],
    "4_八股结尾": [
        r"挑战与机遇并存", r"未来依然可期", r"让我们拭目以待",
        r"未来可期", r"指明了.{0,8}方向",
        r"让我们一起.{0,6}(拥抱|迎接|努力)",
        r"迎接更加美好的明天",
        r"立于不败之地",
        r"总结与展望",
    ],
    "5_公文体假大空": [
        r"高度重视", r"深入贯彻", r"扎实推进", r"切实加强",
        r"充分体现", r"全面落实", r"显著提升", r"强力推动",
    ],
    "6_对称排比": [
        r"不仅(是)?.{0,8}更",
        r"既.{0,8}也",
        r"不只是.{0,8}更是",
        r"不仅仅是.{0,8}更是",
        r"不仅.{0,8}更.{0,8}更",
    ],
    "7_代词它滥用": [
        r"它不再是.{0,8}而是",
    ],
    "8_强加过渡": [
        r"比较直观的变化是", r"具体而言", r"具体来说",
        r"也应当",
    ],
    "9_动词名词化": [
        r"进行了.{0,6}研究", r"开展了.{0,6}分析",
        r"实现了.{0,6}的提升",
    ],
    "10_模糊套话": [
        r"在某种程度上", r"在某种意义上", r"一定程度上",
        r"在一定意义上",
    ],
}


# ========== 反向机械化词典（5 条）==========

OVER_CORRECTION_PATTERNS = {
    "11_电报体": {
        # 检测：连续 3 个以上短句（≤10 字）且平均句长 < 12
        "type": "ratio",
        "check": lambda sentences: _check_telegram_style(sentences),
    },
    "12_第一人称滥用": {
        "type": "count",
        "patterns": [r"(我认为|我觉得|在我看来|笔者认为|我个人)"],
        "max_per_1000": 5,
    },
    "13_假犹豫": {
        "type": "regex",
        "patterns": [
            r"我(也)?还在犹豫",
            r"我(也)?没想清楚",
            r"这一点我自己.{0,4}也没",
        ],
    },
    "14_语体杂糅": {
        "type": "regex",
        "patterns": [
            # 严肃文本中出现"挺""蛮""超""贼"等口语词
            (r"挺(?!.{0,15}(好用|实在|实用|不错))", "warning"),
            (r"\b蛮好\b", "warning"),
            (r"\b超(快|好|赞)\b", "warning"),
        ],
    },
    "15_emoji滥用": {
        "type": "regex",
        "patterns": [
            r"[\U0001F300-\U0001FAFF]",  # emoji 范围
            r"[☀-➿]",          # 符号
        ],
        "max_per_1000": 2,
    },
}


# ========== 阅读呼吸感（4 条）==========

BREATHING_PATTERNS = {
    "19_段落对称": {"type": "ratio", "check": lambda paragraphs: _check_paragraph_symmetry(paragraphs)},
    "20_连接词堆砌": {
        "type": "count",
        "patterns": [r"因此，", r"然而，", r"所以，", r"与此同时，", r"此外，"],
        "max_per_1000": 6,
    },
    "21_破折号密度": {"type": "ratio", "check": lambda text: _check_dash_density(text)},
    "22_冒号三段式": {"type": "regex", "patterns": [r"[A-Z]、.{0,15}、.{0,15}："], "max_per_text": 2},
}


# ========== 辅助检测函数 ==========

def _split_sentences(text: str) -> list[str]:
    """中英文混合分句（按 。！？；\n 切）。"""
    text = re.sub(r"[。！？；\n]+", "。", text)
    return [s.strip() for s in text.split("。") if s.strip()]


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _check_telegram_style(sentences: list[str]) -> tuple[int, list[str]]:
    """检测电报体：连续 3+ 短句（≤10 字）且平均句长 < 12。"""
    if len(sentences) < 3:
        return 0, []
    short_run = 0
    max_run = 0
    for s in sentences:
        if len(s) <= 10:
            short_run += 1
            max_run = max(max_run, short_run)
        else:
            short_run = 0
    avg_len = sum(len(s) for s in sentences) / len(sentences)
    issues = []
    if max_run >= 3 and avg_len < 12:
        issues.append(f"连续短句 ≥3 且平均句长 {avg_len:.1f}")
    return len(issues), issues


def _check_paragraph_symmetry(paragraphs: list[str]) -> tuple[int, list[str]]:
    """段落对称：连续 3 段字数相近（差 ≤5 字）。"""
    if len(paragraphs) < 3:
        return 0, []
    lengths = [len(p) for p in paragraphs]
    issues = []
    for i in range(len(lengths) - 2):
        a, b, c = lengths[i], lengths[i + 1], lengths[i + 2]
        if abs(a - b) <= 5 and abs(b - c) <= 5 and a > 30:
            issues.append(f"段 {i + 1}-{i + 3} 字数 {a}/{b}/{c} 高度对称")
            break
    return len(issues), issues


def _check_dash_density(text: str) -> tuple[int, list[str]]:
    """破折号密度：每段不超过 1 个。"""
    paragraphs = _split_paragraphs(text)
    issues = []
    for i, p in enumerate(paragraphs):
        count = p.count("——") + p.count("—")
        if count > 1:
            issues.append(f"段 {i + 1} 破折号 {count} 个（>1）")
    return len(issues), issues


# ========== 主打分函数 ==========

def _strip_markdown_metadata(text: str) -> str:
    """剥离 markdown 元信息，只保留真正的散文（before/after 主体）。

    策略：识别 markdown 二级及以下标题，按"段"扫描。当遇到 # / ## / ### 等标题时：
    - 如果是目标正文段（"## 原始文本（before）" / "## 改写后（after）" / 类似散文小节），保留后续内容直到下一个 # 标题。
    - 如果是元信息段（"## 命中点扫描" / "## 改写策略" / "## 自检勾选" 等），丢弃后续内容直到下一个 # 标题。
    """
    # 优先级：drop 先于 keep 检查（避免"## 改写策略"被"## 改写"前缀误保留）
    keep_prefixes = (
        "## 原始文本", "## 改写后", "## 原文",
        "## 修改前", "## 修改后",
        "## 示例", "## 输入", "## 输出",
    )
    drop_prefixes = (
        "## 命中点扫描", "## 命中点", "## 扫描报告",
        "## 改写策略", "## 自检勾选", "## 验证门", "## 保留要素",
        "## 破立比", "## 同行对照", "## 注入工具使用", "## 注入工具",
        "## 模式快速索引", "## 场景识别", "## 场景合规提醒",
        "## 命中点清单", "## 场景识别", "## 场景合规",
    )

    lines = text.split("\n")
    kept_paragraphs = []
    in_drop_section = False
    current_paragraph = []

    def flush():
        nonlocal current_paragraph
        if current_paragraph:
            kept_paragraphs.append("\n".join(current_paragraph))
            current_paragraph = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            # 新标题：先把当前段落 flush
            flush()
            if any(stripped.startswith(p) for p in drop_prefixes):
                in_drop_section = True
            elif any(stripped.startswith(p) for p in keep_prefixes):
                in_drop_section = False
                current_paragraph.append(re.sub(r"^#+\s*", "", stripped))
            else:
                # 未知标题（如 "## 场景：公文"）：当作正文保留
                in_drop_section = False
                current_paragraph.append(re.sub(r"^#+\s*", "", stripped))
        elif in_drop_section:
            continue
        else:
            if stripped.startswith("- ") or stripped.startswith("* "):
                current_paragraph.append(stripped[2:])
            elif re.match(r"^\d+\.\s", stripped):
                current_paragraph.append(re.sub(r"^\d+\.\s", "", stripped))
            else:
                current_paragraph.append(line)
    flush()
    return "\n\n".join(p for p in kept_paragraphs if p.strip())


def score_text(text: str) -> dict:
    """对一段中文文本打分，返回结构化报告。"""
    text = _strip_markdown_metadata(text)
    sentences = _split_sentences(text)
    paragraphs = _split_paragraphs(text)

    # —— 机器味残留 ——
    machine_hits = {}
    machine_total = 0
    for group_name, patterns in MACHINE_TASTE_PATTERNS.items():
        hits = []
        for p in patterns:
            for m in re.finditer(p, text):
                hits.append({"match": m.group(0), "pos": m.start()})
        machine_hits[group_name] = hits
        machine_total += len(hits)

    # —— 反向机械化 ——
    over_corr = {}
    over_corr_total = 0
    char_count = max(len(text), 1)
    for key, spec in OVER_CORRECTION_PATTERNS.items():
        if spec["type"] == "regex":
            hits = []
            for p in spec["patterns"]:
                if isinstance(p, tuple):
                    p, severity = p
                else:
                    severity = "warning"
                for m in re.finditer(p, text):
                    hits.append({"match": m.group(0), "severity": severity})
            over_corr[key] = hits
            over_corr_total += len(hits)
        elif spec["type"] == "count":
            total = 0
            hits = []
            for p in spec["patterns"]:
                cnt = len(re.findall(p, text))
                total += cnt
                if cnt:
                    hits.append({"pattern": p, "count": cnt})
            max_allowed = (spec["max_per_1000"] * char_count) // 1000
            over_corr[key] = {
                "total": total,
                "max_allowed": max_allowed,
                "excess": max(0, total - max_allowed),
                "samples": hits,
            }
            if total > max_allowed:
                over_corr_total += total - max_allowed
        elif spec["type"] == "ratio":
            n, issues = spec["check"](sentences)
            over_corr[key] = {"issues": issues}
            over_corr_total += n

    # —— 阅读呼吸感 ——
    breathing = {}
    breathing_total = 0
    for key, spec in BREATHING_PATTERNS.items():
        if spec["type"] == "regex":
            total = 0
            for p in spec["patterns"]:
                total += len(re.findall(p, text))
            max_allowed = spec.get("max_per_text", 999)
            breathing[key] = {"total": total, "max_allowed": max_allowed, "excess": max(0, total - max_allowed)}
            if total > max_allowed:
                breathing_total += total - max_allowed
        elif spec["type"] == "count":
            total = 0
            for p in spec["patterns"]:
                total += len(re.findall(p, text))
            max_allowed = (spec["max_per_1000"] * char_count) // 1000
            breathing[key] = {"total": total, "max_allowed": max_allowed, "excess": max(0, total - max_allowed)}
            if total > max_allowed:
                breathing_total += total - max_allowed
        elif spec["type"] == "ratio":
            if key == "19_段落对称":
                n, issues = spec["check"](paragraphs)
            elif key == "21_破折号密度":
                n, issues = spec["check"](text)
            else:
                n, issues = 0, []
            breathing[key] = {"issues": issues}
            breathing_total += n

    # —— 综合分（百分制）——
    # 起点 100；机器味每处扣 5；反向机械化每处扣 8；呼吸感每处扣 3
    score = 100 - machine_total * 5 - over_corr_total * 8 - breathing_total * 3
    score = max(0, min(100, score))

    if score >= 90:
        grade = "A · 自然"
    elif score >= 75:
        grade = "B · 较自然"
    elif score >= 60:
        grade = "C · 可读但有机器味"
    elif score >= 40:
        grade = "D · 明显机器味"
    else:
        grade = "F · 几乎纯 AI 生成"

    return {
        "score": score,
        "grade": grade,
        "char_count": char_count,
        "sentence_count": len(sentences),
        "paragraph_count": len(paragraphs),
        "machine_taste": {
            "total": machine_total,
            "by_group": machine_hits,
        },
        "over_correction": {
            "total": over_corr_total,
            "by_group": over_corr,
        },
        "breathing": {
            "total": breathing_total,
            "by_group": breathing,
        },
    }


# ========== 报告渲染 ==========

def render_markdown(report: dict) -> str:
    """把报告渲染成 Markdown。"""
    lines = []
    lines.append(f"# 自然中文协议 · 自动打分报告")
    lines.append("")
    lines.append(f"**总分：{report['score']} / 100** — {report['grade']}")
    lines.append("")
    lines.append(f"字符数：{report['char_count']}　句数：{report['sentence_count']}　段数：{report['paragraph_count']}")
    lines.append("")

    # 机器味
    lines.append("## 机器味残留")
    lines.append(f"**总命中：{report['machine_taste']['total']} 处**")
    lines.append("")
    for group, hits in report["machine_taste"]["by_group"].items():
        if hits:
            lines.append(f"- **{group}**：{len(hits)} 处")
            for h in hits[:3]:
                lines.append(f"  - \"{h.get('match', '')}\"")
            if len(hits) > 3:
                lines.append(f"  - ……另有 {len(hits) - 3} 处")
    if report["machine_taste"]["total"] == 0:
        lines.append("✅ 无命中")
    lines.append("")

    # 反向机械化
    lines.append("## 反向机械化")
    lines.append(f"**总命中：{report['over_correction']['total']} 处**")
    lines.append("")
    for group, val in report["over_correction"]["by_group"].items():
        if isinstance(val, list) and val:
            lines.append(f"- **{group}**：{len(val)} 处")
        elif isinstance(val, dict):
            if val.get("total", 0) > val.get("max_allowed", 0):
                lines.append(f"- **{group}**：{val['total']} 处（上限 {val['max_allowed']}）")
            elif val.get("issues"):
                lines.append(f"- **{group}**：{len(val['issues'])} 处")
    if report["over_correction"]["total"] == 0:
        lines.append("✅ 无命中")
    lines.append("")

    # 呼吸感
    lines.append("## 阅读呼吸感")
    lines.append(f"**总命中：{report['breathing']['total']} 处**")
    lines.append("")
    for group, val in report["breathing"]["by_group"].items():
        if isinstance(val, dict):
            if val.get("total", 0) > val.get("max_allowed", 0):
                lines.append(f"- **{group}**：{val['total']} 处（上限 {val['max_allowed']}）")
            elif val.get("issues"):
                lines.append(f"- **{group}**：{len(val['issues'])} 处")
    if report["breathing"]["total"] == 0:
        lines.append("✅ 无命中")
    lines.append("")

    return "\n".join(lines)


# ========== CLI ==========

def main():
    parser = argparse.ArgumentParser(description="natural-chinese 自动打分器")
    parser.add_argument("file", nargs="?", help="文本文件路径（默认 stdin）")
    parser.add_argument("--string", help="直接传入字符串")
    parser.add_argument("--json", action="store_true", help="输出 JSON 而非 Markdown")
    args = parser.parse_args()

    if args.string:
        text = args.string
    elif args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("错误：输入为空", file=sys.stderr)
        sys.exit(1)

    report = score_text(text)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))


if __name__ == "__main__":
    main()