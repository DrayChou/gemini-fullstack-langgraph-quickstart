#!/usr/bin/env python3
"""
Test DeepSeek-V3 model configuration.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from agent.configuration import Configuration
from agent.llm_factory import LLMFactory


def test_deepseek_configuration():
    """Test that DeepSeek-V3 is being used."""
    print("Testing DeepSeek-V3 configuration...")
    
    # Load environment
    load_dotenv()
    
    # Create configuration
    config = Configuration.from_runnable_config()
    
    print(f"API Provider: {config.api_provider}")
    print(f"Effective Provider: {config.get_effective_api_provider()}")
    
    # Test model configurations
    models = {
        "query_generator_model": config.get_model("query_generator_model"),
        "reflection_model": config.get_model("reflection_model"),
        "answer_model": config.get_model("answer_model")
    }
    
    print("\nConfigured Models:")
    for model_type, model_name in models.items():
        print(f"  {model_type}: {model_name}")
    
    # Verify all models are DeepSeek-V3
    all_deepseek = all(model == "deepseek-v3" for model in models.values())
    
    if all_deepseek:
        print("✅ All models correctly configured to use DeepSeek-V3")
    else:
        print("❌ Some models are not using DeepSeek-V3")
        return False
    
    # Test LLM creation
    try:
        llm = LLMFactory.create_llm(
            config=config,
            model_type="query_generator_model",
            temperature=0.7
        )
        
        print(f"✅ LLM Factory created: {type(llm).__name__}")
        print(f"✅ Model name: {llm.model}")
        
        if llm.model == "deepseek-v3":
            print("✅ Confirmed: Using DeepSeek-V3 model")
            return True
        else:
            print(f"❌ Expected deepseek-v3, got: {llm.model}")
            return False
            
    except Exception as e:
        print(f"❌ LLM creation failed: {e}")
        return False


def test_deepseek_api_call():
    """Test actual API call with DeepSeek-V3."""
    print("\nTesting DeepSeek-V3 API call...")
    
    try:
        config = Configuration.from_runnable_config()
        llm = LLMFactory.create_llm(config=config, model_type="query_generator_model")
        
        from langchain_core.messages import HumanMessage
        
        # Simple test message
        messages = [HumanMessage(content="Say 'Hello from DeepSeek-V3' in exactly those words.")]
        
        # Generate response
        response = llm._generate(messages)
        content = response.generations[0].message.content
        
        print(f"✅ API call successful")
        print(f"Response: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False


def main():
    """Run DeepSeek-V3 tests."""
    print("=== DeepSeek-V3 Configuration Test ===\n")
    
    results = []
    
    results.append(("Configuration", test_deepseek_configuration()))
    print()
    
    results.append(("API Call", test_deepseek_api_call()))
    print()
    
    # Summary
    print("=== Test Results ===")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 DeepSeek-V3 is properly configured and working!")
    else:
        print("⚠️ Some tests failed. Check your configuration.")


if __name__ == "__main__":
    main()
