# Quick Fix for Python 3.13 Compatibility Issues

## Problem
Python 3.13 is very new (released Oct 2024) and many packages don't have pre-built wheels yet, causing build failures.

## Solution Options

### Option 1: Use Python 3.11 or 3.12 (Recommended)

```bash
# Install Python 3.11 or 3.12 on Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3.11-dev

# Create virtual environment with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Stay with Python 3.13 (Advanced)

If you want to keep Python 3.13, you need to:

1. **Upgrade pip first** (important!):
```bash
source venv/bin/activate
pip install --upgrade pip setuptools wheel
```

2. **Install without specific versions** (already updated in requirements.txt):
```bash
pip install -r requirements.txt
```

3. **If still fails, install Rust** (for building from source):
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

Then try installing again.

### Option 3: Install packages individually

```bash
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install core packages first
pip install fastapi uvicorn python-dotenv requests

# Install AI packages
pip install openai anthropic

# Install LangChain (latest versions with Python 3.13 support)
pip install langchain langchain-openai langchain-community langchain-core

# Install FAISS
pip install faiss-cpu

# Install pydantic separately
pip install pydantic pydantic-settings
```

## What I Fixed

1. ✅ Updated `faiss-cpu` from 1.7.4 to >=1.9.0
2. ✅ Updated all package versions to latest (Python 3.13 compatible)
3. ✅ Removed strict version pinning (uses >= instead of ==)
4. ✅ Added missing `langchain-core` dependency
5. ✅ Fixed Unicode encoding issue in setup.py for Windows

## Recommended: Use Python 3.11

**Python 3.11** is the sweet spot right now - it's stable, fast, and all packages have pre-built wheels.

```bash
# Quick setup with Python 3.11
cd "c:/Users/ibrah/OneDrive/Documents/AP work/Flow_Assistant"

# Remove old venv if exists
rm -rf venv

# Create new venv with Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Prepare knowledge base
python prepare_knowledge_base.py

# Run the app
python main.py
```

## After Successful Installation

Once dependencies are installed, run:

```bash
# Test the installation
python test_assistant.py

# If tests pass, launch the app
python run.py
```

## Need Help?

If you still get errors, share the specific error message and I'll help you fix it!

