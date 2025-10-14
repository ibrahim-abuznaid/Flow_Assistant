"""
Test script for the Planning Layer (GPT-5).
Run this to verify the planner is working correctly.
"""
from dotenv import load_dotenv
from src.planner import create_guided_input, get_planner

# Load environment variables
load_dotenv()


def test_planner():
    """Test the planning layer with various query types."""
    
    print("\n" + "="*80)
    print("🧪 TESTING PLANNING LAYER")
    print("="*80 + "\n")
    
    test_queries = [
        {
            "name": "Simple Integration Check",
            "query": "Is Gmail available in ActivePieces?"
        },
        {
            "name": "Flow Building",
            "query": "I want to send an email when a new file is added to Google Drive"
        },
        {
            "name": "Explanation Request",
            "query": "How do webhooks work in ActivePieces?"
        },
        {
            "name": "Complex Flow",
            "query": "Create a flow that monitors Twitter mentions, analyzes sentiment, and sends alerts to Slack if negative"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'─'*80}")
        print(f"TEST {i}: {test['name']}")
        print(f"{'─'*80}")
        print(f"Query: \"{test['query']}\"")
        print()
        
        try:
            # Get planner and analyze query
            planner = get_planner()
            plan = planner.analyze_query(test['query'])
            
            # Display results
            print(f"✅ SUCCESS - Plan Generated\n")
            print(f"Intent: {plan.get('intent', 'Unknown')}")
            print(f"Query Type: {plan.get('query_type', 'Unknown')}")
            print(f"\nAction Plan ({len(plan.get('action_plan', []))} steps):")
            for j, step in enumerate(plan.get('action_plan', []), 1):
                print(f"  {j}. {step}")
            print(f"\nRecommended Tools: {', '.join(plan.get('recommended_tools', []))}")
            print(f"Search Queries: {', '.join(plan.get('search_queries', []))}")
            print(f"\nContext: {plan.get('context', 'None')}")
            
        except Exception as e:
            print(f"❌ FAILED - Error: {str(e)}")
    
    print(f"\n{'='*80}")
    print("🏁 TESTING COMPLETE")
    print("="*80 + "\n")
    
    print("Next Steps:")
    print("1. Review the plans above to ensure they make sense")
    print("2. Run the server: python run.py")
    print("3. Test with real queries through the API")
    print("4. Monitor the console for planning output during agent execution")


def test_guided_input():
    """Test the guided input generation."""
    
    print("\n" + "="*80)
    print("🧪 TESTING GUIDED INPUT GENERATION")
    print("="*80 + "\n")
    
    test_query = "Is Slack available in ActivePieces?"
    print(f"Query: \"{test_query}\"\n")
    
    try:
        guided = create_guided_input(test_query)
        
        print("✅ SUCCESS - Guided Input Generated\n")
        print("Enhanced Input Preview:")
        print("─"*80)
        print(guided["enhanced_input"][:500] + "..." if len(guided["enhanced_input"]) > 500 else guided["enhanced_input"])
        print("─"*80)
        print(f"\nOriginal Query: {guided['original_query']}")
        print(f"Plan Type: {guided['plan'].get('query_type', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ FAILED - Error: {str(e)}")
    
    print()


if __name__ == "__main__":
    print("\n🚀 Starting GPT-5 Planning Layer Tests\n")
    
    # Check for API key
    import os
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please add it to your .env file")
        exit(1)
    
    # Run tests
    test_planner()
    test_guided_input()
    
    print("✨ All tests complete!\n")

