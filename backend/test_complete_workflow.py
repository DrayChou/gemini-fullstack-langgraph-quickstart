#!/usr/bin/env python3
"""
End-to-end test of the complete LangGraph agent with OpenAI.
"""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage


def test_complete_workflow():
    """Test the complete agent workflow with OpenAI."""
    print("Testing complete agent workflow with OpenAI...")
    
    # Set environment to use OpenAI
    os.environ["API_PROVIDER"] = "openai"
    
    try:
        from agent.graph import graph
        
        # Create test input
        test_query = "What are the key benefits of using Python for data science?"
        
        input_state = {
            "messages": [HumanMessage(content=test_query)],
            "initial_search_query_count": 2,  # Reduced for faster testing
            "max_research_loops": 1  # Reduced for faster testing
        }
        
        print(f"Input query: {test_query}")
        print("Running agent workflow...")
        
        # Run the complete graph
        result = graph.invoke(input_state, {"configurable": {}})
        
        # Validate results
        if result and "messages" in result:
            final_message = result["messages"][-1]
            print(f"✅ Workflow completed successfully")
            print(f"✅ Final answer length: {len(final_message.content)} characters")
            
            if "sources_gathered" in result:
                print(f"✅ Sources gathered: {len(result['sources_gathered'])}")
            
            if "query_list" in result:
                print(f"✅ Queries generated: {len(result['query_list'])}")
            
            # Show a snippet of the answer
            answer_snippet = final_message.content[:200] + "..."
            print(f"\nAnswer snippet:\n{answer_snippet}")
            
            return True
        else:
            print("❌ Workflow failed: Invalid result structure")
            return False
            
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete workflow test."""
    print("=== Complete OpenAI Agent Workflow Test ===\n")
    
    # Load environment variables
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found. Cannot run test.")
        return
    
    # Run test
    success = test_complete_workflow()
    
    print("\n=== Test Results ===")
    if success:
        print("🎉 Complete workflow test PASSED!")
        print("✅ OpenAI integration is fully functional")
    else:
        print("❌ Complete workflow test FAILED!")
        print("⚠️ Issues need to be resolved")


if __name__ == "__main__":
    main()
