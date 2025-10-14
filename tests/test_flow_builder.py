"""
Test suite for Flow Builder functionality.
"""
import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

def test_flow_builder_basic():
    """Test basic flow builder with a simple request."""
    from src.flow_builder import build_flow
    
    print("\n" + "="*60)
    print("TEST 1: Simple Flow - Email on Google Drive File")
    print("="*60)
    
    request = "Send an email when a new file is added to Google Drive"
    
    result = build_flow(request)
    
    print("\n✓ Flow Analysis:")
    print(f"  Goal: {result['analysis'].get('flow_goal', 'N/A')}")
    print(f"  Clarity: {result['analysis'].get('is_clear', False)}")
    print(f"  Complexity: {result['analysis'].get('complexity', 'N/A')}")
    print(f"  Confidence: {result['analysis'].get('confidence', 'N/A')}")
    
    print("\n✓ Clarifying Questions:")
    for i, q in enumerate(result.get('clarifying_questions', []), 1):
        print(f"  {i}. {q.get('question', 'N/A')}")
    
    print("\n✓ Guide Generated:")
    guide = result.get('guide', '')
    print(f"  Length: {len(guide)} characters")
    print(f"  Preview: {guide[:200]}...")
    
    # Assertions
    assert result is not None, "Result should not be None"
    assert 'guide' in result, "Result should contain 'guide'"
    assert 'analysis' in result, "Result should contain 'analysis'"
    assert len(guide) > 100, "Guide should be substantial"
    
    print("\n✅ TEST 1 PASSED")
    return True


def test_flow_builder_complex():
    """Test flow builder with a complex request."""
    from src.flow_builder import build_flow
    
    print("\n" + "="*60)
    print("TEST 2: Complex Flow - Customer Onboarding")
    print("="*60)
    
    request = "Automate my customer onboarding when they sign up through a form"
    
    result = build_flow(request)
    
    print("\n✓ Flow Analysis:")
    print(f"  Goal: {result['analysis'].get('flow_goal', 'N/A')}")
    print(f"  Clarity: {result['analysis'].get('is_clear', False)}")
    print(f"  Complexity: {result['analysis'].get('complexity', 'N/A')}")
    print(f"  Confidence: {result['analysis'].get('confidence', 'N/A')}")
    
    print("\n✓ Clarifying Questions:")
    for i, q in enumerate(result.get('clarifying_questions', []), 1):
        print(f"  {i}. {q.get('question', 'N/A')}")
        print(f"     Purpose: {q.get('purpose', 'N/A')}")
        print(f"     Optional: {q.get('optional', True)}")
    
    print("\n✓ Guide Generated:")
    guide = result.get('guide', '')
    print(f"  Length: {len(guide)} characters")
    
    # Check for key sections
    has_overview = "overview" in guide.lower()
    has_steps = "step" in guide.lower()
    has_config = "configure" in guide.lower() or "configuration" in guide.lower()
    
    print(f"\n  Has Overview: {has_overview}")
    print(f"  Has Steps: {has_steps}")
    print(f"  Has Configuration: {has_config}")
    
    # Assertions
    assert result is not None, "Result should not be None"
    assert 'guide' in result, "Result should contain 'guide'"
    assert len(guide) > 200, "Complex guide should be substantial"
    assert has_steps, "Guide should contain step-by-step instructions"
    
    print("\n✅ TEST 2 PASSED")
    return True


def test_flow_builder_with_specific_tools():
    """Test flow builder with specific tools mentioned."""
    from src.flow_builder import build_flow
    
    print("\n" + "="*60)
    print("TEST 3: Specific Tools - Slack & Google Sheets")
    print("="*60)
    
    request = "When a new row is added to Google Sheets, send a message to Slack with the row data"
    
    result = build_flow(request)
    
    print("\n✓ Flow Analysis:")
    print(f"  Goal: {result['analysis'].get('flow_goal', 'N/A')}")
    print(f"  Trigger: {result['analysis'].get('trigger_type', 'N/A')}")
    print(f"  Actions: {result['analysis'].get('actions_needed', [])}")
    
    print("\n✓ Found Components:")
    components = result.get('components', {})
    if components.get('trigger'):
        print(f"  Trigger Piece: {components['trigger'].get('piece', {}).get('displayName', 'N/A')}")
    
    if components.get('actions'):
        print(f"  Action Pieces:")
        for action_info in components['actions']:
            print(f"    - {action_info.get('piece', {}).get('displayName', 'N/A')}")
    
    print("\n✓ Guide Generated:")
    guide = result.get('guide', '')
    print(f"  Length: {len(guide)} characters")
    
    # Check for specific tools mentioned
    has_sheets = "sheets" in guide.lower() or "google sheets" in guide.lower()
    has_slack = "slack" in guide.lower()
    
    print(f"\n  Mentions Google Sheets: {has_sheets}")
    print(f"  Mentions Slack: {has_slack}")
    
    # Assertions
    assert result is not None, "Result should not be None"
    assert has_sheets or has_slack, "Guide should mention the requested tools"
    
    print("\n✅ TEST 3 PASSED")
    return True


def test_flow_analysis():
    """Test just the flow analysis component."""
    from src.flow_builder import get_flow_builder
    
    print("\n" + "="*60)
    print("TEST 4: Flow Analysis Only")
    print("="*60)
    
    builder = get_flow_builder()
    
    test_requests = [
        "Send email when file uploaded to Google Drive",
        "Automate my business processes",
        "Create a Trello card when I receive a webhook",
    ]
    
    for i, request in enumerate(test_requests, 1):
        print(f"\n  Request {i}: {request}")
        analysis = builder.analyze_flow_request(request)
        
        print(f"    Clarity: {'Clear' if analysis.get('is_clear') else 'Needs clarification'}")
        print(f"    Complexity: {analysis.get('complexity', 'N/A')}")
        print(f"    Questions: {len(analysis.get('clarifying_questions', []))}")
        
        assert analysis is not None, f"Analysis {i} should not be None"
        assert 'flow_goal' in analysis, f"Analysis {i} should contain 'flow_goal'"
    
    print("\n✅ TEST 4 PASSED")
    return True


def test_component_search():
    """Test component search functionality."""
    from src.flow_builder import get_flow_builder
    
    print("\n" + "="*60)
    print("TEST 5: Component Search")
    print("="*60)
    
    builder = get_flow_builder()
    
    # Create a mock analysis
    analysis = {
        "flow_goal": "Send email on new Google Drive file",
        "trigger_type": "Google Drive - New File",
        "actions_needed": ["Send Email"],
        "is_clear": True,
        "complexity": "simple"
    }
    
    print("\n  Searching for components...")
    components = builder.search_flow_components(analysis)
    
    print(f"\n✓ Search Results:")
    print(f"  Trigger Found: {components.get('trigger') is not None}")
    print(f"  Actions Found: {len(components.get('actions', []))}")
    print(f"  Missing: {components.get('missing', [])}")
    print(f"  Knowledge Context: {len(components.get('knowledge_context', []))} items")
    
    if components.get('trigger'):
        trigger = components['trigger'].get('piece', {})
        print(f"\n  Trigger Details:")
        print(f"    Name: {trigger.get('displayName', 'N/A')}")
        print(f"    Description: {trigger.get('description', 'N/A')[:80]}...")
    
    # Assertions
    assert components is not None, "Components should not be None"
    
    print("\n✅ TEST 5 PASSED")
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("FLOW BUILDER TEST SUITE")
    print("="*60)
    
    # Check if API key is configured
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("\n❌ ERROR: OPENAI_API_KEY not configured in .env file")
        print("Please set your OpenAI API key to run these tests.")
        return False
    
    tests = [
        ("Basic Flow Builder", test_flow_builder_basic),
        ("Complex Flow Builder", test_flow_builder_complex),
        ("Specific Tools", test_flow_builder_with_specific_tools),
        ("Flow Analysis", test_flow_analysis),
        ("Component Search", test_component_search),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}...")
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

