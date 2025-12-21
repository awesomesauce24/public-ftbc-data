#!/usr/bin/env python3
"""
FTBC Wiki Bot - Spongybot v5
Interactive bot interface for wiki management
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from wiki.core.authenticate import authenticate
from wiki.cli.ui import display_welcome
from wiki.cli.commands import cmd_help, cmd_exit, cmd_search, cmd_realms, cmd_subrealms, cmd_create_page


# ==================== COMMAND ROUTER ====================

COMMAND_MAP = {
    'help': cmd_help,
    'exit': cmd_exit,
    'realms': cmd_realms,
    'subrealms': cmd_subrealms,
    'create': cmd_create_page,
    'page': cmd_create_page,
}


def route_command(choice, site=None):
    """
    Route user input to appropriate command
    
    Args:
        choice (str): User input (can include arguments)
        site: Authenticated wiki session (optional)
        
    Returns:
        bool: True if command executed, False if unknown
    """
    choice_lower = choice.strip().lower()
    
    # Handle commands with arguments (e.g., "search Firey")
    if choice_lower.startswith('search '):
        query = choice[7:]  # Remove 'search ' prefix
        cmd_search(query)
        return True
    
    # Handle simple commands
    if choice_lower not in COMMAND_MAP:
        return False
    
    command = COMMAND_MAP[choice_lower]
    
    # Pass site/session to commands that need it
    if choice_lower in ['create', 'page']:
        command(site)
    else:
        command()
    
    return True


# ==================== MAIN LOOP ====================

def main():
    """Main interactive loop"""
    print("="*50)
    print("Authenticating...")
    print("="*50)
    
    # Auto-authenticate
    site = authenticate()
    
    if not site:
        print("Failed to authenticate. Exiting...")
        exit(1)
    
    # Display welcome
    display_welcome()
    
    # Main menu loop
    while True:
        try:
            choice = input("> ").strip()
            
            if not choice:
                continue
            
            if not route_command(choice, site):
                print("Unknown command. Type 'help' for list of commands.")
                
        except EOFError:
            # Handle end of input
            print("\nEnd of input. Exiting...")
            break


# ==================== ENTRY POINT ====================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        exit(0)
