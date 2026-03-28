# LobsterAI 技能合集：文献导读助手 & 开题报告评审专家

> 本仓库包含两个可导入 LobsterAI / OpenClaw 的技能：
> - `academic-literature-guide-v2`：PDF/URL → 四层递进式文献导读（依赖 MinerU，可做 Web Search 验证）
> - `proposal-review-expert`：开题报告分级评审（本科/硕士/博士，可选 AnythingLLM RAG 验证）

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/node-%3E%3D16-green.svg)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](#)

---

## 🎯 技能清单

| 技能目录/包                     |  版本 | 简介                                                 | 处理 PDF       | 可选增强        | 默认输出目录      |
| ------------------------------- | ----: | ---------------------------------------------------- | -------------- | --------------- | ----------------- |
| `academic-literature-guide-v2/` | 2.0.0 | 文献导读：直觉层→概念层→技术层→批判层                | MinerU         | Web Search 验证 | `./文献导读/`     |
| `proposal-review-expert/`       | 2.0.0 | 开题评审：按学位层级动态标准 + 致命伤预警 + 重构建议 | MinerU（可选） | AnythingLLM RAG | `./开题报告评审/` |

## 🆕 proposal-review-expert 2.0 更新要点

- 新增：AnythingLLM RAG 文献专项验证流程（可选启用）
- 增强：评审报告中更系统地呈现“文献对照/致命伤证据/补充文献建议”
- 增强：提供 `rag_query.py` 工具脚本与可复用的检索输出格式

---

## 🚀 快速开始

### 前置要求

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw) 已安装并运行
- [Node.js](https://nodejs.org/) v16 或更高版本（仅在需要安装 MinerU CLI 时）
- [MinerU CLI](https://mineru.net)（可选，但建议安装：两项技能在处理 PDF 时会用到）
- AnythingLLM（可选：仅 `proposal-review-expert` 启用 RAG 时使用）

### 1) 安装 MinerU CLI（可选但建议）

```bash
npm install -g mineru-open-api
```

macOS/Linux 如遇到权限问题：

```bash
npm install -g mineru-open-api --prefix ~/.local
```

### 2) 安装技能

#### 安装 `academic-literature-guide-v2`（文件夹形式）

macOS / Linux：

```bash
cp -r academic-literature-guide-v2 ~/Library/Application\ Support/LobsterAI/SKILLs/
```

Windows（PowerShell）：

```powershell
Copy-Item -Path "academic-literature-guide-v2" -Destination "$env:APPDATA\LobsterAI\SKILLs\" -Recurse
```

#### 安装 `proposal-review-expert`（文件夹形式）

macOS / Linux：

```bash
cp -r proposal-review-expert ~/Library/Application\ Support/LobsterAI/SKILLs/
```

Windows（PowerShell）：

```powershell
Copy-Item -Path "proposal-review-expert" -Destination "$env:APPDATA\LobsterAI\SKILLs\" -Recurse
```

安装后如 LobsterAI 已在运行，重启一次以刷新技能列表。

### 3) 配置 MinerU Token（可选）

如果你需要使用 MinerU 的高精度提取模式（例如大文件、复杂排版、OCR），先获取 Token 并配置：

```bash
mineru-open-api auth
```

### 4) 验证安装

在 LobsterAI 中分别发送：

```
文献导读技能
```

```
开题报告评审
```

---

## 📖 使用方法

### 技能 1：文献导读助手（`academic-literature-guide-v2`）

本地 PDF 文件：

```
帮我解读这篇 PDF：/path/to/paper.pdf
```

URL 链接：

```
帮我解读这个链接的论文：https://arxiv.org/pdf/2509.22186
```

DOI 或标题：

```
帮我生成 10.1080/xxxx 这篇论文的导读
```

输出（默认）：
- 自动保存到 `./文献导读/`

### 技能 2：开题报告评审专家（`proposal-review-expert`）

评审 PDF：

```
评审这份开题报告 PDF：C:\Users\...\开题报告.pdf
```

评审文本：

```
评审这份开题报告（硕士层次）
[粘贴开题报告全文]
```

启用 RAG（AnythingLLM）：

```
评审这份开题，启用 RAG
```

输出（默认）：
- 自动保存到 `./开题报告评审/`

---

## 📦 项目结构

```
myskill/
├── academic-literature-guide-v2/       # 技能：文献导读助手（目录）
├── proposal-review-expert/             # 技能：开题报告评审专家（目录）
├── 安装指南.md                          # 文献导读助手：3 分钟快速安装
├── 使用说明.md                          # 文献导读助手：最佳实践与故障排查
├── PUSH_GUIDE.md                        # 推送到 GitHub 的指引
├── README.md                            # 本文件
└── .gitignore
```

---

## ⚡ MinerU 两种提取模式（适用于 PDF 场景）

| 特性     | flash-extract           | extract             |
| -------- | ----------------------- | ------------------- |
| 适用场景 | 小文件（<10MB, <20 页） | 大文件或复杂排版    |
| 速度     | 快（5-10 秒/页）        | 中等（10-30 秒/页） |
| 精度     | 标准                    | 高精度              |
| Token    | 无需                    | 需要                |
| 成本     | 免费                    | 免费配额 + 付费     |

建议：首次使用可先试用 flash-extract，需要时再配置 Token。

---

## 🛠️ 故障排查

### 问题 1：安装 MinerU 时提示权限不足

macOS/Linux：

```bash
npm install -g mineru-open-api --prefix ~/.local
```

Windows：
- 以管理员身份运行 PowerShell
- 或修改 npm 全局目录权限

### 问题 2：PDF 提取内容为空

可能原因：
- PDF 加密或损坏
- 纯图片扫描件
- 网络连接问题

解决方案：
1. 检查 PDF 是否可正常打开
2. 尝试 extract 模式（支持 OCR）
3. 检查网络连接

### 问题 3：公式显示异常

确保你的 Markdown 阅读器支持 LaTeX 渲染：
- VS Code + Markdown All in One 插件
- Typora
- Obsidian

---

## 📚 文档

| 文档                                                                               | 说明                             |
| ---------------------------------------------------------------------------------- | -------------------------------- |
| [安装指南.md](./安装指南.md)                                                       | 文献导读助手：3 分钟快速安装     |
| [使用说明.md](./使用说明.md)                                                       | 文献导读助手：最佳实践与故障排查 |
| [academic-literature-guide-v2/README.md](./academic-literature-guide-v2/README.md) | 文献导读助手：完整文档           |
| [proposal-review-expert/README.md](./proposal-review-expert/README.md)             | 开题报告评审专家：完整文档       |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 提交规范

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链相关

---

## 📄 许可证

本项目基于 MIT 许可证开源。

```
MIT License

Copyright (c) 2026 LobsterAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🔗 相关链接

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw)
- [MinerU](https://mineru.net)
- [ClawHub](https://clawhub.com)
