# 📚 文献导读助手 - 精简版

> **一键完成「PDF 提取→文献导读」全流程**  
> 让学术论文阅读效率提升 300% 🚀

## 🎯 项目简介

文献导读助手是一个专为科研人员、研究生和学术爱好者设计的全自动文献解读工具。只需提供 PDF 文件或论文链接，即可自动生成**四层递进式导读报告**，帮助你快速理解论文核心内容。

### 核心功能

| 功能 | 说明 | 优势 |
|------|------|------|
| **PDF 自动提取** | 使用 MinerU 将 PDF 转换为 Markdown | 支持表格、公式、OCR 识别 |
| **4 层递进导读** | 直觉层→概念层→技术层→批判层 | 由浅入深，适合不同水平的读者 |
| **LaTeX 公式渲染** | 自动保留原文的数学公式格式 | 完美支持理工科论文 |
| **智能模式选择** | 根据文件大小自动选择提取模式 | 小文件快速处理，大文件精确提取 |
| **知识族谱图** | 自动生成论文的知识脉络关系图 | 快速定位论文在领域中的位置 |
| **一键输出** | 自动保存到指定目录 | 无需手动配置，开箱即用 |

---

## 🚀 快速开始

### 前置要求

- [OpenClaw / LobsterAI](https://github.com/openclaw/openclaw) - 已安装并运行
- [Node.js](https://nodejs.org/) - v16 或更高版本
- [MinerU CLI](https://mineru.net) - PDF 提取工具

### 1. 安装 MinerU CLI

```bash
# 所有平台
npm install -g mineru-open-api

# macOS/Linux 如遇到权限问题
npm install -g mineru-open-api --prefix ~/.local
```

### 2. 安装技能

**macOS / Linux**:
```bash
cp -r academic-literature-guide-v2 ~/Library/Application\ Support/LobsterAI/SKILLs/
```

**Windows** (PowerShell):
```powershell
Copy-Item -Path "academic-literature-guide-v2" -Destination "$env:APPDATA\LobsterAI\SKILLs\" -Recurse
```

### 3. 配置 API Token（可选）

```bash
# 获取 Token: https://mineru.net/apiManage/token
mineru-open-api auth
```

### 4. 验证安装

在 LobsterAI 中发送：
```
文献导读技能
```

---

## 📖 使用方法

### 基本用法

**本地 PDF 文件**:
```
帮我解读这篇 PDF：/path/to/paper.pdf
```

**URL 链接**:
```
帮我解读这个链接的论文：https://arxiv.org/pdf/2509.22186
```

**DOI 或标题**:
```
帮我生成 10.1080/xxxx 这篇论文的导读
```

### 输出示例

技能会自动生成四层递进式导读报告：

1. **🟢 直觉层** - 用生活场景理解问题
2. **🔵 概念层** - 引入必要术语
3. **🟡 技术层** - 拆解研究方法
4. **🔴 批判层** - 培养科学怀疑精神

报告自动保存到 `./文献导读/` 目录。

---

## ⚡ 两种提取模式

| 特性 | flash-extract | extract |
|------|--------------|---------|
| 适用场景 | 小文件（<10MB, <20 页） | 大文件或复杂排版 |
| 速度 | 快（5-10 秒/页） | 中等（10-30 秒/页） |
| 精度 | 标准 | 高精度 |
| Token | ❌ 无需 | ✅ 需要 |
| 成本 | 免费 | 免费配额 + 付费 |

**建议**：首次使用可先试用 flash-extract，需要时再配置 Token。

---

## 🛠️ 故障排查

### 问题 1: 安装时提示权限不足

**macOS/Linux**:
```bash
npm install -g mineru-open-api --prefix ~/.local
```

**Windows**:
- 以管理员身份运行 PowerShell
- 或修改 npm 全局目录权限

### 问题 2: 提取内容为空

可能原因：
- PDF 加密或损坏
- 纯图片扫描件
- 网络连接问题

解决方案：
1. 检查 PDF 是否可正常打开
2. 尝试 extract 模式（支持 OCR）
3. 检查网络连接

### 问题 3: 公式显示异常

确保你的 Markdown 阅读器支持 LaTeX 渲染：
- VS Code + Markdown All in One 插件 ✅
- Typora ✅
- Obsidian ✅

---

**Made with ❤️ for researchers worldwide**
