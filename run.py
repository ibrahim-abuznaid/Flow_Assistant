"""
Helper script to run the AI Assistant application.
"""
import os
import sys
import subprocess
import time
from pathlib import Path


def check_env_file():
    """Check if .env file exists."""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("\nPlease create a .env file with your API keys.")
        print("You can copy .env.example and fill in your keys:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your OPENAI_API_KEY")
        print("  3. (Optional) Add PERPLEXITY_API_KEY")
        return False
    return True


def check_vector_store():
    """Check if vector store exists."""
    if not os.path.exists("ap_faiss_index"):
        print("❌ Vector store not found!")
        print("\nPlease prepare the knowledge base first:")
        print("  python prepare_knowledge_base.py")
        return False
    return True


def check_frontend():
    """Check if frontend is set up."""
    frontend_dir = Path("frontend")
    node_modules = frontend_dir / "node_modules"
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    if not node_modules.exists():
        print("⚠️  Frontend dependencies not installed!")
        print("\nInstalling frontend dependencies...")
        try:
            subprocess.run(
                ["npm", "install"],
                cwd=frontend_dir,
                check=True
            )
            print("✓ Frontend dependencies installed")
        except Exception as e:
            print(f"❌ Failed to install frontend dependencies: {e}")
            return False
    
    return True


def run_backend():
    """Run the FastAPI backend."""
    print("\n" + "="*60)
    print("🚀 Starting Backend Server")
    print("="*60)
    
    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Backend server stopped")
    except Exception as e:
        print(f"\n❌ Error running backend: {e}")
        sys.exit(1)


def run_frontend():
    """Run the React frontend."""
    print("\n" + "="*60)
    print("🚀 Starting Frontend Server")
    print("="*60)
    
    try:
        subprocess.run(
            ["npm", "run", "dev"],
            cwd="frontend",
            check=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Frontend server stopped")
    except Exception as e:
        print(f"\n❌ Error running frontend: {e}")
        sys.exit(1)


def run_both():
    """Run both backend and frontend (Windows only)."""
    print("\n" + "="*60)
    print("🚀 Starting Both Servers")
    print("="*60)
    print("\nBackend: http://localhost:8000")
    print("Frontend: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers")
    print("="*60 + "\n")
    
    try:
        # Start backend in background
        backend_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--reload"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("✓ Backend started")
        time.sleep(2)
        
        # Start frontend in foreground
        print("✓ Starting frontend...\n")
        subprocess.run(
            ["npm", "run", "dev"],
            cwd="frontend",
            check=True
        )
    
    except KeyboardInterrupt:
        print("\n\n✓ Stopping servers...")
        backend_process.terminate()
        backend_process.wait()
        print("✓ Servers stopped")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if 'backend_process' in locals():
            backend_process.terminate()
        sys.exit(1)


def main():
    """Main function."""
    print("="*60)
    print("🤖 ActivePieces AI Assistant - Launcher")
    print("="*60)
    
    # Pre-flight checks
    print("\nRunning pre-flight checks...")
    
    if not check_env_file():
        sys.exit(1)
    
    if not check_vector_store():
        sys.exit(1)
    
    if not check_frontend():
        sys.exit(1)
    
    print("\n✓ All checks passed!")
    
    # Ask what to run
    print("\nWhat would you like to run?")
    print("  1. Backend only (FastAPI)")
    print("  2. Frontend only (React)")
    print("  3. Both (recommended)")
    print("  4. Run tests")
    print("  5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == "1":
        run_backend()
    elif choice == "2":
        run_frontend()
    elif choice == "3":
        run_both()
    elif choice == "4":
        print("\nRunning tests...\n")
        subprocess.run([sys.executable, "test_assistant.py"])
    elif choice == "5":
        print("\nGoodbye! 👋")
        sys.exit(0)
    else:
        print("\n❌ Invalid choice")
        sys.exit(1)


if __name__ == "__main__":
    main()

