---
name: ragflow-client
description: 调用 RAGflow 原生对话 API 进行知识库问答，结果与网页端保持一致。RAGflow 是基于 RAG（检索增强生成）的开源知识库系统。当用户需要向 RAGflow 知识库提问、获取引用来源时使用。
---

# RAGflow 客户端

使用 **原生对话 API** 调用 RAGflow 知识库进行智能对话，结果与网页端完全一致。

## 前置配置

需要以下信息（用户提供）：
- `API_KEY`: RAGflow API 密钥
- `CHAT_ID`: 聊天机器人 ID
- `HOST`: RAGflow 服务地址

## 重要说明

### 为什么使用原生对话 API？

| API 类型 | 端点 | 特点 | 推荐度 |
|----------|------|------|--------|
| ✅ **原生对话 API** | `/api/v1/conversation/completion` | **完全继承 Chat 配置**，结果与网页端一致 | ⭐⭐⭐ 强烈推荐 |
| ⚠️ OpenAI 兼容 API | `/api/v1/chats_openai/{chat_id}/chat/completions` | 无法传递 `prompt`、`similarity_threshold`、`top_n` 等 RAG 参数，结果可能与网页端差异很大 | 兼容用途 |

### 原生 API 的优势

原生对话 API 通过 `session_id` 调用，会话会自动继承 Chat 后台配置的所有参数：
- `prompt` — 系统提示词
- `similarity_threshold` — 相似度阈值
- `top_n` — 喂给 LLM 的分块数量
- `rerank_model` — 重排序模型
- `keywords_similarity_weight` — 关键词相似度权重
- `empty_response` — 无命中时的兜底回复

## API 端点

### 创建会话

**POST** `/api/v1/chats/{chat_id}/sessions`

```json
{
  "name": "API Session"
}
```

### 对话补全（原生 API）

**POST** `/api/v1/conversation/completion`

```json
{
  "session_id": "your-session-id",
  "question": "你的问题",
  "stream": false
}
```

### 响应格式

```json
{
  "code": 0,
  "data": {
    "answer": "AI 回答内容",
    "reference": [
      {
        "document_name": "文档1.pdf",
        "content": "相关片段..."
      }
    ]
  }
}
```

## 配置方式（推荐）

### 方式一：环境变量（最安全）

```bash
# Windows PowerShell
$env:RAGFLOW_API_KEY="ragflow-your-api-key"
$env:RAGFLOW_CHAT_ID="your-chat-id"
$env:RAGFLOW_HOST="your-ragflow-host"

# 然后直接运行
python "skills/ragflow-client/scripts/ragflow_chat.py" "你的问题"
```

```bash
# Linux/macOS
export RAGFLOW_API_KEY="ragflow-your-api-key"
export RAGFLOW_CHAT_ID="your-chat-id"
export RAGFLOW_HOST="your-ragflow-host"

python "skills/ragflow-client/scripts/ragflow_chat.py" "你的问题"
```

### 方式二：配置文件

生成配置文件模板：
```bash
python "skills/ragflow-client/scripts/ragflow_chat.py" --init-config
```

编辑 `~/.config/ragflow/config.json`：
```json
{
  "api_key": "ragflow-your-api-key",
  "chat_id": "your-chat-id",
  "host": "your-ragflow-host",
  "port": 80
}
```

然后直接提问：
```bash
python "skills/ragflow-client/scripts/ragflow_chat.py" "你的问题"
```

### 方式三：命令行参数（不推荐，会暴露敏感信息）

```bash
python "skills/ragflow-client/scripts/ragflow_chat.py" \n  --api-key "ragflow-xxx" \n  --chat-id "your-chat-id" \n  --host "your-ragflow-host" \n  "你的问题"
```

## 使用方法

### 1. 命令行调用

```bash
# 使用原生 API（默认，结果与网页端一致）
python "skills/ragflow-client/scripts/ragflow_chat.py" "什么是双向进入、交叉任职"

# 使用 OpenAI 兼容 API
python "skills/ragflow-client/scripts/ragflow_chat.py" --openai "什么是双向进入、交叉任职"

# 复用已有会话（保持多轮对话上下文）
python "skills/ragflow-client/scripts/ragflow_chat.py" --session-id "xxx" "接着刚才的问题"

# 列出当前 chat 的所有会话
python "skills/ragflow-client/scripts/ragflow_chat.py" --list-sessions
```

### 2. Python 代码调用

```python
from skills.ragflow_client.scripts.ragflow_chat import RAGflowClient

client = RAGflowClient(
    api_key="ragflow-xxx",  # 建议从环境变量读取
    chat_id="your-chat-id",
    host="your-ragflow-host"
)

# 原生 API（推荐）
result = client.chat("你的问题")
print(result["answer"])
print(result["reference"])

# OpenAI 兼容 API（兼容用途）
result = client.chat_openai("你的问题")
print(result["answer"])
```

### 3. 作为模块导入（推荐）

```python
import os
from skills.ragflow_client.scripts.ragflow_chat import RAGflowClient

client = RAGflowClient(
    api_key=os.environ.get('RAGFLOW_API_KEY'),
    chat_id=os.environ.get('RAGFLOW_CHAT_ID'),
    host=os.environ.get('RAGFLOW_HOST')
)

result = client.chat("中国公司治理有哪些特点")
print(result["answer"])
for ref in result.get("reference", []):
    print(f"来源: {ref.get('document_name')}")
```

## 参数说明

### 命令行参数

| 参数 | 说明 |
|------|------|
| `question` | 用户问题 |
| `--api-key` | API 密钥 |
| `--chat-id` | 聊天机器人 ID |
| `--host` | 服务地址 |
| `--port` | 端口号（默认 80）|
| `--config` | 自定义配置文件路径 |
| `--session-id` | 复用已有会话 ID |
| `--openai` | 切换回 OpenAI 兼容 API |
| `--list-sessions` | 列出当前 chat 的所有会话 |
| `--init-config` | 生成配置文件模板 |
| `-h, --help` | 显示帮助信息 |

### chat 方法参数（原生 API）

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | str | 是 | 用户问题 |
| `stream` | bool | 否 | 是否流式响应，默认 False |

### chat_openai 方法参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | str | 是 | 用户问题 |
| `stream` | bool | 否 | 是否流式响应，默认 False |
| `reference` | bool | 否 | 是否返回引用来源，默认 True |

## 完整示例输出

```
根据知识库内容，**双向进入、交叉任职**是中国特色现代企业制度中...

--- 引用来源 ---
[1] 文档1.pdf: 双向进入、交叉任职是指...
[2] 文档2.pdf: 这一机制最早源于...
```

## 常见问题

### Q: API 结果和网页端聊天结果差异很大？

**A:** 这是因为你使用了 OpenAI 兼容 API。该 API 无法传递 Chat 的 RAG 配置参数（如 `similarity_threshold`、`top_n`、`prompt` 等），RAGflow 会使用内部默认值执行检索，导致召回质量和生成结果与网页端不一致。

**解决方案：** 改用原生对话 API `client.chat()`，它会自动创建 `session_id` 并继承 Chat 的完整配置。

## 安全建议

1. **优先使用环境变量** - 不会暴露在 shell 历史和进程列表中
2. **次选配置文件** - 设置文件权限为仅当前用户可读（`chmod 600`）
3. **避免命令行参数** - 会记录在 shell 历史中，其他用户可能通过 `ps` 看到
4. **不要提交到版本控制** - 将配置文件添加到 `.gitignore`