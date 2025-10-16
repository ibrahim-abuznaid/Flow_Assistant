# Activepieces Pieces Database - Portable Package

A **standalone, portable** SQLite database containing all Activepieces integrations (pieces), their actions, triggers, and input properties.

**Copy this entire folder to any project and start querying immediately!**

---

## 📦 What's Included

This folder contains everything you need:

```
activepieces-pieces-db/
├── activepieces-pieces.db        ← SQLite database (2.2 MB)
├── activepieces_db.py            ← Python helper module
├── activepieces_db.js            ← Node.js helper module
├── package.json                  ← Node.js dependencies
├── schema-sqlite.sql             ← Database schema (reference)
├── sample-queries-sqlite.sql     ← 50+ example queries
├── README.md                     ← This file
├── USAGE.md                      ← Quick usage guide
└── CONTEXT.md                    ← AI agent context guide
```

---

## 🚀 Quick Start

### Option 1: Python

```python
from activepieces_db import ActivepiecesDB

# Connect and query
with ActivepiecesDB() as db:
    # Search for pieces
    pieces = db.search_pieces('email')
    for piece in pieces:
        print(piece['display_name'])
    
    # Find actions
    actions = db.search_actions('send email')
    
    # Get action inputs
    inputs = db.get_action_inputs('gmail', 'send_email')
```

### Option 2: Node.js

```javascript
const ActivepiecesDB = require('./activepieces_db');

async function query() {
  const db = new ActivepiecesDB();
  await db.connect();
  
  // Search for pieces
  const pieces = await db.searchPieces('email');
  console.log(pieces);
  
  // Find actions
  const actions = await db.searchActions('send email');
  
  // Get action inputs
  const inputs = await db.getActionInputs('gmail', 'send_email');
  
  await db.close();
}

query();
```

### Option 3: Direct SQL

```python
import sqlite3

conn = sqlite3.connect('activepieces-pieces.db')
cursor = conn.cursor()

cursor.execute('SELECT display_name FROM pieces LIMIT 10')
for row in cursor.fetchall():
    print(row[0])

conn.close()
```

---

## 📊 Database Contents

- **433 Pieces** - All Activepieces integrations
- **2,679 Actions** - Things pieces can do
- **683 Triggers** - Events that start flows
- **9,708 Input Properties** - Required/optional fields
- **Full-text search** - FTS5 for instant search

---

## 🎯 Use in Your Project

### Step 1: Copy This Folder

Copy the entire `activepieces-pieces-db` folder to your project:

```bash
# Copy to your project
cp -r activepieces-pieces-db /path/to/your/project/

# Or on Windows
xcopy activepieces-pieces-db C:\your\project\ /E /I
```

### Step 2: Install Dependencies (Node.js only)

```bash
cd activepieces-pieces-db
npm install
```

Python has no external dependencies - uses built-in `sqlite3` module!

### Step 3: Import and Use

**Python:**
```python
# Import the helper module
from activepieces_db import ActivepiecesDB

# Use it
with ActivepiecesDB() as db:
    results = db.search_pieces('email')
```

**Node.js:**
```javascript
// Require the helper module
const ActivepiecesDB = require('./activepieces_db');

// Use it
const db = new ActivepiecesDB();
await db.connect();
const results = await db.searchPieces('email');
await db.close();
```

---

## 🤖 For AI Agents

This database is perfect for AI agents that need to:

1. **Discover integrations** - "What pieces can send email?"
2. **Find actions** - "How do I send a message on Slack?"
3. **Get inputs** - "What fields are required to send an email?"
4. **Build flows** - Construct Activepieces flows dynamically

See `CONTEXT.md` for the full context to give your AI agent.

---

## 📚 Documentation Files

- **README.md** (this file) - Overview and quick start
- **USAGE.md** - Detailed usage examples
- **CONTEXT.md** - Full context for AI agents
- **schema-sqlite.sql** - Database schema reference
- **sample-queries-sqlite.sql** - 50+ example queries

---

## 🔍 Quick Examples

### Search for email pieces
```python
pieces = db.search_pieces('email')
# Returns: Gmail, Outlook, SendGrid, etc.
```

### Find "send email" actions
```python
actions = db.search_actions('send email')
# Returns all actions that can send email
```

### Get Gmail send_email inputs
```python
inputs = db.get_action_inputs('gmail', 'send_email')
# Returns: to, subject, body, etc. with types and requirements
```

### Get top pieces by capabilities
```python
top_pieces = db.get_top_pieces(limit=10)
# Returns pieces ordered by action+trigger count
```

---

## 📖 API Reference

### Python: `ActivepiecesDB`

```python
class ActivepiecesDB:
    def search_pieces(query: str, limit: int = 10) -> List[Dict]
    def search_actions(query: str, limit: int = 10) -> List[Dict]
    def get_piece_details(piece_name: str) -> Dict
    def get_action_inputs(piece_name: str, action_name: str) -> List[Dict]
    def get_top_pieces(limit: int = 20) -> List[Dict]
    def get_all_pieces() -> List[Dict]
    def get_pieces_by_auth_type(auth_type: str) -> List[Dict]
```

### Node.js: `ActivepiecesDB`

```javascript
class ActivepiecesDB {
  async searchPieces(query, limit = 10)
  async searchActions(query, limit = 10)
  async getPieceDetails(pieceName)
  async getActionInputs(pieceName, actionName)
  async getTopPieces(limit = 20)
  async getAllPieces()
  async getPiecesByAuthType(authType)
}
```

---

## 🗄️ Database Schema

### Tables
- `pieces` - All integrations
- `actions` - What pieces can do
- `triggers` - Events that start flows
- `action_properties` - Input fields for actions
- `trigger_properties` - Configuration for triggers

### Views
- `pieces_with_capabilities` - Pieces with action/trigger counts
- `piece_statistics` - Detailed statistics

### Full-Text Search
- `pieces_fts` - Search pieces
- `actions_fts` - Search actions
- `triggers_fts` - Search triggers

---

## 💡 Why This is Perfect

✅ **Portable** - Single folder with everything  
✅ **No server** - SQLite database, no setup  
✅ **No dependencies** - Python uses built-in sqlite3  
✅ **Fast** - Queries in < 10ms  
✅ **Complete** - All 433 pieces with full details  
✅ **Helper modules** - Easy-to-use Python/JS wrappers  
✅ **Well documented** - Multiple guides and examples  

---

## 🔄 Updating

This database is a **snapshot** of Activepieces integrations. To get the latest:

1. Go back to the original Activepieces project
2. Run the extraction and population scripts
3. Copy the new `activepieces-pieces.db` file here
4. Done!

---

## 📝 Files You Need

### Minimum (just query the database):
- `activepieces-pieces.db` (2.2 MB)

### Recommended (use helper modules):
- `activepieces-pieces.db`
- `activepieces_db.py` OR `activepieces_db.js`
- `package.json` (if using Node.js)

### Full package (includes docs and examples):
- All files in this folder

---

## 🎯 Common Use Cases

### 1. AI Agent Discovery
```python
# User: "I want to send an email"
actions = db.search_actions('send email')
# Agent shows: Gmail, Outlook, SendGrid options
```

### 2. Dynamic Flow Building
```python
# User selects: Gmail > Send Email
inputs = db.get_action_inputs('gmail', 'send_email')
# Agent prompts for: to, subject, body, etc.
```

### 3. Integration Search
```python
# User: "Do we have Slack integration?"
pieces = db.search_pieces('slack')
# Returns Slack piece with all capabilities
```

### 4. Analytics
```python
# Get OAuth2 integrations
oauth_pieces = db.get_pieces_by_auth_type('OAuth2')
# Returns 60+ pieces with OAuth2
```

---

## 🚨 Important Notes

1. **Self-contained** - This folder has everything. Just copy it!
2. **No internet needed** - Database is local and complete
3. **Read-only safe** - Multiple processes can read simultaneously
4. **Python 3.6+** - Uses built-in sqlite3 module
5. **Node.js 12+** - Needs `npm install` for dependencies

---

## 🆘 Troubleshooting

**Database file not found?**
- Make sure `activepieces-pieces.db` is in the same folder as the script
- Or provide explicit path: `ActivepiecesDB('/path/to/db')`

**Module not found (Node.js)?**
```bash
npm install
```

**No results from search?**
- Check your query syntax
- Try broader terms: 'email' instead of 'send email message'

---

## 📞 Questions?

- See `USAGE.md` for detailed usage examples
- See `CONTEXT.md` for AI agent integration
- Check `sample-queries-sqlite.sql` for query examples
- Review schema in `schema-sqlite.sql`

---

## ✨ Ready to Use!

```bash
# Test it works
python activepieces_db.py
# or
node activepieces_db.js
```

**Your Activepieces database is ready! 🚀**

