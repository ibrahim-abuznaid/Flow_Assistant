"""
Setup script to initialize the AI Assistant project.
"""
import os
import sys
import subprocess

# Fix encoding issues on Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def check_python_version():
    """Check if Python version is 3.9+"""
    if sys.version_info < (3, 9):
        print("❌ Python 3.9 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")


def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists(".env"):
        print("✓ .env file already exists")
        return
    
    if os.path.exists(".env.example"):
        print("Creating .env file from .env.example...")
        with open(".env.example", "r") as src:
            content = src.read()
        with open(".env", "w") as dst:
            dst.write(content)
        print("✓ .env file created")
        print("\n⚠️  IMPORTANT: Please edit .env and add your API keys!")
    else:
        print("⚠️  .env.example not found")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Python dependencies installed")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Python dependencies")
        sys.exit(1)


def setup_frontend():
    """Setup frontend dependencies"""
    print("\nSetting up frontend...")
    
    frontend_dir = "frontend"
    
    if not os.path.exists(frontend_dir):
        print(f"⚠️  Frontend directory '{frontend_dir}' not found")
        return
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        # Install frontend dependencies
        print("Installing frontend dependencies...")
        subprocess.run(
            ["npm", "install"],
            cwd=frontend_dir,
            check=True
        )
        print("✓ Frontend dependencies installed")
    except FileNotFoundError:
        print("⚠️  npm not found. Please install Node.js to setup the frontend")
    except subprocess.CalledProcessError:
        print("❌ Failed to install frontend dependencies")


def main():
    """Main setup function"""
    print("="*60)
    print("🚀 ActivePieces AI Assistant Setup")
    print("="*60)
    
    check_python_version()
    create_env_file()
    install_dependencies()
    setup_frontend()
    
    print("\n" + "="*60)
    print("✅ Setup complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Edit .env file and add your API keys")
    print("2. Run: python prepare_knowledge_base.py")
    print("3. Run backend: uvicorn main:app --reload")
    print("4. Run frontend: cd frontend && npm run dev")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()

