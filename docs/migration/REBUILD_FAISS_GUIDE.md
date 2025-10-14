# FAISS Vector Database Rebuild Guide

## Overview

The FAISS vector database stores embeddings of all ActivePieces pieces, actions, and triggers for semantic search. This guide explains how to rebuild the index from your PostgreSQL database with **COMPLETE INFORMATION** including all input properties.

## When to Rebuild

Rebuild the FAISS index when:
- Your PostgreSQL database has been updated with new pieces, actions, or triggers
- You want to ensure the vector search uses the latest data
- The index becomes corrupted or outdated

## Rebuild Versions

### Enhanced Version (RECOMMENDED) ⭐

Includes **ALL** input properties with full details:
```bash
python rebuild_faiss_enhanced.py
```

**Includes:**
- All pieces, actions, and triggers
- **ALL input properties (9,664 action props + 454 trigger props)**
- Property types (text, dropdown, file, etc.)
- Required vs optional indicators
- Property descriptions
- Dropdown options
- Default values

**Best for:** Complete agent responses with full configuration details

### Simple Version

Basic information only (faster, less detailed):
```bash
python rebuild_faiss_simple.py
```

**Includes:**
- Pieces, actions, and triggers
- Basic descriptions
- No property details

**Best for:** Quick lookups without configuration details

## Prerequisites

1. PostgreSQL database must be running and accessible
2. Database connection configured in `db_config.py` (or environment variables)
3. OpenAI API key set in `.env` file as `OPENAI_API_KEY`
4. Required Python packages installed (see `requirements.txt`)

### What Happens

1. **Connects to PostgreSQL** - Fetches all pieces, actions, and triggers
2. **Creates Documents** - Converts database records into text documents
3. **Generates Embeddings** - Uses OpenAI API to create vector embeddings
4. **Builds FAISS Index** - Creates optimized vector search index
5. **Saves to Disk** - Stores index files in `ap_faiss_index/`

### Output Files

- `ap_faiss_index/index.faiss` - FAISS vector index
- `ap_faiss_index/index.pkl` - Document metadata and mappings

### Database Stats (Last Enhanced Rebuild)

- **Pieces**: 433
- **Actions**: 2,678 (with 9,664 input properties)
- **Triggers**: 694 (with 454 configuration properties)
- **Total Properties**: 10,118 (fully detailed)
- **Total Documents**: 3,805
- **Embedding Dimension**: 1,536

**Example of Enhanced Data:**
```
Action: Upload File
Piece: Backblaze
Description: Upload a File to bucket.
Requires Authentication: True

INPUT PROPERTIES:
  - ACL (StaticDropdown, Optional)
  - File (File, Required)
  - File Name (ShortText, Optional)
    Description: my-file-name (no extension)
  - Type (StaticDropdown, Required)
```

### Troubleshooting

**Error: "OPENAI_API_KEY environment variable not set"**
- Solution: Create a `.env` file with `OPENAI_API_KEY=your-key-here`

**Error: "Could not connect to database"**
- Solution: Check PostgreSQL is running and `db_config.py` has correct credentials
- Check environment variables: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`

**Error: "TypeError: Client.__init__() got an unexpected keyword argument 'proxies'"**
- Solution: This is fixed with a monkey patch in the script for Python 3.14 compatibility

### Cost Estimate

Using OpenAI's text-embedding-ada-002 model:
- ~3,805 documents = ~$0.15 per rebuild (approximate)
- Pricing: $0.0001 per 1,000 tokens

### Alternative: Original JSON-Based Rebuild

If you still have the JSON file, you can use:
```bash
python prepare_knowledge_base.py
```

This uses `pieces_knowledge_base.json` instead of PostgreSQL.

## Notes

- The rebuild process takes a few minutes depending on document count
- Internet connection required for OpenAI API calls
- Existing index is overwritten
- The assistant must be restarted after rebuild to use new index

