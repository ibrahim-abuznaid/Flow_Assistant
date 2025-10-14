# Web Search Integration Guide

## Overview

The Flow Assistant now supports two web search providers:
1. **OpenAI Search API** (Default) - Built-in web search using OpenAI's native capabilities
2. **Perplexity API** (Optional) - Alternative search provider with dedicated search models

## Configuration

### Default Setup (OpenAI Search)

By default, the assistant uses OpenAI's web search API. You only need your OpenAI API key:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
SEARCH_PROVIDER=openai  # This is the default, can be omitted
MODEL_NAME=gpt-4o       # Recommended for best search results
```

**Advantages:**
- ✅ No additional API key needed
- ✅ Built into OpenAI's chat completions
- ✅ Seamless integration with the main LLM
- ✅ Cost-effective (included in chat completion pricing)

### Alternative Setup (Perplexity Search)

To use Perplexity for web search instead:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here  # Still needed for LLM and embeddings
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

**Advantages:**
- ✅ Specialized search models (Sonar)
- ✅ Purpose-built for web search tasks
- ✅ Fast response times

## How It Works

### OpenAI Search Implementation

When using OpenAI search, the `web_search` tool:

1. Creates a chat completion request with the `web_search` tool enabled
2. OpenAI automatically searches the web and synthesizes results
3. Returns a concise, accurate answer based on current information

```python
# Simplified code example
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": query}],
    tools=[{
        "type": "web_search",
        "web_search": {"search": {}}
    }]
)
```

### Perplexity Search Implementation

When using Perplexity search, the `web_search` tool:

1. Sends a request to Perplexity's API
2. Uses the Sonar model optimized for online search
3. Returns real-time web information

```python
# Simplified code example
response = requests.post(
    "https://api.perplexity.ai/chat/completions",
    json={
        "model": "llama-3.1-sonar-small-128k-online",
        "messages": [{"role": "user", "content": query}]
    }
)
```

## When Web Search Is Used

The AI agent automatically decides when to use web search based on:

1. **Real-time Information Needs**
   - Current events, news, updates
   - Latest documentation or API changes
   - Version information

2. **Knowledge Gap Detection**
   - Information not in ActivePieces knowledge base
   - Questions outside the agent's training data
   - Verification of current facts

3. **Explicit Search Requests**
   - "Search for..."
   - "What's the latest..."
   - "Find current information about..."

## Usage Examples

### Example 1: Finding Current Information

**User Query:** "What's the latest version of the Slack API?"

**Agent Behavior:**
1. Checks ActivePieces knowledge base
2. If outdated, uses `web_search` tool
3. Returns current version information

### Example 2: Real-time Data

**User Query:** "How many integrations does ActivePieces currently support?"

**Agent Behavior:**
1. Checks local database (433 pieces)
2. May use web search to verify current count
3. Returns up-to-date information

### Example 3: External Service Information

**User Query:** "What are the current API rate limits for Discord?"

**Agent Behavior:**
1. Recognizes need for current information
2. Uses web search to find latest Discord documentation
3. Provides accurate, current limits

## Switching Between Providers

### Switch to OpenAI (Default)

```bash
# Update .env
SEARCH_PROVIDER=openai
# or simply remove the SEARCH_PROVIDER line
```

### Switch to Perplexity

```bash
# Update .env
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=your_key_here
```

**No code changes required** - just update your `.env` file and restart the backend:

```bash
# Stop the server (Ctrl+C)
# Restart
uvicorn src.main:app --reload
```

## API Reference

### OpenAI Search Tool Configuration

```python
tools = [{
    "type": "web_search",
    "web_search": {
        "search": {}  # Uses default search parameters
    }
}]
```

### Perplexity Search Models

Available models:
- `llama-3.1-sonar-small-128k-online` (default) - Fast, cost-effective
- `llama-3.1-sonar-large-128k-online` - More comprehensive results
- `llama-3.1-sonar-huge-128k-online` - Highest quality

To change the Perplexity model, edit `src/tools.py`:

```python
payload = {
    "model": "llama-3.1-sonar-large-128k-online",  # Change here
    ...
}
```

## Cost Considerations

### OpenAI Search Costs

- Included in chat completion pricing
- No separate search API costs
- Uses tokens from your chat completion quota

### Perplexity Search Costs

- Separate API with its own pricing
- Per-request pricing model
- Check [Perplexity Pricing](https://docs.perplexity.ai/docs/pricing) for details

## Troubleshooting

### OpenAI Search Not Working

**Error:** "Web search is not available (no OpenAI API key configured)."

**Solution:**
```bash
# Verify .env file
OPENAI_API_KEY=sk-...  # Should start with sk-
```

### Perplexity Search Not Working

**Error:** "Perplexity search is not available (no API key configured)."

**Solution:**
```bash
# Verify .env file
SEARCH_PROVIDER=perplexity
PERPLEXITY_API_KEY=pplx-...  # Your Perplexity key
```

### Invalid Provider Error

**Error:** "Unknown search provider: xyz"

**Solution:**
```bash
# Use valid provider name
SEARCH_PROVIDER=openai  # or perplexity (lowercase)
```

## Best Practices

1. **Use OpenAI Search for most cases**
   - Simpler setup
   - No extra API key needed
   - Good quality results

2. **Use Perplexity when:**
   - You need specialized search capabilities
   - You want to separate search costs
   - You prefer dedicated search models

3. **Monitor Usage**
   - Track API costs
   - Review search quality
   - Adjust based on needs

## Technical Details

### Code Location

The web search implementation is in `src/tools.py`:

- `web_search()` - Main tool function
- `_search_with_openai()` - OpenAI search implementation
- `_search_with_perplexity()` - Perplexity search implementation

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SEARCH_PROVIDER` | No | `openai` | Search provider to use |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `PERPLEXITY_API_KEY` | Conditional | - | Required only if using Perplexity |
| `MODEL_NAME` | No | `gpt-4o` | OpenAI model for search |

### Response Format

Both providers return plain text responses that are:
- Concise (max 500 tokens)
- Factual and accurate
- Based on current web information

## Migration Guide

### From Perplexity to OpenAI

1. Update `.env`:
   ```bash
   SEARCH_PROVIDER=openai
   # Comment out or remove PERPLEXITY_API_KEY
   ```

2. Restart backend:
   ```bash
   uvicorn src.main:app --reload
   ```

3. Test web search functionality

### From OpenAI to Perplexity

1. Get Perplexity API key from [Perplexity](https://www.perplexity.ai/)

2. Update `.env`:
   ```bash
   SEARCH_PROVIDER=perplexity
   PERPLEXITY_API_KEY=your_key_here
   ```

3. Restart backend and test

## Support

For issues or questions:
1. Check this guide
2. Review [Troubleshooting](../troubleshooting/TROUBLESHOOTING.md)
3. Check API provider documentation:
   - [OpenAI Tools Documentation](https://platform.openai.com/docs/guides/tools-web-search)
   - [Perplexity API Docs](https://docs.perplexity.ai/)

## Updates

This feature was added on 2024 with the following changes:
- Default switched from Perplexity to OpenAI Search API
- Added provider selection via environment variable
- Maintained backward compatibility with Perplexity
- Updated documentation and configuration files

