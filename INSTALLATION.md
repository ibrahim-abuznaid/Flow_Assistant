# Installation Guide

Complete step-by-step installation guide for the ActivePieces AI Assistant.

## Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Python 3.9 or higher**
   - Download from: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Node.js 16+ and npm**
   - Download from: https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **Git** (optional, for cloning)
   - Download from: https://git-scm.com/
   - Verify: `git --version`

### Required API Keys

1. **OpenAI API Key** (Required)
   - Sign up at: https://platform.openai.com/
   - Create an API key in your account settings
   - You'll need credits/billing set up

2. **Perplexity API Key** (Optional)
   - Sign up at: https://www.perplexity.ai/
   - Get API key from your dashboard
   - Only needed if you want web search functionality

## Installation Methods

Choose one of the following methods:

---

## Method 1: Automated Setup (Recommended)

### Step 1: Get the Code

If you have the project files, navigate to the project directory:

```bash
cd path/to/Flow_Assistant
```

### Step 2: Run Setup Script

```bash
python setup.py
```

This will:
- Check Python version
- Create `.env` file
- Install Python dependencies
- Install frontend dependencies

### Step 3: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# On Windows
notepad .env

# On Mac/Linux
nano .env
```

Add your keys:
```ini
OPENAI_API_KEY=sk-your-actual-key-here
PERPLEXITY_API_KEY=your-perplexity-key-here  # Optional
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview
```

Save and close the file.

### Step 4: Prepare Knowledge Base

```bash
python prepare_knowledge_base.py
```

This will take a few minutes as it:
- Loads 409 pieces from the knowledge base
- Creates embeddings for all pieces, actions, and triggers
- Builds and saves the FAISS vector store

**Note:** This step requires an OpenAI API key and will make API calls (costs ~$0.10-0.50 depending on the size).

### Step 5: Verify Installation

```bash
python test_assistant.py
```

This will run tests to verify:
- Environment variables are set
- Knowledge base is loaded
- Vector store is working
- Tools are functional
- LLM is accessible
- Agent is working

### Step 6: Run the Application

```bash
python run.py
```

Choose option 3 to run both backend and frontend.

---

## Method 2: Manual Setup

### Step 1: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### Step 4: Create Environment File

Copy the example file:

```bash
# On Windows
copy .env.example .env

# On Mac/Linux
cp .env.example .env
```

Edit `.env` and add your API keys.

### Step 5: Prepare Knowledge Base

```bash
python prepare_knowledge_base.py
```

### Step 6: Run Backend

In one terminal:

```bash
uvicorn main:app --reload
```

### Step 7: Run Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

### Step 8: Open Browser

Navigate to: http://localhost:5173

---

## Troubleshooting

### Issue: "Python not found"

**Solution:**
- Make sure Python is installed and in your PATH
- Try `python3` instead of `python`
- On Windows, you might need to use `py` instead

### Issue: "npm not found"

**Solution:**
- Install Node.js from https://nodejs.org/
- Restart your terminal after installation
- Verify with `npm --version`

### Issue: "ModuleNotFoundError"

**Solution:**
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again
- Check that you're in the correct directory

### Issue: "OpenAI API key not found"

**Solution:**
- Make sure `.env` file exists in the project root
- Check that `OPENAI_API_KEY` is set in `.env`
- Verify the key is correct (starts with `sk-`)
- Make sure there are no extra spaces or quotes

### Issue: "Vector store not found"

**Solution:**
- Run `python prepare_knowledge_base.py`
- Make sure it completes without errors
- Check that `ap_faiss_index/` directory exists

### Issue: "Cannot connect to backend"

**Solution:**
- Make sure backend is running on port 8000
- Check that no other service is using port 8000
- Verify CORS settings in `main.py`
- Check firewall settings

### Issue: "Frontend build errors"

**Solution:**
- Delete `frontend/node_modules/` and run `npm install` again
- Clear npm cache: `npm cache clean --force`
- Try using a different Node.js version (LTS recommended)

### Issue: "Rate limit errors from OpenAI"

**Solution:**
- Check your OpenAI account has sufficient credits
- Verify your API key has the correct permissions
- Wait a few minutes and try again
- Consider using a different model (e.g., gpt-3.5-turbo)

### Issue: "Port already in use"

**Solution:**
- Backend (8000): Change port in `main.py` or stop the other service
- Frontend (5173): Vite will automatically try the next available port

---

## Verification Steps

After installation, verify everything works:

### 1. Check Backend

Open http://localhost:8000/health

You should see:
```json
{
  "status": "healthy",
  "message": "Service is operational"
}
```

### 2. Check Stats

Open http://localhost:8000/stats

You should see:
```json
{
  "total_pieces": 409,
  "total_actions": 1529,
  "total_triggers": 453,
  ...
}
```

### 3. Test Chat

Open http://localhost:5173 and try asking:
- "Does ActivePieces have a Slack integration?"
- "How can I send an email?"

You should get relevant responses.

---

## Next Steps

Once installed successfully:

1. **Read the Documentation**
   - [README.md](README.md) - Overview and features
   - [QUICKSTART.md](QUICKSTART.md) - Usage guide
   - [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture details

2. **Customize the Assistant**
   - Edit system prompt in `agent.py`
   - Add more tools in `tools.py`
   - Customize UI in `frontend/src/`

3. **Explore the Code**
   - Review `main.py` for API endpoints
   - Check `tools.py` for tool implementations
   - Look at `agent.py` for agent configuration

4. **Deploy to Production**
   - Set up proper environment variables
   - Use a production ASGI server (e.g., Gunicorn)
   - Build frontend for production: `npm run build`
   - Set up HTTPS and authentication

---

## System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **Internet**: Required for API calls

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 5+ GB free space
- **Internet**: Stable broadband connection

---

## Support

If you encounter issues not covered here:

1. Check the error message carefully
2. Review the troubleshooting section
3. Run the test suite: `python test_assistant.py`
4. Check the logs in the terminal
5. Verify all prerequisites are installed

---

## Uninstallation

To remove the application:

1. **Delete the project directory**
   ```bash
   cd ..
   rm -rf Flow_Assistant  # Mac/Linux
   rmdir /s Flow_Assistant  # Windows
   ```

2. **Remove virtual environment** (if created)
   ```bash
   rm -rf venv  # Mac/Linux
   rmdir /s venv  # Windows
   ```

3. **Remove API keys** (optional)
   - Delete from your `.env` file
   - Revoke keys in your API provider dashboards

---

## Additional Resources

- **Python**: https://docs.python.org/3/
- **FastAPI**: https://fastapi.tiangolo.com/
- **LangChain**: https://python.langchain.com/
- **React**: https://react.dev/
- **Vite**: https://vitejs.dev/
- **OpenAI API**: https://platform.openai.com/docs
- **ActivePieces**: https://www.activepieces.com/docs

---

**Installation complete! Happy automating! 🚀**

