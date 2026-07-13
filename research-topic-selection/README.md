# Research Topic Selection — 科研/课题申报选题系统 v1.5.2

AI 辅助的科研选题流程，以研究者自身输入为唯一出发点，把模糊兴趣收敛成经过竞争性解释、证伪条件和小规模 pilot 检验的 3+2 选题。

## 核心特性

- **用户材料驱动** — 不随机生成题目，必须从用户提供的文献、笔记或摘要出发
- **全链路刚性闸门** — scope → materials → scan → scan-review → literature → questions → topics → final，每个阶段有独立校验脚本
- **结构化证据台账** — evidence_registry.jsonl 逐条记录检索结论、来源和反面证据
- **好问题压力测试** — 六维评分（重要性/可行性/可证伪性/证据杠杆/原创性/负向结果价值）筛选候选问题
- **独立审查分离** — scan 和 topics 两道 critical 闸强制独立审查，审查者上下文不含产出过程
- **Grill 决策追问** — 关键节点一次只追问一个决策，每个问题附带推荐答案
- **断点续写** — 支持"从第 X 步继续"，自动重新校验全部上游产物

## 流程概览

| Phase | 产物 | 闸门 | 说明 |
|-------|------|------|------|
| 0-1 | `01_三问与澄清.md`, `protocol.json` | scope | 三问启动 + 协议冻结 |
| 1.5 | `02_用户材料研判.md` | materials | 用户材料交互与研判 |
| 2 | `03_五维扫描.md`, `evidence_registry.jsonl` | scan | 政策/学术/实践/数据/窗口五维扫描 |
| 3 | `04_问题域地图.md` | scan-review | 问题域地图 + 独立审查 |
| 4 | `05_文献脉络.md` | literature | 中等深度文献脉络 |
| 5 | `06_趋势判断.md` | — | 四维度趋势判断 |
| 6 | `07_核心缺口.md` | — | 核心研究缺口 |
| 6.5 | `07A_好问题卡.md`, `question_scores.json` | questions | 好问题压力测试 |
| 7 | `08_选题推荐.md` | topics | 3+2 课题选项 + 独立审查 |
| final | `delivery_manifest.json` | final | 全链路交付校验 |

## 目录结构

```text
research-topic-selection/
├── SKILL.md                        核心流程与闸门规则（v1.5.2）
├── README.md                       本文件
├── scripts/
│   ├── init_project.py             初始化项目目录与协议
│   ├── register_material.py        登记用户材料
│   ├── selection_gate.py           刚性闸门校验脚本
│   └── build_manifest.py           生成交付清单
├── references/
│   ├── artifact-schemas.md         结构化产物字段规范
│   ├── discipline-branches.md      学科分支适配规则
│   ├── good-question-gate.md       好问题闸门与 Grill 压力测试
│   ├── review-nodes.md             审查节点模板与 hash 计算模式
│   ├── scan-checklist.md           五维扫描执行清单
│   └── user-material-intake.md     用户材料交互指引
└── evals/
    └── test_selection_gate.py      闸门脚本单元测试
```

## 外部依赖

- Python 3（运行 scripts/）
- 联网检索工具（anysearch / web_search / web_fetch 等，五维扫描需要）

## 快速开始

```bash
# 初始化项目
python scripts/init_project.py --workdir ./my_project --topic "..." --why-now "..." \
  --research-base "已有数据、理论训练或合作条件" --deliverable-type "基金申报" \
  --discipline-branch "实证量化" --time-window "2021-2026" --language zh-CN

# 过 scope 闸
python scripts/selection_gate.py --workdir ./my_project --enter scope

# 查看当前阻塞点
python scripts/selection_gate.py --workdir ./my_project --status
```

## v1.5.2 更新要点

- 新增 **Grill 决策追问机制**（§十一），关键节点逐字段追问，一次只解决一个决策分支
- 五维扫描证据要求更严格：verified 维度必须有 counter/mixed 证据，unavailable 必须登记两个检索式
- 独立审查 hash 计算支持两种模式：模式 A（主线程预计算 hash 模板，适配 read-only subagent）和模式 B（subagent 自行计算）
- 候选问题评分规范明确：六维 1-5 整数，decision 只能取 selected/parked/dropped
- 检索工具统一规则：优先调用 anysearch / web_search / web_fetch
