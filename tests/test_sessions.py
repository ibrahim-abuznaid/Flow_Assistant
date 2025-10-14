"""
Test script for session-based memory management.
"""
from memory import (
    create_session, 
    load_session, 
    log_interaction, 
    get_all_sessions,
    clear_session
)

def test_sessions():
    """Test session creation, storage, and retrieval."""
    print("🧪 Testing Session Management\n")
    print("="*60)
    
    # Test 1: Create a new session
    print("\n1. Creating new session...")
    session_id = "test_session_001"
    session_data = create_session(session_id)
    print(f"✓ Created session: {session_id}")
    print(f"  Created at: {session_data['created_at']}")
    
    # Test 2: Log interactions
    print("\n2. Logging interactions...")
    log_interaction(
        "Hello, what is ActivePieces?",
        "ActivePieces is a workflow automation platform...",
        session_id=session_id
    )
    print("✓ Logged first interaction")
    
    log_interaction(
        "Can you help me with Gmail integration?",
        "Sure! ActivePieces has a Gmail piece with multiple actions...",
        session_id=session_id
    )
    print("✓ Logged second interaction")
    
    # Test 3: Load session
    print("\n3. Loading session...")
    loaded_session = load_session(session_id)
    if loaded_session:
        print(f"✓ Loaded session with {len(loaded_session['messages'])} messages")
        for i, msg in enumerate(loaded_session['messages'], 1):
            print(f"  Message {i} ({msg['role']}): {msg['message'][:50]}...")
    
    # Test 4: Get all sessions
    print("\n4. Retrieving all sessions...")
    all_sessions = get_all_sessions()
    print(f"✓ Found {len(all_sessions)} session(s)")
    for session in all_sessions:
        print(f"  - {session['session_id']}: {session['message_count']} messages")
        print(f"    Preview: {session['preview'][:50]}...")
    
    # Test 5: Clean up
    print("\n5. Cleaning up test session...")
    clear_session(session_id)
    print(f"✓ Deleted session: {session_id}")
    
    print("\n" + "="*60)
    print("✅ All tests passed!")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_sessions()




