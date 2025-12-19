#!/usr/bin/env python3
"""
FTBC Wiki Bot - Spongybot v4
Interactive bot interface
"""

import os
import sys
import subprocess
from authenticate import authenticate
from scrapers import scrape_realms
from object_formatter import create_object_template, format_from_dict, create_object_with_autofill, check_page_exists, format_wiki_page_name

# ==================== UTILITY FUNCTIONS ====================

def copy_to_clipboard(text):
    """Copy text to clipboard (Windows)"""
    try:
        # Try using PowerShell to copy to clipboard (works on Windows)
        process = subprocess.Popen(['powershell', '-Command', 'Set-Clipboard -Value $input'], 
                                   stdin=subprocess.PIPE, 
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(text.encode('utf-8'))
        if process.returncode == 0:
            return True
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")
    return False

def edit_wiki_page(session, page_name, content, summary="Updated by Spongybot v4"):
    """Edit or create a wiki page using the authenticated session"""
    wiki_url = session.wiki_url
    
    try:
        print(f"Uploading page: {page_name}...")
        
        # Get CSRF token
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'csrf',
            'format': 'json'
        }
        
        response = session.get(f"{wiki_url}/api.php", params=params)
        token_data = response.json()
        
        if 'batchcomplete' not in token_data:
            return False
        
        csrf_token = token_data['query']['tokens']['csrftoken']
        
        # Edit the page
        edit_params = {
            'action': 'edit',
            'title': page_name,
            'text': content,
            'summary': summary,
            'token': csrf_token,
            'format': 'json'
        }
        
        response = session.post(f"{wiki_url}/api.php", data=edit_params)
        result = response.json()
        
        if 'edit' in result:
            edit_result = result['edit']
            if 'pageid' in edit_result or ('result' in edit_result and edit_result['result'] == 'Success'):
                return True
        
        return False
        
    except Exception as e:
        return False

def prompt_post_generation(page_name, formatted_page, mode, session):
    """Prompt user after generating a page. Returns action: 'continue_realm', 'new_realm', 'back', or None"""
    action_text = "EDIT" if mode == "EDITING" else "CREATE"
    
    while True:
        print("\n" + "="*50)
        print("What would you like to do?")
        print("="*50)
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
            url = f"https://ftbc.fandom.com/wiki/{page_name}"
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(url)
                elif os.name == 'posix':  # macOS, Linux
                    os.system(f'open "{url}"' if sys.platform == 'darwin' else f'xdg-open "{url}"')
                print(f"[OK] Opening {url}")
            except Exception as e:
                print(f"[FAIL] Could not open browser: {e}")
                print(f"Visit: {url}")
        
        elif choice in ['3', 'edit', 'create']:
            summary = f"Created by Spongybot v4" if mode == "CREATING" else "Updated by Spongybot v4"
            if edit_wiki_page(session, page_name, formatted_page, summary):
                print(f"[OK] Page successfully {'updated' if mode == 'EDITING' else 'created'}!")
            else:
                print(f"[FAIL] Failed to {'update' if mode == 'EDITING' else 'create'} page")
        
        elif choice in ['4', 'continue', 'another', 'next']:
            return 'continue_realm'
        
        elif choice in ['5', 'realm', 'new_realm', 'choose']:
            return 'new_realm'
        
        elif choice in ['6', 'back', 'menu']:
            return 'back'
        
        else:
            print("Invalid choice")

# ==================== DISPLAY FUNCTIONS ====================

def display_welcome():
    """Display welcome message"""
    print("\n" + "="*50)
    print("Welcome to Spongybot v4")
    print("="*50)
    print("type 'help' for command list\n")

# ==================== COMMAND FUNCTIONS ====================

def cmd_help():
    """Display help information"""
    print("\n" + "="*50)
    print("Commands")
    print("="*50)
    print("help              - Show this help message")
    print("realms            - Show all realms")
    print("subrealms         - Show all sub-realms")
    print("objtemplate       - Show object template")
    print("createobj/co/co   - Create object with auto-filled fields")
    print("exit              - Exit the bot")
    print("="*50 + "\n")

def cmd_exit():
    """Exit the bot"""
    print("Goodbye!")
    sys.exit(0)

def cmd_realms(site):
    """Scrape and display only normal realms"""
    print("\nScraping realms from wiki...")
    realms_data = scrape_realms(site, site.wiki_url)
    
    if not realms_data:
        print("Failed to scrape realms")
        return
    
    # Display Normal Realms only
    if realms_data['normal_realms']:
        print("\n" + "="*50)
        print("Realms")
        print("="*50)
        for realm in realms_data['normal_realms']:
            print(f"  - {realm}")
    print()

def cmd_subrealms(site):
    """Scrape and display all sub-realms"""
    print("\nScraping sub-realms from wiki...")
    realms_data = scrape_realms(site, site.wiki_url)
    
    if not realms_data:
        print("Failed to scrape sub-realms")
        return
    
    # Display Main Realm Sub-Realms
    if realms_data['main_realm_subrealms']:
        print("\n" + "="*50)
        print("Main Realm Sub-Realms")
        print("="*50)
        for subrealm in realms_data['main_realm_subrealms']:
            print(f"  - {subrealm}")
    
    # Display Yoyleland Sub-Realms
    if realms_data['yoyleland_subrealms']:
        print("\n" + "="*50)
        print("Yoyleland Sub-Realms")
        print("="*50)
        for subrealm in realms_data['yoyleland_subrealms']:
            print(f"  - {subrealm}")
    
    # Display The Backrooms Levels
    if realms_data['backrooms_subrealms']:
        print("\n" + "="*50)
        print("The Backrooms Levels")
        print("="*50)
        for level in realms_data['backrooms_subrealms']:
            print(f"  - {level}")
    
    # Display Yoyle Factory Sub-Realms
    if realms_data['yoyle_factory_subrealms']:
        print("\n" + "="*50)
        print("Yoyle Factory Sub-Realms")
        print("="*50)
        for sub in realms_data['yoyle_factory_subrealms']:
            print(f"  - {sub}")
    
    # Display Classic Paradise Sub-Realms
    if realms_data['classic_paradise_subrealms']:
        print("\n" + "="*50)
        print("Classic Paradise Sub-Realms")
        print("="*50)
        for sub in realms_data['classic_paradise_subrealms']:
            print(f"  - {sub}")
    
    # Display Evil Forest Sub-Realms
    if realms_data['evil_forest_subrealms']:
        print("\n" + "="*50)
        print("Evil Forest Sub-Realms")
        print("="*50)
        for sub in realms_data['evil_forest_subrealms']:
            print(f"  - {sub}")
    
    # Display Midnight Rooftops Sub-Realms
    if realms_data['midnight_rooftops_subrealms']:
        print("\n" + "="*50)
        print("Midnight Rooftops Sub-Realms")
        print("="*50)
        for sub in realms_data['midnight_rooftops_subrealms']:
            print(f"  - {sub}")
    print()

def cmd_objtemplate():
    """Display object template for wiki formatting"""
    template = create_object_template()
    
    print("\n" + "="*50)
    print("Object Template Structure")
    print("="*50)
    print("Use this structure to format objects for wiki pages:\n")
    
    for key, value in template.items():
        print(f"{key}: {value}")
    
    print("\n" + "="*50)
    print("Example Formatted Output:")
    print("="*50)
    
    # Example data (using JSON format from template)
    example_data = {
        "name": "American Flag",
        "character_images": [
            {"filename": "AmericanFlag.png", "caption": "American Flag in Main Realm"}
        ],
        "difficulty": "[[File:Hard.png]] <span style=\"color:red\">'''Hard'''</span>",
        "area": "[[Main Realm]]",
        "hint": "Land of the free",
        "previous_difficulties": [],
        "info": "A flag-like character from Main Realm",
        "obtaining": "Found in Main Realm",
        "trivia": ["Represents the USA"],
        "realm": "Main Realm",
        "categories": ["Main Realm Characters", "Flag Characters"]
    }
    
    formatted = format_from_dict(example_data)
    print(formatted)
    print()

def cmd_createobj(site):
    """Create an object with auto-populated fields"""
    realms = [
        "Main Realm", "Inverted Realm", "Yoyleland", "Backrooms",
        "Yoyle Factory", "Classic Paradise", "Evil Forest", "Cherry Grove",
        "Barren Desert", "Frozen World", "Timber Peaks", "Midnight Rooftops",
        "Magma Canyon", "Sakura Serenity", "Polluted Marshlands"
    ]
    
    selected_realm = None
    
    # Outer loop for realm selection
    while True:
        # Get realm choice
        if selected_realm is None:
            print("\n" + "="*50)
            print("Create Object (Auto-fill enabled)")
            print("="*50)
            print("\nSelect realm:")
            for i, realm in enumerate(realms, 1):
                print(f"{i}. {realm}")
            
            try:
                realm_choice = int(input("\nEnter realm number: ")) - 1
                if realm_choice < 0 or realm_choice >= len(realms):
                    print("Invalid choice!")
                    continue
                selected_realm = realms[realm_choice]
            except ValueError:
                print("Invalid input!")
                continue
        
        # Inner loop for objects within the realm
        while True:
            # Get object name
            obj_name = input(f"\nEnter object name (to search for hint in {selected_realm}): ").strip()
            if not obj_name:
                print("Object name cannot be empty!")
                continue
            
            # Auto-populate character image
            images = [{"filename": f"{obj_name}.png", "caption": obj_name}]
            
            # Get info (multiline)
            print("\nEnter info (multiple lines, empty line to finish, or press Enter to use default):")
            info_lines = []
            while True:
                line = input()
                if not line and not info_lines:
                    # First line is empty, use default
                    info = None
                    break
                if not line:
                    # Empty line after some input, finish
                    info = "\n".join(info_lines) if info_lines else None
                    break
                info_lines.append(line)
            
            # Get obtaining (multiline)
            print("\nEnter obtaining info (multiple lines, empty line to finish, or press Enter to skip):")
            obtaining_lines = []
            while True:
                line = input()
                if not line and not obtaining_lines:
                    # First line is empty, skip
                    obtaining = None
                    break
                if not line:
                    # Empty line after some input, finish
                    obtaining = "\n".join(obtaining_lines) if obtaining_lines else None
                    break
                obtaining_lines.append(line)
            
            trivia_input = input("\nEnter trivia (comma-separated, or press Enter for none): ").strip()
            trivia = [t.strip() for t in trivia_input.split(",")] if trivia_input else None
            
            # Get categories
            categories_input = input("Enter categories (comma-separated, or press Enter for default): ").strip()
            categories = [c.strip() for c in categories_input.split(",")] if categories_input else None
            
            # Check if page already exists
            page_name = format_wiki_page_name(obj_name)
            print(f"\nChecking if wiki page exists...")
            print(f"URL: https://ftbc.fandom.com/wiki/{page_name}")
            page_exists = check_page_exists(obj_name)
            
            if page_exists is True:
                print(f"[OK] Page EXISTS! You will be EDITING this page.")
                mode = "EDITING"
            elif page_exists is False:
                print(f"[FAIL] Page does NOT exist. You will be CREATING this page.")
                mode = "CREATING"
            else:
                print(f"? Could not verify page status. Assuming CREATING.")
                mode = "CREATING (assumed)"
            
            # Create object with auto-fill
            formatted = create_object_with_autofill(
                obj_name,
                selected_realm,
                character_images=images,
                info=info,
                obtaining=obtaining,
                trivia=trivia,
                categories=categories
            )
            
            print("\n" + "="*50)
            print(f"Generated Object Page ({mode}):")
            print("="*50)
            print(formatted)
            
            # Prompt for post-generation actions
            action = prompt_post_generation(page_name, formatted, mode, site)
            
            if action == 'continue_realm':
                # Continue to next object in same realm
                continue
            elif action == 'new_realm':
                # Go back to realm selection
                selected_realm = None
                break
            elif action == 'back' or action is None:
                # Return to main menu
                return

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
        sys.exit(1)
    
    # Display welcome
    display_welcome()
    
    # Main menu loop
    while True:
        choice = input("> ").strip().lower()
        
        if choice == "help":
            cmd_help()
        elif choice == "realms":
            cmd_realms(site)
        elif choice == "subrealms":
            cmd_subrealms(site)
        elif choice == "objtemplate":
            cmd_objtemplate()
        elif choice in ["createobj", "co", "createobject"]:
            cmd_createobj(site)
        elif choice == "exit":
            cmd_exit()
        elif choice == "1":
            cmd_exit()
        else:
            print("Unknown command. Type 'help' for list of commands.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
        sys.exit(0)
