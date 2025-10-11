# Fix: Unsupported 'function' Role Error

## ✅ Issue Fixed!

I've updated the agent to use the **modern tool calling format** which is compatible with all OpenAI models.

## 🔧 What I Fixed

1. **Updated agent.py**: Changed from `create_openai_functions_agent` (old) to `create_tool_calling_agent` (new)
2. **This now supports**: GPT-4, GPT-4 Turbo, GPT-3.5 Turbo, and all future models

## ⚠️ Your Model Name is Invalid

Your `.env` file has:
```
MODEL_NAME=gpt-5-2025-08-07
```

**This model doesn't exist!** GPT-5 hasn't been released yet.

## 🔑 Fix Your .env File

Edit your `.env` file and change the model to one of these **valid models**:

### Recommended Models:

**Option 1: GPT-4 Turbo (Recommended - Fast & Powerful)**
```ini
MODEL_NAME=gpt-4-turbo-preview
```

**Option 2: GPT-4 (Most Capable)**
```ini
MODEL_NAME=gpt-4
```

**Option 3: GPT-3.5 Turbo (Fastest & Cheapest)**
```ini
MODEL_NAME=gpt-3.5-turbo
```

**Option 4: Latest GPT-4 Turbo**
```ini
MODEL_NAME=gpt-4-0125-preview
```

## 📝 Complete .env Example

Here's what your `.env` file should look like:

```ini
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-actual-api-key-here

# Model Configuration
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview

# Optional: Perplexity for web search
PERPLEXITY_API_KEY=your-perplexity-key-here
```

## 🚀 How to Fix

1. **Open your `.env` file** in the project root:
   ```bash
   nano .env
   # or
   code .env
   ```

2. **Change MODEL_NAME** to a valid model:
   ```ini
   MODEL_NAME=gpt-4-turbo-preview
   ```

3. **Save the file**

4. **Restart the backend**:
   ```bash
   # Stop the current backend (Ctrl+C)
   # Then restart:
   uvicorn main:app --reload
   ```

## 🧪 Test It

After restarting, try asking again:
- "Does ActivePieces have a Slack integration?"

You should now get a proper response! 🎉

## 💰 Model Costs (Per 1M Tokens)

- **GPT-4 Turbo**: $10 input / $30 output (Recommended)
- **GPT-4**: $30 input / $60 output
- **GPT-3.5 Turbo**: $0.50 input / $1.50 output (Cheapest)

## 📚 Valid Model Names (as of October 2024)

### GPT-4 Models:
- `gpt-4` - Original GPT-4
- `gpt-4-turbo-preview` - GPT-4 Turbo preview
- `gpt-4-0125-preview` - Latest GPT-4 Turbo
- `gpt-4-1106-preview` - November 2023 version

### GPT-3.5 Models:
- `gpt-3.5-turbo` - Latest GPT-3.5
- `gpt-3.5-turbo-0125` - January 2024 version

See the official OpenAI docs for the latest model list:
https://platform.openai.com/docs/models

## ✨ That's It!

After fixing your `.env` file and restarting, everything should work perfectly! 🚀

