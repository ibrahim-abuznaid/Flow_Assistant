# 🎉 START HERE - Portable Activepieces Database

**Welcome! This folder contains everything you need to use the Activepieces database in ANY project.**

---

## ✅ What You Have

A **complete, portable SQLite database** with:

- ✓ **433 Activepieces integrations** (pieces)
- ✓ **2,679 actions** (send email, create task, etc.)
- ✓ **683 triggers** (new email, form submission, etc.)
- ✓ **9,708 input properties** (all required/optional fields)
- ✓ **Full-text search** (FTS5 for instant search)

**Database size:** 2.2 MB  
**Location:** `activepieces-pieces.db`

---

## 🚀 Quick Start (30 seconds)

### Test It Works

```bash
# Python test (no dependencies!)
python activepieces_db.py

# Node.js test (after npm install)
npm install
node activepieces_db.js
```

Both should show example queries and results!

### Use in Your Code

**Python:**
```python
from activepieces_db import ActivepiecesDB

with ActivepiecesDB() as db:
    # Search for email pieces
    pieces = db.search_pieces('email')
    print(pieces)
```

**Node.js:**
```javascript
const ActivepiecesDB = require('./activepieces_db');

const db = new ActivepiecesDB();
await db.connect();
const pieces = await db.searchPieces('email');
await db.close();
```

---

## 📂 Files in This Folder

### Core Files
- `activepieces-pieces.db` - **THE DATABASE** (2.2 MB)
- `activepieces_db.py` - Python helper module
- `activepieces_db.js` - Node.js helper module
- `package.json` - Node.js dependencies

### Documentation (Read These!)
- `START-HERE.md` - **This file** (start here!)
- `README.md` - Complete overview
- `USAGE.md` - Detailed usage examples
- `CONTEXT.md` - AI agent context guide
- `HOW-TO-USE-IN-OTHER-PROJECTS.md` - Moving to other projects

### Reference
- `schema-sqlite.sql` - Database structure
- `sample-queries-sqlite.sql` - 50+ example queries

---

## 🎯 What To Read

### If you want to...

**Get started quickly:**
→ Read this file (START-HERE.md)

**See usage examples:**
→ Read USAGE.md

**Use in another project:**
→ Read HOW-TO-USE-IN-OTHER-PROJECTS.md

**Integrate with AI agent:**
→ Read CONTEXT.md (give this to your AI)

**Understand the database:**
→ Read README.md and schema-sqlite.sql

**See query examples:**
→ Open sample-queries-sqlite.sql

---

## 💡 Most Common Use Cases

### 1. Search for Integrations

```python
pieces = db.search_pieces('email')
# Returns: Gmail, Outlook, SendGrid, etc.
```

### 2. Find Actions

```python
actions = db.search_actions('send email')
# Returns all actions that can send email
```

### 3. Get Required Inputs

```python
inputs = db.get_action_inputs('gmail', 'send_email')
# Returns: to, subject, body, etc.
```

### 4. Get Top Integrations

```python
top = db.get_top_pieces(limit=10)
# Returns most capable pieces
```

---

## 📦 Copy to Another Project

### Step 1: Copy This Entire Folder

```bash
# Linux/Mac
cp -r activepieces-pieces-db /path/to/your/project/

# Windows (PowerShell)
Copy-Item -Recurse activepieces-pieces-db C:\your\project\

# Windows (Command Prompt)
xcopy activepieces-pieces-db C:\your\project\activepieces-pieces-db\ /E /I
```

### Step 2: Install Dependencies (Node.js only)

```bash
cd activepieces-pieces-db
npm install
```

### Step 3: Import and Use

```python
# Python
from activepieces_db import ActivepiecesDB
```

```javascript
// Node.js
const ActivepiecesDB = require('./activepieces_db');
```

**That's it!** All paths are relative - works anywhere!

---

## 🤖 For AI Agents

Give your AI agent this context:

```
You have access to a SQLite database with 433 Activepieces integrations.

Location: ./activepieces-pieces-db/activepieces-pieces.db

Helper module:
- Python: from activepieces_db import ActivepiecesDB
- Node.js: const ActivepiecesDB = require('./activepieces_db')

Key methods:
- search_pieces(query) - Find integrations
- search_actions(query) - Find operations
- get_piece_details(name) - Get complete info
- get_action_inputs(piece, action) - Get required fields

Full context in CONTEXT.md
```

---

## 📊 Database Contents

```
433 Pieces
├── Gmail, Slack, HubSpot, Asana...
├── Each has:
│   ├── Actions (things it can do)
│   ├── Triggers (events it can detect)
│   └── Authentication info

2,679 Actions
├── Send Email, Create Task, Update Row...
├── Each has:
│   ├── Display name and description
│   ├── Required/optional inputs
│   └── Input types and defaults

683 Triggers
├── New Email, Form Submission, New Row...
├── Each has:
│   ├── Trigger type (webhook/polling)
│   └── Configuration options
```

---

## 🎯 Quick Reference

### Python API

```python
class ActivepiecesDB:
    search_pieces(query, limit=10)
    search_actions(query, limit=10)
    get_piece_details(piece_name)
    get_action_inputs(piece_name, action_name)
    get_top_pieces(limit=20)
    get_all_pieces()
    get_pieces_by_auth_type(auth_type)
```

### Node.js API

```javascript
class ActivepiecesDB {
  async searchPieces(query, limit=10)
  async searchActions(query, limit=10)
  async getPieceDetails(pieceName)
  async getActionInputs(pieceName, actionName)
  async getTopPieces(limit=20)
  async getAllPieces()
  async getPiecesByAuthType(authType)
}
```

---

## 🔍 Example Queries

### Find Gmail send_email inputs

```python
with ActivepiecesDB() as db:
    inputs = db.get_action_inputs('gmail', 'send_email')
    
    for inp in inputs:
        if inp['required']:
            print(f"✓ {inp['display_name']} ({inp['type']})")
```

### Search for Slack actions

```python
with ActivepiecesDB() as db:
    actions = db.search_actions('slack message')
    
    for action in actions:
        print(f"{action['piece_display_name']}: {action['action_display_name']}")
```

### Get OAuth2 pieces

```python
with ActivepiecesDB() as db:
    pieces = db.get_pieces_by_auth_type('OAuth2')
    print(f"Found {len(pieces)} OAuth2 pieces")
```

---

## ✨ Why This is Awesome

✅ **Portable** - Copy folder = copy everything  
✅ **No server** - SQLite, no setup needed  
✅ **No dependencies** (Python) - Uses built-in sqlite3  
✅ **Fast** - Queries in < 10ms  
✅ **Complete** - All 433 pieces with full details  
✅ **Well documented** - 5 documentation files  
✅ **Helper modules** - Easy Python/JS wrappers  
✅ **Full-text search** - FTS5 for instant search  
✅ **Tested** - Both examples work perfectly  

---

## 🚨 Important Notes

1. **Keep files together** - Don't separate files in this folder
2. **Database is read-only** - Don't modify the database
3. **Python needs nothing** - Uses built-in sqlite3
4. **Node.js needs npm install** - Run once after copying
5. **All paths work anywhere** - Everything is relative
6. **Give AI the CONTEXT.md** - Complete context for agents

---

## 📞 Need Help?

1. **Quick start** → Read this file (START-HERE.md)
2. **Usage examples** → Read USAGE.md
3. **Moving to other project** → Read HOW-TO-USE-IN-OTHER-PROJECTS.md
4. **AI integration** → Read CONTEXT.md
5. **Database structure** → Read schema-sqlite.sql
6. **SQL examples** → Read sample-queries-sqlite.sql

---

## ✅ Checklist

- [ ] Tested Python example: `python activepieces_db.py`
- [ ] Tested Node.js example: `node activepieces_db.js`
- [ ] Read README.md
- [ ] Read USAGE.md
- [ ] Understood how to import in your project
- [ ] Gave CONTEXT.md to AI agent (if applicable)

---

## 🎉 You're Ready!

Everything you need is in this folder!

**Next steps:**
1. ✅ Files tested and working
2. 📖 Read the documentation
3. 📋 Copy folder to your project
4. 🚀 Start coding!

**Location:** `C:\AP work\activepieces\activepieces-pieces-db`

**Happy automating! 🚀**

