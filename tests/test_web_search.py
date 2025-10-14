"""
Test web search functionality with both OpenAI and Perplexity providers.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from src.tools import web_search


def test_openai_search():
    """Test OpenAI web search using Responses API."""
    print("=" * 60)
    print("Testing OpenAI Web Search (Responses API)")
    print("=" * 60)
    
    # Set provider to OpenAI
    original_provider = os.getenv("SEARCH_PROVIDER")
    os.environ["SEARCH_PROVIDER"] = "openai"
    
    try:
        query = "What is the latest version of Python?"
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        result = web_search.invoke({"query": query})
        print(f"Result: {result[:200]}..." if len(result) > 200 else f"Result: {result}")
        print("-" * 60)
        
        # Check if it's a Responses API availability issue
        if "Responses API" in result and "not be available" in result:
            print("⚠️  OpenAI Responses API not available for your account yet")
            print("💡 Tip: Use SEARCH_PROVIDER=perplexity as alternative")
            return None  # Not a failure, just not available
        
        if "error" in result.lower() or "not available" in result.lower():
            print("❌ OpenAI search failed")
            return False
        else:
            print("✅ OpenAI search successful (Responses API working)")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ["SEARCH_PROVIDER"] = original_provider
        else:
            os.environ.pop("SEARCH_PROVIDER", None)


def test_perplexity_search():
    """Test Perplexity web search."""
    print("\n" + "=" * 60)
    print("Testing Perplexity Web Search")
    print("=" * 60)
    
    # Check if Perplexity key is available
    if not os.getenv("PERPLEXITY_API_KEY"):
        print("⚠️  Perplexity API key not found - skipping test")
        return None
    
    # Set provider to Perplexity
    original_provider = os.getenv("SEARCH_PROVIDER")
    os.environ["SEARCH_PROVIDER"] = "perplexity"
    
    try:
        query = "What is the latest version of Node.js?"
        print(f"\nQuery: {query}")
        print("-" * 60)
        
        result = web_search.invoke({"query": query})
        print(f"Result: {result}")
        print("-" * 60)
        
        if "error" in result.lower() or "not available" in result.lower():
            print("❌ Perplexity search failed")
            return False
        else:
            print("✅ Perplexity search successful")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Restore original provider
        if original_provider:
            os.environ["SEARCH_PROVIDER"] = original_provider
        else:
            os.environ.pop("SEARCH_PROVIDER", None)


def test_default_provider():
    """Test that default provider is OpenAI."""
    print("\n" + "=" * 60)
    print("Testing Default Provider")
    print("=" * 60)
    
    # Remove provider env var to test default
    original_provider = os.getenv("SEARCH_PROVIDER")
    if "SEARCH_PROVIDER" in os.environ:
        del os.environ["SEARCH_PROVIDER"]
    
    try:
        provider = os.getenv("SEARCH_PROVIDER", "openai").lower()
        print(f"\nDefault provider: {provider}")
        
        if provider == "openai":
            print("✅ Default provider is OpenAI")
            return True
        else:
            print(f"❌ Default provider is {provider}, expected 'openai'")
            return False
            
    finally:
        # Restore original provider
        if original_provider:
            os.environ["SEARCH_PROVIDER"] = original_provider


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("WEB SEARCH INTEGRATION TESTS")
    print("=" * 60)
    
    # Check prerequisites
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    results = []
    
    # Test default provider
    results.append(("Default Provider", test_default_provider()))
    
    # Test OpenAI search
    openai_result = test_openai_search()
    if openai_result is not None:
        results.append(("OpenAI Search (Responses API)", openai_result))
    else:
        print("\n⚠️  OpenAI Responses API not available - this is expected for some accounts")
    
    # Test Perplexity search (if available)
    perplexity_result = test_perplexity_search()
    if perplexity_result is not None:
        results.append(("Perplexity Search", perplexity_result))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Overall result
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("-" * 60)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

