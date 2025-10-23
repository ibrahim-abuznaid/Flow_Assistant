# Quick Deployment Steps - Database Update

## What You Need to Do

I've updated the database with more accurate data from the Activepieces API. Here's what you need to do to deploy it:

## Step 1: Commit and Push Changes (On Your Windows Machine)

```powershell
# 1. Stage all changes
git add .

# 2. Commit with a descriptive message
git commit -m "Update: New database from flow-assistant-tools with 450 pieces, 2890 actions, 834 triggers"

# 3. Push to GitHub
git push origin main
```

## Step 2: Deploy on Server

```bash
# SSH into your server
ssh root@your-server-ip

# Navigate to project
cd /var/www/Flow_Assistant

# Stop services
sudo systemctl stop activepieces-backend activepieces-frontend

# Pull changes
git pull origin main

# Verify new database
python3 -c "import sqlite3; conn = sqlite3.connect('data/activepieces.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM pieces'); print(f'Pieces: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM actions'); print(f'Actions: {cursor.fetchone()[0]}'); cursor.execute('SELECT COUNT(*) FROM triggers'); print(f'Triggers: {cursor.fetchone()[0]}')"

# Regenerate FAISS vector index (IMPORTANT!)
python3 scripts/migration/prepare_vector_store_from_sqlite.py

# Restart services
sudo systemctl restart activepieces-backend activepieces-frontend

# Check status
sudo systemctl status activepieces-backend
```

## Step 3: Verify It Works

```bash
# Test API
curl http://localhost:8000/stats

# Should show:
# {"pieces": 450, "actions": 2890, "triggers": 834}
```

## That's It!

Your database is now updated with the most accurate data from the Activepieces API.

## If Something Goes Wrong

See the detailed guide: `DEPLOYMENT_DATABASE_UPDATE_GUIDE.md`

Or rollback:
```bash
sudo systemctl stop activepieces-backend
cp old_database/activepieces_old.db data/activepieces.db
cp -r old_database/ap_faiss_index_old data/ap_faiss_index
sudo systemctl restart activepieces-backend
```

---

## Summary of Changes

### What Changed:
- ✅ **New Database**: Generated from `flow-assistant-tools/export_pieces_database.py`
- ✅ **More Data**: 450 pieces (vs 433 before), 2890 actions, 834 triggers
- ✅ **Old Backups**: Saved in `old_database/` folder
- ✅ **Fixed Scripts**: Updated export and FAISS generation scripts

### Files to Commit:
- `data/activepieces.db` - New database
- `flow-assistant-tools/export_pieces_database.py` - Updated export script
- `scripts/migration/prepare_vector_store_from_sqlite.py` - Fixed FAISS script
- `old_database/` - Backups
- `DEPLOYMENT_DATABASE_UPDATE_GUIDE.md` - This guide
- `QUICK_DEPLOYMENT_STEPS.md` - Quick reference

### On Server, You Must:
1. Pull the changes
2. **Regenerate FAISS index** (very important!)
3. Restart services

That's all!

