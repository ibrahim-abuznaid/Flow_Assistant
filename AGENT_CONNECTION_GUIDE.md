# Agent Connection Guide - Activepieces Pieces Database

This guide explains how to connect an AI agent or application to your Activepieces pieces PostgreSQL database.

## Database Connection Details

**Host:** `localhost` (or `127.0.0.1`)  
**Port:** `5433` (⚠️ Not the default 5432!)  
**Database Name:** `activepieces_pieces`  
**Username:** `postgres`  
**Password:** `7777`  

### Connection String Format

```
postgresql://postgres:7777@localhost:5433/activepieces_pieces
```

Or for some libraries:
```
postgres://postgres:7777@localhost:5433/activepieces_pieces
```

---

## Database Schema Overview

### Tables Structure

```
pieces
├── id (PRIMARY KEY)
├── name (UNIQUE)
├── display_name
├── description
├── logo_url
├── version
├── minimum_supported_release
├── auth_type
├── categories (ARRAY)
├── authors (ARRAY)
├── created_at
├── updated_at
└── metadata (JSONB)

actions
├── id (PRIMARY KEY)
├── piece_id (FOREIGN KEY → pieces.id)
├── name
├── display_name
├── description
├── requires_auth
├── created_at
├── updated_at
└── metadata (JSONB)

triggers
├── id (PRIMARY KEY)
├── piece_id (FOREIGN KEY → pieces.id)
├── name
├── display_name
├── description
├── trigger_type
├── requires_auth
├── created_at
├── updated_at
└── metadata (JSONB)

action_properties
├── id (PRIMARY KEY)
├── action_id (FOREIGN KEY → actions.id)
├── property_name
├── display_name
├── description
├── property_type
├── required
├── default_value
├── created_at
├── updated_at
└── metadata (JSONB)

trigger_properties
├── id (PRIMARY KEY)
├── trigger_id (FOREIGN KEY → triggers.id)
├── property_name
├── display_name
├── description
├── property_type
├── required
├── default_value
├── created_at
├── updated_at
└── metadata (JSONB)

property_options
├── id (PRIMARY KEY)
├── property_id
├── property_type ('action' or 'trigger')
├── option_label
├── option_value
└── created_at
```

### Useful Views

**piece_statistics** - Quick stats per piece:
- id, name, display_name
- action_count, trigger_count
- total_action_properties, total_trigger_properties

**pieces_with_capabilities** - Complete piece info with all actions and triggers as JSON

---

## Connection Examples by Language

### 1. Python (Using psycopg2)

```python
import psycopg2
import json

# Connect to database
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="activepieces_pieces",
    user="postgres",
    password="7777"
)

# Create cursor
cur = conn.cursor()

# Example query: Search for pieces
cur.execute("""
    SELECT display_name, description, categories 
    FROM pieces 
    WHERE display_name ILIKE %s
    LIMIT 10
""", ('%slack%',))

results = cur.fetchall()
for row in results:
    print(f"Piece: {row[0]}, Description: {row[1]}")

# Close connections
cur.close()
conn.close()
```

Install: `pip install psycopg2-binary`

### 2. Python (Using SQLAlchemy - Better for ORMs)

```python
from sqlalchemy import create_engine, text
import pandas as pd

# Create engine
engine = create_engine('postgresql://postgres:7777@localhost:5433/activepieces_pieces')

# Query as DataFrame
query = """
    SELECT p.display_name, a.display_name as action_name 
    FROM pieces p 
    JOIN actions a ON p.id = a.piece_id 
    WHERE p.name = 'slack'
"""
df = pd.read_sql(query, engine)
print(df)

# Or use with context manager
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM pieces"))
    print(f"Total pieces: {result.scalar()}")
```

Install: `pip install sqlalchemy psycopg2-binary pandas`

### 3. Node.js/TypeScript (Using pg)

```javascript
const { Pool } = require('pg');

// Create connection pool
const pool = new Pool({
  host: 'localhost',
  port: 5433,
  database: 'activepieces_pieces',
  user: 'postgres',
  password: '7777',
});

// Query example
async function searchPieces(keyword) {
  try {
    const result = await pool.query(
      'SELECT display_name, description FROM pieces WHERE display_name ILIKE $1',
      [`%${keyword}%`]
    );
    return result.rows;
  } catch (err) {
    console.error('Error:', err);
  }
}

// Use it
searchPieces('email').then(pieces => {
  console.log(pieces);
});

// Clean up
// pool.end();
```

Install: `npm install pg`

### 4. Node.js with TypeORM (Type-safe)

```typescript
import { DataSource } from 'typeorm';

const AppDataSource = new DataSource({
  type: 'postgres',
  host: 'localhost',
  port: 5433,
  username: 'postgres',
  password: '7777',
  database: 'activepieces_pieces',
  entities: [],
  synchronize: false,
});

// Initialize
await AppDataSource.initialize();

// Query
const pieces = await AppDataSource.query(
  'SELECT * FROM pieces WHERE name = $1',
  ['slack']
);

console.log(pieces);
```

Install: `npm install typeorm pg`

### 5. C# (.NET)

```csharp
using Npgsql;

string connString = "Host=localhost;Port=5433;Username=postgres;Password=7777;Database=activepieces_pieces";

await using var conn = new NpgsqlConnection(connString);
await conn.OpenAsync();

await using var cmd = new NpgsqlCommand("SELECT display_name, description FROM pieces LIMIT 10", conn);
await using var reader = await cmd.ExecuteReaderAsync();

while (await reader.ReadAsync())
{
    Console.WriteLine($"{reader.GetString(0)}: {reader.GetString(1)}");
}
```

Install: `dotnet add package Npgsql`

### 6. Java (JDBC)

```java
import java.sql.*;

String url = "jdbc:postgresql://localhost:5433/activepieces_pieces";
String user = "postgres";
String password = "7777";

try (Connection conn = DriverManager.getConnection(url, user, password)) {
    String query = "SELECT display_name, description FROM pieces LIMIT 10";
    Statement st = conn.createStatement();
    ResultSet rs = st.executeQuery(query);
    
    while (rs.next()) {
        System.out.println(rs.getString("display_name") + ": " + rs.getString("description"));
    }
} catch (SQLException e) {
    e.printStackTrace();
}
```

Maven dependency:
```xml
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.6.0</version>
</dependency>
```

---

## Common Queries for AI Agents

### 1. Search for pieces by keyword

```sql
SELECT 
    p.id,
    p.name,
    p.display_name,
    p.description,
    p.categories,
    (SELECT COUNT(*) FROM actions WHERE piece_id = p.id) as action_count,
    (SELECT COUNT(*) FROM triggers WHERE piece_id = p.id) as trigger_count
FROM pieces p
WHERE 
    p.display_name ILIKE '%{keyword}%' 
    OR p.description ILIKE '%{keyword}%'
ORDER BY p.display_name;
```

### 2. Get all actions for a piece

```sql
SELECT 
    a.name,
    a.display_name,
    a.description,
    a.requires_auth
FROM actions a
JOIN pieces p ON a.piece_id = p.id
WHERE p.name = '{piece_name}'
ORDER BY a.display_name;
```

### 3. Get action details with properties

```sql
SELECT 
    p.display_name as piece_name,
    a.display_name as action_name,
    a.description as action_description,
    json_agg(
        json_build_object(
            'property', ap.property_name,
            'display_name', ap.display_name,
            'type', ap.property_type,
            'required', ap.required,
            'description', ap.description
        )
    ) as properties
FROM pieces p
JOIN actions a ON p.id = a.piece_id
LEFT JOIN action_properties ap ON a.id = ap.action_id
WHERE p.name = '{piece_name}' AND a.name = '{action_name}'
GROUP BY p.display_name, a.display_name, a.description;
```

### 4. Search for specific functionality

```sql
-- Find all pieces that can send emails
SELECT DISTINCT
    p.display_name,
    a.display_name as action_name,
    a.description
FROM pieces p
JOIN actions a ON p.id = a.piece_id
WHERE 
    a.display_name ILIKE '%send%email%'
    OR a.description ILIKE '%send%email%'
ORDER BY p.display_name;
```

### 5. Get pieces by category

```sql
SELECT 
    display_name,
    description,
    categories
FROM pieces
WHERE '{category}' = ANY(categories)
ORDER BY display_name;
```

Common categories: `COMMUNICATION`, `PRODUCTIVITY`, `MARKETING`, `DEVELOPER_TOOLS`, etc.

---

## Building an AI Agent

### Example: Simple Question-Answering Agent (Python)

```python
import psycopg2
from psycopg2.extras import RealDictCursor

class ActivepiecesAgent:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="activepieces_pieces",
            user="postgres",
            password="7777",
            cursor_factory=RealDictCursor
        )
    
    def search_pieces(self, keyword):
        """Search for pieces by keyword"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT display_name, description, categories
                FROM pieces
                WHERE display_name ILIKE %s OR description ILIKE %s
                LIMIT 10
            """, (f'%{keyword}%', f'%{keyword}%'))
            return cur.fetchall()
    
    def get_piece_actions(self, piece_name):
        """Get all actions for a piece"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT a.display_name, a.description
                FROM actions a
                JOIN pieces p ON a.piece_id = p.id
                WHERE p.name = %s
                ORDER BY a.display_name
            """, (piece_name,))
            return cur.fetchall()
    
    def search_actions(self, keyword):
        """Search for actions by functionality"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    p.display_name as piece,
                    a.display_name as action,
                    a.description
                FROM pieces p
                JOIN actions a ON p.id = a.piece_id
                WHERE 
                    a.display_name ILIKE %s 
                    OR a.description ILIKE %s
                ORDER BY p.display_name
            """, (f'%{keyword}%', f'%{keyword}%'))
            return cur.fetchall()
    
    def get_action_details(self, piece_name, action_name):
        """Get detailed information about an action including properties"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    a.display_name,
                    a.description,
                    json_agg(
                        json_build_object(
                            'name', ap.property_name,
                            'display_name', ap.display_name,
                            'type', ap.property_type,
                            'required', ap.required,
                            'description', ap.description
                        )
                    ) FILTER (WHERE ap.id IS NOT NULL) as properties
                FROM actions a
                JOIN pieces p ON a.piece_id = p.id
                LEFT JOIN action_properties ap ON a.id = ap.action_id
                WHERE p.name = %s AND a.name = %s
                GROUP BY a.display_name, a.description
            """, (piece_name, action_name))
            return cur.fetchone()
    
    def close(self):
        self.conn.close()

# Usage
agent = ActivepiecesAgent()

# Search for email-related pieces
results = agent.search_pieces("email")
for piece in results:
    print(f"{piece['display_name']}: {piece['description']}")

# Get Slack actions
actions = agent.get_piece_actions("slack")
for action in actions:
    print(f"- {action['display_name']}")

# Search for send email actions
send_email_actions = agent.search_actions("send email")
for result in send_email_actions:
    print(f"{result['piece']} - {result['action']}")

agent.close()
```

### Example: LangChain Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="activepieces_pieces",
    user="postgres",
    password="7777",
    cursor_factory=RealDictCursor
)

def search_pieces_tool(query: str) -> str:
    """Search for Activepieces pieces by keyword"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT display_name, description 
            FROM pieces 
            WHERE display_name ILIKE %s OR description ILIKE %s 
            LIMIT 5
        """, (f'%{query}%', f'%{query}%'))
        results = cur.fetchall()
        return "\n".join([f"- {r['display_name']}: {r['description']}" for r in results])

def search_actions_tool(query: str) -> str:
    """Search for Activepieces actions by functionality"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT p.display_name as piece, a.display_name as action, a.description
            FROM pieces p
            JOIN actions a ON p.id = a.piece_id
            WHERE a.display_name ILIKE %s OR a.description ILIKE %s
            LIMIT 5
        """, (f'%{query}%', f'%{query}%'))
        results = cur.fetchall()
        return "\n".join([f"- {r['piece']}: {r['action']} - {r['description']}" for r in results])

# Create tools
tools = [
    Tool(
        name="Search Pieces",
        func=search_pieces_tool,
        description="Search for Activepieces integrations/pieces by keyword. Input should be a search term."
    ),
    Tool(
        name="Search Actions",
        func=search_actions_tool,
        description="Search for specific actions/functionality. Input should be what you want to do (e.g., 'send email')."
    )
]

# Initialize agent
llm = OpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Use the agent
response = agent.run("What pieces can I use to send emails?")
print(response)
```

---

## Security Considerations

### For Production Use:

1. **Change the default password:**
   ```sql
   ALTER USER postgres WITH PASSWORD 'your_secure_password';
   ```

2. **Create a dedicated read-only user:**
   ```sql
   CREATE USER agent_user WITH PASSWORD 'secure_password';
   GRANT CONNECT ON DATABASE activepieces_pieces TO agent_user;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO agent_user;
   ```

3. **Use environment variables:**
   ```python
   import os
   
   DB_CONFIG = {
       'host': os.getenv('DB_HOST', 'localhost'),
       'port': int(os.getenv('DB_PORT', 5433)),
       'database': os.getenv('DB_NAME', 'activepieces_pieces'),
       'user': os.getenv('DB_USER', 'postgres'),
       'password': os.getenv('DB_PASSWORD'),
   }
   ```

4. **Use connection pooling** for better performance
5. **Implement rate limiting** if exposing via API
6. **Use SSL/TLS** for production connections

---

## Testing Your Connection

### Quick Connection Test (Python)

```python
import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5433,
        database="activepieces_pieces",
        user="postgres",
        password="7777"
    )
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM pieces")
    count = cur.fetchone()[0]
    print(f"✓ Connected successfully! Found {count} pieces in database.")
    cur.close()
    conn.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

### Quick Connection Test (Node.js)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'localhost',
  port: 5433,
  database: 'activepieces_pieces',
  user: 'postgres',
  password: '7777',
});

pool.query('SELECT COUNT(*) FROM pieces', (err, res) => {
  if (err) {
    console.log('✗ Connection failed:', err);
  } else {
    console.log(`✓ Connected successfully! Found ${res.rows[0].count} pieces in database.`);
  }
  pool.end();
});
```

---

## Troubleshooting

### Common Issues:

1. **Connection refused:**
   - Check that PostgreSQL service is running
   - Verify you're using port **5433** (not 5432)
   - Check firewall settings

2. **Authentication failed:**
   - Verify password is correct (7777)
   - Check pg_hba.conf allows connections

3. **Database does not exist:**
   - Ensure database was created successfully
   - Check connection string

4. **Tables not found:**
   - Verify schema was initialized
   - Check you're connected to the right database

### Check PostgreSQL Status:

```powershell
# Windows PowerShell
Get-Service postgresql-x64-18

# Restart if needed
Restart-Service postgresql-x64-18
```

---

## Additional Resources

- Full schema: `tools/pieces-db/schema.sql`
- Sample queries: `tools/pieces-db/sample-queries.sql`
- PostgreSQL documentation: https://www.postgresql.org/docs/
- psycopg2 documentation: https://www.psycopg.org/docs/
- node-postgres documentation: https://node-postgres.com/

---

**Need help?** Check the README.md or QUICKSTART.md in the `tools/pieces-db/` directory.

