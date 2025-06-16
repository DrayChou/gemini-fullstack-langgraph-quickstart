#!/usr/bin/env python3
"""
Test OpenAI configuration specifically.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set OpenAI configuration
os.environ["API_PROVIDER"] = "openai"
os.environ["SEARCH_PROVIDER"] = "duckduckgo"

from agent.configuration import Configuration


def test_openai_configuration():
    """Test OpenAI configuration."""
    print("Testing OpenAI configuration...")
    
    config = Configuration.from_runnable_config()
    
    print(f"API Provider: {config.api_provider}")
    print(f"Query Model: {config.get_model('query_generator_model')}")
    print(f"Reflection Model: {config.get_model('reflection_model')}")
    print(f"Answer Model: {config.get_model('answer_model')}")
    
    # Test LLM factory
    from agent.llm_factory import LLMFactory
    
    try:
        llm = LLMFactory.create_llm(config, "query_generator_model")
        print(f"✓ LLM created: {type(llm).__name__}")
        
        # Test structured output
        structured_llm = llm.with_structured_output(dict)
        print("✓ Structured output wrapper created")
        
        return True
        
    except Exception as e:
        print(f"✗ LLM creation failed: {e}")
        return False


def test_openai_adapter():
    """Test OpenAI adapter directly."""
    print("Testing OpenAI adapter...")
    
    try:
        from agent.openai_adapter import CustomOpenAIChat
        
        # Test creation (should work even without API key for basic functionality)
        llm = CustomOpenAIChat(
            model="gpt-3.5-turbo",
            api_key="test-key"  # Fake key for testing
        )
        
        print(f"✓ OpenAI adapter created: {type(llm).__name__}")
        
        # Test structured output wrapper
        from agent.tools_and_schemas import SearchQueryList
        structured_llm = llm.with_structured_output(SearchQueryList)
        print("✓ Structured output wrapper created")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenAI adapter test failed: {e}")
        return False


def main():
    """Run OpenAI specific tests."""
    print("=== OpenAI Configuration Tests ===\n")
    
    results = []
    
    results.append(("OpenAI Configuration", test_openai_configuration()))
    print()
    
    results.append(("OpenAI Adapter", test_openai_adapter()))
    print()
    
    # Summary
    print("=== Test Results ===")
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()
