# 自然中文协议

> 让 AI 生成的中文重归人写的状态——**破除机器味，立起人味**。

[MIT] [ClawHub] [Anthropic Skills] [v2.0.0] [更新 2026-07-26]

---

## 你什么时候需要它？

- **场景 1**：刚用 AI 生成了一篇公众号文章，老板说"读起来像 AI 写的，能改得人味一点吗？"
- **场景 2**：让 AI 写了一篇学术摘要，结果被审稿人指出"过度使用排比与确信副词"。
- **场景 3**：让 AI 出了一份工作汇报，套话太多（高度重视、扎实推进、切实加强），发不出去。

---

## 它会交付什么？

下面是同一段文字打磨前后的对比：

> **改前**（机器味 50 分）：朋友们，我相信很多人都有这样的经历。每当我们打开 ChatGPT，总想着"再问一个问题就关掉"，结果一抬头已经过去了两个小时。这不仅仅是一次简单的习惯改变，更是一次认知层面的深度重构。在这个 AI 飞速发展的时代，让我们一起拥抱这个变化，与 AI 共成长。
>
> **改后**（机器味 92 分）：我自己最近一个月就这么过——每次说"再问一个就关"，抬头一看已经过了两小时。后来我给自己加了一个 25 分钟闹钟，到点强制合上屏幕。这个办法不优雅，但确实有用。

完整的三场景对比见 [`examples/`](examples/)：公文、学术、新媒体各一。

---

## 快速开始

```bash
# 一键安装（如果你用 ClawHub）
npx skills add natural-chinese

# 或者直接把整个目录拷到 ~/.claude/skills/natural-chinese/
# 之后用 /natural-chinese 或自然语言触发
```

---

## 触发方式

对 Agent 说以下任何一句话即可触发：

- "帮我去一下 AI 味"
- "把这段改得更像人写的"
- "润色一下，别那么机械"
- "按自然中文协议重写这段"
- "This Chinese text sounds too AI, humanize it"
- "用自然中文改写：……"

---

## 示例

见 `examples/` 三个完整案例：

- [`examples/gongwen/`](examples/gongwen/) — 公文 / 工作汇报
- [`examples/xueshu/`](examples/xueshu/) — 学术 / 研究摘要
- [`examples/xinmeiti/`](examples/xinmeiti/) — 新媒体 / 公众号长文

每个案例含 `before.md`（典型 AI 味文本）、`after.md`（按协议改写）、`scan.md`（命中点 + 改写策略 + 自检勾选）。

---

## 它和同类有什么不同？

| 维度 | natural-chinese | humanizer-zh | stop-ai-slop-zh | academic-humanizer |
|---|---|---|---|---|
| 语言 | 中文母语原创 | 翻译 blader/humanizer | 中文原创 | 英文学术 |
| 场景适配 | **6 类场景 × 策略矩阵** | 通用 | 通用 | 仅学术 |
| 注入工具 | **5 条人味工具（破+立双轨）** | 仅"破" | 仅"破" | 仅"破" |
| 自检清单 | **28 条打勾式** + 豁免规则 | 无 | 无 | 有，但不公开 |
| 量化打分 | **`scripts/score.py` 自动化** | 无 | 无 | 无 |
| 示例对照 | **3 场景 before/after** | 无 | 无 | 无 |
| 跨 runtime | claude-code / codex / opencode / hermes / openclaw | 主要 claude-code | 通用 | claude-code / codex |

**一句话差异**：natural-chinese 是少有的"**场景适配 + 破立双轨 + 可验证自检**"三件套齐备的方法论级协议。

---

## 安全边界

- ✅ **不动**数字、统计量、引用、专有名词、事实陈述。
- ✅ **不动**原始数据的语义（仅润色文字，不重写观点）。
- ❌ **不**会为了"像人"而捏造犹豫、不确定或第一人称承担（学术/公文豁免）。
- ❌ **不**帮你逃避 AI 检测器（参见 haning-humanize 的反检测器叙事）。
- ❌ **不**改写核心信息与意图——改写是手段，不是重写。

---

## 文件结构

```
natural-chinese/
├── SKILL.md                # 顶层流程（四步 + 完成判据 + 反模式 + 兄弟关系）
├── README.md               # 本文件
├── LICENSE                 # MIT
├── references/
│   ├── patterns.md         # 19 类机器味模式 + 完整优化示例 + 快速索引
│   ├── scenarios.md        # 6 类场景 × 4 列策略矩阵 + 跨场景红线
│   ├── injection.md        # 5 条人味注入工具 + 反人味陷阱
│   └── self-check.md       # 28 条打勾式自检清单 + 最短自检路径
├── examples/
│   ├── gongwen/            # 公文案例
│   ├── xueshu/             # 学术案例
│   └── xinmeiti/           # 新媒体案例
├── scripts/
│   └── score.py            # 自动打分器（按 self-check 量化输出）
└── test-prompts.json       # 固化测试样例 + 期望模式 + 必保要素
```

---

## 验证与测试

### 自动打分

```bash
# 对任意中文文本打分
python scripts/score.py examples/gongwen/before.md

# 输出 Markdown 报告
python scripts/score.py --json examples/xueshu/after.md > report.json
```

实测打分对比（按本协议打磨前后）：

| 案例 | 改前 | 改后 | 提升 |
|---|---:|---:|---:|
| 公文 / 工作汇报 | 60 | 97 | +37 |
| 学术 / 研究摘要 | 60 | 97 | +37 |
| 新媒体 / 公众号 | 50 | 92 | +42 |

### 固化测试

见 [`test-prompts.json`](test-prompts.json)。包含 5 条测试用例（公文/学术/新媒体/商业/边界场景），每条含 prompt、期望模式、必须保留要素、改写禁区。

---

## 致谢

本协议的灵感、语感切片与迭代校准，离不开真实人类对母语的敏锐洞察与热爱。特此鸣谢：

- 罗著Jude
- 郭敏定
- 青山随云走

---

## 许可证

MIT