# Research Topic Selection（科研/课题申报选题系统 v1.4）

AI 辅助的科研选题流程，**以研究者自身输入为唯一出发点**——不随机生成题目，而是把模糊兴趣收敛成经过竞争性解释、证伪条件和小规模 pilot 检验的 3+2 选题。

## 核心特性

| 特性 | 说明 |
|---|---|
| **冻结协议** | 初始化时锁定研究边界、学科分支、利害关系档，防止中途无痕改题 |
| **刚性闸门** | 7 道 BLOCKING 闸门（scope / scan / scan-review / literature / questions / topics / final），产物未过闸不得进入下一步 |
| **独立审查分离** | scan 和 topics 两道 critical 闸强制 independent 审查，审查者上下文不含产出过程 |
| **好问题压力测试** | 核心缺口转化为可检验的研究问题，经六维评分 + 竞争性解释 + 推翻条件筛选 |
| **结构化证据台账** | 五维扫描的每条证据写入 `evidence_registry.jsonl`，带 stance（support/counter/mixed） |
| **断点续写** | 支持从任意阶段继续，后段闸门自动重验全部上游产物 |
| **降级有痕** | 无可靠来源时显式标注 unavailable，不静默伪造 |

## 流程概览

```
Phase 0-1  三问启动 + 协议冻结    → 00/01/protocol.json
Phase 2    五维扫描               → 03_五维扫描.md + 证据台账
Phase 3    问题域地图             → 04_问题域地图.md
Phase 4    中等深度文献脉络       → 05_文献脉络.md
Phase 5    总体趋势判断           → 06_趋势判断.md
Phase 6    核心缺口               → 07_核心缺口.md
Phase 6.5  好问题闸门             → 07A_好问题卡.md + question_scores.json
Phase 7    3+2 课题选项           → 08_选题推荐.md
final      交付 manifest          → delivery_manifest.json
```

## 闸门一览

| enter | 数字入口 | 校验内容 | 退出码 |
|---|---|---|---|
| scope | 1 | 冻结协议字段、风险档位映射、三问与澄清 | 0 PASS / 1 FAIL |
| scan | 2 | scope + 03 五维 + 证据台账 + 反面证据 | 同上 |
| scan-review | 4 | 03+04 结构 + scan review verdict=PASS + hash 闭环 | 同上 |
| literature | 5 | 重跑 scan 链 + 05 文献脉络 | 同上 |
| questions | 6 | 重跑上游链 + 07 缺口 + 好问题卡 + 六维评分 | 同上 |
| topics | 7 | 07+07A+08 + topics review verdict=PASS + hash 闭环 | 同上 |
| final | - | 重跑全部上游链 + delivery manifest hash 血缘 | 同上 |

```bash
# 过闸
python scripts/selection_gate.py --workdir <wd> --enter scan

# 数字入口
python scripts/selection_gate.py --workdir <wd> --enter 2

# 诊断最早阻塞点
python scripts/selection_gate.py --workdir <wd> --status

# 生成审查 hash 模板
python scripts/selection_gate.py --workdir <wd> --hash-template scan
```

## 目录结构

```
research-topic-selection/
├── SKILL.md                          核心流程定义（v1.4）
├── README.md                         本文件
├── scripts/
│   ├── init_project.py               初始化项目（生成协议 + 空产物）
│   ├── selection_gate.py             刚性闸门校验
│   └── build_manifest.py             构建交付 manifest
├── references/
│   ├── artifact-schemas.md           结构化产物规范（protocol / evidence / scores / manifest）
│   ├── discipline-branches.md        学科分支适配（实证量化 / 质性案例 / 理论建构 / 工程应用）
│   ├── good-question-gate.md         好问题闸门规则与评分维度
│   ├── review-nodes.md               独立审查节点定义与 verdict 模板
│   └── scan-checklist.md             五维扫描执行清单（含反确认偏差自检）
└── evals/
    └── test_selection_gate.py        闸门脚本测试
```

## 适用场景

- 经济/管理/社科为主的论文选题与课题申报
- 自然/工程类走"工程应用"分支
- 课程论文、学位论文、期刊论文、基金申报均可使用

## 触发词

科研选题、论文选题、课题申报选题、AI 辅助选题、研究缺口、文献脉络、学术趋势、课题申报、社科选题、经管选题、研究问题优化、选题可证伪性

## 依赖

- Python 3（闸门脚本、初始化脚本、manifest 构建）
- 联网检索工具（五维扫描阶段强制使用，禁止编造时效性信息）
- 可选：学术 API（OpenAlex / Semantic Scholar / arXiv / PubMed）

## 信任边界

闸门校验字段、hash 绑定、transcript hash 与 P0 处置闭环**不提供密码学身份保证**。蓄意伪造一整套自洽 transcript + verdict + 匹配 hash 仍可能（v1.4 级残留）。彻底闭合需受控 runner 外部登记审查行为，超出本技能范围。
