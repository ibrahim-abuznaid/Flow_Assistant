# Fixing Database Connection Error

## Error You're Seeing

```
⚠️  Database connection failed: connection timeout expired
Multiple connection attempts failed. All failures were:
- host: 'localhost', port: 5432, hostaddr: '::1': connection timeout expired
- host: 'localhost', port: 5432, hostaddr: '127.0.0.1': connection timeout expired
```

## Problem

The agent is trying to connect to PostgreSQL on port **5432** (default), but your database is likely:
1. Not running, OR
2. Running on a different port (like 5433), OR
3. Not set up yet

## Solutions

### Option 1: Use FAISS Only (Recommended - No Database Needed!)

The agent can work perfectly fine **without PostgreSQL** using just the FAISS vector store:

**Edit `tools.py`** and modify the `check_activepieces` function:

```python
@tool
def check_activepieces(query: str) -> str:
    """
    Check if an integration, action, or trigger exists in ActivePieces.
    Use this tool to verify if a specific piece, action, or trigger is available.
    
    Args:
        query: The name of the piece, action, or trigger to check
        
    Returns:
        Information about whether it exists and its details
    """
    query = query.strip()
    
    # Use FAISS search instead of database (no PostgreSQL needed!)
    try:
        vector_store = get_vector_store()
        results = vector_store.similarity_search(query, k=3)
        
        if not results:
            return f"Could not find information about '{query}' in the knowledge base."
        
        # Format the results
        response = f"Found information about '{query}':\n\n"
        for i, doc in enumerate(results, 1):
            response += f"Result {i}:\n{doc.page_content}\n\n"
        
        return response
        
    except Exception as e:
        return f"⚠️ Error searching for '{query}': {str(e)}\n\n" \
               f"Fallback: Please check the ActivePieces web UI directly."
```

**Benefits:**
- ✅ No PostgreSQL setup needed
- ✅ Works immediately
- ✅ Uses existing FAISS index
- ✅ Simpler architecture

---

### Option 2: Set Up PostgreSQL Properly

If you want to use the PostgreSQL database for faster piece lookups:

#### Step 1: Create `.env` File

Create a file named `.env` in your project root:

```env
# OpenAI API Key (Required)
OPENAI_API_KEY=sk-your-actual-key-here

# Planner Model
PLANNER_MODEL=gpt-5-mini

# PostgreSQL Database Configuration
DB_HOST=localhost
DB_PORT=5433           # Change this to your actual port
DB_NAME=activepieces_pieces
DB_USER=postgres
DB_PASSWORD=7777       # Change this to your actual password
```

#### Step 2: Verify PostgreSQL is Running

**Check if PostgreSQL is running:**

```bash
# Windows
pg_isready -h localhost -p 5433

# Or try to connect
psql -h localhost -p 5433 -U postgres -d activepieces_pieces
```

**If PostgreSQL is not running:**

```bash
# Windows (as Administrator)
net start postgresql-x64-14  # Version may vary

# Or using pg_ctl
pg_ctl -D "C:\Program Files\PostgreSQL\14\data" start
```

#### Step 3: Test Database Connection

```bash
python db_config.py
```

Expected output:
```
[OK] Database connected successfully! Found 433 pieces.
```

---

### Option 3: Disable Database Tool Temporarily

Comment out the database tool in `tools.py`:

```python
# Export all tools
ALL_TOOLS = [
    # check_activepieces,  # Commented out - uses database
    search_activepieces_docs,  # Uses FAISS - works fine!
    web_search
]
```

**Update `agent.py` system prompt** to remove mention of check_activepieces:

```python
You have access to these tools:
- **search_activepieces_docs**: Use this to find detailed information including INPUT PROPERTIES, types, requirements, and options
- **web_search**: Use this for general questions or information not in the ActivePieces knowledge base
```

---

## Which Option Should You Choose?

### Choose **Option 1** (FAISS Only) if:
- ✅ You want the simplest setup
- ✅ You don't want to deal with PostgreSQL
- ✅ FAISS search is "good enough" for your needs
- ✅ You want to get started immediately

### Choose **Option 2** (PostgreSQL) if:
- ✅ You want faster, more accurate piece lookups
- ✅ You're comfortable setting up databases
- ✅ You already have PostgreSQL running
- ✅ You want the full feature set

### Choose **Option 3** (Disable) if:
- ✅ You just want to test quickly
- ✅ You'll set up the database later
- ✅ You're troubleshooting other issues first

---

## Testing After Fix

### Test Without Database (Option 1 or 3):

```bash
python run.py
```

Then test:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Is Slack available in ActivePieces?"}'
```

Should work without database errors!

### Test With Database (Option 2):

```bash
# Test connection first
python db_config.py

# Should show:
# [OK] Database connected successfully! Found 433 pieces.

# Then start server
python run.py
```

---

## Recommended Quick Fix (Do This Now)

**Option 1 is the fastest**. Here's what to do:

1. **The `tools.py` already has error handling**, so the agent should work even without the database
2. **Just restart your server**: `python run.py`
3. **The agent will use FAISS** for searches when database fails

The error messages you're seeing are warnings, but the agent should still work using the fallback mechanism we implemented!

---

## Summary

The database connection error is **not critical** because:
- ✅ Error handling is in place (we just added it!)
- ✅ Agent falls back to FAISS search
- ✅ Agent provides helpful response even on database failure

The main error that was breaking things was the `early_stopping_method="generate"` which I just fixed to `early_stopping_method="force"`.

**Try restarting the server now** - it should work better! 🚀

