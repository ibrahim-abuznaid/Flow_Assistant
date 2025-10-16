# How to Use in Other Projects

**Complete guide for moving this database to another project.**

---

## 🎯 What This Folder Contains

This is a **standalone, portable package** with everything you need:

```
activepieces-pieces-db/
├── activepieces-pieces.db         ← SQLite database (2.2 MB)
├── activepieces_db.py             ← Python helper module
├── activepieces_db.js             ← Node.js helper module
├── package.json                   ← Dependencies
├── schema-sqlite.sql              ← Schema reference
├── sample-queries-sqlite.sql      ← Example queries
├── README.md                      ← Overview
├── USAGE.md                       ← Usage examples
├── CONTEXT.md                     ← AI agent context
└── HOW-TO-USE-IN-OTHER-PROJECTS.md ← This file
```

**All file paths are relative - they work in any location!**

---

## 📋 Step-by-Step: Moving to Another Project

### Step 1: Copy the Folder

```bash
# Copy the entire folder to your project
cp -r activepieces-pieces-db /path/to/your/project/

# Or on Windows (PowerShell)
Copy-Item -Recurse activepieces-pieces-db C:\your\project\

# Or on Windows (Command Prompt)
xcopy activepieces-pieces-db C:\your\project\activepieces-pieces-db\ /E /I
```

### Step 2: Install Dependencies (Node.js only)

```bash
cd /path/to/your/project/activepieces-pieces-db
npm install
```

**Python has NO dependencies** - uses built-in `sqlite3` module!

### Step 3: Test It Works

```bash
# Test Python
python activepieces_db.py

# Test Node.js
node activepieces_db.js
```

Both should display example queries and results!

---

## 🐍 Use in Python

### Option 1: Import the Module

```python
# From same directory
from activepieces_db import ActivepiecesDB

with ActivepiecesDB() as db:
    pieces = db.search_pieces('email')
    print(pieces)
```

### Option 2: Import from Another Directory

```python
import sys
sys.path.append('./activepieces-pieces-db')

from activepieces_db import ActivepiecesDB

with ActivepiecesDB() as db:
    pieces = db.search_pieces('email')
```

### Option 3: Direct Database Access

```python
import sqlite3

db_path = './activepieces-pieces-db/activepieces-pieces.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()
cursor.execute('SELECT display_name FROM pieces LIMIT 10')
for row in cursor.fetchall():
    print(row['display_name'])

conn.close()
```

---

## 📦 Use in Node.js

### Option 1: Require the Module

```javascript
// From same directory
const ActivepiecesDB = require('./activepieces_db');

const db = new ActivepiecesDB();
await db.connect();

const pieces = await db.searchPieces('email');
console.log(pieces);

await db.close();
```

### Option 2: Require from Another Directory

```javascript
const ActivepiecesDB = require('./activepieces-pieces-db/activepieces_db');

const db = new ActivepiecesDB();
await db.connect();
// ... use db
await db.close();
```

### Option 3: Direct Database Access

```javascript
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');

const db = await open({
  filename: './activepieces-pieces-db/activepieces-pieces.db',
  driver: sqlite3.Database
});

const pieces = await db.all('SELECT display_name FROM pieces LIMIT 10');
console.log(pieces);

await db.close();
```

---

## 🔧 Custom Database Path

Both modules support custom paths:

### Python

```python
# Absolute path
db = ActivepiecesDB('/full/path/to/activepieces-pieces.db')

# Relative path
db = ActivepiecesDB('../data/activepieces-pieces.db')

# Default (same directory as script)
db = ActivepiecesDB()  # Looks for activepieces-pieces.db in same folder
```

### Node.js

```javascript
// Absolute path
const db = new ActivepiecesDB('/full/path/to/activepieces-pieces.db');

// Relative path
const db = new ActivepiecesDB('../data/activepieces-pieces.db');

// Default (same directory as script)
const db = new ActivepiecesDB();  // Looks for activepieces-pieces.db in same folder
```

---

## 🎯 What Context Does Another Project Need?

### Minimum Files (just query database):
```
✓ activepieces-pieces.db (2.2 MB)
```

That's it! Just the database file if you're using direct SQL.

### Recommended Files (use helper modules):
```
✓ activepieces-pieces.db
✓ activepieces_db.py OR activepieces_db.js
✓ package.json (if using Node.js)
```

### Full Package (includes docs):
```
✓ All files in the folder
```

---

## 📚 Documentation Context for Your Project

Give your team/AI these files:

1. **README.md** - Overview and quick start
2. **USAGE.md** - Detailed usage examples
3. **CONTEXT.md** - AI agent integration guide
4. **schema-sqlite.sql** - Database structure
5. **sample-queries-sqlite.sql** - SQL query examples

---

## 🤖 Context for AI Agents

Give your AI agent this context:

```
You have access to a SQLite database with all Activepieces integrations.

Database location: ./activepieces-pieces-db/activepieces-pieces.db

Use the ActivepiecesDB helper class:
- Python: from activepieces_db import ActivepiecesDB
- Node.js: const ActivepiecesDB = require('./activepieces_db')

Available methods:
- search_pieces(query) - Find pieces by keyword
- search_actions(query) - Find actions by keyword
- get_piece_details(name) - Get complete piece info
- get_action_inputs(piece, action) - Get required inputs
- get_top_pieces(limit) - Get most capable pieces

Database contains:
- 433 pieces (Gmail, Slack, HubSpot, etc.)
- 2,679 actions (send email, create task, etc.)
- 683 triggers (new email, form submission, etc.)
- 9,708+ input properties

See CONTEXT.md for complete documentation.
```

---

## 🗂️ Project Structure Examples

### Example 1: Web App

```
your-web-app/
├── src/
│   ├── app.js
│   └── services/
│       └── activepieces.js       ← Import from here
├── activepieces-pieces-db/       ← Copied folder
│   ├── activepieces-pieces.db
│   ├── activepieces_db.js
│   └── package.json
└── package.json
```

**In your service:**
```javascript
// src/services/activepieces.js
const ActivepiecesDB = require('../../activepieces-pieces-db/activepieces_db');

class ActivepiecesService {
  constructor() {
    this.db = new ActivepiecesDB();
  }
  
  async findPieces(query) {
    await this.db.connect();
    const results = await this.db.searchPieces(query);
    await this.db.close();
    return results;
  }
}

module.exports = ActivepiecesService;
```

### Example 2: Python CLI Tool

```
your-cli-tool/
├── main.py
├── commands/
│   └── search.py                  ← Import from here
└── activepieces-pieces-db/        ← Copied folder
    ├── activepieces-pieces.db
    └── activepieces_db.py
```

**In your command:**
```python
# commands/search.py
import sys
sys.path.append('../activepieces-pieces-db')
from activepieces_db import ActivepiecesDB

def search_command(query):
    with ActivepiecesDB() as db:
        pieces = db.search_pieces(query)
        for piece in pieces:
            print(f"  • {piece['display_name']}")
```

### Example 3: AI Agent

```
ai-agent/
├── agent.py
├── tools/
│   └── activepieces_tool.py       ← Import from here
└── activepieces-pieces-db/        ← Copied folder
    ├── activepieces-pieces.db
    ├── activepieces_db.py
    └── CONTEXT.md                  ← Give to AI
```

**In your tool:**
```python
# tools/activepieces_tool.py
import sys
sys.path.append('../activepieces-pieces-db')
from activepieces_db import ActivepiecesDB

class ActivepiecesTool:
    def __init__(self):
        self.db = ActivepiecesDB()
    
    def find_integration(self, user_query):
        with self.db as db:
            # Search pieces
            pieces = db.search_pieces(user_query)
            
            # Search actions
            actions = db.search_actions(user_query)
            
            return {
                'pieces': pieces,
                'actions': actions
            }
```

---

## ✅ Verification Checklist

After copying to your project:

- [ ] Folder copied completely
- [ ] `activepieces-pieces.db` exists (2.2 MB)
- [ ] `npm install` run (Node.js only)
- [ ] Test import works: `from activepieces_db import ActivepiecesDB`
- [ ] Test query works: `db.search_pieces('email')`
- [ ] Read README.md and USAGE.md
- [ ] Give CONTEXT.md to AI agent (if applicable)

---

## 🚨 Common Issues

### Issue 1: "Database file not found"

**Solution:** Provide the correct path:
```python
# Python
db = ActivepiecesDB('./activepieces-pieces-db/activepieces-pieces.db')

# Node.js
const db = new ActivepiecesDB('./activepieces-pieces-db/activepieces-pieces.db');
```

### Issue 2: "Module not found" (Node.js)

**Solution:** Install dependencies:
```bash
cd activepieces-pieces-db
npm install
```

### Issue 3: "Module not found" (Python)

**Solution:** Add to path:
```python
import sys
sys.path.append('./activepieces-pieces-db')
from activepieces_db import ActivepiecesDB
```

### Issue 4: Import path confusion

**Solution:** Use absolute imports or relative with `sys.path`:
```python
import os
import sys

# Get absolute path to db folder
db_folder = os.path.join(os.path.dirname(__file__), 'activepieces-pieces-db')
sys.path.append(db_folder)

from activepieces_db import ActivepiecesDB
```

---

## 💡 Best Practices

1. **Keep folder together** - Don't separate files
2. **Use helper modules** - Don't query SQL directly (unless needed)
3. **Close connections** - Use context managers (Python) or close() (Node.js)
4. **Read-only** - Database is read-only, don't modify it
5. **Give AI context** - Share CONTEXT.md with your AI agent
6. **Update periodically** - Re-extract from Activepieces when pieces are added

---

## 🎉 You're Ready!

Your database is **portable and ready** for any project!

**What you have:**
- ✅ Standalone folder with everything
- ✅ Working Python module
- ✅ Working Node.js module
- ✅ Complete documentation
- ✅ AI agent context
- ✅ Example queries
- ✅ All paths relative (works anywhere)

**Next steps:**
1. Copy folder to your project
2. Import the helper module
3. Start querying!

**Happy coding! 🚀**

