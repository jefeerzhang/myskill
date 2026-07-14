# myskill - Agent 技能仓库

按目录组织的 Agent 技能包合集。从科研工具起步，现已扩展为四类能力：

- **学术研究与评审** — 文献导读、科研选题、开题评审、同行评议、基金评审
- **写作与去 AI 味** — 公众号长文、英文/中文去 AI 痕迹、经管文献综述
- **方案拷打与对齐** — 高强度追问式设计审查，带文档同步
- **工具与教学** — RAGflow 客户端、Stata coefplot 作图、口播视频制作、Mem0 记忆管理、技能教学

每个子目录都是一个独立技能，核心文件是 `SKILL.md`。不带 `SKILL.md` 的目录不属于技能模块。

## 技能清单

| 目录 | 分类 | 一句话说明 | 典型输入 | 外部依赖 |
|---|---|---|---|---|
| `academic-literature-guide-v2/` | 学术研究 | PDF / URL / DOI 转四层递进式文献导读 | PDF、链接、DOI、标题 | `mineru-open-api` |
| `proposal-review-expert/` | 学术评审 | 开题报告 / 研究计划分层评审 | 开题报告 PDF、纯文本 | 可选 `mineru-open-api` |
| `peer-review/` | 学术评审 | 同行评议、审稿意见回复、基金申请书评审 | 论文全文、审稿意见、基金申请书 | 无 |
| `econ-literature-review-writer/` | 学术写作 | 经济管理类文献综述与 GB/T 7714 参考文献整理 | 文献摘要、笔记、参考文献清单 | 无 |
| `research-topic-selection/` | 学术研究 | AI 辅助科研选题全流程（v1.5.2），含冻结协议、刚性闸门、独立审查、Grill 决策追问、好问题压力测试与断点续写 | 研究兴趣、政策材料、数据基础 | Python 3 |
| `社科基金题目评审/` | 学术申报 | 评审社科基金题目是否规范、清晰、可申报 | 题目候选 | 无 |
| `social-science-fund-topic-guide/` | 学术申报 | 生成 500 字内选题说明 | 题目、问题意识、政策依据 | 无 |
| `ragflow-client/` | 工具 | 调用 RAGflow 知识库问答，结果与网页端一致 | 问题文本、会话 ID | Python 3、RAGflow 服务 |
| `coefplot/` | 工具 | 生成 Stata `coefplot` 回归系数图代码与示例 | 回归模型、作图需求 | Stata、`coefplot` ado |
| `口播视频制作/` | 多媒体 | 文章 / 口播稿转配音动画视频 | 文稿、音色要求、输出目录 | HyperFrames、FFmpeg、MiMo TTS |
| `mem0-memory-flow/` | 工具 / 记忆 | 有审批流程的 Mem0 长期记忆管理 | 待记忆的事实、用户偏好、项目规则 | Python 3、Mem0 API |
| `khazix-writer/` | 写作 | 基于素材生成公众号长文 | brief、链接、PDF、录音转文字 | 无 |
| `avoid-ai-writing/` | 写作 | 英文或通用文本去 AI 味，支持审计和改写 | 文本、文件 | 无 |
| `stop-ai-slop-zh/` | 写作 | 中文文本去 AI 味，六维量规评分 ≥35 | 中文文案、邮件、摘要、长文 | 无 |
| `grill-me/` | 方案评审 | 围绕 plan/design 持续追问，直到对齐 | 计划、设计稿、需求 | 无 |
| `grill-with-docs/` | 方案评审 | 结合项目文档和术语体系拷打方案，同步文档 | 方案、项目文档、术语约定 | 项目上下文 |
| `mattpocock-grilling/` | 方案评审 | 高强度追问式设计审查 | 计划、设计稿 | 无 |
| `teach/` | 教学 | 在当前 workspace 中讲解新技能或概念 | 待讲解的 skill 或概念 | 无 |

## 安装

### 快速安装

把需要的技能目录复制到你的 Agent 技能根目录下。

以 Claude Code / opencode 为例，技能根目录通常是 `~/.config/opencode/skills/`：

```powershell
# Windows
Copy-Item -Path ".\peer-review" -Destination "$env:USERPROFILE\.config\opencode\skills\" -Recurse
Copy-Item -Path ".\stop-ai-slop-zh" -Destination "$env:USERPROFILE\.config\opencode\skills\" -Recurse
```

```bash
# macOS / Linux
cp -r ./peer-review ~/.config/opencode/skills/
cp -r ./stop-ai-slop-zh ~/.config/opencode/skills/
```

### 安装后检查

1. 技能目录下有 `SKILL.md`
2. 客户端已重载或重启
3. 外部依赖已单独安装（参见上表最后一列）

## 快速验证

安装后先测最短触发语，再测完整任务。

```text
文献导读
科研选题
开题评审
同行评议
文献综述
coefplot
ragflow-client
去 AI 味
grill me
teach
口播视频制作
mem0 suggest
```

完整任务示例：

```text
帮我解读这篇 PDF：/path/to/paper.pdf
请把这段中文改得不像 AI 写的，保留原意。
来 grill 一下我这个产品方案。
我在 Stata 里已经跑完回归，请给我一份 coefplot 多模型对比图代码。
把这段对话中的关键偏好记入 Mem0：用户偏好使用英文回答技术问题。
```

## 仓库结构

```text
myskill/
├── academic-literature-guide-v2/      学术文献导读
├── coefplot/                          Stata 回归系数图
├── econ-literature-review-writer/     经管文献综述
├── peer-review/                       同行评议
├── proposal-review-expert/            开题评审
├── research-topic-selection/          科研选题全流程（v1.5.2）
├── social-science-fund-topic-guide/   社科基金选题说明（500 字内）
├── 社科基金题目评审/                  基金题目评审
├── avoid-ai-writing/                  英文去 AI 味
├── stop-ai-slop-zh/                   中文去 AI 味
├── khazix-writer/                     公众号长文
├── grill-me/                          拷打方案（基础版）
├── grill-with-docs/                   拷打方案（带文档同步）
├── mattpocock-grilling/               拷打方案（高强度版）
├── ragflow-client/                    RAGflow 问答客户端
├── mem0-memory-flow/                  Mem0 记忆管理工作流
├── 口播视频制作/                      配音动画视频
└── teach/                             技能教学
```

## 文档入口

| 文档 | 说明 |
|---|---|
| [stop-ai-slop-zh/SKILL.md](./stop-ai-slop-zh/SKILL.md) | 中文去 AI 味定制版（六维量规） |
| [academic-literature-guide-v2/README.md](./academic-literature-guide-v2/README.md) | 文献导读技能说明 |
| [proposal-review-expert/README.md](./proposal-review-expert/README.md) | 开题报告评审说明 |
| [peer-review/README.md](./peer-review/README.md) | 同行评议说明 |
| [peer-review/templates.md](./peer-review/templates.md) | 同行评议输出模板 |
| [peer-review/references.md](./peer-review/references.md) | 同行评议参考清单 |
| [econ-literature-review-writer/README.md](./econ-literature-review-writer/README.md) | 经管类文献综述说明 |
| [coefplot/docs/demo.md](./coefplot/docs/demo.md) | coefplot 场景示例 |
| [ragflow-client/SKILL.md](./ragflow-client/SKILL.md) | RAGflow 客户端说明 |
| [research-topic-selection/README.md](./research-topic-selection/README.md) | 科研选题系统说明（v1.5.2） |
| [research-topic-selection/SKILL.md](./research-topic-selection/SKILL.md) | 科研选题核心流程与闸门规则 |
| [research-topic-selection/references/](./research-topic-selection/references/) | 选题参考文档 |
| [mem0-memory-flow/SKILL.md](./mem0-memory-flow/SKILL.md) | Mem0 记忆管理工作流说明 |

## 说明

- 各技能来源不完全一致，有的目录带 `_meta.json` 元数据文件，有的只有 `SKILL.md`，属于正常情况。
- 敏感配置不要写死在 `SKILL.md` 或脚本里，优先使用环境变量或 `.env.local`。
- 根目录 `README` 只维护总览；具体规则、触发方式和输出格式，以各目录内 `SKILL.md` 为准。
