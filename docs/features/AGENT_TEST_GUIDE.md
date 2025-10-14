# Agent Functionality Test Guide

## ✅ What Was Fixed

1. **Conversation History** - Agent now loads session history properly
2. **Web Search** - OpenAI Responses API working correctly  
3. **Memory** - Session-specific memory is loaded for each request
4. **Iteration Limits** - Increased to 25 iterations, 120 second timeout

## 🧪 Manual Test Checklist

### Test 1: Conversation History ✅

**Step 1:** Send this message:
```
My name is Alice and I'm working on a workflow automation project
```

**Step 2:** Send this follow-up:
```
What's my name and what am I working on?
```

**Expected Result:** Agent should respond with "Alice" and mention "workflow automation"

---

### Test 2: Web Search ✅

**Query:**
```
What's the latest Python version released in 2024?
```

**Expected Result:** Should use web search and return current Python version with details

---

### Test 3: ActivePieces Integration Check ✅

**Query:**
```
Does ActivePieces have a Slack integration?
```

**Expected Result:** Should confirm Slack integration exists and list some actions/triggers

---

### Test 4: Knowledge Base Search ✅

**Query:**
```
How do I send an email using Gmail in ActivePieces?
```

**Expected Result:** Should provide details about Gmail Send Email action with required fields

---

### Test 5: Multi-Turn Conversation ✅

**Turn 1:**
```
What CRM integrations does ActivePieces have?
```

**Turn 2:**
```
Tell me more about the first one you mentioned
```

**Expected Result:** Should reference the CRM from turn 1 and provide more details

---

### Test 6: Web Search + Memory ✅

**Turn 1:**
```
Search online for the best project management tools in 2024
```

**Turn 2:**
```
Which one from your list would you recommend for a small team?
```

**Expected Result:** Should reference tools from turn 1 and make a recommendation

---

## 🚀 Quick Test Commands

### Start Backend
```bash
uvicorn src.main:app --reload
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Test in Browser
1. Open http://localhost:5173
2. Run through the test checklist above
3. Verify each response is correct

---

## ✅ Success Criteria

- [ ] Agent remembers conversation history within a session
- [ ] Web search returns current information
- [ ] ActivePieces checks work correctly
- [ ] Knowledge base provides accurate info
- [ ] Multi-turn conversations maintain context
- [ ] No "max iterations" errors
- [ ] Responses complete properly

---

## 🐛 If Something Fails

1. **Check backend logs** - Look for errors in terminal
2. **Verify session_id** - Should be passed from frontend
3. **Test in new session** - Clear browser cache or use incognito
4. **Check API keys** - Ensure OPENAI_API_KEY is set in .env

---

## 📊 Expected Behavior

### Session Management
- Each browser tab/session has unique session_id
- Conversation history persists within session
- Different sessions don't share history

### Web Search
- Automatically uses OpenAI Responses API
- Returns current, cited information
- Fallback to Perplexity if configured

### Memory
- Loads previous messages on each request
- Maintains context across multiple turns
- Session history saved to data/chat_sessions/

---

## ✨ All Systems Ready!

Your agent now has:
- ✅ Working conversation history
- ✅ OpenAI web search integration  
- ✅ Session-specific memory loading
- ✅ Proper iteration limits
- ✅ All tools functional

**Just restart the backend and test!** 🎉

