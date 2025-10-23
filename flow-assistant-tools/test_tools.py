#!/usr/bin/env python3
"""
Interactive Test Tool for Flow Assistant Tools
Run this to test all tools with a friendly menu interface
"""

import sys
import os
from typing import Optional

# Color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")

def print_menu(title: str, options: list):
    """Print menu with options"""
    print(f"\n{Colors.BOLD}{title}{Colors.END}")
    print("-" * len(title))
    for i, option in enumerate(options, 1):
        print(f"{Colors.CYAN}{i}.{Colors.END} {option}")
    print(f"{Colors.CYAN}0.{Colors.END} Back/Exit")

def get_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default"""
    if default:
        prompt = f"{prompt} [{default}]"
    user_input = input(f"{Colors.YELLOW}? {prompt}: {Colors.END}").strip()
    return user_input if user_input else default

def confirm(prompt: str, default: bool = True) -> bool:
    """Ask for confirmation"""
    default_str = "Y/n" if default else "y/N"
    response = get_input(f"{prompt} ({default_str})", "y" if default else "n")
    return response.lower() in ['y', 'yes'] if response else default

def run_command(cmd: str):
    """Run a shell command"""
    print(f"\n{Colors.BLUE}Running: {cmd}{Colors.END}\n")
    print("-" * 70)
    result = os.system(cmd)
    print("-" * 70)
    if result == 0:
        print_success("Command completed successfully!")
    else:
        print_error(f"Command failed with exit code {result}")
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def test_connection():
    """Test API connection"""
    print_header("Test API Connection")
    print_info("Testing connection to Activepieces API...")
    
    try:
        from api_client import ActivepiecesAPIClient
        client = ActivepiecesAPIClient()
        print_success(f"API URL: {client.base_url}")
        
        # Try to fetch categories (simple endpoint)
        categories = client.get_piece_categories()
        print_success(f"Connection successful! Found {len(categories)} categories")
        
        if confirm("Show categories?", True):
            for cat in categories:
                print(f"  • {cat}")
        
    except Exception as e:
        print_error(f"Connection failed: {e}")
        print_info("Make sure Activepieces is running and config.json is correct")
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")

def test_get_all_pieces():
    """Test get_all_pieces.py"""
    print_header("Test: Get All Pieces")
    
    options = [
        "Summary view (recommended)",
        "Full JSON output",
        "Search for specific pieces",
        "Filter by suggestion type",
        "Save to file"
    ]
    
    print_menu("Choose an option:", options)
    choice = get_input("Select option", "1")
    
    if choice == "1":
        run_command("python get_all_pieces.py --summary")
    
    elif choice == "2":
        if confirm("This will output a lot of JSON. Continue?", False):
            run_command("python get_all_pieces.py")
    
    elif choice == "3":
        query = get_input("Enter search query (e.g., 'slack')", "slack")
        run_command(f'python get_all_pieces.py --search "{query}" --summary')
    
    elif choice == "4":
        print("\nSuggestion Types:")
        print("1. ACTION")
        print("2. TRIGGER")
        print("3. ACTION_AND_TRIGGER")
        type_choice = get_input("Choose type", "1")
        types = ["ACTION", "TRIGGER", "ACTION_AND_TRIGGER"]
        suggestion_type = types[int(type_choice) - 1] if type_choice in ["1", "2", "3"] else "ACTION"
        run_command(f"python get_all_pieces.py --suggestion-type {suggestion_type} --summary")
    
    elif choice == "5":
        filename = get_input("Enter filename", "pieces.json")
        run_command(f"python get_all_pieces.py --output {filename}")
        print_success(f"Saved to {filename}")

def test_search_pieces():
    """Test search_pieces.py"""
    print_header("Test: Search Pieces")
    
    query = get_input("Enter search query", "email")
    
    options = []
    cmd = f'python search_pieces.py "{query}"'
    
    if confirm("Rank results by relevance?", True):
        cmd += " --rank"
    
    if confirm("Limit results?", True):
        limit = get_input("How many results?", "5")
        cmd += f" --limit {limit}"
    
    run_command(cmd)

def test_get_piece_details():
    """Test get_piece_details.py"""
    print_header("Test: Get Piece Details")
    
    print_info("Common piece names:")
    print("  • @activepieces/piece-slack")
    print("  • @activepieces/piece-gmail")
    print("  • @activepieces/piece-openai")
    print("  • @activepieces/piece-http")
    
    piece_name = get_input("Enter piece name", "@activepieces/piece-slack")
    
    cmd = f'python get_piece_details.py "{piece_name}"'
    
    if confirm("Show verbose details (all properties)?", False):
        cmd += " --verbose"
    
    if confirm("JSON output only?", False):
        cmd += " --json-only"
    
    run_command(cmd)

def test_get_actions():
    """Test get_piece_actions.py"""
    print_header("Test: Get Piece Actions")
    
    piece_name = get_input("Enter piece name", "@activepieces/piece-slack")
    
    cmd = f'python get_piece_actions.py "{piece_name}"'
    
    if confirm("Show properties for each action?", True):
        cmd += " --show-properties"
    
    run_command(cmd)

def test_get_triggers():
    """Test get_piece_triggers.py"""
    print_header("Test: Get Piece Triggers")
    
    piece_name = get_input("Enter piece name", "@activepieces/piece-slack")
    
    cmd = f'python get_piece_triggers.py "{piece_name}"'
    
    if confirm("Show properties for each trigger?", True):
        cmd += " --show-properties"
    
    run_command(cmd)

def test_get_categories():
    """Test get_piece_categories.py"""
    print_header("Test: Get Piece Categories")
    
    if confirm("Show pieces in each category?", True):
        run_command("python get_piece_categories.py --with-pieces")
    else:
        run_command("python get_piece_categories.py")

def test_format_for_llm():
    """Test format_for_llm.py"""
    print_header("Test: Format for LLM")
    
    print_menu("Choose format:", [
        "Compact (recommended for most assistants)",
        "Full (detailed with all info)",
        "Full with verbose properties",
        "JSON only"
    ])
    
    choice = get_input("Select format", "1")
    
    filename = get_input("Enter output filename", "llm_context.md")
    
    if choice == "1":
        cmd = f"python format_for_llm.py --format compact --output {filename}"
    elif choice == "2":
        cmd = f"python format_for_llm.py --format full --output {filename}"
    elif choice == "3":
        cmd = f"python format_for_llm.py --format full --verbose --output {filename}"
    else:
        cmd = f"python format_for_llm.py --format json --output {filename}"
    
    if confirm("Filter by search query?", False):
        query = get_input("Enter search query")
        if query:
            cmd += f' --search "{query}"'
    
    if confirm("Filter by categories?", False):
        print_info("Example categories: COMMUNICATION, AI, PRODUCTIVITY, DEVELOPER_TOOLS")
        categories = get_input("Enter categories (space-separated)")
        if categories:
            cats = ' '.join([f'"{cat}"' for cat in categories.split()])
            cmd += f" --categories {cats}"
    
    run_command(cmd)
    print_success(f"Context saved to {filename}")

def test_export_database():
    """Test export_pieces_database.py"""
    print_header("Test: Export Pieces Database")
    
    print_menu("Choose export format:", [
        "JSON",
        "CSV (pieces)",
        "CSV (actions only)",
        "CSV (triggers only)",
        "SQLite database",
        "All formats"
    ])
    
    choice = get_input("Select format", "1")
    
    formats = {
        "1": "json",
        "2": "csv",
        "3": "csv-actions",
        "4": "csv-triggers",
        "5": "sqlite",
        "6": "all"
    }
    
    format_type = formats.get(choice, "json")
    filename = get_input("Enter output filename/prefix", "pieces_export")
    
    cmd = f"python export_pieces_database.py --format {format_type} --output {filename}"
    
    if confirm("Include hidden pieces?", False):
        cmd += " --include-hidden"
    
    run_command(cmd)

def test_toolkit_api():
    """Test pieces_toolkit.py API"""
    print_header("Test: Python Toolkit API")
    
    print_info("This will run the toolkit example code")
    run_command("python pieces_toolkit.py")

def show_main_menu():
    """Show main menu and handle selection"""
    while True:
        print_header("Flow Assistant Tools - Interactive Tester")
        
        print(f"{Colors.BOLD}Testing Tools:{Colors.END}")
        tools = [
            "Test API Connection (Start here!)",
            "Get All Pieces",
            "Search Pieces",
            "Get Piece Details",
            "Get Piece Actions",
            "Get Piece Triggers",
            "Get Categories",
            "Format for LLM (Generate Context)",
            "Export Database",
            "Test Python Toolkit API"
        ]
        
        print_menu("Select a tool to test:", tools)
        
        choice = get_input("\nSelect option", "1")
        
        if choice == "0":
            print_success("Goodbye!")
            sys.exit(0)
        
        try:
            choice_num = int(choice)
            if choice_num == 1:
                test_connection()
            elif choice_num == 2:
                test_get_all_pieces()
            elif choice_num == 3:
                test_search_pieces()
            elif choice_num == 4:
                test_get_piece_details()
            elif choice_num == 5:
                test_get_actions()
            elif choice_num == 6:
                test_get_triggers()
            elif choice_num == 7:
                test_get_categories()
            elif choice_num == 8:
                test_format_for_llm()
            elif choice_num == 9:
                test_export_database()
            elif choice_num == 10:
                test_toolkit_api()
            else:
                print_error("Invalid option")
                input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
        except ValueError:
            print_error("Please enter a number")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
            if confirm("\nExit?", True):
                print_success("Goodbye!")
                sys.exit(0)

def main():
    """Main entry point"""
    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # Show welcome message
    print(f"{Colors.GREEN}{Colors.BOLD}")
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║        FLOW ASSISTANT TOOLS - INTERACTIVE TESTER             ║
    ║                                                               ║
    ║     Test all tools with a user-friendly menu interface       ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(Colors.END)
    
    print_info("Welcome! This tool helps you test all Flow Assistant Tools.")
    print_info("Make sure Activepieces is running before starting.\n")
    
    if not confirm("Ready to start?", True):
        print_success("Goodbye!")
        return
    
    # Show main menu
    show_main_menu()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        print_success("Goodbye!")
        sys.exit(0)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

