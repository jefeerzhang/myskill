#!/usr/bin/env python3
"""
RAGflow API 客户端 (OpenAI 兼容版本)

调用 RAGflow 知识库进行智能对话。
支持环境变量和配置文件读取敏感信息。
"""

import http.client
import json
import sys
import os
import argparse
from pathlib import Path


class RAGflowClient:
    """RAGflow API 客户端 - 使用 OpenAI 兼容 API"""
    
    def __init__(self, api_key: str, chat_id: str, host: str, port: int = 80):
        self.api_key = api_key
        self.chat_id = chat_id
        self.host = host
        self.port = port
    
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
            data = resp.read().decode()
            
            return json.loads(data)
        finally:
            conn.close()
    
    def chat(self, question: str, stream: bool = False, reference: bool = True) -> dict:
        """
        发送消息并获取回复 (OpenAI 兼容 API)
        
        Args:
            question: 用户问题
            stream: 是否流式响应
            reference: 是否返回引用来源
        
        Returns:
            包含 answer, reference 的字典
        """
        path = f"/api/v1/chats_openai/{self.chat_id}/chat/completions"
        
        payload = {
            "model": "model",
            "messages": [{"role": "user", "content": question}],
            "stream": stream,
            "extra_body": {
                "reference": reference
            }
        }
        
        resp = self._request("POST", path, payload)
        
        if resp.get("choices"):
            message = resp["choices"][0].get("message", {})
            return {
                "answer": message.get("content", ""),
                "role": message.get("role", "assistant"),
                "usage": resp.get("usage", {})
            }
        else:
            return {
                "error": resp.get("message", "Unknown error"),
                "code": resp.get("code", -1)
            }


def load_config_from_file(config_path: str = None) -> dict:
    """从配置文件加载配置"""
    if config_path is None:
        # 默认路径: ~/.config/ragflow/config.json
        config_path = Path.home() / ".config" / "ragflow" / "config.json"
    else:
        config_path = Path(config_path)
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def get_config(args) -> dict:
    """
    获取配置，优先级：命令行 > 环境变量 > 配置文件
    """
    config = {}
    
    # 1. 尝试从配置文件加载
    file_config = load_config_from_file(args.config if hasattr(args, 'config') else None)
    config.update(file_config)
    
    # 2. 环境变量覆盖配置文件
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
    
    # 3. 命令行参数覆盖环境变量
    if hasattr(args, 'api_key') and args.api_key:
        config['api_key'] = args.api_key
    if hasattr(args, 'chat_id') and args.chat_id:
        config['chat_id'] = args.chat_id
    if hasattr(args, 'host') and args.host:
        config['host'] = args.host
    if hasattr(args, 'port') and args.port:
        config['port'] = args.port
    
    return config


def validate_config(config: dict) -> bool:
    """验证配置是否完整"""
    required = ['api_key', 'chat_id', 'host']
    missing = [k for k in required if not config.get(k)]
    
    if missing:
        print(f"错误: 缺少必要配置: {', '.join(missing)}", file=sys.stderr)
        print("\n可通过以下方式提供：", file=sys.stderr)
        print("  1. 环境变量: RAGFLOW_API_KEY, RAGFLOW_CHAT_ID, RAGFLOW_HOST", file=sys.stderr)
        print("  2. 配置文件: ~/.config/ragflow/config.json", file=sys.stderr)
        print("  3. 命令行参数: --api-key, --chat-id, --host", file=sys.stderr)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(
        description='RAGflow API 客户端',
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
        """
    )
    
    parser.add_argument('question', nargs='?', help='要询问的问题')
    parser.add_argument('--api-key', help='API 密钥 (或环境变量 RAGFLOW_API_KEY)')
    parser.add_argument('--chat-id', help='聊天机器人 ID (或环境变量 RAGFLOW_CHAT_ID)')
    parser.add_argument('--host', help='RAGflow 服务地址 (或环境变量 RAGFLOW_HOST)')
    parser.add_argument('--port', type=int, help='端口号 (或环境变量 RAGFLOW_PORT，默认 80)')
    parser.add_argument('--config', help='配置文件路径 (默认 ~/.config/ragflow/config.json)')
    parser.add_argument('--init-config', action='store_true', help='生成配置文件模板')
    
    args = parser.parse_args()
    
    # 生成配置文件模板
    if args.init_config:
        config_dir = Path.home() / ".config" / "ragflow"
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = config_dir / "config.json"
        
        template = {
            "api_key": "ragflow-your-api-key-here",
            "chat_id": "your-chat-id-here",
            "host": "your-ragflow-host",
            "port": 80
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
        
        print(f"配置文件模板已生成: {config_file}")
        print("请编辑文件填入你的实际配置信息")
        return
    
    # 获取配置
    config = get_config(args)
    
    # 验证配置
    if not validate_config(config):
        sys.exit(1)
    
    # 如果没有提供问题，提示输入
    question = args.question
    if not question:
        question = input("请输入问题: ").strip()
        if not question:
            print("错误: 问题不能为空", file=sys.stderr)
            sys.exit(1)
    
    # 创建客户端
    client = RAGflowClient(
        api_key=config['api_key'],
        chat_id=config['chat_id'],
        host=config['host'],
        port=config.get('port', 80)
    )
    
    print(f"问题: {question}\n")
    
    result = client.chat(question)
    
    if "error" in result:
        print(f"错误: {result['error']}")
        sys.exit(1)
    else:
        print(f"回答:\n{result['answer']}\n")
        if result.get("usage"):
            print(f"Token 使用: {result['usage']}")


if __name__ == "__main__":
    main()
