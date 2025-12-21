#!/usr/bin/env python3
"""
UI components and prompts for FTBC Wiki Bot
Handles user interaction and menu displays
"""

from .utils import copy_to_clipboard, open_browser, edit_wiki_page


def display_header(title):
    """Display a formatted header"""
    print("\n" + "="*50)
    print(title)
    print("="*50)


def display_footer():
    """Display a footer separator"""
    print("="*50 + "\n")


def display_welcome():
    """Display welcome message"""
    display_header("Welcome to Spongybot v5!")
    print("type 'help' for command list\n")


def display_help():
    """Display help message"""
    display_header("Commands")
    print("help                  - Show this help message")
    print("search <query>        - Search for objects")
    print("realms                - List all main realms")
    print("subrealms             - List all subrealms")
    print("create_page           - Create wiki pages for objects")
    print("exit                  - Exit the bot")
    display_footer()


def display_realms(realms_list):
    """Display a list of realms"""
    display_header("Realms")
    for realm in realms_list:
        print(f"  - {realm}")
    display_footer()


def display_subrealm_section(title, subrealms_list):
    """Display a subrealm section"""
    if not subrealms_list:
        return
    display_header(title)
    for subrealm in subrealms_list:
        print(f"  - {subrealm}")


def prompt_post_generation(page_name, formatted_page, mode, session):
    """
    Prompt user after generating a page
    
    Args:
        page_name (str): Name of the wiki page
        formatted_page (str): Formatted wiki page content
        mode (str): Either "EDITING" or "CREATING"
        session: Authenticated wiki session
        
    Returns:
        str: Action to take ('continue_realm', 'new_realm', 'back', or None)
    """
    action_text = "EDIT" if mode == "EDITING" else "CREATE"
    
    while True:
        display_header("What would you like to do?")
        print(f"1. Copy to clipboard")
        print(f"2. Open wiki page in browser")
        print(f"3. {action_text} page on wiki")
        print(f"4. Add another object to this realm")
        print(f"5. Choose another realm")
        print(f"6. Back to main menu")
        print("="*50)
        
        choice = input("> ").strip().lower()
        
        if choice in ['1', 'clipboard', 'copy']:
            if copy_to_clipboard(formatted_page):
                print("[OK] Copied to clipboard!")
            else:
                print("[FAIL] Failed to copy to clipboard")
        
        elif choice in ['2', 'open', 'browser']:
            open_browser(page_name)
        
        elif choice in ['3', 'edit', 'create']:
            summary = "Created by Spongybot v4" if mode == "CREATING" else "Updated by Spongybot v4"
            if edit_wiki_page(session, page_name, formatted_page, summary):
                action = "updated" if mode == "EDITING" else "created"
                print(f"[OK] Page successfully {action}!")
            else:
                action = "update" if mode == "EDITING" else "create"
                print(f"[FAIL] Failed to {action} page")
        
        elif choice in ['4', 'continue', 'another', 'next']:
            return 'continue_realm'
        
        elif choice in ['5', 'realm', 'new_realm', 'choose']:
            return 'new_realm'
        
        elif choice in ['6', 'back', 'menu']:
            return 'back'
        
        else:
            print("Invalid choice. Please try again.")
