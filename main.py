#!/usr/bin/env python3
"""
FTBC Wiki Management System - Main Entry Point

This script authenticates with the Fandom wiki and provides access to
the wiki management CLI and data extraction tools.
"""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from auth import authenticate
from create_pages import create, update_realm, update_realm_format


def show_help():
    """Display help message with available commands."""
    print()
    print("=" * 60)
    print("Available Commands:")
    print("=" * 60)
    print("  create       - Create a new wiki object page")
    print("  update       - Update realm pages from wiki")
    print("  format       - Format pages + create stubs for missing")
    print("  help         - Show this help message")
    print("  exit         - Exit the CLI")
    print("=" * 60)
    print()


def main():
    """Main entry point with CLI loop."""
    print("=" * 60)
    print("FTBC Wiki Management System")
    print("=" * 60)
    print()
    
    try:
        # Authenticate with wiki
        session = authenticate()
        print()
        print("[+] Ready to use the wiki management system")
        print("    Type 'help' for commands or 'exit' to quit")
        print()
        
        # CLI loop
        while True:
            try:
                command = input("> ").strip().lower()
                
                if not command:
                    continue
                
                if command == "create":
                    create(session)
                
                elif command == "update":
                    update_realm(session)
                
                elif command == "format":
                    update_realm_format(session)
                
                elif command == "help":
                    show_help()
                
                elif command == "exit":
                    print("Exiting...")
                    break
                
                else:
                    print(f"[x] Unknown command: {command}")
                    print("    Type 'help' for available commands")
            
            except KeyboardInterrupt:
                print("\n\nExiting...")
                break
        
    except Exception as e:
        print(f"\n[x] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

