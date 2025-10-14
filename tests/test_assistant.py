"""
Test script to verify the AI Assistant setup and functionality.
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()


def test_environment():
    """Test environment variables."""
    print("Testing environment variables...")
    
    required_keys = ["OPENAI_API_KEY"]
    optional_keys = ["PERPLEXITY_API_KEY", "MODEL_PROVIDER", "MODEL_NAME"]
    
    missing = []
    for key in required_keys:
        if not os.getenv(key):
            missing.append(key)
            print(f"  ❌ {key} - NOT SET")
        else:
            print(f"  ✓ {key} - SET")
    
    for key in optional_keys:
        if os.getenv(key):
            print(f"  ✓ {key} - SET ({os.getenv(key)})")
        else:
            print(f"  ⚠️  {key} - NOT SET (optional)")
    
    if missing:
        print(f"\n❌ Missing required keys: {', '.join(missing)}")
        return False
    
    print("✓ Environment variables OK\n")
    return True


def test_knowledge_base():
    """Test knowledge base file."""
    print("Testing knowledge base...")
    
    if not os.path.exists("data/pieces_knowledge_base.json"):
        print("  ❌ data/pieces_knowledge_base.json not found")
        return False
    
    try:
        with open("data/pieces_knowledge_base.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        pieces = data.get("pieces", [])
        
        print(f"  ✓ Total pieces: {metadata.get('totalPieces', 0)}")
        print(f"  ✓ Total actions: {metadata.get('totalActions', 0)}")
        print(f"  ✓ Total triggers: {metadata.get('totalTriggers', 0)}")
        print(f"  ✓ Loaded {len(pieces)} pieces")
        
        print("✓ Knowledge base OK\n")
        return True
    
    except Exception as e:
        print(f"  ❌ Error loading knowledge base: {e}")
        return False


def test_vector_store():
    """Test vector store."""
    print("Testing vector store...")
    
    if not os.path.exists("data/ap_faiss_index"):
        print("  ❌ Vector store not found")
        print("  Run: python scripts/migration/prepare_knowledge_base.py")
        return False
    
    try:
        from langchain_openai import OpenAIEmbeddings
        from langchain_community.vectorstores import FAISS
        
        embeddings = OpenAIEmbeddings()
        vector_store = FAISS.load_local(
            "data/ap_faiss_index", 
            embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Test search
        results = vector_store.similarity_search("Slack integration", k=1)
        
        if results:
            print(f"  ✓ Vector store loaded successfully")
            print(f"  ✓ Test search returned {len(results)} results")
            print("✓ Vector store OK\n")
            return True
        else:
            print("  ⚠️  Vector store loaded but search returned no results")
            return True
    
    except Exception as e:
        print(f"  ❌ Error loading vector store: {e}")
        return False


def test_tools():
    """Test tool functions."""
    print("Testing tools...")
    
    try:
        from src.tools import find_piece_by_name, find_action_by_name
        
        # Test finding a piece
        slack = find_piece_by_name("Slack")
        if slack:
            print(f"  ✓ Found piece: {slack.get('displayName')}")
        else:
            print("  ⚠️  Could not find Slack piece")
        
        # Test finding an action
        actions = find_action_by_name("send message")
        if actions:
            print(f"  ✓ Found {len(actions)} actions matching 'send message'")
        else:
            print("  ⚠️  Could not find any actions")
        
        print("✓ Tools OK\n")
        return True
    
    except Exception as e:
        print(f"  ❌ Error testing tools: {e}")
        return False


def test_llm():
    """Test LLM initialization."""
    print("Testing LLM initialization...")
    
    try:
        from src.llm_config import get_llm
        
        llm = get_llm()
        print("  ✓ LLM initialized successfully")
        
        # Test a simple call
        response = llm.invoke("Say 'Hello'")
        print(f"  ✓ LLM response: {response.content[:50]}...")
        
        print("✓ LLM OK\n")
        return True
    
    except Exception as e:
        print(f"  ❌ Error testing LLM: {e}")
        return False


def test_agent():
    """Test agent creation."""
    print("Testing agent...")
    
    try:
        from src.agent import get_agent
        
        agent = get_agent()
        print("  ✓ Agent created successfully")
        
        # Test a simple query
        print("  Testing agent with query: 'Does ActivePieces have Slack?'")
        result = agent.invoke({"input": "Does ActivePieces have Slack?"})
        
        response = result.get("output", "")
        print(f"  ✓ Agent response: {response[:100]}...")
        
        print("✓ Agent OK\n")
        return True
    
    except Exception as e:
        print(f"  ❌ Error testing agent: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("🧪 ActivePieces AI Assistant - Test Suite")
    print("="*60 + "\n")
    
    tests = [
        ("Environment", test_environment),
        ("Knowledge Base", test_knowledge_base),
        ("Vector Store", test_vector_store),
        ("Tools", test_tools),
        ("LLM", test_llm),
        ("Agent", test_agent),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except KeyboardInterrupt:
            print("\n\n⚠️  Tests interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {name}: {e}\n")
            results[name] = False
    
    # Summary
    print("="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your assistant is ready to use.")
        print("\nNext steps:")
        print("1. Run backend: uvicorn src.main:app --reload")
        print("2. Run frontend: cd frontend && npm run dev")
        print("3. Open browser: http://localhost:5173")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)
    
    print("="*60)


if __name__ == "__main__":
    main()

