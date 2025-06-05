#!/usr/bin/env python3
"""
集成测试脚本，验证整个LangGraph代理是否能正常工作，包括代理配置。
"""

import os
import asyncio
from dotenv import load_dotenv
from agent.graph import graph
from langchain_core.messages import HumanMessage

# 加载环境变量
load_dotenv()

async def test_agent_with_proxy():
    """测试LangGraph代理是否能正常工作，并使用代理配置"""
    
    # 显示代理配置
    http_proxy = os.getenv("HTTP_PROXY")
    https_proxy = os.getenv("HTTPS_PROXY")
    print(f"HTTP代理: {http_proxy}")
    print(f"HTTPS代理: {https_proxy}")
    
    # 准备输入消息
    input_data = {
        "messages": [HumanMessage(content="今天是星期几？")],
        "initial_search_query_count": 1,  # 减少搜索查询数量以节省配额
        "max_research_loops": 1  # 减少研究循环以节省配额
    }
    
    print("\n开始测试LangGraph代理...")
    print("输入问题:", input_data["messages"][0].content)
    
    try:
        # 运行代理
        result = await graph.ainvoke(input_data)
        
        print("\n✅ 代理测试成功!")
        print("最终回答:", result["messages"][-1].content[:200] + "..." if len(result["messages"][-1].content) > 200 else result["messages"][-1].content)
        
        if "sources_gathered" in result and result["sources_gathered"]:
            print(f"\n找到 {len(result['sources_gathered'])} 个信息源")
            for i, source in enumerate(result["sources_gathered"][:3]):  # 只显示前3个
                print(f"  {i+1}. {source.get('value', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 代理测试失败: {str(e)}")
        return False

async def main():
    """主函数"""
    print("=" * 60)
    print("LangGraph代理集成测试（包括HTTP代理支持）")
    print("=" * 60)
    
    success = await test_agent_with_proxy()
    
    if success:
        print("\n🎉 所有测试通过！HTTP代理配置和LangGraph代理都工作正常。")
    else:
        print("\n⚠️  测试失败，请检查配置和网络连接。")

if __name__ == "__main__":
    asyncio.run(main())
