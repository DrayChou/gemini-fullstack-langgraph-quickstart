#!/usr/bin/env python3
"""
直接启动LangGraph代理服务的脚本
"""

import uvicorn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 首先加载环境变量
load_dotenv()

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# 导入代理图和应用
from agent.graph import graph
from agent.app import app

# 检查配置
from agent.configuration import Configuration

def check_configuration():
    """检查配置是否正确"""
    print("🔧 检查配置...")
    
    config = Configuration.from_runnable_config()
    
    print(f"✅ API Provider: {config.api_provider}")
    print(f"✅ Effective Provider: {config.get_effective_api_provider()}")
    
    if hasattr(config, 'openai_model') and config.openai_model:
        print(f"✅ OpenAI Model: {config.openai_model}")
    
    # 检查模型配置
    print("\n📋 模型配置:")
    print(f"  - Query Generator: {config.get_model('query_generator_model')}")
    print(f"  - Reflection: {config.get_model('reflection_model')}")
    print(f"  - Answer: {config.get_model('answer_model')}")
    
    # 检查API密钥
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ OpenAI API Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ OpenAI API Key not found")
        return False
    
    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        print(f"✅ OpenAI Base URL: {base_url}")
    
    return True

def start_server():
    """启动服务器"""
    print("\n🚀 启动LangGraph代理服务...")
    print("📍 访问地址:")
    print("   - API: http://localhost:8000")
    print("   - 文档: http://localhost:8000/docs")
    print("   - 前端: http://localhost:8000/app")
    print("\n按 Ctrl+C 停止服务\n")
    
    # 启动服务器
    uvicorn.run(
        "agent.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["src"]
    )

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 LangGraph Agent with DeepSeek-V3")
    print("=" * 50)
    
    if check_configuration():
        start_server()
    else:
        print("❌ 配置检查失败，请检查环境变量设置")
        sys.exit(1)
