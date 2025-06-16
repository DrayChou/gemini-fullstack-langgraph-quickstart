#!/usr/bin/env python3
"""
Comprehensive test to verify OpenAI adapter can fully replace Gemini functionality.
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
from agent.llm_factory import LLMFactory
from agent.tools_and_schemas import SearchQueryList, Reflection


def test_openai_structured_output():
    """Test OpenAI structured output capability."""
    print("Testing OpenAI structured output...")
    
    # Set environment to use OpenAI
    os.environ["API_PROVIDER"] = "openai"
    
    try:
        config = Configuration.from_runnable_config()
        
        # Create LLM
        llm = LLMFactory.create_llm(
            config=config,
            model_type="query_generator_model",
            temperature=0.7,
            max_retries=2,
        )
        
        # Test structured output with SearchQueryList
        structured_llm = llm.with_structured_output(SearchQueryList)
        
        prompt = """
Generate 3 search queries about machine learning fundamentals.
Format the response as JSON with a 'query' field containing an array of strings.
"""
        
        result = structured_llm.invoke(prompt)
        
        if result and hasattr(result, 'query') and isinstance(result.query, list):
            print(f"✅ Structured output test passed")
            print(f"✅ Generated {len(result.query)} queries:")
            for i, query in enumerate(result.query, 1):
                print(f"   {i}. {query}")
            return True
        else:
            print(f"❌ Structured output test failed: Invalid result format")
            return False
            
    except Exception as e:
        print(f"❌ Structured output test failed: {e}")
        return False


def test_openai_reflection_schema():
    """Test OpenAI with Reflection schema."""
    print("Testing OpenAI Reflection schema...")
    
    try:
        config = Configuration.from_runnable_config()
        
        # Create LLM
        llm = LLMFactory.create_llm(
            config=config,
            model_type="reflection_model",
            temperature=0.3,
            max_retries=2,
        )
        
        # Test structured output with Reflection
        structured_llm = llm.with_structured_output(Reflection)
        
        prompt = """
Analyze this research: "Python is a popular programming language for AI."
Determine if more research is needed and provide follow-up queries.
Format as JSON with 'follow_up_queries' (array) and 'is_sufficient' (boolean).
"""
        
        result = structured_llm.invoke(prompt)
        
        if result and hasattr(result, 'is_sufficient') and hasattr(result, 'follow_up_queries'):
            print(f"✅ Reflection schema test passed")
            print(f"✅ Is sufficient: {result.is_sufficient}")
            print(f"✅ Follow-up queries: {len(result.follow_up_queries)}")
            return True
        else:
            print(f"❌ Reflection schema test failed: Invalid result format")
            return False
            
    except Exception as e:
        print(f"❌ Reflection schema test failed: {e}")
        return False


def test_openai_vs_gemini_interface():
    """Test that OpenAI adapter has the same interface as Gemini."""
    print("Testing OpenAI vs Gemini interface compatibility...")
    
    try:
        config = Configuration.from_runnable_config()
        
        # Test both providers if available
        providers_to_test = []
        
        if os.getenv("OPENAI_API_KEY"):
            providers_to_test.append("openai")
            
        if os.getenv("GEMINI_API_KEY"):
            providers_to_test.append("gemini")
        
        interfaces_match = True
        
        for provider in providers_to_test:
            # Temporarily set provider
            original_provider = config.api_provider
            config.api_provider = provider
            
            try:
                llm = LLMFactory.create_llm(
                    config=config,
                    model_type="query_generator_model"
                )
                
                # Test common methods
                assert hasattr(llm, 'with_structured_output'), f"{provider} missing with_structured_output"
                assert hasattr(llm, '_generate'), f"{provider} missing _generate"
                assert hasattr(llm, '_llm_type'), f"{provider} missing _llm_type"
                
                print(f"✅ {provider.title()} interface check passed")
                
            except Exception as e:
                if provider == "gemini" and "location" in str(e).lower():
                    print(f"⚠️  Gemini skipped due to region restriction")
                else:
                    print(f"❌ {provider.title()} interface check failed: {e}")
                    interfaces_match = False
            finally:
                # Restore original provider
                config.api_provider = original_provider
        
        return interfaces_match
        
    except Exception as e:
        print(f"❌ Interface compatibility test failed: {e}")
        return False


def test_graph_integration():
    """Test integration with the main graph."""
    print("Testing graph integration...")
    
    # Set environment to use OpenAI
    os.environ["API_PROVIDER"] = "openai"
    
    try:
        from agent.graph import generate_query
        
        # Create test state
        state = {
            "messages": [HumanMessage(content="What is artificial intelligence?")],
            "initial_search_query_count": 2
        }
        
        # Test query generation
        result = generate_query(state, {"configurable": {}})
        
        if result and 'query_list' in result and isinstance(result['query_list'], list):
            print(f"✅ Graph integration test passed")
            print(f"✅ Generated {len(result['query_list'])} queries")
            return True
        else:
            print(f"❌ Graph integration test failed: Invalid result")
            return False
            
    except Exception as e:
        print(f"❌ Graph integration test failed: {e}")
        return False


def main():
    """Run all OpenAI compatibility tests."""
    print("=== OpenAI Gemini Replacement Tests ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check API keys
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_gemini = bool(os.getenv("GEMINI_API_KEY"))
    
    print(f"OpenAI API Key: {'✅' if has_openai else '❌'}")
    print(f"Gemini API Key: {'✅' if has_gemini else '❌'}")
    print()
    
    if not has_openai:
        print("❌ OpenAI API key not found. Cannot run tests.")
        return
    
    # Run tests
    results = []
    
    results.append(("Structured Output", test_openai_structured_output()))
    print()
    
    results.append(("Reflection Schema", test_openai_reflection_schema()))
    print()
    
    results.append(("Interface Compatibility", test_openai_vs_gemini_interface()))
    print()
    
    results.append(("Graph Integration", test_graph_integration()))
    print()
    
    # Summary
    print("=== Test Results Summary ===")
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 OpenAI adapter can fully replace Gemini functionality!")
    else:
        print("⚠️ Some tests failed. OpenAI adapter needs more work.")


if __name__ == "__main__":
    main()
