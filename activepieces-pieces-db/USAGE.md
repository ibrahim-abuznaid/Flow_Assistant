# Usage Guide - Activepieces Pieces Database

Complete guide for using the Activepieces database in your project.

---

## 📦 Setup

### Copy to Your Project

```bash
# Copy the entire folder
cp -r activepieces-pieces-db /path/to/your/project/

# Navigate to it
cd /path/to/your/project/activepieces-pieces-db
```

### Install Dependencies (Node.js only)

```bash
npm install
```

Python has no dependencies (uses built-in `sqlite3`)!

---

## 🐍 Python Usage

### Basic Import

```python
from activepieces_db import ActivepiecesDB

# Create connection
with ActivepiecesDB() as db:
    # Query database
    results = db.search_pieces('email')
```

### Custom Database Path

```python
db = ActivepiecesDB('/custom/path/to/activepieces-pieces.db')
with db as connection:
    results = connection.search_pieces('email')
```

### Complete Example

```python
from activepieces_db import ActivepiecesDB

def find_email_integration():
    with ActivepiecesDB() as db:
        # Search for email pieces
        print("=== Email Integrations ===")
        pieces = db.search_pieces('email', limit=5)
        
        for piece in pieces:
            print(f"\n{piece['display_name']}")
            print(f"  Auth: {piece['auth_type']}")
            print(f"  Actions: {piece['action_count']}")
            print(f"  Triggers: {piece['trigger_count']}")
        
        # Get Gmail details
        print("\n=== Gmail Details ===")
        gmail = db.get_piece_details('gmail')
        
        if gmail:
            print(f"Name: {gmail['display_name']}")
            print(f"Actions: {len(gmail['actions'])}")
            
            print("\nAvailable actions:")
            for action in gmail['actions']:
                print(f"  • {action['display_name']}")
        
        # Get send_email inputs
        print("\n=== Gmail Send Email Inputs ===")
        inputs = db.get_action_inputs('gmail', 'send_email')
        
        required = [i for i in inputs if i['required']]
        optional = [i for i in inputs if not i['required']]
        
        print("Required fields:")
        for field in required:
            print(f"  • {field['display_name']} ({field['type']})")
        
        print("\nOptional fields:")
        for field in optional[:5]:  # Show first 5
            print(f"  • {field['display_name']} ({field['type']})")

if __name__ == '__main__':
    find_email_integration()
```

---

## 📦 Node.js Usage

### Basic Import

```javascript
const ActivepiecesDB = require('./activepieces_db');

async function query() {
  const db = new ActivepiecesDB();
  await db.connect();
  
  const results = await db.searchPieces('email');
  console.log(results);
  
  await db.close();
}

query();
```

### Custom Database Path

```javascript
const db = new ActivepiecesDB('/custom/path/to/activepieces-pieces.db');
await db.connect();
```

### Complete Example

```javascript
const ActivepiecesDB = require('./activepieces_db');

async function findEmailIntegration() {
  const db = new ActivepiecesDB();
  await db.connect();
  
  try {
    // Search for email pieces
    console.log('=== Email Integrations ===');
    const pieces = await db.searchPieces('email', 5);
    
    for (const piece of pieces) {
      console.log(`\n${piece.display_name}`);
      console.log(`  Auth: ${piece.auth_type}`);
      console.log(`  Actions: ${piece.action_count}`);
      console.log(`  Triggers: ${piece.trigger_count}`);
    }
    
    // Get Gmail details
    console.log('\n=== Gmail Details ===');
    const gmail = await db.getPieceDetails('gmail');
    
    if (gmail) {
      console.log(`Name: ${gmail.display_name}`);
      console.log(`Actions: ${gmail.actions.length}`);
      
      console.log('\nAvailable actions:');
      for (const action of gmail.actions) {
        console.log(`  • ${action.display_name}`);
      }
    }
    
    // Get send_email inputs
    console.log('\n=== Gmail Send Email Inputs ===');
    const inputs = await db.getActionInputs('gmail', 'send_email');
    
    const required = inputs.filter(i => i.required);
    const optional = inputs.filter(i => !i.required);
    
    console.log('Required fields:');
    for (const field of required) {
      console.log(`  • ${field.display_name} (${field.type})`);
    }
    
    console.log('\nOptional fields:');
    for (const field of optional.slice(0, 5)) {  // Show first 5
      console.log(`  • ${field.display_name} (${field.type})`);
    }
    
  } finally {
    await db.close();
  }
}

findEmailIntegration().catch(console.error);
```

---

## 💾 Direct SQL Usage

### Python

```python
import sqlite3

conn = sqlite3.connect('activepieces-pieces.db')
conn.row_factory = sqlite3.Row  # Return dicts
cursor = conn.cursor()

# Simple query
cursor.execute('SELECT display_name, action_count FROM pieces_with_capabilities LIMIT 10')
for row in cursor.fetchall():
    print(f"{row['display_name']}: {row['action_count']} actions")

conn.close()
```

### Node.js

```javascript
const sqlite3 = require('sqlite3');
const { open } = require('sqlite');

async function query() {
  const db = await open({
    filename: './activepieces-pieces.db',
    driver: sqlite3.Database
  });

  const rows = await db.all(`
    SELECT display_name, action_count 
    FROM pieces_with_capabilities 
    LIMIT 10
  `);

  for (const row of rows) {
    console.log(`${row.display_name}: ${row.action_count} actions`);
  }

  await db.close();
}

query();
```

---

## 🔍 Common Queries

### 1. Search for Pieces

```python
# Search by keyword
pieces = db.search_pieces('email')

# Multiple terms (OR)
pieces = db.search_pieces('slack OR discord OR teams')

# Multiple terms (AND)
pieces = db.search_pieces('email AND automation')
```

### 2. Search for Actions

```python
# Find "send email" actions
actions = db.search_actions('send email')

# Find "create task" actions
actions = db.search_actions('create task')

# Find API actions
actions = db.search_actions('api call')
```

### 3. Get Piece Details

```python
# Get full piece information
gmail = db.get_piece_details('gmail')

print(gmail['display_name'])      # Gmail
print(gmail['auth_type'])          # OAuth2
print(len(gmail['actions']))       # 5
print(len(gmail['triggers']))      # 2
print(gmail['actions'][0]['name']) # get_email
```

### 4. Get Action Inputs

```python
# Get all inputs for an action
inputs = db.get_action_inputs('gmail', 'send_email')

for inp in inputs:
    print(f"{inp['display_name']}: {inp['type']}")
    if inp['required']:
        print("  (Required)")
    if inp['description']:
        print(f"  {inp['description']}")
```

### 5. Get Top Pieces

```python
# Most capable pieces
top = db.get_top_pieces(limit=20)

for piece in top:
    total = piece['action_count'] + piece['trigger_count']
    print(f"{piece['display_name']}: {total} capabilities")
```

### 6. Get All Pieces

```python
# Get all pieces
all_pieces = db.get_all_pieces()

print(f"Total pieces: {len(all_pieces)}")

for piece in all_pieces[:10]:  # First 10
    print(f"{piece['display_name']}: {piece['action_count']} actions")
```

### 7. Filter by Auth Type

```python
# Get OAuth2 pieces
oauth_pieces = db.get_pieces_by_auth_type('OAuth2')

print(f"OAuth2 pieces: {len(oauth_pieces)}")

for piece in oauth_pieces[:10]:
    print(piece['display_name'])
```

---

## 🎯 Real-World Examples

### Example 1: Build a Flow Recommendation System

```python
from activepieces_db import ActivepiecesDB

class FlowRecommender:
    def __init__(self):
        self.db = ActivepiecesDB()
    
    def recommend_flow(self, user_intent):
        """Recommend a flow based on user intent."""
        
        with self.db as db:
            # Parse intent
            if 'email' in user_intent.lower():
                actions = db.search_actions('send email', limit=5)
                
                print("I can help you send emails using:")
                for action in actions:
                    piece = action['piece_display_name']
                    action_name = action['action_display_name']
                    print(f"  • {piece}: {action_name}")
                
                # Get inputs for first option
                first = actions[0]
                inputs = db.get_action_inputs(
                    first['piece_name'],
                    first['action_name']
                )
                
                print(f"\nTo use {first['piece_display_name']}, you'll need:")
                for inp in inputs:
                    if inp['required']:
                        print(f"  • {inp['display_name']}")
                
                return actions[0]

recommender = FlowRecommender()
recommender.recommend_flow("I want to send an email")
```

### Example 2: Integration Discovery Tool

```javascript
const ActivepiecesDB = require('./activepieces_db');

class IntegrationExplorer {
  constructor() {
    this.db = new ActivepiecesDB();
  }
  
  async explore(category) {
    await this.db.connect();
    
    try {
      // Search for pieces
      const pieces = await this.db.searchPieces(category, 10);
      
      console.log(`Found ${pieces.length} integrations for "${category}":\n`);
      
      for (const piece of pieces) {
        console.log(`${piece.display_name}`);
        console.log(`  ${piece.description || 'No description'}`);
        console.log(`  ${piece.action_count} actions, ${piece.trigger_count} triggers`);
        console.log(`  Auth: ${piece.auth_type || 'None'}\n`);
      }
      
      return pieces;
    } finally {
      await this.db.close();
    }
  }
}

const explorer = new IntegrationExplorer();
explorer.explore('email').catch(console.error);
```

### Example 3: Dynamic Form Generator

```python
from activepieces_db import ActivepiecesDB

class ActionFormGenerator:
    def __init__(self):
        self.db = ActivepiecesDB()
    
    def generate_form(self, piece_name, action_name):
        """Generate a form schema for an action."""
        
        with self.db as db:
            inputs = db.get_action_inputs(piece_name, action_name)
            
            form_schema = {
                'piece': piece_name,
                'action': action_name,
                'fields': []
            }
            
            for inp in inputs:
                field = {
                    'name': inp['name'],
                    'label': inp['display_name'],
                    'type': inp['type'],
                    'required': bool(inp['required']),
                    'description': inp['description'],
                    'default': inp['default_value']
                }
                form_schema['fields'].append(field)
            
            return form_schema

generator = ActionFormGenerator()
form = generator.generate_form('gmail', 'send_email')

print(f"Form for: {form['piece']} - {form['action']}")
print(f"Fields: {len(form['fields'])}")

for field in form['fields']:
    print(f"\n{field['label']}")
    print(f"  Type: {field['type']}")
    print(f"  Required: {field['required']}")
```

---

## 📊 Advanced Queries

### Get Statistics

```python
with ActivepiecesDB() as db:
    pieces = db.get_all_pieces()
    
    total_pieces = len(pieces)
    total_actions = sum(p['action_count'] for p in pieces)
    total_triggers = sum(p['trigger_count'] for p in pieces)
    
    oauth_pieces = db.get_pieces_by_auth_type('OAuth2')
    
    print(f"Total pieces: {total_pieces}")
    print(f"Total actions: {total_actions}")
    print(f"Total triggers: {total_triggers}")
    print(f"OAuth2 pieces: {len(oauth_pieces)}")
```

### Complex Search

```python
import sqlite3

conn = sqlite3.connect('activepieces-pieces.db')
conn.row_factory = sqlite3.Row

# Find pieces with both actions AND triggers
cursor = conn.execute("""
    SELECT display_name, action_count, trigger_count
    FROM pieces_with_capabilities
    WHERE has_actions = 1 AND has_triggers = 1
    ORDER BY (action_count + trigger_count) DESC
    LIMIT 10
""")

print("Pieces with both actions and triggers:")
for row in cursor.fetchall():
    print(f"  {row['display_name']}: {row['action_count']} actions, {row['trigger_count']} triggers")

conn.close()
```

---

## 🚨 Error Handling

### Python

```python
from activepieces_db import ActivepiecesDB

try:
    with ActivepiecesDB('/path/to/db') as db:
        results = db.search_pieces('email')
except FileNotFoundError:
    print("Database file not found!")
except Exception as e:
    print(f"Error: {e}")
```

### Node.js

```javascript
const ActivepiecesDB = require('./activepieces_db');

async function query() {
  let db;
  
  try {
    db = new ActivepiecesDB();
    await db.connect();
    
    const results = await db.searchPieces('email');
    console.log(results);
    
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    if (db) {
      await db.close();
    }
  }
}
```

---

## 💡 Tips

1. **Always use context managers (Python)** or properly close connections (Node.js)
2. **Use search methods first** - They're fuzzy and more forgiving
3. **Piece names are lowercase** - Use 'gmail', not 'Gmail'
4. **Check required fields** - Not all inputs are mandatory
5. **Parse JSON fields** - categories, authors, metadata need parsing

---

## 📝 Quick Reference

### Python Methods

```python
db.search_pieces(query, limit=10)
db.search_actions(query, limit=10)
db.get_piece_details(piece_name)
db.get_action_inputs(piece_name, action_name)
db.get_top_pieces(limit=20)
db.get_all_pieces()
db.get_pieces_by_auth_type(auth_type)
```

### Node.js Methods

```javascript
await db.searchPieces(query, limit=10)
await db.searchActions(query, limit=10)
await db.getPieceDetails(pieceName)
await db.getActionInputs(pieceName, actionName)
await db.getTopPieces(limit=20)
await db.getAllPieces()
await db.getPiecesByAuthType(authType)
```

---

## ✅ Ready to Use!

You now have everything you need to use the Activepieces database in your project. Check:

- `README.md` for overview
- `CONTEXT.md` for AI agent integration
- `sample-queries-sqlite.sql` for SQL examples

**Happy coding! 🚀**

