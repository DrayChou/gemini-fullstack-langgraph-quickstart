#!/usr/bin/env python3
"""
Simple API connection test for OpenAI and Gemini.
"""

from dotenv import load_dotenv
import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_openai():
    """Test OpenAI API connection."""
    try:
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OpenAI API key not found")
            return False
        base_url = os.getenv(
            "OPENAI_BASE_URL",
            "https://api.openai.com/v1")
        if not base_url.startswith("http"):
            print("❌ OpenAI API base URL is not valid")
            return False

        client = OpenAI(api_key=api_key, base_url=base_url)

        # Simple test request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, respond with 'OK'"}],
            max_tokens=10
        )

        result = response.choices[0].message.content
        print(f"✅ OpenAI test successful: {result}")
        return True

    except ImportError:
        print("❌ OpenAI package not installed")
        return False
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False


def test_gemini():
    """Test Gemini API connection."""
    try:
        from google.genai import Client

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ Gemini API key not found")
            return False

        client = Client(api_key=api_key)

        # Simple test request
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents="Hello, respond with 'OK'",
        )

        result = response.text
        print(f"✅ Gemini test successful: {result}")
        return True

    except ImportError:
        print("❌ Gemini package not installed")
        return False
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False


def test_duckduckgo():
    """Test DuckDuckGo search."""
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            results = list(ddgs.text("python programming", max_results=2))

        if results:
            print(f"✅ DuckDuckGo search successful: {len(results)} results")
            return True
        else:
            print("❌ DuckDuckGo search returned no results")
            return False

    except ImportError:
        print("❌ DuckDuckGo search package not installed")
        return False
    except Exception as e:
        print(f"❌ DuckDuckGo search failed: {e}")
        return False


def main():
    print("=== API Connection Tests ===\n")

    # Load environment variables
    load_dotenv()

    # Test APIs
    openai_ok = test_openai()
    gemini_ok = test_gemini()
    search_ok = test_duckduckgo()

    print("\n=== Summary ===")
    print(f"OpenAI: {'✅' if openai_ok else '❌'}")
    print(f"Gemini: {'✅' if gemini_ok else '❌'}")
    print(f"Search: {'✅' if search_ok else '❌'}")

    if openai_ok or gemini_ok:
        print("\n✅ At least one LLM provider is working!")
    else:
        print("\n❌ No LLM providers are working. Please check your API keys.")


if __name__ == "__main__":
    main()
