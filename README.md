# LobsterAI / OpenClaw 技能包合集

本仓库提供 3 个可直接导入 LobsterAI / OpenClaw 的技能包，覆盖「文献导读」「开题评审」「通用文档提取（MinerU）」三个高频场景。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D16-green.svg)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)

---

## 🎯 技能清单

| 技能包                          |  版本 | 一句话说明                                                | 适用输入           | 关键依赖/可选增强                 | 默认输出          |
| ------------------------------- | ----: | --------------------------------------------------------- | ------------------ | --------------------------------- | ----------------- |
| `academic-literature-guide-v2/` | 2.0.0 | PDF/URL → 四层递进式文献导读（直觉→概念→技术→批判）       | PDF、URL、DOI/标题 | MinerU；可做 Web Search 验证      | `./文献导读/`     |
| `proposal-review-expert/`       | 3.0.0 | 开题报告分级评审（本科/硕士/博士）+ 致命伤预警 + 重构建议 | PDF、纯文本        | 可选 MinerU；可选 AnythingLLM RAG | `./开题报告评审/` |
| `mineru-extract/`               | 1.0.7 | 通用文档提取：PDF/图片/网页 → md/html/latex/docx          | PDF、图片、网页    | MinerU CLI（`mineru-open-api`）   | 视命令/参数而定   |

---

## 🆕 更新说明（节选）

- `academic-literature-guide-v2` 2.0：整合 MinerU 提取 + 四层递进导读，补充 LaTeX 公式渲染与模式选择策略（详见 [README.md](./academic-literature-guide-v2/README.md)）
- `proposal-review-expert` 3.0：版本号提升与文档同步（详见 [CHANGES.md](./proposal-review-expert/CHANGES.md)）
- 新增：`mineru-extract` 技能包（MinerU 通用提取工作流封装）

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
cp -r academic-literature-guide-v2 proposal-review-expert mineru-extract ~/Library/Application\ Support/LobsterAI/SKILLs/
```

Windows（PowerShell）：

```powershell
Copy-Item -Path "academic-literature-guide-v2","proposal-review-expert","mineru-extract" -Destination "$env:APPDATA\LobsterAI\SKILLs\" -Recurse
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
mineru
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

### 3) MinerU 通用提取（`mineru-extract`）

```
用 mineru 把这个 PDF 提取成 Markdown：/path/to/file.pdf
```

---

## 📦 仓库结构

```
myskill/
├── academic-literature-guide-v2/
├── proposal-review-expert/
├── mineru-extract/
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
| [proposal-review-expert/README.md](./proposal-review-expert/README.md)             | 开题报告评审专家：完整文档       |
| [mineru-extract/SKILL.md](./mineru-extract/SKILL.md)                               | MinerU 通用提取：命令与能力清单  |

---

## 🔗 相关链接

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw)
- [MinerU](https://mineru.net)
- [ClawHub](https://clawhub.com)
