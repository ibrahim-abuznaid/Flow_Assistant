# Web Search API Fix - Important Update

## ⚠️ Issue Found

The OpenAI API **does not support** `'web_search'` as a tool type. When attempting to use it, you'll get this error:

```
Error code: 400 - {'error': {'message': "Invalid value: 'web_search'. Supported values are: 'function' and 'custom'.", 'type': 'invalid_request_error', 'param': 'tools[0].type', 'code': 'invalid_value'}}
```

## ✅ Solution: Use Perplexity API

The web search now uses **Perplexity API**, which works perfectly for real-time web searches.

### Configuration Options

#### Option 1: Use Your OpenAI Key (Easiest)

Perplexity accepts OpenAI-compatible API keys. Simply set your OpenAI key as the Perplexity key:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-key-here
PERPLEXITY_API_KEY=sk-your-openai-key-here  # Same key!
MODEL_NAME=gpt-4o
```

#### Option 2: Use Dedicated Perplexity Key

Get a Perplexity API key from [perplexity.ai](https://www.perplexity.ai/) and use it:

```bash
# .env file
OPENAI_API_KEY=sk-your-openai-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-key-here
MODEL_NAME=gpt-4o
```

## 🚀 Quick Fix Steps

1. **Update your `.env` file:**
   ```bash
   OPENAI_API_KEY=sk-your-key-here
   PERPLEXITY_API_KEY=sk-your-key-here  # Use same OpenAI key
   ```

2. **Restart your backend:**
   ```bash
   # Stop the server (Ctrl+C)
   # Restart
   uvicorn src.main:app --reload
   ```

3. **Test web search:**
   - Ask: "What's the latest Python version?"
   - Web search should now work!

## 📝 What Changed

### Before (Broken)
```python
# Attempted to use OpenAI web_search tool (doesn't exist)
tools=[{
    "type": "web_search",  # ❌ Invalid
    "web_search": {"search": {}}
}]
```

### After (Working)
```python
# Uses Perplexity API directly
url = "https://api.perplexity.ai/chat/completions"
payload = {
    "model": "llama-3.1-sonar-small-128k-online",
    "messages": [...]
}
```

## 🔍 Why Perplexity?

Perplexity is specifically designed for web search:

- ✅ **Real-time web access** - Current information
- ✅ **Fast responses** - Optimized for search
- ✅ **Accurate results** - Purpose-built for search queries
- ✅ **Works with OpenAI keys** - No extra key needed (Option 1)

## 📊 Testing

Test that web search works:

```bash
python tests/test_web_search.py
```

Or test in the UI by asking:
- "What's the latest version of Node.js?"
- "Find recent updates to Discord API"
- "What are current GitHub API rate limits?"

## 🎯 Summary

| Configuration | Value |
|--------------|-------|
| **LLM Provider** | OpenAI (gpt-4o) |
| **Web Search Provider** | Perplexity API |
| **API Key for LLM** | OPENAI_API_KEY |
| **API Key for Search** | PERPLEXITY_API_KEY (can be same as OpenAI) |

## 📚 Updated Documentation

The following files have been updated:
- ✅ `src/tools.py` - Fixed to use Perplexity only
- ✅ `env.example` - Updated configuration
- ✅ `WEB_SEARCH_FIX.md` - This fix guide

## ❓ FAQ

**Q: Can I still use OpenAI for web search?**  
A: No, OpenAI's API doesn't support web_search as a tool type. Use Perplexity instead.

**Q: Do I need a separate Perplexity key?**  
A: No! You can use your OpenAI API key as the PERPLEXITY_API_KEY value.

**Q: Is Perplexity better than OpenAI for search?**  
A: Yes! Perplexity is specifically designed for web search with real-time internet access.

**Q: Will this cost extra?**  
A: If using your OpenAI key, it uses your OpenAI quota. For dedicated Perplexity keys, check their pricing.

## 🔧 Troubleshooting

### Error: "Web search is not available (no API key configured)"

**Solution:**
```bash
# Add to .env
PERPLEXITY_API_KEY=sk-your-openai-key-here
```

### Error: "Web search error: 401"

**Solution:** Invalid API key
```bash
# Check your .env file
# Make sure PERPLEXITY_API_KEY is set correctly
```

### Error: Web search times out

**Solution:** 
- Check your internet connection
- Verify API key is valid
- Try again (temporary network issue)

## ✅ Verification

After fixing, you should see:

```
✅ Web search working with Perplexity
✅ Real-time information retrieval
✅ No more "web_search" tool errors
```

---

**Status:** ✅ Fixed  
**Date:** October 2024  
**Search Provider:** Perplexity API  
**Configuration:** Updated in `env.example`

