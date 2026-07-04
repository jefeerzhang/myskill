# myskill 技能库

这是一个按目录组织的 Agent Skills 仓库。当前内容已经不再只是“科研技能包”，而是扩展成四类能力：

- 学术研究与评审
- 写作与去 AI 味
- 方案 / 设计拷打与对齐
- 教学与讲解

每个子目录基本都是一个可独立安装的技能，核心文件是 `SKILL.md`。少数目录还带 `_meta.json` 或 `_skillhub_meta.json`，这些文件也应随技能目录一起保留。

## 技能清单

| 目录 | 类型 | 一句话说明 | 典型输入 | 主要依赖 |
| --- | --- | --- | --- | --- |
| `academic-literature-guide-v2/` | 学术研究 | PDF / URL / DOI 转四层递进式文献导读 | PDF、链接、DOI、标题 | `mineru-open-api` |
| `material-ideation/` | 学术研究 | 从材料中提炼研究问题、假设和识别策略 | 文件夹、PDF、Word、Markdown | 本地文件读取，可选 RAG |
| `proposal-review-expert/` | 学术评审 | 开题报告 / 研究计划分层评审 | 开题报告 PDF、纯文本 | 可选 `mineru-open-api` |
| `peer-review/` | 学术评审 | 同行评议、审稿意见回复、基金申请书评审 | 论文全文、审稿意见、基金申请书 | 无强制外部依赖 |
| `econ-literature-review-writer/` | 学术写作 | 经济管理类文献综述与 GB/T 7714 参考文献整理 | 文献摘要、笔记、参考文献清单 | 无强制外部依赖 |
| `社科基金题目评审/` | 学术申报 | 评审社科基金题目是否规范、清晰、可申报 | 题目候选 | 无强制外部依赖 |
| `社科基金选题说明撰写指南/` | 学术申报 | 生成 500 字内选题说明 | 题目、问题意识、政策依据 | 无强制外部依赖 |
| `ragflow-client/` | 工具 | 调用 RAGflow 知识库问答，支持原生对话 API | 问题文本、会话 ID | Python 3、RAGflow 服务 |
| `coefplot/` | 工具 | 生成 Stata `coefplot` 回归系数图代码与示例 | 回归模型、作图需求 | Stata、`coefplot` ado |
| `口播视频制作/` | 多媒体 | 文章 / 口播稿转配音动画视频 | 文稿、音色要求、输出目录 | HyperFrames、FFmpeg、MiMo TTS |
| `khazix-writer/` | 写作 | 基于素材生成公众号长文 | brief、链接、PDF、录音转文字 | 无强制外部依赖 |
| `avoid-ai-writing/` | 写作 | 英文或通用文本去 AI 味，支持审计和改写 | 文本、文件 | 无强制外部依赖 |
| `stop-ai-slop-zh/` | 写作 | 中文文本去 AI 味，清理套话、排比和八股 | 中文文案、邮件、摘要、长文 | 无强制外部依赖 |
| `grill-me/` | 方案评审 | 围绕 plan / design 持续追问，直到对齐 | 计划、设计稿、需求 | 无强制外部依赖 |
| `grill-with-docs/` | 方案评审 | 结合项目文档和术语体系拷打方案，并同步文档 | 方案、项目文档、术语约定 | 依赖项目上下文 |
| `mattpocock-grilling/` | 方案评审 | 高强度追问式设计审查 | 计划、设计稿 | 无强制外部依赖 |
| `teach/` | 教学 | 在当前 workspace 中讲解一个新 skill 或概念 | 问题、主题、代码上下文 | 无强制外部依赖 |

## 怎么选技能

### 1. 做研究 / 写论文 / 做申报

推荐路线：

1. `material-ideation`：从材料中找研究问题。
2. `academic-literature-guide-v2`：快速读懂关键论文。
3. `proposal-review-expert`：在开题阶段做结构性评审。
4. `peer-review`：在投稿或返修阶段做同行评议。
5. `econ-literature-review-writer`：整理文献综述。
6. `社科基金题目评审` + `社科基金选题说明撰写指南`：基金申报场景。

### 2. 改写文本 / 去 AI 味

- 英文或通用文本：`avoid-ai-writing`
- 中文文本：`stop-ai-slop-zh`
- 公众号长文成稿：`khazix-writer`

### 3. 拷打计划 / 对齐设计

- 一般性的“来拷打我这个方案”：`grill-me`
- 需要结合项目术语和文档：`grill-with-docs`
- 想用更直接的 Matt Pocock 风格 grilling：`mattpocock-grilling`

### 4. 工具或多媒体任务

- 知识库问答：`ragflow-client`
- Stata 系数图：`coefplot`
- 文章转视频：`口播视频制作`
- 教人理解某个概念或 skill：`teach`

## 安装方式

这个仓库不是单体程序，而是一组独立技能目录。正确做法是按需安装单个技能，而不是把整个仓库当成一个包。

### 推荐方式：导入单个技能目录

适用于支持“导入 Skill / 导入本地目录”的客户端。

安装原则：

1. 只选择你要用的那个目录。
2. 目录根级必须直接包含 `SKILL.md`。
3. 如果目录里还有 `README.md`、`_meta.json`、`_skillhub_meta.json`，一并保留。

示例：

- 安装同行评议：导入 `peer-review/`
- 安装文献导读：导入 `academic-literature-guide-v2/`
- 安装中文去 AI 味：导入 `stop-ai-slop-zh/`
- 安装方案拷打：导入 `grill-me/`

### 手动复制方式

如果你的客户端不支持可视化导入，就把“某个技能目录”完整复制到客户端自己的 `skills` 目录。

正确结构应类似：

```text
skills/
└── peer-review/
    ├── SKILL.md
    ├── README.md
    └── _skillhub_meta.json
```

不要复制成这样：

```text
skills/
└── myskill/
    └── peer-review/
        └── SKILL.md
```

Windows PowerShell 示例：

```powershell
Copy-Item -Path ".\peer-review" -Destination "<你的 skills 目录>" -Recurse
Copy-Item -Path ".\stop-ai-slop-zh" -Destination "<你的 skills 目录>" -Recurse
```

macOS / Linux 示例：

```bash
cp -r ./peer-review "<你的 skills 目录>/"
cp -r ./stop-ai-slop-zh "<你的 skills 目录>/"
```

### 安装后检查

安装完成后，确认这几件事：

1. 技能目录下有 `SKILL.md`
2. 客户端已经重载或重启
3. 技能所需依赖已单独安装，例如 `mineru-open-api`、Python、Stata、FFmpeg、HyperFrames

## 快速验证

安装后先测最短触发语，再测完整任务。

```text
文献导读
开题评审
同行评议
文献综述
coefplot
ragflow-client
去 AI 味
grill me
teach
口播视频制作
```

完整任务示例：

```text
帮我解读这篇 PDF：/path/to/paper.pdf
```

```text
请把这段中文改得不像 AI 写的，保留原意。
```

```text
来 grill 一下我这个产品方案。
```

```text
我在 Stata 里已经跑完回归，请给我一份 coefplot 多模型对比图代码。
```

## 仓库结构

```text
myskill/
├── academic-literature-guide-v2/
├── avoid-ai-writing/
├── coefplot/
├── econ-literature-review-writer/
├── grill-me/
├── grill-with-docs/
├── khazix-writer/
├── material-ideation/
├── mattpocock-grilling/
├── peer-review/
├── proposal-review-expert/
├── ragflow-client/
├── stop-ai-slop-zh/
├── teach/
├── 口播视频制作/
├── 社科基金选题说明撰写指南/
└── 社科基金题目评审/
```

## 文档入口

当前仓库里有额外说明文档的目录主要是这些：

| 文档 | 说明 |
| --- | --- |
| [academic-literature-guide-v2/README.md](./academic-literature-guide-v2/README.md) | 文献导读技能说明 |
| [proposal-review-expert/README.md](./proposal-review-expert/README.md) | 开题报告评审说明 |
| [peer-review/README.md](./peer-review/README.md) | 同行评议说明 |
| [peer-review/templates.md](./peer-review/templates.md) | 同行评议输出模板 |
| [peer-review/references.md](./peer-review/references.md) | 同行评议参考清单 |
| [econ-literature-review-writer/README.md](./econ-literature-review-writer/README.md) | 经管类文献综述说明 |
| [coefplot/docs/demo.md](./coefplot/docs/demo.md) | `coefplot` 场景示例 |
| [ragflow-client/SKILL.md](./ragflow-client/SKILL.md) | RAGflow 客户端说明 |

## 说明

- 仓库中不同技能来源并不完全一致，有的目录带元数据文件，有的只有 `SKILL.md`，这是正常的。
- 敏感配置不要写死在 `SKILL.md` 或脚本里，优先使用环境变量或本地配置文件。
- 根 `README` 只维护总览；具体规则、触发方式和输出格式，以各目录内的 `SKILL.md` 为准。
