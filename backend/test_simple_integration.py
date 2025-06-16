#!/usr/bin/env python3
"""
Multi-provider integration test for testing both Gemini and OpenAI configurations.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from agent.configuration import Configuration


def test_simple_query_generation():
    """Test basic query generation functionality."""
    print("Testing simple query generation...")
    
    try:
        from agent.graph import generate_query
        
        # Create test state
        state = {
            "messages": [HumanMessage(content="What is machine learning?")]
        }
        
        # Test query generation
        result = generate_query(state, {"configurable": {}})
        
        print(f"✓ Query generation successful")
        print(f"✓ Generated {len(result['query_list'])} queries")
        
        return True
        
    except Exception as e:
        print(f"✗ Query generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_functionality():
    """Test search functionality."""
    print("Testing search functionality...")
    
    try:
        from agent.search_adapter import web_search
        
        # Test DuckDuckGo search
        results = web_search("Python tutorial", num_results=2)
        
        print(f"✓ Search successful")
        print(f"✓ Found {len(results)} results")
        
        return True
        
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return False


def main():
    """Run integration tests."""
    print("=== Simple Integration Tests ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check current configuration
    config = Configuration()
    print(f"Current API Provider: {config.api_provider}")
    print(f"Current Search Provider: {config.search_provider}")
    print()
    
    # Run tests
    results = []
    
    results.append(("Query Generation", test_simple_query_generation()))
    print()
    
    results.append(("Search Functionality", test_search_functionality()))
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
