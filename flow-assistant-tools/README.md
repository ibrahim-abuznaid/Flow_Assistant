# Flow Assistant Tools

A comprehensive toolkit for fetching and working with Activepieces pieces, actions, and triggers data. These tools help you build context for AI assistants and flow builders.

## 📋 Table of Contents

- [Setup](#setup)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Usage Examples](#usage-examples)
- [API Client](#api-client)
- [Use Cases](#use-cases)

## 🚀 Setup

### Prerequisites

- Python 3.7+
- `requests` library
- Running Activepieces instance

### Installation

```bash
# Install required dependencies
pip install requests

# Update config.json with your Activepieces API URL
# Default is http://localhost:80
```

## ⚙️ Configuration

Edit `config.json` to configure the API connection:

```json
{
  "api_base_url": "http://localhost:80",
  "api_version": "v1",
  "default_locale": "en",
  "default_edition": "COMMUNITY"
}
```

## 🛠️ Available Tools

### 1. **get_all_pieces.py** - List All Pieces

Lists all available pieces with optional filtering and sorting.

```bash
# Get all pieces (summary)
python get_all_pieces.py --summary

# Search for specific pieces
python get_all_pieces.py --search "slack" --summary

# Filter by suggestion type
python get_all_pieces.py --suggestion-type ACTION --summary

# Save full data to JSON
python get_all_pieces.py --output pieces.json

# Sort by popularity
python get_all_pieces.py --sort-by POPULARITY --order-by DESC --summary
```

**Options:**
- `--search` - Search query to filter pieces
- `--include-hidden` - Include hidden pieces
- `--include-tags` - Include piece tags
- `--suggestion-type` - Filter by ACTION, TRIGGER, or ACTION_AND_TRIGGER
- `--sort-by` - Sort by NAME, UPDATED, CREATED, POPULARITY
- `--order-by` - ASC or DESC
- `--output` - Save to JSON file
- `--summary` - Show summary only (names and counts)

---

### 2. **get_piece_details.py** - Get Detailed Piece Info

Retrieves complete information about a specific piece including all actions and triggers.

```bash
# Get piece details
python get_piece_details.py "@activepieces/piece-slack"

# Get verbose output with all properties
python get_piece_details.py "@activepieces/piece-slack" --verbose

# Get specific version
python get_piece_details.py "@activepieces/piece-slack" --version "0.5.0"

# Save to JSON
python get_piece_details.py "@activepieces/piece-slack" --output slack.json

# Get raw JSON only
python get_piece_details.py "@activepieces/piece-slack" --json-only
```

**Options:**
- `piece_name` - (Required) Piece name
- `--version` - Specific piece version
- `--verbose` - Show all properties and details
- `--json-only` - Output raw JSON only
- `--output` - Save to JSON file

---

### 3. **get_piece_actions.py** - Get Piece Actions

Lists all actions for a specific piece with their properties.

```bash
# Get all actions for a piece
python get_piece_actions.py "@activepieces/piece-slack"

# Show properties for each action
python get_piece_actions.py "@activepieces/piece-slack" --show-properties

# Get specific action only
python get_piece_actions.py "@activepieces/piece-slack" --action-name send_message_action

# Save to JSON
python get_piece_actions.py "@activepieces/piece-slack" --output slack_actions.json
```

**Options:**
- `piece_name` - (Required) Piece name
- `--show-properties` - Show all properties for each action
- `--action-name` - Filter to specific action
- `--json-only` - Output raw JSON only
- `--output` - Save to JSON file

---

### 4. **get_piece_triggers.py** - Get Piece Triggers

Lists all triggers for a specific piece with their properties.

```bash
# Get all triggers for a piece
python get_piece_triggers.py "@activepieces/piece-slack"

# Show properties for each trigger
python get_piece_triggers.py "@activepieces/piece-slack" --show-properties

# Get specific trigger only
python get_piece_triggers.py "@activepieces/piece-slack" --trigger-name new_message

# Save to JSON
python get_piece_triggers.py "@activepieces/piece-slack" --output slack_triggers.json
```

**Options:**
- `piece_name` - (Required) Piece name
- `--show-properties` - Show all properties for each trigger
- `--trigger-name` - Filter to specific trigger
- `--json-only` - Output raw JSON only
- `--output` - Save to JSON file

---

### 5. **search_pieces.py** - Search Pieces

Search for pieces by query with smart ranking.

```bash
# Search for pieces
python search_pieces.py "email"

# Search with ranking
python search_pieces.py "email" --rank

# Limit results
python search_pieces.py "database" --rank --limit 5

# Filter by type
python search_pieces.py "notification" --suggestion-type ACTION

# Save results
python search_pieces.py "email" --rank --output email_pieces.json
```

**Options:**
- `query` - (Required) Search query
- `--rank` - Rank results by relevance (client-side)
- `--suggestion-type` - Filter by ACTION, TRIGGER, or ACTION_AND_TRIGGER
- `--limit` - Limit number of results
- `--json-only` - Output raw JSON only
- `--output` - Save to JSON file

---

### 6. **get_piece_categories.py** - Get Available Categories

Lists all available piece categories.

```bash
# Get all categories
python get_piece_categories.py

# Show pieces in each category
python get_piece_categories.py --with-pieces

# Save to JSON
python get_piece_categories.py --with-pieces --output categories.json
```

**Options:**
- `--with-pieces` - Show pieces in each category
- `--output` - Save to JSON file

---

### 7. **format_for_llm.py** - Format for LLM Context

Formats pieces data into optimized format for LLM assistants.

```bash
# Format all pieces for LLM (full format)
python format_for_llm.py --output pieces_context.md

# Compact format (smaller context)
python format_for_llm.py --format compact --output pieces_compact.md

# Verbose format with all properties
python format_for_llm.py --format full --verbose --output pieces_full.md

# Filter by search
python format_for_llm.py --search "google" --format compact --output google_pieces.md

# Filter by categories
python format_for_llm.py --categories "COMMUNICATION" "PRODUCTIVITY" --output filtered.md

# Filter by suggestion type
python format_for_llm.py --suggestion-type ACTION --format compact --output actions_only.md
```

**Options:**
- `--output` - (Required) Output file path
- `--format` - Format: full, compact, or json
- `--verbose` - Include all properties (full format only)
- `--search` - Filter pieces by search query
- `--categories` - Filter by categories
- `--suggestion-type` - Filter by ACTION, TRIGGER, or ACTION_AND_TRIGGER

---

### 8. **export_pieces_database.py** - Export Complete Database

Exports all pieces data to various formats.

```bash
# Export to JSON
python export_pieces_database.py --format json --output pieces_db.json

# Export to CSV (pieces)
python export_pieces_database.py --format csv --output pieces.csv

# Export actions to CSV
python export_pieces_database.py --format csv-actions --output actions.csv

# Export triggers to CSV
python export_pieces_database.py --format csv-triggers --output triggers.csv

# Export to SQLite database
python export_pieces_database.py --format sqlite --output pieces.db

# Export all formats
python export_pieces_database.py --format all --output pieces_export

# Include hidden pieces
python export_pieces_database.py --format all --output full_export --include-hidden
```

**Options:**
- `--format` - Export format: json, csv, csv-actions, csv-triggers, sqlite, all
- `--output` - Output file/directory path
- `--include-hidden` - Include hidden pieces

---

## 📚 Usage Examples

### Example 1: Building LLM Context for Flow Assistant

```bash
# 1. Export all pieces in compact format for initial context
python format_for_llm.py --format compact --output assistant_context.md

# 2. Export detailed info for popular categories
python format_for_llm.py --categories "COMMUNICATION" "PRODUCTIVITY" "DEVELOPER_TOOLS" \
  --format full --verbose --output detailed_context.md

# 3. Export JSON for programmatic access
python get_all_pieces.py --include-tags --output pieces_full.json
```

### Example 2: Analyzing Specific Integration

```bash
# Get complete Slack integration details
python get_piece_details.py "@activepieces/piece-slack" --verbose

# Get only actions
python get_piece_actions.py "@activepieces/piece-slack" --show-properties

# Get only triggers
python get_piece_triggers.py "@activepieces/piece-slack" --show-properties
```

### Example 3: Finding Integrations for User Query

```bash
# User asks: "How do I send emails?"
python search_pieces.py "email" --rank --suggestion-type ACTION

# User asks: "What triggers are available for Slack?"
python get_piece_triggers.py "@activepieces/piece-slack"
```

### Example 4: Building a Knowledge Base

```bash
# Export everything to SQLite for queries
python export_pieces_database.py --format sqlite --output knowledge_base.db

# Then query using SQL:
# sqlite3 knowledge_base.db
# SELECT * FROM actions WHERE description LIKE '%send%email%';
```

### Example 5: Generating Documentation

```bash
# Generate markdown documentation for all pieces
python format_for_llm.py --format full --verbose --output documentation.md

# Generate category-specific docs
python format_for_llm.py --categories "AI" "COMMUNICATION" \
  --format full --output ai_comm_docs.md
```

## 🔧 API Client

All tools use the `api_client.py` module which provides:

### ActivepiecesAPIClient

```python
from api_client import ActivepiecesAPIClient

# Initialize client
client = ActivepiecesAPIClient()

# List pieces
pieces = client.list_pieces(
    search_query="slack",
    suggestion_type="ACTION_AND_TRIGGER"
)

# Get piece details
piece = client.get_piece("@activepieces/piece-slack")

# Get categories
categories = client.get_piece_categories()

# Get versions
versions = client.get_piece_versions(
    name="@activepieces/piece-slack",
    release="0.30.0"
)
```

### Available Methods

- `list_pieces(...)` - List all pieces with filters
- `get_piece(name, version, locale)` - Get detailed piece info
- `get_piece_categories()` - Get all categories
- `get_piece_versions(name, release)` - Get available versions

## 💡 Use Cases

### For AI Flow Assistants

1. **Initial Context Loading:**
   ```bash
   python format_for_llm.py --format compact --output context.md
   ```
   Use the output as initial context for your AI assistant.

2. **Dynamic Query Handling:**
   ```python
   # When user asks about specific integration
   python search_pieces.py "user_query" --rank --limit 3
   ```

3. **Action/Trigger Lookup:**
   ```bash
   python get_piece_actions.py "@activepieces/piece-name" --json-only
   ```

### For Flow Builders

1. **Populate Piece Selector:**
   ```bash
   python get_all_pieces.py --suggestion-type ACTION --output actions.json
   ```

2. **Get Action Properties:**
   ```bash
   python get_piece_actions.py "piece_name" --action-name "action_name" --json-only
   ```

3. **Search Functionality:**
   ```bash
   python search_pieces.py "user_search" --rank
   ```

### For Documentation

1. **Generate Piece Docs:**
   ```bash
   python format_for_llm.py --format full --verbose --output docs.md
   ```

2. **Export to Database:**
   ```bash
   python export_pieces_database.py --format sqlite --output pieces.db
   ```

## 🔍 API Endpoints Reference

These tools interact with the following Activepieces API endpoints:

- `GET /v1/pieces` - List all pieces
- `GET /v1/pieces/{name}` - Get piece details
- `GET /v1/pieces/categories` - Get categories
- `GET /v1/pieces/versions` - Get piece versions

## 📝 Notes

- All tools require a running Activepieces instance
- The API endpoints are the same ones used by the Activepieces flow builder UI
- Data is fetched in real-time from your Activepieces instance
- Tools can work offline once data is exported to JSON/SQLite
- Default locale is English (en), but can be changed in config.json

## 🤝 Contributing

Feel free to extend these tools with additional functionality:
- Add more export formats
- Implement caching
- Add batch processing
- Create visualization tools

## 📄 License

These tools are part of the Activepieces project and follow the same license.

---

**Created for building Flow Assistants and automation tools with Activepieces**

