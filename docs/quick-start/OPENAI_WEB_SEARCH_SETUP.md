# OpenAI Web Search Setup - Complete Guide

## ✅ Fixed Implementation

The web search now correctly uses **OpenAI's Responses API** with the `web_search` tool!

## 🚀 Quick Setup

### Step 1: Update Your `.env` File

```bash
# Just add your OpenAI API key
OPENAI_API_KEY=sk-your-actual-key-here
MODEL_NAME=gpt-4o

# Optional: Explicitly set OpenAI as search provider (it's default)
SEARCH_PROVIDER=openai
```

That's it! No Perplexity key needed.

### Step 2: Restart Your Backend

```bash
# Stop the server (Ctrl+C in terminal)
# Then restart:
uvicorn src.main:app --reload
```

### Step 3: Test Web Search

Ask questions like:
- "What's the latest Python version?"
- "Find recent Discord API updates"
- "What are current GitHub rate limits?"

## 🔧 How It Works

The implementation uses OpenAI's **Responses API** (not Chat Completions):

```python
from openai import OpenAI

client = OpenAI(api_key=api_key)

response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search"}],
    input=query
)

answer = response.output_text
```

## 📋 Configuration Options

### Option 1: OpenAI Search (Default - Recommended)

```bash
# .env file
OPENAI_API_KEY=sk-your-key
SEARCH_PROVIDER=openai  # or omit (openai is default)
```

**Benefits:**
- ✅ Uses OpenAI Responses API
- ✅ No extra API key needed
- ✅ Real-time web search built-in
- ✅ Proper citations and sources

### Option 2: Perplexity Search (Alternative)

```bash
# .env file
OPENAI_API_KEY=sk-your-key
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your-perplexity-key
```

**Benefits:**
- ✅ Dedicated search models
- ✅ Fast specialized search
- ✅ Easy fallback option

## 🔄 Switching Between Providers

### Use OpenAI (Default)
```bash
SEARCH_PROVIDER=openai
# or just remove the line
```

### Use Perplexity
```bash
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-your-key
```

**No code changes needed!** Just update `.env` and restart.

## 📝 Complete `.env` Example

```ini
# ============================================================================
# LLM Configuration
# ============================================================================
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# ============================================================================
# Web Search Configuration
# ============================================================================
SEARCH_PROVIDER=openai  # openai or perplexity

# Only needed if SEARCH_PROVIDER=perplexity
# PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxx
```

## 🧪 Testing

### Test OpenAI Web Search

```bash
# Make sure .env has:
# OPENAI_API_KEY=sk-...
# SEARCH_PROVIDER=openai (or omit)

# Start backend
uvicorn src.main:app --reload

# Ask in the UI:
# "What's the latest version of Node.js?"
```

Expected: Web search works with current info! ✅

### Test Perplexity (Optional)

```bash
# Update .env:
# SEARCH_PROVIDER=perplexity
# PERPLEXITY_API_KEY=pplx-...

# Restart backend
uvicorn src.main:app --reload
```

## ⚠️ Important Notes

### OpenAI Responses API Availability

The Responses API with `web_search` is available for:
- ✅ `gpt-4o` models
- ✅ `gpt-5` models  
- ✅ `o4-mini` models
- ✅ Most OpenAI accounts

If you get a "404" or "responses not found" error:
1. The Responses API might not be available yet for your account
2. Switch to Perplexity temporarily: `SEARCH_PROVIDER=perplexity`
3. Check OpenAI's API status

### Model Compatibility

**Recommended Models for Web Search:**
- `gpt-4o` - Best balance (default)
- `gpt-5` - Most advanced
- `o4-mini` - Fast and efficient

## 🐛 Troubleshooting

### Error: "Web search is not available"

**Solution:**
```bash
# Add OpenAI API key to .env
OPENAI_API_KEY=sk-your-key-here
```

### Error: "OpenAI Responses API error: 404"

**Solution:** Responses API not available yet
```bash
# Switch to Perplexity temporarily
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-your-key
```

### Error: "Unknown search provider"

**Solution:**
```bash
# Use valid provider name (lowercase)
SEARCH_PROVIDER=openai  # or perplexity
```

### Web Search Returns Old Information

**Solution:**
```bash
# Use newer model
MODEL_NAME=gpt-4o  # or gpt-5
```

## 📊 Comparison

| Feature | OpenAI Search | Perplexity |
|---------|--------------|------------|
| **API Used** | Responses API | Chat Completions |
| **Extra Key** | ❌ No | ✅ Yes |
| **Setup** | Very Easy | Easy |
| **Citations** | ✅ Yes | ❌ No |
| **Speed** | Fast | Very Fast |
| **Quality** | Excellent | Excellent |
| **Cost** | Included | Separate |

## ✨ What's New

### Before (Broken)
```python
# ❌ Tried to use non-existent tool in Chat Completions
tools=[{"type": "web_search"}]  # Invalid
```

### After (Working)
```python
# ✅ Uses correct Responses API
response = client.responses.create(
    model="gpt-4o",
    tools=[{"type": "web_search"}],
    input=query
)
```

## 📚 Files Updated

- ✅ `src/tools.py` - Correct OpenAI Responses API implementation
- ✅ `env.example` - Updated configuration template
- ✅ `README.md` - Corrected documentation
- ✅ `OPENAI_WEB_SEARCH_SETUP.md` - This guide

## 🎯 Summary

1. **Add your OpenAI API key** to `.env`
2. **Set `SEARCH_PROVIDER=openai`** (or omit - it's default)
3. **Restart backend**
4. **Test web search** - it should work!

That's it! Your OpenAI web search is now working correctly. 🎉

## 📞 Support

- **OpenAI Responses API Docs**: https://platform.openai.com/docs/api-reference/responses
- **Web Search Guide**: https://platform.openai.com/docs/guides/tools-web-search
- **Perplexity Fallback**: Set `SEARCH_PROVIDER=perplexity` if needed

---

**Status:** ✅ Working with OpenAI Responses API  
**Default Provider:** OpenAI (uses your OpenAI key)  
**Fallback:** Perplexity (optional alternative)  
**Date:** October 2024

