# Database Update Deployment Guide

## Overview

This guide explains how to deploy the new, more accurate database generated from the `flow-assistant-tools` scripts to your production server.

## What Changed

1. **New Database Source**: Database is now generated from the Activepieces API using `flow-assistant-tools/export_pieces_database.py`
2. **More Accurate Data**: Contains 450 pieces, 2890 actions, and 834 triggers
3. **Old Databases Backed Up**: Previous databases moved to `old_database/` folder
4. **FAISS Index**: Needs to be regenerated on the server

## Local Changes Summary

### Files Changed:
- ✅ `data/activepieces.db` - New database generated from API
- ✅ `flow-assistant-tools/export_pieces_database.py` - Updated schema to match proper SQLite structure
- ✅ `scripts/migration/prepare_vector_store_from_sqlite.py` - Fixed OpenAI embeddings initialization
- ✅ `old_database/` - Created folder with backup of old databases

### Files Backed Up:
- `old_database/activepieces_old.db` - Previous main database
- `old_database/activepieces-pieces_old.db` - Previous pieces database
- `old_database/ap_faiss_index_old/` - Previous FAISS vector index

## Deployment Steps

### Step 1: Commit and Push Changes

```bash
# From your local machine (Windows)
cd C:\AP_work\Flow_Assistant

# Add all changes
git add flow-assistant-tools/
git add old_database/
git add data/activepieces.db
git add scripts/migration/prepare_vector_store_from_sqlite.py

# Commit changes
git commit -m "Update database with more accurate API data from flow-assistant-tools"

# Push to GitHub
git push origin main
```

### Step 2: Pull Changes on Server

```bash
# SSH into your server
ssh root@your-server-ip

# Navigate to project directory
cd /var/www/Flow_Assistant

# Stop the services
sudo systemctl stop activepieces-backend
sudo systemctl stop activepieces-frontend

# Pull latest changes
git pull origin main

# Verify the new database
python3 -c "import sqlite3; conn = sqlite3.connect('data/activepieces.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM pieces'); print(f'Pieces: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM actions'); print(f'Actions: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM triggers'); print(f'Triggers: {cursor.fetchone()[0]}')"
```

Expected output:
```
Pieces: 450
Actions: 2890
Triggers: 834
```

### Step 3: Regenerate FAISS Vector Index on Server

The FAISS vector index needs to be regenerated from the new database:

```bash
# Make sure you're in the project directory
cd /var/www/Flow_Assistant

# Activate virtual environment (if using one)
source venv/bin/activate  # or however your venv is activated

# Run the vector store generation script
python3 scripts/migration/prepare_vector_store_from_sqlite.py
```

This will:
1. Load all pieces, actions, and triggers from the new database
2. Generate embeddings using OpenAI API (requires OPENAI_API_KEY in .env)
3. Create new FAISS index at `data/ap_faiss_index/`
4. Save index.faiss and index.pkl files

**Note**: This process may take 5-10 minutes as it generates embeddings for ~4,000 documents.

### Step 4: Verify Vector Store

```bash
# Check if vector store files exist
ls -lh data/ap_faiss_index/

# Should show:
# - index.faiss (FAISS index file)
# - index.pkl (document store and mappings)
```

### Step 5: Restart Services

```bash
# Restart backend service
sudo systemctl restart activepieces-backend

# Restart frontend service  
sudo systemctl restart activepieces-frontend

# Check status
sudo systemctl status activepieces-backend
sudo systemctl status activepieces-frontend
```

### Step 6: Test the System

```bash
# Check backend logs
sudo journalctl -u activepieces-backend -f

# Test the API (in another terminal)
curl http://localhost:8000/health

# Test database connection
curl http://localhost:8000/stats
```

Expected response should show:
```json
{
  "pieces": 450,
  "actions": 2890,
  "triggers": 834
}
```

## Troubleshooting

### Database Connection Issues

If you see database errors:

```bash
# Check database permissions
ls -lah data/activepieces.db

# Should be readable by the app user
sudo chown www-data:www-data data/activepieces.db  # Or appropriate user
```

### FAISS Index Generation Issues

If vector store generation fails:

```bash
# Check OpenAI API key
grep OPENAI_API_KEY .env

# Check Python dependencies
pip3 list | grep -E "langchain|openai|faiss"

# Required versions:
# - langchain>=0.3.15
# - langchain-openai>=0.2.14
# - openai>=1.50.0
# - faiss-cpu>=1.9.0
```

### Service Won't Start

```bash
# Check logs
sudo journalctl -u activepieces-backend -n 50 --no-pager

# Common issues:
# 1. Database file not found - check path in src/db_config.py
# 2. FAISS index not found - regenerate with prepare_vector_store_from_sqlite.py
# 3. Port already in use - check with: sudo lsof -i :8000
```

## Rollback Procedure

If you need to rollback to the old database:

```bash
# Stop services
sudo systemctl stop activepieces-backend

# Restore old database
cp old_database/activepieces_old.db data/activepieces.db

# Restore old FAISS index
rm -rf data/ap_faiss_index
cp -r old_database/ap_faiss_index_old data/ap_faiss_index

# Restart services
sudo systemctl restart activepieces-backend
```

## Generating Fresh Database from API

If you need to regenerate the database from the Activepieces API:

```bash
cd flow-assistant-tools

# Make sure config.json points to correct API URL
cat config.json

# Generate new database
python3 export_pieces_database.py --format sqlite --output ../data/activepieces

# This will:
# 1. Fetch all pieces from Activepieces API
# 2. Create SQLite database with proper schema
# 3. Include all actions, triggers, and metadata
# 4. Create FTS indexes for fast searching
```

## Verification Checklist

After deployment, verify:

- [ ] Database file exists: `data/activepieces.db`
- [ ] Database has correct data (450 pieces, 2890 actions, 834 triggers)
- [ ] FAISS index exists: `data/ap_faiss_index/index.faiss` and `index.pkl`
- [ ] Backend service running: `sudo systemctl status activepieces-backend`
- [ ] Frontend service running: `sudo systemctl status activepieces-frontend`
- [ ] API health check passes: `curl http://localhost:8000/health`
- [ ] Stats endpoint shows correct counts: `curl http://localhost:8000/stats`
- [ ] Frontend loads: `http://your-server-ip`
- [ ] Chat functionality works
- [ ] Database search works in chat

## Benefits of New Database

1. **More Accurate**: Generated directly from Activepieces API
2. **Complete Schema**: Includes all metadata, categories, authors
3. **Full-Text Search**: FTS5 indexes for fast searching
4. **Better Performance**: Optimized indexes and views
5. **Easy Updates**: Can regenerate anytime from API

## Maintenance

To update the database periodically:

```bash
# On server, pull latest from API
cd /var/www/Flow_Assistant/flow-assistant-tools
python3 export_pieces_database.py --format sqlite --output ../data/activepieces

# Regenerate FAISS index
cd /var/www/Flow_Assistant
python3 scripts/migration/prepare_vector_store_from_sqlite.py

# Restart services
sudo systemctl restart activepieces-backend
```

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u activepieces-backend -f`
2. Verify database: `sqlite3 data/activepieces.db ".tables"`
3. Check file permissions: `ls -lah data/`
4. Test database connection: `python3 src/db_config.py`
5. Verify vector store: `python3 -c "import faiss; print(faiss.read_index('data/ap_faiss_index/index.faiss').ntotal)"`

---

**Last Updated**: October 23, 2025
**Database Version**: Generated from flow-assistant-tools
**Total Items**: 450 pieces, 2890 actions, 834 triggers

