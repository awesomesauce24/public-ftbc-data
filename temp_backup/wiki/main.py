#!/usr/bin/env python3
"""
FTBC Wiki Management CLI
Command-line interface for managing wiki pages and content
"""

import sys
import os
from pathlib import Path

# Handle relative imports when run as script
if __name__ == '__main__' and __package__ is None:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from wiki.auth import get_wiki_client
    from wiki.create_pages import main as create_pages_main
else:
    from .auth import get_wiki_client
    from .create_pages import main as create_pages_main

def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if sys.platform == "win32" else "clear")

class WikiCLI:
    """CLI interface for wiki management"""
    
    def __init__(self):
        self.session = None
        self.is_authenticated = False
        self.history = []
    
    def print_banner(self):
        """Print the CLI banner"""
        print("\n" + "="*60)
        print("FTBC WIKI MANAGEMENT CLI")
        print("="*60)
    
    def print_help(self):
        """Print help information"""
        help_text = """
  AVAILABLE COMMANDS:
  
    create    - Create/edit object wiki pages
    list      - List all realms and objects
    status    - Show authentication status
    help      - Show this help message
    exit      - Exit the CLI
    back      - Go back to previous menu
    clear     - Clear screen

  EXAMPLES:
    > create
    > list
    > help
    > exit
"""
        print(help_text)
    
    def authenticate(self):
        """Authenticate with the wiki"""
        if self.is_authenticated:
            print("✓ Already authenticated to wiki")
            return True
        
        try:
            print("Authenticating with wiki...")
            self.session = get_wiki_client()
            self.is_authenticated = True
            print("[OK] Successfully authenticated")
            return True
        except Exception as e:
            print(f"[ERROR] Authentication failed: {e}")
            return False
    
    def show_status(self):
        """Show authentication status"""
        status = "[OK] Authenticated" if self.is_authenticated else "[NOT OK] Not authenticated"
        print(f"\nStatus: {status}")
        if self.is_authenticated:
            print("Session: Active")
    
    def create_pages_command(self):
        """Run the create pages interface"""
        print("\nEntering Create/Edit Pages mode...")
        print("(Type 'back' to return to main menu, 'help' for commands)\n")
        
        try:
            create_pages_main(self.session)
        except KeyboardInterrupt:
            pass
    
    def list_command(self):
        """List realms and objects"""
        from .create_pages import load_realms, load_subrealms, load_realm_objects, load_subrealm_objects
        
        realms = load_realms()
        subrealms = load_subrealms()
        
        print("\n" + "="*60)
        print("REALMS AND OBJECTS")
        print("="*60)
        
        print("\nNORMAL REALMS:")
        for realm in realms["normal"]:
            print(f"\n  {realm['label']}:")
            try:
                obj_data = load_realm_objects(realm["label"])
                if obj_data and obj_data.get("objects"):
                    count = len(obj_data["objects"])
                    print(f"    Objects: {count}")
                    for obj in obj_data["objects"][:5]:  # Show first 5
                        print(f"      - {obj['name']} ({obj['difficulty']})")
                    if count > 5:
                        print(f"      ... and {count - 5} more")
            except Exception as e:
                print(f"    Error loading objects: {e}")
        
        print("\n\nSUB-REALMS:")
        for parent, subs in subrealms.items():
            print(f"\n  {parent}:")
            for sub in subs:
                print(f"    - {sub['label']}")
    
    def process_command(self, command):
        """Process a user command"""
        cmd = command.strip().lower()
        
        if not cmd:
            return True
        
        if cmd == "exit":
            print("\nGoodbye!")
            return False
        
        elif cmd == "help":
            self.print_help()
        
        elif cmd == "status":
            self.show_status()
        
        elif cmd == "create":
            self.create_pages_command()
        
        elif cmd == "list":
            self.list_command()
        
        elif cmd == "clear":
            clear_screen()
            self.print_banner()
        
        elif cmd == "back":
            print("Already at main menu. Type 'exit' to quit.")
        
        else:
            print(f"Unknown command: '{cmd}'")
            print("Type 'help' for available commands.")
        
        return True
    
    def run(self):
        """Main CLI loop"""
        # Clear screen on startup
        clear_screen()
        
        # Authenticate first
        print("Authenticating with wiki...")
        if not self.authenticate():
            print("\nCannot proceed without authentication.")
            return
        
        clear_screen()
        self.print_banner()
        print("\nType 'help' for available commands or 'exit' to quit.\n")
        
        while True:
            try:
                command = input("> ").strip()
                if not self.process_command(command):
                    break
                print()
            except KeyboardInterrupt:
                print("\n\nExit.")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Entry point"""
    cli = WikiCLI()
    cli.run()

if __name__ == "__main__":
    main()
