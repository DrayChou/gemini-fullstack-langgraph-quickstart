#!/usr/bin/env python3
"""
测试运行中的LangGraph API服务
"""

import requests
import json
import time

def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API服务运行正常")
            return True
        else:
            print(f"❌ API健康检查失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API服务: {e}")
        return False

def test_agent_query():
    """测试代理查询功能"""
    print("\n🧪 测试代理查询功能...")
    
    # 这里需要根据实际的API端点来调整
    # 通常LangGraph会提供类似 /runs 或 /invoke 的端点
    test_query = {
        "messages": [
            {
                "role": "human",
                "content": "什么是人工智能？"
            }
        ]
    }
    
    try:
        # 尝试不同的可能端点
        endpoints_to_try = [
            "/agent/runs",
            "/runs",
            "/invoke",
            "/chat"
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = requests.post(
                    f"http://localhost:8000{endpoint}",
                    json=test_query,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ 端点 {endpoint} 响应成功")
                    result = response.json()
                    print(f"📝 响应摘要: {str(result)[:100]}...")
                    return True
                else:
                    print(f"⚠️ 端点 {endpoint} 返回状态码: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"⚠️ 端点 {endpoint} 请求失败: {e}")
                continue
        
        print("❌ 所有测试端点都无法正常工作")
        return False
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

def main():
    """主函数"""
    print("🧪 LangGraph API 测试工具")
    print("=" * 40)
    
    # 测试API健康状态
    if not test_api_health():
        print("\n💡 请确保服务器正在运行:")
        print("   运行: python start_server.py")
        return
    
    # 等待一秒
    time.sleep(1)
    
    # 测试代理功能
    test_agent_query()
    
    print("\n📖 更多信息:")
    print("   - API文档: http://localhost:8000/docs")
    print("   - 前端界面: http://localhost:8000/app")

if __name__ == "__main__":
    main()
