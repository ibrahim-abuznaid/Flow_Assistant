# Activepieces Database - Flow_Assistant Integration Guide

**Welcome to your Flow_Assistant project!** This database is ready to use.

---

## ✅ Setup Complete

The database is already copied and working in your project:

```
C:\AP work\Flow_Assistant\activepieces-pieces-db\
├── activepieces-pieces.db        ← Database (2.2 MB, 433 pieces)
├── activepieces_db.py            ← Python helper
├── activepieces_db.js            ← Node.js helper
├── example_usage.py              ← Python example
├── example_usage.js              ← Node.js example
└── [documentation files]
```

---

## 🚀 Quick Test

```bash
cd "C:\AP work\Flow_Assistant\activepieces-pieces-db"

# Test Python
python example_usage.py

# Test Node.js
node example_usage.js
```

Both examples show how to use the database in your Flow_Assistant!

---

## 💻 Use in Your Flow_Assistant Code

### Python

```python
# Add to your Python path if needed
import sys
sys.path.append('./activepieces-pieces-db')

from activepieces_db import ActivepiecesDB

# In your Flow Assistant code
def find_integration(user_query):
    with ActivepiecesDB() as db:
        # Search for pieces
        pieces = db.search_pieces(user_query)
        
        # Search for actions
        actions = db.search_actions(user_query)
        
        return {
            'pieces': pieces,
            'actions': actions
        }

# Example usage
result = find_integration('send email')
print(result['actions'])
```

### Node.js

```javascript
// In your Flow Assistant code
const ActivepiecesDB = require('./activepieces-pieces-db/activepieces_db');

async function findIntegration(userQuery) {
  const db = new ActivepiecesDB();
  await db.connect();
  
  try {
    // Search for pieces
    const pieces = await db.searchPieces(userQuery);
    
    // Search for actions
    const actions = await db.searchActions(userQuery);
    
    return { pieces, actions };
  } finally {
    await db.close();
  }
}

// Example usage
findIntegration('send email').then(console.log);
```

---

## 🤖 For Your AI Agent

Add this to your AI agent's system prompt:

```
You have access to a SQLite database with 433 Activepieces integrations.

Location: ./activepieces-pieces-db/activepieces-pieces.db

Helper module (Python):
from activepieces_db import ActivepiecesDB

with ActivepiecesDB() as db:
    # Search integrations
    pieces = db.search_pieces('email')
    
    # Find actions
    actions = db.search_actions('send email')
    
    # Get required inputs
    inputs = db.get_action_inputs('gmail', 'send_email')

Available methods:
- search_pieces(query, limit=10) - Find integrations by keyword
- search_actions(query, limit=10) - Find actions by keyword
- get_piece_details(name) - Get complete piece information
- get_action_inputs(piece, action) - Get required/optional inputs
- get_top_pieces(limit=20) - Get most capable pieces
- get_all_pieces() - Get all pieces
- get_pieces_by_auth_type(type) - Filter by auth type

The database contains:
- 433 pieces (Gmail, Slack, HubSpot, Asana, etc.)
- 2,679 actions (send email, create task, update row, etc.)
- 683 triggers (new email, form submission, webhook, etc.)
- 9,708+ input properties (all required/optional fields)

For complete context, see: ./activepieces-pieces-db/CONTEXT.md
```

---

## 📋 Common Use Cases for Flow_Assistant

### 1. User asks: "Can I send emails?"

```python
with ActivepiecesDB() as db:
    actions = db.search_actions('send email')
    
    print("Yes! You can send emails using:")
    for action in actions[:5]:
        print(f"  • {action['piece_display_name']}")
```

### 2. User asks: "What integrations do you have?"

```python
with ActivepiecesDB() as db:
    top = db.get_top_pieces(limit=20)
    
    print("Top integrations:")
    for piece in top:
        print(f"  • {piece['display_name']}: {piece['action_count']} actions")
```

### 3. User asks: "How do I send an email with Gmail?"

```python
with ActivepiecesDB() as db:
    inputs = db.get_action_inputs('gmail', 'send_email')
    
    required = [i for i in inputs if i['required']]
    
    print("To send email with Gmail, you need:")
    for inp in required:
        print(f"  • {inp['display_name']}: {inp['description']}")
```

### 4. Build a flow dynamically

```python
with ActivepiecesDB() as db:
    # User: "Send Slack message when I get email"
    
    # Find trigger
    triggers = db.search_actions('new email')  # Note: search in actions/triggers
    
    # Find action
    actions = db.search_actions('send slack message')
    
    # Get inputs for chosen action
    inputs = db.get_action_inputs('slack', 'send_message_to_channel')
    
    # Build flow configuration...
```

---

## 🗂️ Project Structure Example

```
Flow_Assistant/
├── main.py                        ← Your main app
├── agents/
│   └── flow_builder.py           ← Import DB here
├── activepieces-pieces-db/       ← Database folder
│   ├── activepieces-pieces.db
│   ├── activepieces_db.py
│   └── ...
└── requirements.txt
```

**In your agent:**
```python
# agents/flow_builder.py
import sys
sys.path.append('../activepieces-pieces-db')
from activepieces_db import ActivepiecesDB

class FlowBuilderAgent:
    def __init__(self):
        self.db = ActivepiecesDB()
    
    def suggest_flow(self, user_intent):
        with self.db as db:
            actions = db.search_actions(user_intent)
            # Build flow...
```

---

## 📊 What's in the Database

```
433 Pieces
├── Communication: Gmail, Slack, Discord, Teams, Telegram
├── Project Management: Asana, Trello, Monday, ClickUp
├── CRM: HubSpot, Salesforce, Pipedrive
├── Spreadsheets: Google Sheets, Airtable, Excel
├── Forms: Typeform, Google Forms, Jotform
└── And 400+ more...

2,679 Actions
├── Send Email, Create Task, Update Row
├── Post Message, Upload File, Delete Record
└── Thousands more operations...

683 Triggers
├── New Email, Form Submission, New Row
├── Webhook Received, Scheduled
└── Hundreds more events...
```

---

## 📚 Documentation Files

All in `./activepieces-pieces-db/`:

1. **START-HERE.md** - Quick start guide
2. **README.md** - Complete overview
3. **USAGE.md** - Detailed usage examples
4. **CONTEXT.md** - AI agent context (give this to your AI!)
5. **HOW-TO-USE-IN-OTHER-PROJECTS.md** - Integration guide
6. **schema-sqlite.sql** - Database structure
7. **sample-queries-sqlite.sql** - 50+ query examples

---

## ✅ Verification

Test that everything works:

```bash
cd "C:\AP work\Flow_Assistant\activepieces-pieces-db"

# Python test
python example_usage.py

# Node.js test
node example_usage.js
```

Both should show:
- ✓ Email integrations search
- ✓ Send message actions
- ✓ Gmail required inputs
- ✓ Top 10 integrations

---

## 🎯 Next Steps

1. ✅ Database copied and tested
2. 📖 Read `START-HERE.md` for overview
3. 📖 Read `CONTEXT.md` for AI integration
4. 💻 Run `example_usage.py` or `example_usage.js`
5. 🚀 Import into your Flow_Assistant code!

---

## 🆘 Need Help?

- **Quick start:** `START-HERE.md`
- **Usage examples:** `USAGE.md`
- **AI integration:** `CONTEXT.md`
- **SQL queries:** `sample-queries-sqlite.sql`

---

## 🎉 You're Ready!

The Activepieces database is now integrated into your Flow_Assistant project!

**Database path:**
```
C:\AP work\Flow_Assistant\activepieces-pieces-db\activepieces-pieces.db
```

**Import and use:**
```python
from activepieces_db import ActivepiecesDB
```

**Start building flows! 🚀**

