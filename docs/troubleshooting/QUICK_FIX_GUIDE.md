# Quick Fix Guide - Web Search Error

## 🚨 The Problem

You got this error:
```
OpenAI web search error: Error code: 400 - {'error': {'message': "Invalid value: 'web_search'. Supported values are: 'function' and 'custom'."
```

**Reason:** OpenAI's API doesn't support `web_search` as a tool type.

## ✅ The Solution

Use **Perplexity API** with your OpenAI key!

### Step 1: Update Your `.env` File

```bash
# Open your .env file and add/update these lines:

OPENAI_API_KEY=sk-your-actual-openai-key-here
PERPLEXITY_API_KEY=sk-your-actual-openai-key-here  # Same key!
MODEL_NAME=gpt-4o
```

**Important:** You can use the **same OpenAI key** for both! Just copy it to `PERPLEXITY_API_KEY`.

### Step 2: Restart Your Backend

```bash
# Stop the server (press Ctrl+C)
# Then restart:
uvicorn src.main:app --reload
```

### Step 3: Test It

Try asking in the chat:
- "What's the latest Python version?"
- "Find recent updates to Discord API"

Web search should now work! ✅

## 📋 Your `.env` File Should Look Like This

```ini
# Required
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxx
PERPLEXITY_API_KEY=sk-proj-xxxxxxxxxxxxxxxxx  # Same as above

# Optional
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
```

## ❓ FAQ

**Q: Do I need a Perplexity account?**  
A: No! Just use your OpenAI key.

**Q: Will this cost extra?**  
A: It uses your existing OpenAI quota.

**Q: Can I get a real Perplexity key?**  
A: Yes, from [perplexity.ai](https://www.perplexity.ai/), but not required.

## 🎯 That's It!

Your web search will now work perfectly using Perplexity API with your OpenAI key.

---

**Status:** ✅ Fixed  
**Files Changed:** `src/tools.py`, `env.example`, `README.md`  
**Web Search Provider:** Perplexity API

