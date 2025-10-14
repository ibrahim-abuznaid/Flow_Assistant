# OpenAI Search API Integration - Update Summary

## What Changed

The Flow Assistant now uses **OpenAI's Web Search API** as the default web search provider, replacing Perplexity as the primary option while keeping it available as an alternative.

## Key Changes

### 1. Default Search Provider
- **Before:** Perplexity API (required separate API key)
- **After:** OpenAI Search API (uses existing OpenAI key)

### 2. Configuration
- **New Environment Variable:** `SEARCH_PROVIDER` (default: `openai`)
- **Backward Compatible:** Perplexity still works when configured

### 3. Code Changes

#### Updated Files:
- ✅ `src/tools.py` - Added OpenAI search integration
- ✅ `env.example` - Added search provider configuration
- ✅ `README.md` - Updated documentation
- ✅ `docs/features/WEB_SEARCH_GUIDE.md` - Comprehensive guide

#### New Implementation:
```python
# Main web_search tool now routes based on SEARCH_PROVIDER
@tool
def web_search(query: str) -> str:
    search_provider = os.getenv("SEARCH_PROVIDER", "openai").lower()
    
    if search_provider == "openai":
        return _search_with_openai(query)
    elif search_provider == "perplexity":
        return _search_with_perplexity(query)
```

## Migration Guide

### For New Users

Simply set up your OpenAI API key:

```bash
# .env
OPENAI_API_KEY=your_openai_api_key_here
# SEARCH_PROVIDER=openai  # This is default, can be omitted
MODEL_NAME=gpt-4o
```

### For Existing Users (Currently Using Perplexity)

**Option 1: Switch to OpenAI (Recommended)**
```bash
# Update .env
SEARCH_PROVIDER=openai
# Keep your OPENAI_API_KEY
# Can remove PERPLEXITY_API_KEY if you're not using it
```

**Option 2: Keep Using Perplexity**
```bash
# Update .env
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_perplexity_key
```

## Benefits of OpenAI Search

1. **Simplified Setup**
   - No additional API key required
   - Uses existing OpenAI infrastructure
   
2. **Better Integration**
   - Native OpenAI tool
   - Seamless with chat completions
   - Consistent response format

3. **Cost Effective**
   - Included in chat completion pricing
   - No separate search API costs
   - Better token utilization

4. **Quality Results**
   - Uses latest GPT models for synthesis
   - Real-time web information
   - Accurate and concise answers

## How It Works

### OpenAI Search Flow
1. User asks a question requiring current information
2. Agent determines web search is needed
3. Calls `web_search` tool with query
4. Tool uses OpenAI's web_search capability
5. OpenAI searches web and synthesizes results
6. Returns concise answer to user

### Technical Implementation
```python
from openai import OpenAI

client = OpenAI(api_key=api_key)

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[...],
    tools=[{
        "type": "web_search",
        "web_search": {"search": {}}
    }]
)
```

## Configuration Reference

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | Your OpenAI API key |
| `SEARCH_PROVIDER` | No | `openai` | `openai` or `perplexity` |
| `PERPLEXITY_API_KEY` | No* | - | *Required only if using Perplexity |
| `MODEL_NAME` | No | `gpt-4o` | OpenAI model to use |

### Example Configurations

**Minimal Setup (OpenAI only):**
```bash
OPENAI_API_KEY=sk-...
```

**With Perplexity Option:**
```bash
OPENAI_API_KEY=sk-...
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-...
```

**Custom Model:**
```bash
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini  # or gpt-4-turbo
SEARCH_PROVIDER=openai
```

## Testing

### Test OpenAI Search
```bash
# Start the backend
uvicorn src.main:app --reload

# Ask questions requiring web search:
# - "What's the latest version of Python?"
# - "What are the current Discord API rate limits?"
# - "Find recent updates to the Slack API"
```

### Test Perplexity Search
```bash
# Update .env
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_key

# Restart backend
uvicorn src.main:app --reload

# Test same queries
```

## Troubleshooting

### Common Issues

**1. "Web search is not available (no OpenAI API key configured)"**
```bash
# Solution: Add OpenAI API key to .env
OPENAI_API_KEY=sk-...
```

**2. "Unknown search provider: xyz"**
```bash
# Solution: Use valid provider name
SEARCH_PROVIDER=openai  # or perplexity (lowercase)
```

**3. Search not working with OpenAI**
```bash
# Check model supports web search
MODEL_NAME=gpt-4o  # Recommended
# gpt-4-turbo also works
```

## Files Modified

### Core Implementation
- `src/tools.py` - Web search logic

### Configuration
- `env.example` - Environment template

### Documentation
- `README.md` - Main readme
- `docs/features/WEB_SEARCH_GUIDE.md` - Detailed guide
- `docs/features/OPENAI_SEARCH_UPDATE.md` - This file

## Next Steps

1. **Update your `.env` file** with the new configuration
2. **Restart the backend** to apply changes
3. **Test web search** functionality
4. **Review costs** and monitor usage
5. **Read the full guide** at `docs/features/WEB_SEARCH_GUIDE.md`

## References

- [OpenAI Web Search API](https://platform.openai.com/docs/guides/tools-web-search)
- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Web Search Guide](./WEB_SEARCH_GUIDE.md)

## Support

For questions or issues:
1. Check [Web Search Guide](./WEB_SEARCH_GUIDE.md)
2. Review [Troubleshooting](../troubleshooting/TROUBLESHOOTING.md)
3. See [README.md](../../README.md) for general setup

---

**Update Date:** October 2024
**Status:** ✅ Complete and Ready
**Backward Compatible:** Yes (Perplexity still supported)

