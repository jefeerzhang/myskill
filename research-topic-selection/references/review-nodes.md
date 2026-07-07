# 选题审查节点规则（v1.1）

> **加载时机**：执行 scan / topics 任一审查节点前。
> **审查分离原则**：选题技能只有两道 critical 闸（scan、topics），均强制 independent 审查；
> 其余阶段（三问/澄清/趋势/缺口）由主线程自检，不强制独立审查。

## 一、审查者与档位

| node   | 最低档位     | 说明 |
|--------|--------------|------|
| scan   | independent  | critical：五维扫描是否覆盖、是否确认偏差、问题域地图是否成立 |
| topics | independent  | critical：缺口是否真实、3+2 推荐是否可执、判断是否自洽 |

- **审查者永远 ≠ 产出者**：independent 档指在本地 GenericAgent 下用**独立上下文 / 独立模型调用**执行审查，
  其上下文不含产出过程（不读主线程中间草稿，只读落盘产物）。
- `reviewer_agent_id` / `producer_agent_id` 必须如实填写且不相等（selection_gate 字段级校验）。
- 不依赖 codex-verify 等外部受控 runner；本地可用 subagent 机制或另起会话承担 independent 审查。

## 二、审查者输出（verdict JSON 模板）

审查者在报告末尾必须附一个 fenced JSON 块，主线程**原样**保存两份：
- 完整原始输出 → `review/transcripts/<node>_r<round>.md`
- fenced JSON 块 → `review/review_<node>.json`，仅允许主线程落盘时追加一个字段
  `agent_output_sha256`（= transcript 文件的 sha256）。

```json
{
  "node": "scan",
  "workdir": "/abs/path/to/workdir",
  "reviewer_kind": "independent",
  "reviewer_model": "模型标识",
  "reviewer_agent_id": "reviewer-session-xxx",
  "producer_agent_id": "main-thread-yyy",
  "verdict": "PASS",
  "p0_open": 0,
  "p0": [],
  "p1": [{"id": "P1-1", "issue": "..."}],
  "round": 1,
  "re_reviewed_dispositions": true,
  "artifact_hashes": {
    "03_五维扫描.md": "<sha256>",
    "04_问题域地图.md": "<sha256>"
  },
  "history": [
    {"round": 1, "p0_found": 0, "p0_open": 0, "p0_ids": []}
  ]
}
```

要点：
- `artifact_hashes` 由**审查者本人**对它实际读到的产物计算（shell `sha256sum` 或等价），
  逐文件填写——声明"我审的就是这一版"。selection_gate 会与当前文件实算值比对，
  防旧 verdict 重放、防审后再改产物。
- 各节点绑定文件以 `scripts/selection_gate.py` 的 `REVIEW_BINDINGS` 为准
  （scan → 03_五维扫描.md + 04_问题域地图.md；topics → 07_核心缺口.md + 08_选题推荐.md）。
- `history` 每轮如实记录；`p0_found > 0` 的轮必须列 `p0_ids`。

## 三、处置闭环（禁自审的核心）

审查报 P0 后：
1. 执行者逐条处置，写 `review/dispositions_<node>.json`：
   ```json
   {"findings": [{"id": "P0-1", "status": "已修正", "evidence": "修正说明/diff/新值",
                  "reviewer_decision": null}]}
   ```
   status ∈ 已修正（附修正内容）/ 反驳成立（附证据，如检索记录、原文截图）/ 不适用（附理由）。
2. **回送原审查者复核**：审查者逐条裁决 `reviewer_decision: accepted | rejected`，
   写回 `review/dispositions_<node>.json`。rejected 的 P0 必须重新修正并再审。
3. 回环有界：单节点 round ≤ 3（selection_gate 超界 exit 3，升级人类裁决，不许自动重试）。

## 四、审查关注点清单（选题专用）

**scan 节点：**
- 五维是否齐全（政策/文献/实践/数据/窗口），无维度仅写"暂无"。
- 是否确认偏差：扫描是否只找支持预设方向的证据，忽略反面/竞争性解释。
- 文献是否虚构/过期：引用政策/文献须标出来源与时效，禁止编造近期性。
- 问题域地图是否成立：核心问题↔学术分支↔数据↔切口是否自洽、是否过度发散。

**topics 节点：**
- 缺口是否真实：1–3 个核心缺口须有"既有研究已解释 / 仍不足 / 为何重要"三段支撑。
- 3+2 是否可执：每个选题的数据/方法路径是否具体、是否与用户基础匹配。
- 判断是否自洽：优先/可以/谨慎/暂缓的分级理由是否一致，最推荐项是否有压倒性依据。
- 去 AI 味：中文表述是否落入模板腔（参考本地 writing_principles_sop）。

## 五、信任边界（如实声明）

本机制只校验字段与 hash 绑定，**不提供密码学身份保证**。蓄意伪造一整套自洽
transcript + verdict + 匹配 hash 仍是可能的（v1.1 级残留）。
彻底闭合需受控 runner 外部登记审查行为，超出本技能范围。
