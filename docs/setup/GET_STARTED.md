# 🚀 Get Started in 5 Minutes

The fastest way to get your ActivePieces AI Assistant up and running!

## ⚡ Quick Start

### 1️⃣ Prerequisites Check

Make sure you have:
- ✅ Python 3.9+ installed
- ✅ Node.js 16+ and npm installed
- ✅ OpenAI API key ready

### 2️⃣ Run Setup (1 command)

```bash
python setup.py
```

### 3️⃣ Add Your API Key

Open `.env` file and add your OpenAI API key:

```ini
OPENAI_API_KEY=sk-your-key-here
```

### 4️⃣ Prepare Knowledge Base

```bash
python prepare_knowledge_base.py
```

⏱️ This takes 2-3 minutes and costs ~$0.10-0.50 in OpenAI API calls.

### 5️⃣ Launch!

```bash
python run.py
```

Choose option **3** (Both servers)

### 6️⃣ Open Browser

Go to: **http://localhost:5173**

🎉 **You're ready!** Start chatting with your AI assistant!

---

## 💬 Try These Questions

Once your assistant is running, try asking:

1. **"Does ActivePieces have a Slack integration?"**
   - Tests the JSON lookup tool

2. **"How can I send an email using ActivePieces?"**
   - Tests the semantic search

3. **"What actions are available for Google Sheets?"**
   - Tests knowledge base retrieval

4. **"Show me all triggers for Gmail"**
   - Tests filtering and search

5. **"How do I filter data in a workflow?"**
   - Tests conceptual understanding

---

## 🎯 What You Get

### Backend (FastAPI)
- 🔌 RESTful API on port 8000
- 🤖 AI agent with 3 tools
- 💾 Persistent chat memory
- 📊 Knowledge base with 409 pieces

### Frontend (React)
- 💬 Beautiful chat interface
- 📱 Responsive design
- ⚡ Real-time updates
- 🎨 Modern gradient UI

### Knowledge Base
- **409 Pieces** (integrations)
- **1,529 Actions** (operations)
- **453 Triggers** (events)

---

## 🔧 Common Issues & Quick Fixes

### "Python not found"
```bash
# Try these alternatives:
python3 setup.py
py setup.py
```

### "OpenAI API key not found"
- Make sure `.env` file exists
- Check that key starts with `sk-`
- No extra spaces or quotes

### "Vector store not found"
```bash
python prepare_knowledge_base.py
```

### "Port already in use"
- Backend uses port 8000
- Frontend uses port 5173
- Close other services or change ports

---

## 📚 Documentation

Need more details? Check these guides:

- **[README.md](README.md)** - Overview and features
- **[INSTALLATION.md](INSTALLATION.md)** - Detailed installation
- **[QUICKSTART.md](QUICKSTART.md)** - Usage and examples
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Architecture

---

## 🧪 Test Your Setup

Run the test suite to verify everything works:

```bash
python test_assistant.py
```

This checks:
- ✅ Environment variables
- ✅ Knowledge base
- ✅ Vector store
- ✅ Tools
- ✅ LLM connection
- ✅ Agent functionality

---

## 🎓 Understanding the System

### How It Works

```
User Question
    ↓
Frontend (React)
    ↓
Backend API (FastAPI)
    ↓
AI Agent (LangChain)
    ↓
Decides which tool to use:
    ├─ Check Tool (JSON lookup)
    ├─ Search Tool (Vector DB)
    └─ Web Search (Perplexity)
    ↓
LLM synthesizes answer
    ↓
Response to user
```

### The 3 Tools

1. **check_activepieces**
   - Fast JSON lookup
   - "Does X exist?"
   - Exact matching

2. **search_activepieces_docs**
   - Semantic search
   - "How do I...?"
   - Conceptual queries

3. **web_search**
   - External info
   - General questions
   - Real-time data

---

## 🎨 Customization

### Change the LLM Model

Edit `.env`:

```ini
# Use GPT-3.5 (faster, cheaper)
MODEL_NAME=gpt-3.5-turbo

# Use Claude
MODEL_PROVIDER=anthropic
MODEL_NAME=claude-3-opus-20240229
ANTHROPIC_API_KEY=your-key
```

### Customize System Prompt

Edit `agent.py` and modify the `SYSTEM_PROMPT` variable.

### Change UI Colors

Edit `frontend/src/App.css` and modify the gradient colors.

---

## 📊 Usage Stats

After using the assistant, check stats:

```bash
curl http://localhost:8000/stats
```

Response:
```json
{
  "total_pieces": 409,
  "total_actions": 1529,
  "total_triggers": 453
}
```

---

## 🔄 Reset Conversation

Clear chat history:

1. **Via UI**: Click the "🗑️ Clear" button
2. **Via API**: 
   ```bash
   curl -X POST http://localhost:8000/reset
   ```
3. **Manually**: Delete `chat_history.json`

---

## 🚀 Next Steps

Now that you're up and running:

1. **Explore the codebase**
   - Check out `tools.py` for tool implementations
   - Look at `agent.py` for agent configuration
   - Review `main.py` for API endpoints

2. **Customize it**
   - Add your own tools
   - Modify the system prompt
   - Enhance the UI

3. **Deploy it**
   - Set up on a server
   - Add authentication
   - Use production settings

---

## 💡 Pro Tips

1. **Save API costs**: Use `gpt-3.5-turbo` for development
2. **Faster responses**: Keep vector store in memory
3. **Better answers**: Customize the system prompt
4. **Debug mode**: Check terminal output for agent reasoning
5. **Test first**: Run `test_assistant.py` after changes

---

## 🆘 Need Help?

1. **Check error messages** in terminal
2. **Run tests**: `python test_assistant.py`
3. **Review logs** for detailed info
4. **Check documentation** in this repo

---

## 🎉 Success!

If you see the chat interface and can ask questions, you're all set!

**Enjoy your AI assistant! 🤖**

---

## 📝 Quick Reference

### Start Everything
```bash
python run.py  # Choose option 3
```

### Start Backend Only
```bash
uvicorn main:app --reload
```

### Start Frontend Only
```bash
cd frontend && npm run dev
```

### Run Tests
```bash
python test_assistant.py
```

### Prepare Knowledge Base
```bash
python prepare_knowledge_base.py
```

### Check Health
```bash
curl http://localhost:8000/health
```

---

**That's it! You're ready to automate with AI! 🚀**

