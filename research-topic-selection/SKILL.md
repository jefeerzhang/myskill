---
name: research-topic-selection
description: |
  AI 辅助科研选题系统 v1.2：从模糊兴趣到
  3+2 可申报课题的全流程构建。集成刚性推进闸门（scripts/selection_gate.py）、
  独立审查分离（references/review-nodes.md）、五维扫描清单（references/scan-checklist.md）、
  学科分支适配（references/discipline-branches.md）。
  适用经济/管理/社科为主的论文选题与课题申报；自然/工程类走"工程应用"分支。
  触发词：科研选题、论文选题、课题申报选题、AI辅助选题、研究缺口、文献脉络、
  学术趋势、课题申报、社科选题、经管选题。
version: 1.2.0
---

# Research Topic Selection（科研/课题申报选题系统 v1.2）

AI 辅助的科研选题流程，**以研究者自身输入为唯一出发点**——不随机生成题目，而是把模糊兴趣收敛成可申报的 3+2 选题。

本技能 v1.2 使用**刚性推进闸门**与**独立审查分离**：
关键产物完成后必须过 `scripts/selection_gate.py`；scan / topics 两道 critical 闸强制独立审查，
处置闭环经原审查者复核，断点续写不可静默绕过上游闸。详见 `references/review-nodes.md`。

---

## 一、三问启动（Phase 0）

用三个问题把模糊需求逼出结构化，**不要直接生成题目**：

1. **你在关心什么问题？**（现象/矛盾/政策/现象皆可，不求学术化）
2. **为什么是现在？**（新政策、新数据、新现象、个人节点）
3. **你已有什么材料或基础？**（数据、田野、理论训练、合作方）

若用户拒绝回答或输入过薄，停在 Phase 0，不硬编。

## 二、小澄清（Phase 1，可选）

确认：学科取向（实证量化/质性案例/理论建构/工程应用，见 `references/discipline-branches.md`）、
利害关系档（课程论文/学位论文/期刊/基金申报）、时间范围、中英文偏好。
落盘：`01_三问与澄清.md`。

## 三、五维扫描（Phase 2，BLOCKING）

系统扫描研究对象所处的五维环境，加载 `references/scan-checklist.md` 严格按清单执行：

- **政策扫描**：国家/地方政策方向、试点、窗口期。
- **学术文献扫描**：主要分支、经典问题、近 3 年趋势、核心争论。
- **现实实践扫描**：案例、新兴现象、组织模式。
- **数据/材料扫描**：公开数据集、可得性分级（可得/需申请/不可得）。
- **发表/申报窗口扫描**：目标期刊、基金指南、截止时间。

**硬性约束**：凡涉时效性必须实际调用检索（本地 anysearch / web_google 等联网检索工具），
禁止编造近期性；每维至少 1 条反面/竞争性证据（反确认偏差，清单 §六）。
落盘：`03_五维扫描.md`（含末尾"反确认偏差记录"段）。

> 生成 03 后过 `python scripts/selection_gate.py --workdir <wd> --enter scan`
> （兼容旧命令 `--enter 2`；校验 03 五维齐全且含反确认偏差段）。

## 四、问题域地图（Phase 3）

把扫描结果织成一张地图，落到 6 点：
1. 核心现实问题
2. 主要学术分支
3. 政策/实践变化
4. 可用数据和材料
5. 潜在研究切口
6. 初步风险判断

落盘：`04_问题域地图.md`。地图须自洽（核心问题↔分支↔数据↔切口），过度发散须收敛。

> **scan 独立审查（critical，independent）**：过闸后调用独立审查者审 03+04，
> 输出 verdict JSON（模板见 `references/review-nodes.md`），`p0_open=0` 才放行进入 Phase 5。
> 前过 `python scripts/selection_gate.py --workdir <wd> --enter scan-review`
> （兼容旧命令 `--enter 4`；校验 03+04、scan review、hash、transcript 与 P0 闭环）。

## 五、中等深度文献脉络（Phase 4）

围绕地图中的切口，做中等深度而非穷尽的文献脉络：前沿方向、核心争论、方法谱系。
落盘：`05_文献脉络.md`。

> 生成 05 后过 `python scripts/selection_gate.py --workdir <wd> --enter literature`
> （兼容旧命令 `--enter 5`；校验 05 含前沿方向、核心争论、方法谱系）。

## 六、总体趋势判断（Phase 5）

四维度 + 阶段判断：
- 政策趋势 / 实践趋势 / 学术趋势 / 数据与方法趋势
- 阶段判断（起步/上升/成熟/转型/衰退）

落盘：`06_趋势判断.md`。

## 七、核心缺口（Phase 6，BLOCKING）

只取 1–3 个核心缺口，每个含三段：既有研究已解释 / 仍不足 / 为何重要。带风险标注。
落盘：`07_核心缺口.md`。

## 八、3+2 课题选项（Phase 7，BLOCKING）

- **主推选题 3 个**：每个含研究问题、数据/方法路径（按学科分支具体化）、预期贡献、可行性。
- **备选选题 2 个**：明确各自降级场景。
- **推荐判断**：最推荐推进 / 理由 / 主要风险 / 下一步需补充。

落盘：`08_选题推荐.md`。

> **topics 独立审查（critical，independent）**：调用独立审查者审 07+08，verdict `p0_open=0` 才放行 final。
> 前过 `python scripts/selection_gate.py --workdir <wd> --enter topics`
> （兼容旧命令 `--enter 7`；校验 07+08、topics review、hash、transcript 与 P0 闭环）。

## 九、交付（final，BLOCKING）

> 进入前过 `python scripts/selection_gate.py --workdir <wd> --enter final`
> （校验 07+08 存在、结构完整，并复核 topics 独立审查仍绑定当前文件版本）。

交付 `08_选题推荐.md` 给用户，并附：
- 研究主题与范围
- 关键缺口与最推荐选题
- 主要风险与下一步需补充
- 打包目录位置

---

## 十、刚性闸门与审查机制（v1.2 核心，适配选题轻量特性）

### 10.1 闸门

`python scripts/selection_gate.py --workdir <wd> --enter {scan,scan-review,literature,topics,final}`

旧数字入口仍可用：`2=scan`，`4=scan-review`，`5=literature`，`7=topics`。

| enter | 校验内容 | 退出码 |
|-------|----------|--------|
| scan / 2 | 03_五维扫描.md 五维齐全，且含有足量"反确认偏差记录" | 0 PASS / 1 FAIL |
| scan-review / 4 | 03+04 结构完整 + scan review verdict=PASS + artifact_hashes/transcript/P0 闭环均匹配 | 同上 |
| literature / 5 | 05_文献脉络.md 含前沿方向、核心争论、方法谱系且内容非空 | 同上 |
| topics / 7 | 07+08 结构完整 + topics review verdict=PASS + artifact_hashes/transcript/P0 闭环均匹配 | 同上 |
| final | 07+08 结构完整，并复核 topics review 仍绑定当前文件版本 | 同上 |
| —  | 单节点审查 round > 3 | 3（超界，升级人类） |

生成审查 hash 模板可用：

`python scripts/selection_gate.py --workdir <wd> --hash-template scan`

或：

`python scripts/selection_gate.py --workdir <wd> --hash-template topics`

### 10.2 审查分离（强制）

- scan / topics 两道 critical 闸强制 **independent** 审查：审查者上下文不含产出过程，只读落盘产物。
- `reviewer_agent_id ≠ producer_agent_id`（闸门字段级校验）。
- 不依赖特定外部 runner；本地用 subagent 机制或另起会话承担。
- 其余阶段（三问/澄清/趋势/缺口）主线程自检，不强制独立审查。

### 10.3 处置闭环（禁自审）

审查报 P0 → 执行者写 `review/dispositions_<node>.json` → **回送原审查者复核**
（`reviewer_decision: accepted|rejected`），rejected 须重修正再审。回环 ≤ 3 轮。

### 10.4 降级车道（降级有痕，不静默）

| id | 触发 | 处理方式 | 是否降 high |
|----|------|----------|--------------|
| scan-fallback | 某维无可靠来源 | 标"暂无可靠来源，风险标注"，不伪造 | 否 |
| data-unavailable | 数据不可得 | 选题可行性标红，转备选或改切口 | 否 |
| explicit-opt-out | 用户主动放弃独立审查 | 记 justification，下游知情 | 否 |
| resume-jump | 用户"从某步继续" | **必过前置闸**，上游 BLOCKING 不可静默绕过 | 否 |

### 10.5 断点续写

用户"从第 X 步继续/从推荐开始"等：跳入必先 `selection_gate --enter <对应>` 过前置校验，
上游产物缺失则 FAIL，不构成质量降级。

### 10.6 信任边界（如实声明）

闸门校验字段、hash 绑定、transcript hash 与 P0 处置闭环，**不提供密码学身份保证**。
蓄意伪造一整套自洽 transcript+verdict+匹配 hash 仍可能（v1.2 级残留）。
彻底闭合需受控 runner 外部登记审查行为，超出本技能范围。

---

## 输出模板（供 08_选题推荐.md）

```markdown
# AI 辅助选题结果

## 1. 三问与澄清
- 关心的问题：
- 现在关心的原因：
- 材料或基础：

## 2. 初步问题域假设

## 3. 五维扫描摘要
### 政策扫描
### 学术文献扫描
### 现实实践扫描
### 数据/材料扫描
### 发表/申报窗口扫描

## 4. 问题域地图
1. 核心现实问题：
2. 主要学术分支：
3. 政策/实践变化：
4. 可用数据和材料：
5. 潜在研究切口：
6. 初步风险判断：

## 5. 中等深度文献脉络

## 6. 总体趋势判断
- 政策趋势：
- 实践趋势：
- 学术趋势：
- 数据与方法趋势：
- 阶段判断：

## 7. 核心缺口

## 8. 3+2 课题选项
### 主推选题 1
### 主推选题 2
### 主推选题 3
### 备选选题 1
### 备选选题 2

## 9. 推荐判断
- 最推荐推进：
- 推荐理由：
- 主要风险：
- 下一步需要补充：
```

---

## Interaction Rules

- If the user is still designing the workflow itself, ask one decision question at a time.
- If the user wants actual topic selection, execute the workflow directly.
- If the input is too thin, ask the three-question start instead of generating topics immediately.
- If the user provides an article, policy, document, or URL as source material, read/analyze it first and preserve useful knowledge according to the knowledge-wiki rules.
- If current policy, literature, journal, or grant information is needed, use web/search tools; do not fabricate recency.
- Do not include “research draft grill me” as part of the default workflow. Only pressure-test drafts if the user explicitly asks.
- **v1.2 要求**：BLOCKING 产物完成后必须先过 `selection_gate.py`；scan/topics 必须独立审查，
  禁止主线程自审自盖合格章；降级必须留痕，断点续写不得静默绕过上游闸。
