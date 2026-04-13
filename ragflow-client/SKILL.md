---
name: ragflow-client
description: 调用 RAGflow OpenAI 兼容 API 进行知识库问答。RAGflow 是基于 RAG（检索增强生成）的开源知识库系统。当用户需要向 RAGflow 知识库提问、获取引用来源时使用。
---

# RAGflow 客户端

使用 **OpenAI 兼容 API** 调用 RAGflow 知识库进行智能对话。

## 前置配置

需要以下信息（用户提供）：
- `API_KEY`: RAGflow API 密钥
- `CHAT_ID`: 聊天机器人 ID
- `HOST`: RAGflow 服务地址

## 重要说明

⚠️ **必须使用 OpenAI 兼容 API**

| API 类型 | 端点 | 状态 |
|----------|------|------|
| ❌ 原生 API | `/api/v1/chats/{chat_id}/completions` | 返回固定问候语，无法检索知识库 |
| ✅ OpenAI 兼容 API | `/api/v1/chats_openai/{chat_id}/chat/completions` | 正常工作，返回知识库内容 |

## API 端点

**POST** `/api/v1/chats_openai/{chat_id}/chat/completions`

### 请求格式

```json
{
  "model": "model",
  "messages": [{"role": "user", "content": "你的问题"}],
  "stream": false,
  "extra_body": {
    "reference": true
  }
}
```

### 响应格式

```json
{
  "choices": [{
    "message": {
      "content": "AI 回答内容",
      "role": "assistant"
    }
  }],
  "usage": {
    "prompt_tokens": 16,
    "completion_tokens": 587,
    "total_tokens": 603
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
python "skills/ragflow-client/scripts/ragflow_chat.py" \
  --api-key "ragflow-xxx" \
  --chat-id "your-chat-id" \
  --host "your-ragflow-host" \
  "你的问题"
```

## 使用方法

### 1. 命令行调用

```bash
# 使用环境变量或配置文件后，直接提问
python "skills/ragflow-client/scripts/ragflow_chat.py" "什么是双向进入、交叉任职"

# 或使用交互式输入
python "skills/ragflow-client/scripts/ragflow_chat.py"
# 然后按提示输入问题
```

### 2. Python 代码调用

```python
from skills.ragflow_client.scripts.ragflow_chat import RAGflowClient

client = RAGflowClient(
    api_key="ragflow-xxx",  # 建议从环境变量读取
    chat_id="your-chat-id",
    host="your-ragflow-host"
)

result = client.chat("你的问题")
print(result["answer"])
```

### 3. 作为模块导入（推荐）

```python
import os
from skills.ragflow_client.scripts.ragflow_chat import RAGflowClient

# 从环境变量读取（安全）
client = RAGflowClient(
    api_key=os.environ.get('RAGFLOW_API_KEY'),
    chat_id=os.environ.get('RAGFLOW_CHAT_ID'),
    host=os.environ.get('RAGFLOW_HOST')
)

result = client.chat("中国公司治理有哪些特点")
print(result["answer"])
print(f"Token 使用: {result['usage']}")
```

## 参数说明

### 命令行参数

| 参数 | 说明 |
|------|------|
| `question` | 用户问题（可选，不提供则交互式输入）|
| `--api-key` | API 密钥 |
| `--chat-id` | 聊天机器人 ID |
| `--host` | 服务地址 |
| `--port` | 端口号（默认 80）|
| `--config` | 自定义配置文件路径 |
| `--init-config` | 生成配置文件模板 |
| `-h, --help` | 显示帮助信息 |

### chat 方法参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `question` | str | 是 | 用户问题 |
| `stream` | bool | 否 | 是否流式响应，默认 False |
| `reference` | bool | 否 | 是否返回引用来源，默认 True |

## 完整示例输出

```
问题: 什么是双向进入、交叉任职

回答:
根据知识库内容，**双向进入、交叉任职**是中国特色现代企业制度中...

Token 使用: {
  'prompt_tokens': 16,
  'completion_tokens': 587,
  'total_tokens': 603
}
```

## 安全建议

1. **优先使用环境变量** - 不会暴露在 shell 历史和进程列表中
2. **次选配置文件** - 设置文件权限为仅当前用户可读（`chmod 600`）
3. **避免命令行参数** - 会记录在 shell 历史中，其他用户可能通过 `ps` 看到
4. **不要提交到版本控制** - 将配置文件添加到 `.gitignore`
