# 科研选题系统（research-topic-selection）v1.2

AI 辅助的科研 / 课题申报选题系统：**以研究者自身输入为唯一出发点**——不随机生成题目，而是把模糊兴趣收敛成可申报的 3+2 选题（3 个主推 + 2 个备选）。

本技能 v1.2 使用**刚性推进闸门**与**独立审查分离**机制，保证关键产物完成且经独立审查后才放行下游，断点续写不可静默绕过上游闸。

## 🎯 这个技能解决什么问题？

当你需要下列产出时，用 `research-topic-selection`：

- 从“我大概关心 XX 方向”出发，收敛出可申报的论文选题 / 课题方向
- 做课题申报前的选题论证（社科 / 经管 / 政策研究为主；自然 / 工程类走“工程应用”分支）
- 系统扫描五维环境、梳理文献脉络与趋势、定位核心研究缺口
- 在选题流程中保留**反确认偏差**证据与**独立审查**留痕，而非主线程自审自盖合格章

## ✅ 触发方式

触发词（建议在对话中显式表达任一意图即可）：

> 科研选题、论文选题、课题申报选题、AI 辅助选题、研究缺口、文献脉络、学术趋势、课题申报、社科选题、经管选题

## 📥 输入建议

- 你关心的研究问题 / 现象 / 矛盾 / 政策方向
- 为什么是现在（新政策、新数据、新现象、个人研究节点）
- 已具备的材料或基础（数据、田野、理论训练、合作方）
- 学科取向（实证量化 / 质性案例 / 理论建构 / 工程应用）与利害关系档（课程 / 学位 / 期刊 / 基金）

## 🔀 完整流程（9 Phase + 刚性闸门）

| Phase | 名称 | 产物 | 闸门（BLOCKING 点） |
| --- | --- | --- | --- |
| 0 | 三问启动 | — | — |
| 1 | 小澄清（可选） | `01_三问与澄清.md` | — |
| 2 | 五维扫描 | `03_五维扫描.md` | **scan** |
| 3 | 问题域地图 | `04_问题域地图.md` | —（scan 审查校验 03+04） |
| 4 | 中等深度文献脉络 | `05_文献脉络.md` | **literature** |
| 5 | 总体趋势判断 | `06_趋势判断.md` | — |
| 6 | 核心缺口 | `07_核心缺口.md` | —（topics 审查校验 07+08） |
| 7 | 3+2 课题选项 | `08_选题推荐.md` | **topics** |
| 8/9 | 交付（final） | 交付 `08_选题推荐.md` | **final** |

两道 **critical 闸**（scan、topics）强制 **independent** 审查：审查者上下文不含产出过程，只读落盘产物，且 `reviewer_agent_id ≠ producer_agent_id`（闸门字段级校验）。

## 🔒 刚性推进闸门（scripts/selection_gate.py）

### 入口

```bash
python scripts/selection_gate.py --workdir <wd> --enter {scan,scan-review,literature,topics,final}
```

旧数字别名仍兼容：`2=scan`、`4=scan-review`、`5=literature`、`7=topics`、`final=final`。

### 各入口校验内容

| enter | 校验内容 | 退出码 |
|-------|----------|--------|
| `scan` / `2` | `03_五维扫描.md` 五维齐全，且含有足量“反确认偏差记录” | 0 PASS / 1 FAIL |
| `scan-review` / `4` | `03+04` 结构完整 + scan review verdict=PASS + artifact_hashes / transcript / P0 闭环均匹配 | 同上 |
| `literature` / `5` | `05_文献脉络.md` 含前沿方向、核心争论、方法谱系且内容非空 | 同上 |
| `topics` / `7` | `07+08` 结构完整 + topics review verdict=PASS + artifact_hashes / transcript / P0 闭环均匹配 | 同上 |
| `final` | `07+08` 结构完整，并复核 topics review 仍绑定当前文件版本 | 同上 |
| — | 单节点审查 round > 3 | 3（超界，升级人类） |

### 审查 hash 模板

送审前可生成当前 artifact hash 模板供审查者核对：

```bash
python scripts/selection_gate.py --workdir <wd> --hash-template scan
python scripts/selection_gate.py --workdir <wd> --hash-template topics
```

审查者仍应以自己实际读取到的文件为准填写 hash；模板只用于降低手工出错率。

### 审查校验要点（v1.2 强化）

- verdict 必须绑定 `node`、`workdir`（跨目录复制旧 verdict 会被拒绝）、`reviewer_kind=independent`（scan / topics）。
- `verdict=PASS`、`p0_open=0`、当前 `p0` 列表为空。
- `artifact_hashes` 由审查者本人对实际读到的产物计算，闸门与当前文件实算值比对（防重放 / 审后再改）。
- `agent_output_sha256` 必须等于完整 transcript 文件的 sha256；闸门读取 transcript 末尾 fenced JSON，与 `review_<node>.json` 原始字段逐项比对。
- 只要 `history` 中任一轮 `p0_found > 0`，最终 verdict 必须设置 `re_reviewed_dispositions: true`，且 `review/dispositions_<node>.json` 中每条历史 P0 都须有合法 `status`、非空 `evidence`、`reviewer_decision: accepted`。

## 🛡️ 审查分离与处置闭环

- 审查报 P0 → 执行者写 `review/dispositions_<node>.json` → **回送原审查者复核**（`reviewer_decision: accepted|rejected`），rejected 须重修正再审。
- 回环 ≤ 3 轮；超界 exit 3，升级人类裁决，不许自动重试。
- 降级必须留痕（如 `explicit-opt-out` 记录 justification），断点续写（resume-jump）必过前置闸，上游 BLOCKING 不可静默绕过。

## 📜 信任边界（如实声明）

闸门校验字段、hash 绑定、transcript hash 与 P0 处置闭环，**不提供密码学身份保证**。蓄意伪造一整套自洽 transcript + verdict + 匹配 hash 仍是可能的（v1.2 级残留）。彻底闭合需受控 runner 外部登记审查行为，超出本技能范围。

## 📚 关联文件

- 核心提示词与完整阶段规则：见 `SKILL.md`
- 审查节点规则（verdict 模板、处置闭环、hash 模板辅助）：见 `references/review-nodes.md`
- 五维扫描清单：见 `references/scan-checklist.md`
- 学科分支适配：见 `references/discipline-branches.md`
- 闸门脚本：见 `scripts/selection_gate.py`（Python 3）

## 🚀 安装（CoPaw / opencode）

将本仓库的 `research-topic-selection/` 目录复制到 Agent 技能根目录下（需 Python 3 运行闸门脚本）。

```text
~/.copaw/skills/
└── research-topic-selection/
    ├── SKILL.md
    ├── README.md
    ├── references/
    │   ├── review-nodes.md
    │   ├── scan-checklist.md
    │   └── discipline-branches.md
    └── scripts/
        └── selection_gate.py
```
