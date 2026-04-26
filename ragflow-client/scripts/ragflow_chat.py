#!/usr/bin/env python3
"""
RAGflow API 客户端 (原生对话 API 精简版本)

调用 RAGflow 知识库进行智能对话，结果与网页端保持一致。
支持环境变量和配置文件读取敏感信息。
"""

import http.client
import json
import sys
import os
import argparse
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


class RAGflowClient:
    """RAGflow API 客户端 - 使用原生对话 API，完全继承 Chat 配置"""

    def __init__(self, api_key: str, chat_id: str, host: str, port: int = 80):
        self.api_key = api_key
        self.chat_id = chat_id
        self.host = host
        self.port = port
        self.session_id = None

    def _request(self, method: str, path: str, payload: dict = None) -> dict:
        """发送 HTTP 请求"""
        conn = http.client.HTTPConnection(self.host, self.port, timeout=60)
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload else None
            conn.request(method, path, body=body, headers=headers)
            resp = conn.getresponse()
            return json.loads(resp.read().decode())
        finally:
            conn.close()

    def create_session(self, name: str = "API Session") -> str:
        """创建对话会话"""
        path = f"/api/v1/chats/{self.chat_id}/sessions"
        resp = self._request("POST", path, {"name": name})

        if resp.get("code") != 0:
            raise RuntimeError(f"创建会话失败: {resp.get('message', 'Unknown error')}")

        self.session_id = resp["data"]["id"]
        return self.session_id

    def chat(self, question: str, stream: bool = False) -> dict:
        """
        发送消息并获取回复（原生对话 API）。
        首次调用自动创建 session，后续复用 session_id，结果与网页端一致。
        """
        if not self.session_id:
            self.create_session()

        path = f"/api/v1/chats/{self.chat_id}/completions"
        payload = {
            "question": question,
            "stream": stream,
            "session_id": self.session_id
        }

        resp = self._request("POST", path, payload)

        if resp.get("code") != 0:
            return {
                "error": resp.get("message", "Unknown error"),
                "code": resp.get("code", -1)
            }

        data = resp.get("data", {})
        return {
            "answer": data.get("answer", ""),
            "reference": data.get("reference", {}),
            "session_id": self.session_id
        }

    def chat_openai(self, question: str, stream: bool = False, reference: bool = True) -> dict:
        """
        OpenAI 兼容 API。无需 session，但无法继承 Chat 的完整 RAG 配置。
        """
        path = f"/api/v1/chats_openai/{self.chat_id}/chat/completions"
        payload = {
            "model": "model",
            "messages": [{"role": "user", "content": question}],
            "stream": stream,
            "extra_body": {"reference": reference}
        }
        resp = self._request("POST", path, payload)

        if resp.get("choices"):
            message = resp["choices"][0].get("message", {})
            return {
                "answer": message.get("content", ""),
                "role": message.get("role", "assistant"),
                "usage": resp.get("usage", {})
            }
        return {
            "error": resp.get("message", "Unknown error"),
            "code": resp.get("code", -1)
        }

    def list_sessions(self) -> list:
        """列出当前 chat 的所有会话"""
        path = f"/api/v1/chats/{self.chat_id}/sessions"
        resp = self._request("GET", path)
        if resp.get("code") != 0:
            return []
        return resp.get("data", [])


def load_config_from_file(config_path: str = None) -> dict:
    """从配置文件加载配置"""
    if config_path is None:
        config_path = Path.home() / ".config" / "ragflow" / "config.json"
    else:
        config_path = Path(config_path)

    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_config(args) -> dict:
    """获取配置，优先级：命令行 > 环境变量 > 配置文件"""
    config = load_config_from_file(args.config if hasattr(args, 'config') else None)

    env_mappings = {
        'RAGFLOW_API_KEY': 'api_key',
        'RAGFLOW_CHAT_ID': 'chat_id',
        'RAGFLOW_HOST': 'host',
        'RAGFLOW_PORT': 'port'
    }
    for env_var, key in env_mappings.items():
        value = os.environ.get(env_var)
        if value:
            config[key] = value if key != 'port' else int(value)

    for key in ['api_key', 'chat_id', 'host', 'port']:
        val = getattr(args, key, None)
        if val is not None:
            config[key] = val if key != 'port' else int(val)

    return config


def validate_config(config: dict) -> bool:
    """验证配置是否完整"""
    missing = [k for k in ['api_key', 'chat_id', 'host'] if not config.get(k)]
    if missing:
        print(f"错误: 缺少必要配置: {', '.join(missing)}", file=sys.stderr)
        print("\n可通过以下方式提供：", file=sys.stderr)
        print("  1. 环境变量: RAGFLOW_API_KEY, RAGFLOW_CHAT_ID, RAGFLOW_HOST", file=sys.stderr)
        print("  2. 配置文件: ~/.config/ragflow/config.json", file=sys.stderr)
        print("  3. 命令行参数: --api-key, --chat-id, --host", file=sys.stderr)
        return False
    return True


def print_references(reference: dict):
    """打印引用来源"""
    if not reference:
        return
    chunks = reference.get("chunks", {})
    if not chunks:
        return
    print("\n--- 引用来源 ---")
    items = chunks.items() if isinstance(chunks, dict) else enumerate(chunks, 1)
    for idx, ref in items:
        if isinstance(ref, tuple):
            _, ref = ref
        doc_name = ref.get("document_name", "未知文档")
        chunk = ref.get("content", "")[:200].replace("\n", " ")
        print(f"[{idx}] {doc_name}: {chunk}...")


def main():
    parser = argparse.ArgumentParser(
        description='RAGflow API 客户端（原生对话 API，结果与网页端一致）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
配置优先级: 命令行参数 > 环境变量 > 配置文件

环境变量:
  RAGFLOW_API_KEY    API 密钥
  RAGFLOW_CHAT_ID    聊天机器人 ID
  RAGFLOW_HOST       服务地址
  RAGFLOW_PORT       端口号 (默认 80)

配置文件示例 (~/.config/ragflow/config.json):
  {
    "api_key": "ragflow-your-api-key",
    "chat_id": "your-chat-id",
    "host": "your-ragflow-host",
    "port": 80
  }

使用 --openai 可切换回 OpenAI 兼容 API（结果可能与网页端不一致）。
        """
    )

    parser.add_argument('question', nargs='?', help='要询问的问题')
    parser.add_argument('--api-key', help='API 密钥')
    parser.add_argument('--chat-id', help='聊天机器人 ID')
    parser.add_argument('--host', help='服务地址')
    parser.add_argument('--port', type=int, default=80, help='端口号 (默认 80)')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--session-id', help='复用已有会话 ID')
    parser.add_argument('--openai', action='store_true', help='使用 OpenAI 兼容 API')
    parser.add_argument('--init-config', action='store_true', help='生成配置文件模板')
    parser.add_argument('--list-sessions', action='store_true', help='列出当前 chat 的所有会话')

    args = parser.parse_args()

    if args.init_config:
        config_dir = Path.home() / ".config" / "ragflow"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "config.json"
        template = {
            "api_key": "ragflow-your-api-key",
            "chat_id": "your-chat-id",
            "host": "your-ragflow-host",
            "port": 80
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        print(f"配置文件模板已生成: {config_path}")
        print("请编辑该文件填入真实信息后使用。")
        sys.exit(0)

    if args.list_sessions:
        config = get_config(args)
        if not validate_config(config):
            sys.exit(1)
        client = RAGflowClient(
            api_key=config['api_key'],
            chat_id=config['chat_id'],
            host=config['host'],
            port=config.get('port', 80)
        )
        sessions = client.list_sessions()
        if not sessions:
            print("暂无会话记录")
        else:
            print(f"共 {len(sessions)} 个会话:\n")
            for s in sessions:
                sid = s.get('id', 'N/A')
                name = s.get('name', '未命名')
                print(f"  ID: {sid}  |  名称: {name}")
        sys.exit(0)

    config = get_config(args)
    if not validate_config(config):
        sys.exit(1)

    client = RAGflowClient(
        api_key=config['api_key'],
        chat_id=config['chat_id'],
        host=config['host'],
        port=config.get('port', 80)
    )

    if args.session_id:
        client.session_id = args.session_id

    if not args.question:
        print("错误: 请提供要询问的问题", file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)

    try:
        if args.openai:
            result = client.chat_openai(args.question)
        else:
            result = client.chat(args.question)

        if "error" in result:
            print(f"请求失败: [{result.get('code', -1)}] {result['error']}", file=sys.stderr)
            sys.exit(1)

        print(result.get("answer", ""))
        print_references(result.get("reference", {}))

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()