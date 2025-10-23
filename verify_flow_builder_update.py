"""
Quick verification script to ensure Flow Builder is updated for new database.
Run this to verify all components are working correctly.
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_database_stats():
    """Test that database has correct statistics."""
    print("\n" + "="*60)
    print("TEST 1: Database Statistics")
    print("="*60)
    
    try:
        import sqlite3
        conn = sqlite3.connect('data/activepieces.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM pieces')
        pieces = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM actions')
        actions = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM triggers')
        triggers = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"[OK] Database found at data/activepieces.db")
        print(f"[OK] Pieces: {pieces}")
        print(f"[OK] Actions: {actions}")
        print(f"[OK] Triggers: {triggers}")
        
        expected = (450, 2890, 834)
        actual = (pieces, actions, triggers)
        
        if actual == expected:
            print(f"[PASS] Database stats match expected values!")
            return True
        else:
            print(f"[WARN] Stats don't match expected (450, 2890, 834)")
            print(f"       Got: {actual}")
            return False
            
    except Exception as e:
        print(f"[FAIL] Database test failed: {e}")
        return False


def test_tools_integration():
    """Test that tools work with new database."""
    print("\n" + "="*60)
    print("TEST 2: Tools Integration")
    print("="*60)
    
    try:
        from tools import find_piece_by_name, find_action_by_name, find_trigger_by_name
        
        # Test piece lookup
        piece = find_piece_by_name("Gmail")
        if piece:
            print(f"[OK] find_piece_by_name('Gmail') works")
            print(f"     Found: {piece.get('displayName')}")
        else:
            print(f"[WARN] find_piece_by_name('Gmail') returned None")
            return False
        
        # Test action search
        actions = find_action_by_name("send email", limit=5)
        if actions and len(actions) > 0:
            print(f"[OK] find_action_by_name('send email') works")
            print(f"     Found {len(actions)} actions")
        else:
            print(f"[WARN] find_action_by_name returned no results")
            return False
        
        # Test trigger search
        triggers = find_trigger_by_name("new message", limit=5)
        if triggers and len(triggers) > 0:
            print(f"[OK] find_trigger_by_name('new message') works")
            print(f"     Found {len(triggers)} triggers")
        else:
            print(f"[WARN] find_trigger_by_name returned no results")
            return False
        
        print(f"[PASS] All tools working correctly!")
        return True
        
    except Exception as e:
        print(f"[FAIL] Tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_flow_builder_prompts():
    """Test that flow builder has updated prompts."""
    print("\n" + "="*60)
    print("TEST 3: Flow Builder Prompts")
    print("="*60)
    
    try:
        with open('src/flow_builder.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for updated statistics
        checks = [
            ("450 pieces", "450 pieces mentioned"),
            ("2,890 actions", "2,890 actions mentioned"),
            ("834 triggers", "834 triggers mentioned"),
            ("SQLite database with FTS5", "FTS5 full-text search mentioned"),
            ("Complete property metadata", "Property metadata mentioned"),
        ]
        
        all_passed = True
        for check_str, desc in checks:
            if check_str in content:
                print(f"[OK] {desc}")
            else:
                print(f"[WARN] Missing: {desc}")
                all_passed = False
        
        if all_passed:
            print(f"[PASS] All flow builder prompts updated!")
            return True
        else:
            print(f"[WARN] Some prompts may need updating")
            return False
            
    except Exception as e:
        print(f"[FAIL] Prompt check failed: {e}")
        return False


def test_agent_prompt():
    """Test that agent has updated prompt."""
    print("\n" + "="*60)
    print("TEST 4: Agent System Prompt")
    print("="*60)
    
    try:
        with open('src/agent.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = [
            ("450 pieces", "450 pieces in agent prompt"),
            ("2,890 actions", "2,890 actions in agent prompt"),
            ("834 triggers", "834 triggers in agent prompt"),
        ]
        
        all_passed = True
        for check_str, desc in checks:
            if check_str in content:
                print(f"[OK] {desc}")
            else:
                print(f"[WARN] Missing: {desc}")
                all_passed = False
        
        if all_passed:
            print(f"[PASS] Agent prompt updated!")
            return True
        else:
            print(f"[WARN] Agent prompt may need updating")
            return False
            
    except Exception as e:
        print(f"[FAIL] Agent prompt check failed: {e}")
        return False


def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("FLOW BUILDER DATABASE UPDATE VERIFICATION")
    print("="*60)
    
    results = []
    
    # Run tests
    results.append(("Database Stats", test_database_stats()))
    results.append(("Tools Integration", test_tools_integration()))
    results.append(("Flow Builder Prompts", test_flow_builder_prompts()))
    results.append(("Agent Prompt", test_agent_prompt()))
    
    # Summary
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print("\n" + "="*60)
    if passed == total:
        print(f"[SUCCESS] ALL TESTS PASSED ({passed}/{total})")
        print("="*60)
        print("\nFlow Builder is fully updated and ready to use!")
        return 0
    else:
        print(f"[WARNING] SOME TESTS FAILED ({passed}/{total})")
        print("="*60)
        print("\nPlease review the failed tests above.")
        return 1


if __name__ == "__main__":
    exit(main())
