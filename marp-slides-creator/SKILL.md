---
name: marp-slides-creator
description: 专业Marp演示文稿制作助手。提供简洁工作流程：内容分析、slides制作、多维度审阅、终稿输出。所有产出物保存在项目工作文件夹的05_final目录中。当用户提到"制作slides"、"做PPT"、"演示文稿"、"Marp"、"幻灯片"、"presentation"等关键词时自动启用。Professional Marp presentation assistant with streamlined workflow: content analysis, slide creation, multi-dimensional review, and final output. All outputs saved in 05_final directory.
allowed-tools: Read, Write, Edit, Bash, Task, Glob
---

# Marp Slides 制作助手

## 技能概述

本技能提供简洁的Marp演示文稿制作流程：内容分析、slides制作、多维度审阅、终稿输出。对于中文演示文稿，额外包含中文语言规范审阅阶段。所有产出物保存在项目工作文件夹的05_final目录中。

**支持多种主题风格**：内置 15 款精选主题，涵盖学术、商务、创意等场景。详见 `themes/README.md`。

## 核心原则

### Slides设计原则

| 原则 | 说明 | 要点 |
|------|------|------|
| 一页一点 | 每页只讲一个核心观点 | 避免信息过载 |
| 视觉层次 | 标题→要点→细节 | 使用粗体、列表、引用区分 |
| 留白充足 | 内容不超过页面60% | 给观众呼吸空间 |
| 文字精简 | 每页文字不超过8行 | 关键词优于完整句子 |

### 内容密度控制

- **标题页**：主标题 + 副标题 + 作者信息
- **内容页**：标题 + 3-5个要点（每点1-2行）
- **对比页**：两栏对比，每栏不超过4点
- **总结页**：3-5个核心要点

### 字体大小规范

不同主题字体大小差显著，制作时需根据主题调整：

| 元素 | 推荐范围 | 说明 |
|------|----------|------|
| 标题页标题 | 40-60px / 2.5-3em | 主标题醒目 |
| 内容页标题 | 24-32px / 1.5-2em | 避免过大 |
| 正文内容 | 18-24px / 1-1.4em | 阅读舒适 |
| 要点列表 | 16-20px / 0.9-1.1em | 略小于正文 |
| 引用块 | 16-20px / 0.9-1.1em | 与列表相近 |
| 注释/页脚 | 12-14px / 0.7-0.8em | 最小字号 |

**各主题字体大小参考**：

| 主题 | 正文字号 | 标题字号 | 备注 |
|------|----------|----------|------|
| companySZ | 23-24px | 36-40px | 企业正式风格 |
| companyLightBlue | 21-23px | 36-40px | 企业清新风格 |
| zju | 21-24px | 36px | 浙大官方风格 |
| jobs | 34px | 48px+ | 发布会风格，字号偏大 |
| turing | 27-32px | 46px | 技术风格 |
| einstein | 27px | 32px | 科学风格 |
| academic | 0.9-1em | - | 使用相对单位 |
| beam | 0.6-0.65em | - | 最小字号主题 |
| graph_paper | 0.65-0.9em | - | 手写笔记感 |
| simple | 100% | 200% | 极简风格 |
| gaia | 1-1.5em | 1.5em | 自定义主题 |

**安全值**：内容页正文不低于 `0.9em`（约14-16px），确保可读性。

**警告值**：低于 `0.7em`（约11px）可能导致阅读困难。

> 注：Marp 默认 1em ≈ 20px。实际像素值取决于主题基础设置。

## 四阶段工作流程

严格按照以下流程执行，每阶段结束后询问用户确认：

### 阶段一：工作空间初始化与主题选择

**触发**：用户请求制作slides时立即执行

**执行步骤**：

1. **确定项目名称**：
   - 根据用户提供的主题/文件名确定项目名称
   - 使用简短的英文或拼音命名，用连字符连接
   - 示例：`academic-writing`、`ai-introduction`、`product-launch`

2. **创建工作文件夹结构**：
   ```bash
   # 创建主工作文件夹
   mkdir -p slides_[项目名]/05_final
   ```

3. **文件夹结构说明**：

   ```text
   slides_[项目名]/
   └── 05_final/              # 最终产出
       ├── presentation.md       # 最终Markdown
       ├── slides.html           # HTML版本
       └── slides.pdf            # PDF版本
   ```

4. **主题选择**：

   使用 question 工具让用户选择主题风格：

   ```
   questions:
     - question: "请选择演示文稿的主题风格"
       header: "主题风格"
       multiSelect: false
       options:
         - label: "academic (学术风格)"
           description: "适合学术报告、论文答辩，maroon红色标题栏"
         - label: "beam (Beamer风格)"
           description: "仿LaTeX Beamer，适合学术演讲、技术研讨"
         - label: "jobs (乔布斯风格)"
           description: "Apple发布会风格，适合产品发布、商业演示"
         - label: "graph_paper (方格纸风格)"
           description: "技术分享、教学演示，手写笔记感"
         - label: "gaia (自定义主题)"
           description: "商务风格，Times New Roman + 宋体，蓝色下划线"
         - label: "companyLightBlue (企业浅蓝)"
           description: "清新浅蓝配色，专业商务风格"
         - label: "companySZ (企业深色)"
           description: "深色企业风格，正式庄重"
         - label: "zju (浙大风格)"
           description: "浙江大学官方配色，高校学术演示"
         - label: "turing (图灵风格)"
           description: "计算机科学、技术主题"
         - label: "simple (极简风格)"
           description: "极简设计，最少装饰"
         - label: "gradient (渐变背景)"
           description: "现代感渐变背景，创意展示"
         - label: "socrates (苏格拉底风格)"
           description: "哲学、人文学科演示"
         - label: "einstein (爱因斯坦风格)"
           description: "科学、物理学演示"
         - label: "border (边框简约)"
           description: "简约边框装饰，通用演示"
         - label: "academic-lightblue (学术浅蓝)"
           description: "学术风格浅蓝配色"
   ```

   **主题文件位置**：`themes/` 目录下所有 `.css` 文件

**输出**：工作文件夹路径、选择的主题名称，告知用户所有产出物将保存在此文件夹中

---

### 阶段二：内容分析与消化

**触发**：工作空间创建完成后，用户提供输入文件（PDF、论文、文档、笔记等）

**执行步骤**：

1. **初步阅读**：使用 Read 工具读取输入文件，了解整体结构
2. **深度分析**：
   - 提取核心论点和关键信息
   - 识别逻辑结构（问题-方案-结论 / 现状-分析-建议 等）
   - 标记重要数据、引用、案例
3. **内容分类**：
   - 核心观点（必须包含）
   - 支撑证据（选择性包含）
   - 背景信息（简化或省略）
4. **大纲生成**：
   - 确定slides数量（建议10-20页）
   - 规划每页主题和内容密度
   - 设计叙事流程

**输出**：直接向用户展示内容分析和大纲，请用户确认后继续

### 阶段三：Slides制作

**触发**：用户确认内容分析和大纲

**执行步骤**：

1. **读取模板**：使用 Read 工具读取 `marp-template.md`
2. **应用主题**：
   - 在 YAML frontmatter 中设置用户选择的主题：
     ```yaml
     ---
     marp: true
     theme: [用户选择的主题名]
     ---
     ```
   - 不同主题可能支持特殊的 class，参考 `themes/README.md`

3. **主题适配（自动调整）**：

   不同主题对标题格式有不同要求，制作 slides 时必须根据主题自动调整：

   | 主题 | 内容页标题格式 | 说明 |
   |------|----------------|------|
   | **beam** | `#` (h1) | h1 显示在顶部蓝色条中 |
   | **academic** | `#` (h1) | h1 用于页面标题 |
   | **jobs** | `#` (h1) | h1 有特殊下划线样式 |
   | **gaia** | `##` (h2) | h2 带蓝色下划线装饰 |
   | graph_paper | `##` (h2) | 标准 h2 标题 |
   | simple | `##` (h2) | 标准 h2 标题 |
   | companyLightBlue | `##` (h2) | 企业浅蓝风格 |
   | companySZ | `##` (h2) | 企业深色风格 |
   | zju | `##` (h2) | 浙大官方风格 |
   | turing | `##` (h2) | 图灵风格 |
   | gradient | `##` (h2) | 渐变背景风格 |
   | socrates | `##` (h2) | 苏格拉底风格 |
   | einstein | `##` (h2) | 爱因斯坦风格 |
   | border | `##` (h2) | 边框简约风格 |
   | academic-lightblue | `##` (h2) | 学术浅蓝风格 |

   **beam 主题特殊处理**：
   - 每页第一个 `#` (h1) 会自动显示在顶部蓝色装饰条中
   - 标题页使用 `<!-- _class: title -->` 指令
   - 内容页直接使用 `#` 标题（不是 `##`）
   - 示例：
     ```markdown
     ---
     # 页面标题在蓝色条中

     正文内容...
     ```

   **academic/jobs 主题特殊处理**：
   - 同样使用 `#` (h1) 作为页面标题
   - 支持 `class: lead` 用于特殊页面

   **gaia 主题特殊处理**：
   - 使用 `##` (h2) 作为内容页标题，带蓝色下划线装饰
   - 字体：Times New Roman（英文）、SimSun（中文）
   - 支持 `class: lead` 用于标题页
   - 适合商务演示、学术报告

4. **必须包含居中样式**：frontmatter 的 `style` 中必须包含以下 CSS，否则图片和表格会左对齐：
     ```css
     /* 图片居中 */
     img {
       display: block !important;
       margin: 0 auto !important;
     }
     /* 表格居中（覆盖主题的 width:100% 和 display:block） */
     section table {
       display: table !important;
       width: auto !important;
       margin-left: auto !important;
       margin-right: auto !important;
     }
     ```
     > **原因**：Marp 基础 CSS 设置 `section table { display: block; width: max-content }`，多数自定义主题又设置 `table { width: 100% }`，两者都会导致表格无法居中。必须用 `!important` 同时覆盖 `display`、`width` 和 `margin` 三个属性才能生效。`marp-template.md` 已包含这些样式。

5. **修改Header**：根据演讲主题调整
6. **逐页制作**：
   - 遵循模板中的页面类型和格式
   - 每页严格控制内容量
   - 使用适当的Markdown格式（粗体、引用、列表）

**页面类型选择**（参考 `references/slide-types.md`）：

- 标题页：开场
- 目录页：内容预告
- 单点页：核心观点展示
- 列表页：多要点展示
- 对比页：两种观点/方案对比
- 引用页：重要引用展示
- 分隔页：章节过渡
- 总结页：要点回顾

**文件保存**：

- 保存初稿：`slides_[项目名]/05_final/presentation.md`

### 阶段四：多维度审阅

**触发**：初稿完成后自动进入

**执行方式**：使用 Task 工具并行派遣4个专业agent，每个负责一个审阅维度

**并行Agent部署**：

在单个消息中同时发起4个Task调用，设置 run_in_background=true。各 Agent 需将审阅报告写入 `slides_[项目名]/review_agent_N.txt`（N为1-4），主流程依次读取汇总。
```

#### Agent 1：内容审阅专家

```
Task 工具参数：
- subagent_type: "general-purpose"
- run_in_background: true
- prompt:

你是一个内容审阅专家。请对比审阅slides内容。

## 输入材料

### 用户原始输入文件
[插入用户提供的原始文件内容]

### 用户的具体要求
[插入用户提出的要求和偏好]

### 制作的Slides初稿
[插入presentation.md内容]

## 审阅任务

1. **完整性检查**：
   - 原始材料中的核心论点是否都已体现？
   - 是否有重要信息被遗漏？
   - 列出遗漏的关键内容

2. **准确性检查**：
   - slides内容是否准确反映原始材料？
   - 是否有曲解或过度简化？
   - 数据和事实是否正确转述？

3. **用户要求符合度**：
   - 是否满足用户提出的具体要求？
   - 风格和重点是否符合用户期望？
   - 列出未满足的要求

4. **逻辑流检查**：
   - 叙事顺序是否合理？
   - 各页之间过渡是否自然？
   - 整体结构是否清晰？

## 输出格式

### 内容审阅报告

#### 完整性评估
- 评分：[A/B/C/D]
- 遗漏内容：[列表]

#### 准确性评估
- 评分：[A/B/C/D]
- 问题页面：[页码和问题描述]

#### 用户要求符合度
- 评分：[A/B/C/D]
- 未满足要求：[列表]

#### 逻辑流评估
- 评分：[A/B/C/D]
- 建议调整：[具体建议]

#### 需修改页面清单
| 页码 | 问题类型 | 问题描述 | 修改建议 |
|------|----------|----------|----------|
| ... | ... | ... | ... |
```

#### Agent 2：格式审阅专家

```
Task 工具参数：
- subagent_type: "general-purpose"
- run_in_background: true
- prompt:

你是一个Marp格式审阅专家。请检查slides的格式规范性。

## Slides内容
[插入presentation.md内容]

## 审阅任务

1. **YAML Frontmatter检查**：
   - marp: true 是否存在？
   - theme 是否正确设置？
   - header 是否配置？
   - style 块语法是否正确？

2. **分页符检查**：
   - `---` 分页符是否正确使用？
   - 是否有多余或缺失的分页符？
   - 分页符前后是否有空行？

3. **Markdown语法检查**：
   - 标题层级是否正确（#, ##, ###）？
   - 列表格式是否统一？
   - 粗体、斜体语法是否正确？
   - 引用块语法是否正确？
   - 代码块是否正确闭合？

4. **缩进和空行检查**：
   - 缩进是否一致？
   - 空行使用是否规范？
   - 是否有多余的空白字符？

## 输出格式

### 格式审阅报告

#### 语法正确性
- 评分：[A/B/C/D]
- 语法错误：[列表，含行号]

#### 格式一致性
- 评分：[A/B/C/D]
- 不一致处：[列表]

#### 需修正项
| 行号 | 问题类型 | 原内容 | 建议修正 |
|------|----------|--------|----------|
| ... | ... | ... | ... |
```

#### Agent 3：密度审阅专家

```
Task 工具参数：
- subagent_type: "general-purpose"
- run_in_background: true
- prompt:

你是一个slides内容密度审阅专家。请逐页检查内容密度。

## Slides内容
[插入presentation.md内容]

## 密度标准

| 指标 | 安全值 | 警告值 | 危险值 |
|------|--------|--------|--------|
| 每页文字行数 | ≤6行 | 7-8行 | >8行 |
| 每行字符数 | ≤35字符 | 36-45字符 | >45字符 |
| 列表项数量 | ≤5项 | 6项 | >6项 |
| 嵌套列表深度 | 1层 | 2层 | >2层 |
| 段落长度 | ≤2行 | 3行 | >3行 |
| 正文字号 | ≥0.9em | 0.7-0.9em | <0.7em |

## 审阅任务

逐页分析：
1. 统计每页的文字行数
2. 检查最长行的字符数
3. 统计列表项数量
4. 检查是否有过长段落
5. 评估整体视觉密度

## 输出格式

### 密度审阅报告

#### 逐页密度分析

| 页码 | 行数 | 最长行 | 列表项 | 字号 | 密度评级 | 状态 |
|------|------|--------|--------|------|----------|------|
| 1 | X | X字符 | X项 | Xem | 低/中/高 | ✓/⚠/✗ |
| 2 | ... | ... | ... | ... | ... | ... |

#### 高密度页面（需处理）
- 第X页：[问题描述]，建议：[拆分/精简/重组]
- ...

#### 拆分建议
对于需要拆分的页面，提供具体拆分方案：
- 第X页 → 拆分为 X-1 和 X-2
  - X-1 内容：...
  - X-2 内容：...
```

#### Agent 4：视觉审阅专家

```
Task 工具参数：
- subagent_type: "general-purpose"
- run_in_background: true
- prompt:

你是一个slides视觉设计审阅专家。请检查视觉层次和设计规范。

## Slides内容
[插入presentation.md内容]

## 审阅任务

1. **标题层次检查**：
   - 每页是否有清晰的标题？
   - 标题层级使用是否合理？
   - h1用于分隔页，h2用于内容页？

2. **强调元素检查**：
   - 粗体是否用于关键词/要点？
   - 引用块是否用于重要引语？
   - 强调是否过度（全篇都是粗体）？

3. **视觉焦点检查**：
   - 每页是否有明确的视觉焦点？
   - 信息层次是否清晰？
   - 是否有页面过于平淡或过于杂乱？

4. **一致性检查**：
   - 相似内容的页面格式是否统一？
   - 列表符号是否一致？
   - 整体风格是否协调？

## 输出格式

### 视觉审阅报告

#### 标题层次
- 评分：[A/B/C/D]
- 问题页面：[列表]

#### 强调使用
- 评分：[A/B/C/D]
- 改进建议：[列表]

#### 视觉焦点
- 评分：[A/B/C/D]
- 需优化页面：[列表]

#### 一致性
- 评分：[A/B/C/D]
- 不一致处：[列表]

#### 需修改页面清单
| 页码 | 问题 | 建议 |
|------|------|------|
| ... | ... | ... |
```

**汇总审阅结果**：

依次等待各 Agent 完成（背景 Task 完成后读取结果），整合为统一的审阅报告。

**结果收集方式**：各 Agent 将审阅报告写入 `slides_[项目名]/review_agent_N.txt`，主流程依次读取并汇总。

**输出**：向用户展示综合审阅报告，按优先级排列的修改清单

#### 中文语言规范审阅（仅中文演示文稿）

**触发**：多维度审阅完成后，如果是中文演示文稿则执行此阶段

**执行方式**：使用 Task 工具派遣 subagent 执行

**Subagent 调用指令**：

```text
使用 Task 工具，设置 subagent_type="general-purpose"，prompt 内容如下：

你是一个中文语言规范专家。请对以下Marp Slides进行逐页审阅，确保符合中文书写规范和演示文稿语言习惯：

[插入 slides_[项目名]/05_final/presentation.md 的内容]

审阅要求：

1. **标点符号检查**：
   - 必须使用中文标点：。，？！：；“” ‘’（）……——
   - 禁止使用英文标点：. , ? ! : ; ""'' () ... --
   - 列表项末尾可省略句号
   - 标题末尾不加标点

2. **引号使用规范**（重要）：
   - 原则：Slides中能不用引号就不用，让文字更简洁
   - 删除不必要的引号，例如：
     - ✗ 这就是所谓的"核心概念" → ✓ 这就是核心概念
     - ✗ AI的"智能"表现 → ✓ AI的智能表现
   - 仅在以下情况保留引号：
     - 直接引语（如：他说："……"）
     - 表示反讽或特殊含义
     - 专有名词首次出现且需要解释

3. **语言习惯检查**：
   - 避免欧化句式（如"被"字句滥用）
   - 避免翻译腔
   - 删除冗余表达（Slides需要极简文字）
   - 使用自然的中文表达顺序
   - 避免长句，每个要点保持简短

4. **中英文混排规范**：
   - 中文与英文/数字之间加空格（如：Claude Code 是工具）
   - 全角标点与英文之间不加空格
   - 技术术语保持一致（如：API、SDK 等全文统一）

5. **Slides特有检查**：
   - 标题是否简洁有力
   - 要点是否用词精准
   - 是否避免了口语化表达
   - 专业术语是否一致

输出格式：

## 中文规范审阅报告

### 标点符号修正
| 页码 | 原文 | 修正后 |
|------|------|--------|
| ... | ... | ... |

### 引号精简
| 页码 | 修改内容 |
|------|----------|
| ... | 删除"xxx"的引号 |

### 表达优化
| 页码 | 原表达 | 优化后 |
|------|--------|--------|
| ... | ... | ... |

### 中英文混排修正
| 页码 | 原文 | 修正后 |
|------|------|--------|
| ... | ... | ... |

### 修正后的完整Slides
[输出完成所有修正的Slides内容]
```

**后续处理**：

- 收到 subagent 返回的审阅报告后，使用 Edit 工具将修正应用到 `slides_[项目名]/05_final/presentation.md`

---

### 阶段五：生成终稿

**触发**：审阅修改完成后

**执行步骤**：

1. **导出HTML和PDF**：

   ```bash
   # 导出HTML预览版本
   npx @marp-team/marp-cli slides_[项目名]/05_final/presentation.md -o slides_[项目名]/05_final/slides.html --html --theme-set ./themes/

   # 导出PDF版本
   npx @marp-team/marp-cli slides_[项目名]/05_final/presentation.md -o slides_[项目名]/05_final/slides.pdf --theme-set ./themes/ --allow-local-files
   ```

**最终产出**：

- `slides_[项目名]/05_final/presentation.md` - 最终Markdown
- `slides_[项目名]/05_final/slides.html` - HTML预览版本
- `slides_[项目名]/05_final/slides.pdf` - PDF版本

**输出**：告知用户终稿文件位置和预览方式

## 常见问题处理

### 文字溢出

**原因**：单页内容过多

**解决方案**：
1. **拆分法**：将内容拆分为多页
   ```markdown
   ## 原始页面：五个要点

   拆分为：

   ## 要点概览（1/2）
   1. 要点一
   2. 要点二
   3. 要点三

   ---

   ## 要点概览（2/2）
   4. 要点四
   5. 要点五
   ```

2. **精简法**：删除次要信息
3. **层次法**：使用子列表缩短主列表

### 代码块过长

**解决方案**：
- 只展示关键代码片段
- 使用伪代码替代完整代码
- 分多页展示，每页一个逻辑单元

### 表格过大

**解决方案**：
- 拆分为多个小表格
- 转换为列表形式
- 只展示关键数据行

### 字体过小

**判断标准**：正文字号小于 0.7em 时多数人会阅读困难

**解决方案**：
1. **拆分法**：将内容拆分为多页，减少每页信息量
2. **精简法**：删除次要要点，保留核心内容
3. **视觉辅助法**：用图表、图标代替文字说明

## 模板使用说明

模板文件：
- **`marp-template.md`** - 英文模板（graph_paper 主题）
- **`marp-template-zh.md`** - 中文模板（graph_paper 主题，带中文注释和示例）

**gaia 主题模板配置示例**：
```yaml
---
marp: true
theme: gaia
class: lead
paginate: true
backgroundColor: #fff
backgroundImage: url('https://marp.app/assets/hero-background.jpg')
style: |
  section {
    font-family: 'Times New Roman', 'SimSun', serif;
  }
  h1 {
    color: #2c3e50;
    font-size: 1.5em;
  }
  h2 {
    color: #34495e;
    border-bottom: 2px solid #3498db;
  }
  img {
    display: block !important;
    margin: 0 auto !important;
  }
  section table {
    display: table !important;
    width: auto !important;
    margin-left: auto !important;
    margin-right: auto !important;
  }
---

# 标题页

副标题

---

## 内容页标题

正文内容...
```

**修改Header**：
```yaml
header: '你的课程/演讲标题'
```

## 资源引用

### 参考文件
- **`marp-template.md`** - Marp模板文件
- **`references/slide-types.md`** - 页面类型详解
- **`references/review-checklist.md`** - 审阅检查清单
- **`themes/README.md`** - 主题说明文档
- **`themes/*.css`** - 15款精选主题文件

## Marp-CLI 命令参考

```bash
# 预览（启动本地服务器）
npx @marp-team/marp-cli -s slides_[项目名]/05_final/presentation.md --theme-set ./themes/

# 导出HTML版本
npx @marp-team/marp-cli slides_[项目名]/05_final/presentation.md -o slides_[项目名]/05_final/slides.html --html --theme-set ./themes/

# 导出PDF版本
npx @marp-team/marp-cli slides_[项目名]/05_final/presentation.md -o slides_[项目名]/05_final/slides.pdf --theme-set ./themes/ --allow-local-files
```

**参数说明**：

| 参数 | 说明 |
|------|------|
| `--theme-set ./themes/` | 加载本地 themes 文件夹中的所有主题 |
| `--allow-local-files` | 允许加载本地图片和资源（PDF 导出必需） |
| `--html` | 启用 HTML 标签支持 |
| `-s` | 启动预览服务器 |

**导出格式说明**：

| 格式 | 用途 | 文件扩展名 |
|------|------|-----------|
| HTML | 网页展示、在线分享 | `.html` |
| PDF | 打印、正式分发 | `.pdf` |

## 交互规范

1. 每阶段结束后询问用户是否继续
2. 内容分析后让用户确认大纲再继续
3. 检查发现问题时，说明问题和建议的修复方案
4. 提供选择时给出推荐选项和理由

## Windows 路径注意

Windows 环境下路径使用反斜杠或正斜杠均可，但建议统一使用正斜杠以兼容 WSL：

```bash
# Windows - 统一使用正斜杠
slides_project-name/05_final/presentation.md
```

## 禁止事项

- 不跳过内容分析直接制作slides
- 不在单页放置过多内容
- 不使用过小的字体或过密的排版
- 不输出未经验证的终稿
