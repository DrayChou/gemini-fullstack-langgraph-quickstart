#!/usr/bin/env python3
"""
验证环境变量加载的脚本
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """测试环境变量加载"""
    print("=== 环境变量测试 ===")
    
    # 加载环境变量
    load_dotenv()
    
    # 检查关键环境变量
    env_vars = [
        "API_PROVIDER",
        "OPENAI_API_KEY", 
        "OPENAI_BASE_URL",
        "OPENAI_MODEL"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            if "API_KEY" in var:
                # 隐藏API密钥的大部分内容
                display_value = f"{value[:10]}...{value[-4:]}"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: Not Set")
    
    print("\n=== 配置类测试 ===")
    
    # 测试配置类
    try:
        import sys
        from pathlib import Path
        
        # 添加src目录到Python路径
        src_path = Path(__file__).parent / "src"
        sys.path.insert(0, str(src_path))
        
        from agent.configuration import Configuration
        from agent.llm_factory import LLMFactory
        
        config = Configuration.from_runnable_config()
        
        print(f"✅ API Provider: {config.api_provider}")
        print(f"✅ Effective Provider: {config.get_effective_api_provider()}")
        
        if hasattr(config, 'openai_model') and config.openai_model:
            print(f"✅ OpenAI Model: {config.openai_model}")
        
        # 验证API密钥
        provider = config.get_effective_api_provider()
        if LLMFactory.validate_api_key(provider):
            print(f"✅ {provider.upper()} API Key is valid")
        else:
            print(f"❌ {provider.upper()} API Key is missing or invalid")
            
        print("\n=== LLM创建测试 ===")
        
        # 尝试创建LLM
        llm = LLMFactory.create_llm(
            config=config,
            model_type="query_generator_model"
        )
        
        print(f"✅ LLM created successfully: {type(llm).__name__}")
        print(f"✅ Model name: {llm.model}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_env_loading()
    
    if success:
        print("\n🎉 所有环境变量和配置都正常！")
    else:
        print("\n❌ 配置有问题，请检查环境变量")
