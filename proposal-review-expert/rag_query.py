"""
AnythingLLM RAG 查询工具 - 开题报告评审专用
"""
import requests
import json
import os

# 配置文件路径
CONFIG_FILE = ".rag_config.json"


def load_config():
    """加载 RAG 配置"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {
            "base_url": "http://localhost:3001",
            "api_key": "",
            "workspace_slug": ""
        }


def rag_query(question, base_url=None, api_key=None, workspace_slug=None, timeout=180):
    """
    向 AnythingLLM 发起 RAG 查询
    
    Args:
        question: 查询问题
        base_url: AnythingLLM 服务地址
        api_key: API Key
        workspace_slug: 工作区 Slug
        timeout: 超时时间（秒）
    
    Returns:
        dict: 包含 textResponse 和 sources 的响应
    """
    config = load_config()
    
    base_url = base_url or config.get("base_url", "http://localhost:3001")
    api_key = api_key or config.get("api_key")
    workspace_slug = workspace_slug or config.get("workspace_slug")
    
    if not api_key:
        return {"error": "API Key 未配置"}
    
    if not workspace_slug:
        return {"error": "Workspace Slug 未配置"}
    
    url = f"{base_url}/api/v1/workspace/{workspace_slug}/chat"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"message": question}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        return {"error": "RAG 查询超时，请重试"}
    except requests.exceptions.ConnectionError:
        return {"error": "无法连接到 AnythingLLM 服务，请检查是否已启动"}
    except requests.exceptions.RequestException as e:
        return {"error": f"RAG 查询失败：{str(e)}"}


def execute_rag_validation(topic, core_variables, theory):
    """
    执行完整的 RAG 文献验证流程（最多 3 次查询）
    
    Args:
        topic: 研究主题
        core_variables: 核心变量列表
        theory: 核心理论
    
    Returns:
        dict: 包含 3 次检索结果的报告
    """
    queries = [
        {
            "name": "领域核心文献",
            "query": f"{topic} 的影响因素 文献",
            "purpose": "验证学生是否遗漏重要文献"
        },
        {
            "name": "变量测量方法",
            "query": f"{core_variables[0] if core_variables else '核心变量'} 如何测量 指标",
            "purpose": "验证学生使用的测量方法是否规范"
        },
        {
            "name": "理论机制",
            "query": f"{theory} 机制 路径",
            "purpose": "验证理论框架是否完整"
        }
    ]
    
    results = []
    for q in queries:
        print(f"\n[*] 执行检索：{q['name']}")
        print(f"    Query: {q['query']}")
        result = rag_query(q['query'])
        
        if 'error' in result:
            results.append({
                "name": q['name'],
                "query": q['query'],
                "purpose": q['purpose'],
                "error": result['error']
            })
        else:
            results.append({
                "name": q['name'],
                "query": q['query'],
                "purpose": q['purpose'],
                "textResponse": result.get('textResponse', ''),
                "sources": result.get('sources', []),
                "source_count": len(result.get('sources', []))
            })
    
    return {
        "queries": queries,
        "results": results,
        "total_queries": len(queries),
        "successful_queries": sum(1 for r in results if 'error' not in r)
    }


def format_rag_report(validation_result):
    """
    格式化 RAG 文献验证报告
    
    Args:
        validation_result: execute_rag_validation 的返回值
    
    Returns:
        str: Markdown 格式的报告
    """
    report = []
    report.append("### RAG 文献验证报告\n")
    
    for i, result in enumerate(validation_result['results'], 1):
        report.append(f"**检索{i}：{result['name']}**")
        report.append(f"- Query: {result['query']}")
        report.append(f"- 目的：{result['purpose']}")
        
        if 'error' in result:
            report.append(f"- [ERROR] 错误：{result['error']}")
        else:
            report.append(f"- 检索结果：{result['source_count']} 篇相关文献")
            if result['textResponse']:
                # 截取前 500 字作为摘要
                summary = result['textResponse'][:500]
                if len(result['textResponse']) > 500:
                    summary += "..."
                report.append(f"- 关键发现：{summary}")
        
        report.append("")
    
    # 文献缺口识别（需要人工判断，这里只提供框架）
    report.append("**文献缺口识别**：")
    report.append("- 学生未引用的重要文献：[待评审者补充]")
    report.append("- 测量方法不一致：[待评审者补充]")
    report.append("- 理论框架缺失环节：[待评审者补充]")
    
    return "\n".join(report)


if __name__ == "__main__":
    # 测试 RAG 查询
    print("=" * 60)
    print("AnythingLLM RAG 文献验证工具")
    print("=" * 60)
    
    config = load_config()
    print(f"\n当前配置:")
    print(f"  Base URL: {config.get('base_url')}")
    print(f"  Workspace: {config.get('workspace_slug')}")
    
    # 示例查询
    print("\n执行示例查询...")
    result = rag_query("家庭金融的影响因素有哪些？")
    
    if 'error' in result:
        print(f"[ERROR] 错误：{result['error']}")
    else:
        print(f"[OK] 查询成功")
        print(f"检索到 {len(result.get('sources', []))} 篇文献")
        print(f"\n回答摘要:")
        print(result.get('textResponse', '')[:500])
