#!/usr/bin/env python3
"""
Test script for the multi-provider LLM configuration.
Tests both Gemini and OpenAI API integration.
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
from agent.search_factory import SearchFactory

def test_configuration():
    """Test configuration loading."""
    print("Testing configuration...")
    
    # Load environment variables
    load_dotenv()
    
    # Test default configuration
    config = Configuration()
    print(f"API Provider: {config.api_provider}")
    print(f"Query Generator Model: {config.query_generator_model}")
    print(f"Reflection Model: {config.reflection_model}")
    print(f"Answer Model: {config.answer_model}")
    print(f"Search Provider: {config.search_provider}")
    print()

def test_api_keys():
    """Test API key availability."""
    print("Testing API key availability...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    print(f"Gemini API Key: {'✓ Available' if gemini_key else '✗ Not set'}")
    print(f"OpenAI API Key: {'✓ Available' if openai_key else '✗ Not set'}")
    print()

def test_llm_factory():
    """Test LLM factory."""
    print("Testing LLM Factory...")
    
    config = Configuration()
    
    try:
        # Test query generator model
        llm = LLMFactory.create_llm(config, "query_generator_model")
        print(f"✓ Query Generator LLM created: {type(llm).__name__}")
        
        # Test reflection model
        llm = LLMFactory.create_llm(config, "reflection_model")
        print(f"✓ Reflection LLM created: {type(llm).__name__}")
        
        # Test answer model
        llm = LLMFactory.create_llm(config, "answer_model")
        print(f"✓ Answer LLM created: {type(llm).__name__}")
        
    except Exception as e:
        print(f"✗ LLM Factory test failed: {e}")
    
    print()

def test_search_factory():
    """Test search factory."""
    print("Testing Search Factory...")
    
    config = Configuration()
    
    try:
        # Test DuckDuckGo search directly
        from agent.search_adapter import web_search
        search_results = web_search("Python programming", num_results=3)
        
        print(f"✓ Search completed: {len(search_results)} results")
        if search_results:
            print(f"✓ First result: {search_results[0].get('title', 'No title')}")
        
    except Exception as e:
        print(f"✗ Search Factory test failed: {e}")
    
    print()

def main():
    """Run all tests."""
    print("=== Multi-Provider LLM Configuration Test ===\n")
    
    test_configuration()
    test_api_keys()
    test_llm_factory()
    test_search_factory()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
