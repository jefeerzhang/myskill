# LobsterAI / OpenClaw 技能包合集

本仓库提供多个可直接导入 LobsterAI / OpenClaw 的技能包，覆盖「文献导读」「开题评审」「基于材料的研究构思」等高频场景。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D16-green.svg)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)

---

## 🎯 技能清单

| 技能包                          |  版本 | 一句话说明                                                | 适用输入            | 关键依赖/可选增强                 | 默认输出                 |
| ------------------------------- | ----: | --------------------------------------------------------- | ------------------- | --------------------------------- | ------------------------ |
| `academic-literature-guide-v2/` | 2.0.0 | PDF/URL → 四层递进式文献导读（直觉→概念→技术→批判）       | PDF、URL、DOI/标题  | MinerU；可做 Web Search 验证      | `./文献导读/`            |
| `proposal-review-expert/`       | 1.0.0 | 开题报告分级评审（本科/硕士/博士）+ 致命伤预警 + 重构建议 | PDF、纯文本         | 可选 MinerU；可选 AnythingLLM RAG | `./开题报告评审/`        |
| `material-ideation/`            |     — | 材料/文件夹 → 研究问题 + 假设 + 识别策略                  | 文件夹、PDF/Word/MD | 依赖本地文件读取；可选 RAG        | `./研究构想/<材料名称>/` |

---

## ✅ 触发条件（除 mineru）

下表来自各技能 `SKILL.md` 中的【触发场景 / 触发关键词】描述，用于你快速判断“该用哪个技能”。

| 技能                                       | 触发场景                                                                  | 触发关键词（示例）                                                                                                                     | 典型指令（示例）                                                                          |
| ------------------------------------------ | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `academic-literature-guide-v2`（文献导读） | 上传 PDF；提供论文链接；请求解读文献；需要文献导读报告                    | 帮我读懂这篇、解读 PDF、生成导读、literature guide、explain this paper、一键导读、自动导读                                             | `帮我解读这篇 PDF：...` / `帮我解读这个链接的论文：...`                                   |
| `proposal-review-expert`（开题评审）       | 上传开题报告 PDF/文本；请求评审开题；开题评估；研究计划审核               | 开题评审、开题报告、评审这个开题、开题评估、proposal review、research proposal、开题答辩、评审 PDF                                     | `评审这份开题报告（硕士层次）...` / `评审这份开题，启用 RAG`                              |
| `material-ideation`（材料构思）            | 用户提供具体材料（文件夹/文件路径），并请求基于材料提出研究问题/假设/识别 | 帮我看看这些材料能做什么研究、基于材料提出研究问题、有什么因果识别思路、从这些文献里提炼研究假设、读一下这个文件夹里的文件帮我构思研究 | `读一下这个文件夹里的文件，帮我构思研究：...` / `基于这些材料提出研究问题与识别策略：...` |

---

## 🚀 安装与验证

### 前置要求

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw) 已安装并运行
- 如需处理 PDF/图片/网页提取：安装 MinerU CLI（`mineru-open-api`）
- 如需 `proposal-review-expert` 启用 RAG：本地或远程可访问的 AnythingLLM（可选）

### 1) 安装 MinerU CLI（推荐）

```bash
npm install -g mineru-open-api
```

macOS/Linux 如遇到权限问题：

```bash
npm install -g mineru-open-api --prefix ~/.local
```

### 2) 安装技能包（复制目录）

macOS / Linux：

```bash
cp -r academic-literature-guide-v2 material-ideation proposal-review-expert ~/Library/Application\ Support/LobsterAI/SKILLs/
```

Windows（PowerShell）：

```powershell
Copy-Item -Path "academic-literature-guide-v2","material-ideation","proposal-review-expert" -Destination "$env:APPDATA\LobsterAI\SKILLs\" -Recurse
```

如果 LobsterAI 已在运行，重启一次以刷新技能列表。

### 3) 验证安装

在 LobsterAI 中分别发送：

```
文献导读技能
```

```
开题报告评审
```

```
材料构思
```

---

## 📖 使用方法（示例）

### 1) 文献导读助手（`academic-literature-guide-v2`）

```
帮我解读这篇 PDF：/path/to/paper.pdf
```

```
帮我解读这个链接的论文：https://arxiv.org/pdf/2509.22186
```

### 2) 开题报告评审专家（`proposal-review-expert`）

```
评审这份开题报告（硕士层次）
[粘贴开题报告全文]
```

```
评审这份开题，启用 RAG
```

### 3) 材料构思（`material-ideation`）

```
读一下这个文件夹里的文件，帮我构思研究：/path/to/materials/
```

```
基于这些材料提出研究问题、假设与识别策略：/path/to/materials/
```

---

## 📦 仓库结构

```
myskill/
├── academic-literature-guide-v2/
├── material-ideation/
├── proposal-review-expert/
├── 安装指南.md
├── 使用说明.md
├── PUSH_GUIDE.md
├── README.md
└── .gitignore
```

---

## 📚 文档入口

| 文档                                                                               | 说明                             |
| ---------------------------------------------------------------------------------- | -------------------------------- |
| [安装指南.md](./安装指南.md)                                                       | 文献导读助手：3 分钟快速安装     |
| [使用说明.md](./使用说明.md)                                                       | 文献导读助手：最佳实践与故障排查 |
| [academic-literature-guide-v2/README.md](./academic-literature-guide-v2/README.md) | 文献导读助手：完整文档           |
| [material-ideation/SKILL.md](./material-ideation/SKILL.md)                         | 材料构思：工作流与输出规范       |
| [proposal-review-expert/README.md](./proposal-review-expert/README.md)             | 开题报告评审专家：完整文档       |

---

## 🔗 相关链接

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw)
- [MinerU](https://mineru.net)
- [ClawHub](https://clawhub.com)
