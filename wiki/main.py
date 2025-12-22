#!/usr/bin/env python3
"""
FTBC Wiki System - Main Entry Point
Revamped v6 with modular architecture
"""

import sys
import os

# Fix encoding for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')

from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from wiki.cli.commands import RealmCommands
from wiki.core.config import Config


def fuzzy_match(query: str, items: list) -> list:
    """Fuzzy match items based on query"""
    query_lower = query.lower()
    matches = []
    
    for item in items:
        item_lower = item.lower()
        if query_lower == item_lower:
            # Exact match - highest priority
            matches.insert(0, item)
        elif query_lower in item_lower:
            # Substring match
            matches.append(item)
    
    return matches


def check_realm_pages(realms_path: Path) -> dict:
    """Check which realms have page.txt files"""
    pages_status = {}
    for realm_dir in sorted(realms_path.iterdir()):
        if realm_dir.is_dir():
            page_file = realm_dir / "page.txt"
            pages_status[realm_dir.name] = "✓" if page_file.exists() else "✗"
    
    return pages_status


def load_realm_objects(realm_name: str, realms_path: Path) -> list:
    """Load objects from realm JSON file, sorted alphabetically"""
    import json
    
    realm_dir = realms_path / realm_name
    json_file = realm_dir / f"{realm_name}.json"
    
    if json_file.exists():
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                objects = json.load(f)
                # Sort alphabetically by ObjectName
                return sorted(objects, key=lambda x: x.get('ObjectName', '').lower())
        except Exception as e:
            print(f"✗ Error loading JSON: {e}")
            return []
    return []


def format_source_editor_preview(page_data: dict) -> str:
    """Format object page data as it would appear in wiki source editor"""
    from wiki.generators import ObjectPageGenerator
    
    obj = page_data.get('object', {})
    
    # Generate actual wiki markup
    markup = ObjectPageGenerator.generate_wiki_markup(
        name=obj.get('name', 'Unknown'),
        difficulty=obj.get('difficulty', 'Unknown'),
        area=obj.get('area', 'Unknown'),
        hint=obj.get('hint', ''),
        info=obj.get('info', ''),
        obtaining=obj.get('obtaining', ''),
        image=obj.get('image', ''),
        background=obj.get('background', ''),
        previous_difficulties=obj.get('previousDifficulties', '')
    )
    
    return markup



def check_object_pages(realm_name: str, realms_path: Path) -> dict:
    """Check which objects have wiki pages on ftbc.fandom.com (cached)"""
    import json
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    pages_status = {}
    objects = load_realm_objects(realm_name, realms_path)
    
    # Create cache file path
    cache_dir = Path(Config.REALMS_PATH) / ".cache"
    cache_file = cache_dir / f"{realm_name}_pages.json"
    
    # Try to load from cache first
    if cache_file.exists():
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Build cache by checking wiki (parallel with threading)
    print(f"  Building wiki cache for {realm_name}... (checking {len(objects)} objects)")
    
    def check_object_page(obj_name: str) -> tuple:
        """Check if single object has wiki page"""
        if not obj_name:
            return (obj_name, "[NO]")
        
        wiki_url = f"https://ftbc.fandom.com/wiki/{obj_name.replace(' ', '_')}"
        try:
            import urllib.request
            import socket
            socket.setdefaulttimeout(1.0)  # 1 second timeout
            
            # Try HEAD request first with User-Agent
            req = urllib.request.Request(wiki_url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            try:
                with urllib.request.urlopen(req) as response:
                    return (obj_name, "✓" if response.status == 200 else "[NO]")
            except urllib.error.HTTPError as e:
                # If 404 or other client error, page doesn't exist
                if e.code == 404:
                    return (obj_name, "[NO]")
                # For other errors, try GET as fallback
                raise
            except:
                # If HEAD fails, try GET
                req = urllib.request.Request(wiki_url)
                req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                with urllib.request.urlopen(req) as response:
                    # If GET succeeds, page exists
                    return (obj_name, "✓" if response.status == 200 else "[NO]")
        except urllib.error.HTTPError as e:
            # 404 means page doesn't exist
            if e.code == 404:
                return (obj_name, "[NO]")
            # Other HTTP errors treated as page doesn't exist
            return (obj_name, "[NO]")
        except:
            # Network errors or timeouts treated as unknown
            return (obj_name, "[NO]")
    
    # Check objects in parallel (max 10 threads)
    checked = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_object_page, obj.get('ObjectName', '')): obj for obj in objects}
        
        for future in as_completed(futures):
            obj_name, status = future.result()
            pages_status[obj_name] = status
            checked += 1
            
            # Show progress every 25 objects
            if checked % 25 == 0:
                print(f"    Checked {checked}/{len(objects)}...")
    
    print(f"    Done! Found {sum(1 for v in pages_status.values() if v == '✓')} pages")
    
    # Cache the results
    try:
        cache_dir.mkdir(exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(pages_status, f)
    except:
        pass
    
    return pages_status


def display_help():
    """Display help menu"""
    print("\n" + "="*60)
    print("FTBC Wiki System v6.0 - Help")
    print("="*60)
    print("\nAvailable Commands:")
    print("  realms              - Display all realms and subrealms")
    print("  create              - Create a new realm page")
    print("  help                - Show this help menu")
    print("  exit                - Exit the program")
    print("="*60 + "\n")


def edit_object_page(realm_name: str, area_name: str, obj_data: dict, object_pages: dict) -> str:
    """Edit or create object wiki page. Returns 'create', 'realm', 'area', or 'exit'"""
    import json
    from wiki.generators import ObjectPageGenerator
    from wiki.templates import TemplateLoader
    
    obj_name = obj_data.get('ObjectName', 'Unknown')
    difficulty = obj_data.get('Difficulty', 'Unknown')
    area = area_name  # Use the selected area/subrealm
    hint = obj_data.get('Description', '')
    
    page_exists = object_pages.get(obj_name, "[NO]") == "✓"
    
    print("\n" + "="*60)
    print(f"Object: {obj_name} {'[EXISTS]' if page_exists else '[CREATE]'}")
    print("="*60)
    print(f"Difficulty: {difficulty}")
    print(f"Area: {area}")
    print(f"Hint: {hint}\n")
    
    # Get player input for INFO section (multi-line)
    print("Enter INFO section (description).")
    print("(Type lines of text, then press Enter twice to finish):")
    info_lines = []
    while True:
        line = input()
        if line == "":
            if info_lines and info_lines[-1] == "":
                info_lines.pop()  # Remove the extra empty line
                break
            info_lines.append("")
        else:
            info_lines.append(line)
    info_text = "\n".join(info_lines).strip()
    
    print("\nEnter OBTAINING section (how to get it).")
    print("(Type lines of text, then press Enter twice to finish):")
    obtaining_lines = []
    while True:
        line = input()
        if line == "":
            if obtaining_lines and obtaining_lines[-1] == "":
                obtaining_lines.pop()  # Remove the extra empty line
                break
            obtaining_lines.append("")
        else:
            obtaining_lines.append(line)
    obtaining_text = "\n".join(obtaining_lines).strip()
    
    # Ask for additional metadata
    print("\nEnter image file name (press Enter to use default: {}.png):".format(obj_name))
    image = input("> ").strip() or f"{obj_name}.png"
    
    print("\nEnter previous difficulties (if any, e.g., 'Insane, Hard'):")
    previous_difficulties = input("> ").strip()
    
    # Generate page using template
    page_data = ObjectPageGenerator.generate_object_page(
        obj_name, 
        difficulty, 
        area, 
        hint, 
        info_text, 
        obtaining_text,
        image=image
    )
    
    # Also store the wiki markup for easy copying
    wiki_markup = ObjectPageGenerator.generate_wiki_markup(
        obj_name,
        difficulty,
        area,
        hint,
        info_text,
        obtaining_text,
        image=image,
        previous_difficulties=previous_difficulties
    )
    
    # Store markup in the data for reference
    page_data['wiki_markup'] = wiki_markuphh
    
    page_data['object']['image'] = image
    page_data['object']['previousDifficulties'] = previous_difficulties
    
    # Display source editor preview
    print("\n" + "="*60)
    print("Source Editor Preview (Copy & Paste into Fandom):")
    print("="*60)
    print(wiki_markup)
    
    print("\n" + "="*60)
    print("Save this page? (yes/no):")
    confirm = input("> ").strip().lower()
    
    if confirm == 'yes':
        # Save the page data
        cache_dir = Path(Config.REALMS_PATH) / f"{realm_name}" / "objects"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        page_file = cache_dir / f"{obj_name}.json"
        
        try:
            with open(page_file, 'w', encoding='utf-8') as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Page saved to {page_file}")
        except Exception as e:
            print(f"[ERR] Failed to save: {e}")
            print("[OK] Page not saved")
            return 'exit'
        
        # Ask if user wants to publish to wiki
        print("\n" + "="*60)
        print("Publish to Fandom wiki now? (yes/no):")
        publish_confirm = input("> ").strip().lower()
        
        if publish_confirm == 'yes':
            publish_to_fandom(obj_name, wiki_markup, realm_name)
    else:
        print("[OK] Page not saved")
    
    # Prompt for next action
    print("\n" + "="*60)
    print("What would you like to do?")
    print("="*60)
    print("(1) Create another object page")
    print("(2) Choose another realm")
    print("(3) Exit")
    print()
    
    choice = input("> ").strip().lower()
    
    if choice == '1':
        return 'create'
    elif choice == '2':
        return 'realm'
    else:
        return 'exit'


def display_help():
    """Display help menu"""
    print("\n" + "="*60)
    print("FTBC Wiki System v6.0 - Help")
    print("="*60)
    print("\nAvailable Commands:")
    print("  realms              - Display all realms and subrealms")
    print("  create              - Create a new realm page")
    print("  setup               - Setup Fandom credentials for publishing")
    print("  help                - Show this help menu")
    print("  exit                - Exit the program")
    print("="*60 + "\n")


def publish_to_fandom(page_title: str, markup: str, realm_name: str):
    """Publish a page to Fandom wiki using bot credentials"""
    from wiki.publishers import FandomPublisher, load_credentials
    
    # Load saved credentials
    creds = load_credentials()
    
    if not creds.get('username') or not creds.get('password'):
        print("\n[ERR] No bot credentials saved.")
        print("Run 'setup' command to configure bot publishing.")
        return
    
    print(f"\n[...] Publishing with bot: {creds['username']}")
    publisher = FandomPublisher(creds['username'], creds['password'])
    
    success, msg = publisher.login()
    if not success:
        print(f"[ERR] {msg}")
        return
    
    print("[OK] Bot logged in to Fandom")
    
    # Check if page exists
    success, exists = publisher.check_page_exists(page_title)
    if success:
        action = "Updating" if exists else "Creating"
        print(f"[...] {action} page: {page_title}")
    
    # Publish the page
    success, msg = publisher.publish_page(
        page_title, 
        markup, 
        summary=f"Updated object page via FTBC Wiki Bot"
    )
    
    if success:
        print(f"[OK] {msg}")
    else:
        print(f"[ERR] {msg}")


def setup_fandom_credentials():
    """Setup Fandom bot login credentials"""
    from wiki.publishers import save_credentials, load_credentials
    
    print("\n" + "="*60)
    print("Fandom Bot Credentials Setup")
    print("="*60)
    print("\nEnter your bot's Fandom username:")
    print("(e.g., ChruustGaming@Spongybot)")
    username = input("> ").strip()
    
    if not username:
        print("[ERR] Username cannot be empty")
        return
    
    print("\nEnter your bot's Fandom password:")
    password = input("> ").strip()
    
    if not password:
        print("[ERR] Password cannot be empty")
        return
    
    # Test credentials
    from wiki.publishers import FandomPublisher
    print("\n[...] Testing bot credentials...")
    publisher = FandomPublisher(username, password)
    success, msg = publisher.login()
    
    if not success:
        print(f"[ERR] {msg}")
        print("[ERR] Credentials not saved")
        return
    
    # Save credentials
    if save_credentials(username, password):
        print(f"[OK] Bot credentials saved for: {username}")
        print("[OK] Bot can now publish pages to the wiki!")
    else:
        print("[ERR] Failed to save credentials")


def main():
    """Main entry point"""
    realm_cmd = RealmCommands()
    
    print("\n[OK] FTBC Wiki System v6.0")
    print("Type 'help' for help, or 'exit' to leave the program\n")
    
    while True:
        try:
            user_input = input("> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == "realms":
                display_realms_list(realm_cmd)
            
            elif command == "create":
                create_realm_page(realm_cmd)
            
            elif command == "setup":
                setup_fandom_credentials()
            
            elif command == "help":
                display_help()
            
            elif command == "exit":
                print("\n[OK] Goodbye!")
                sys.exit(0)
            
            else:
                print(f"[ERR] Unknown command: '{command}'")
                print("Type 'help' for available commands")
        
        except KeyboardInterrupt:
            print("\n\n[OK] Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"[ERR] Error: {e}")


def display_realms_list(realm_cmd):
    """Display all realms with their subrealms in numbered list format"""
    realms = realm_cmd.list_realms()
    
    print("="*60)
    print("FTBC Wiki System v6.0 - Realms")
    print("="*60 + "\n")
    
    for idx, realm in enumerate(realms, 1):
        print(f"({idx}) {realm}")
        try:
            subrealms = realm_cmd.list_subrealms(realm)
            for sub in subrealms:
                print(f"  > {sub}")
        except:
            pass
    
    print("\n" + "="*60)
    print("Commands: help, exit")
    print("="*60)


def create_realm_page(realm_cmd):
    """Interactive realm page creation with fuzzy matching"""
    all_realms = realm_cmd.list_realms()
    pages_status = check_realm_pages(Path(Config.REALMS_PATH))
    
    # Remove .cache from realm list if present
    all_realms = [r for r in all_realms if r != '.cache']
    
    selected_realm = None
    selected_area = None
    
    while True:
        if selected_realm is None:
            # Realm selection mode
            print("\n" + "="*60)
            print("Create Realm Page - Search Realms")
            print("="*60)
            print("Enter realm name to search (or 'back' to return):\n")
            
            search_input = input("> ").strip()
            
            if search_input.lower() == 'back':
                return
            
            if not search_input:
                print("[ERR] Please enter a search term")
                continue
            
            # Try to parse as number first
            try:
                idx = int(search_input) - 1
                if 0 <= idx < len(all_realms):
                    selected_realm = all_realms[idx]
                    continue
                else:
                    print(f"[ERR] Number out of range (1-{len(all_realms)})")
                    continue
            except ValueError:
                pass
            
            # Fuzzy match by name
            matches = fuzzy_match(search_input, all_realms)
            
            if not matches:
                print(f"[ERR] No realms found matching '{search_input}'")
                continue
            
            if len(matches) == 1:
                selected_realm = matches[0]
                continue
            else:
                # Multiple matches - let user choose
                print(f"\nFound {len(matches)} realms:\n")
                for idx, realm in enumerate(matches, 1):
                    status = pages_status.get(realm, "[NO]")
                    print(f"({idx}) {status} {realm}")
                
                print("\nEnter number to select (or 'back'):")
                choice_input = input("> ").strip()
                
                if choice_input.lower() == 'back':
                    continue
                
                try:
                    choice_idx = int(choice_input) - 1
                    if 0 <= choice_idx < len(matches):
                        selected_realm = matches[choice_idx]
                        continue
                    else:
                        print(f"[ERR] Invalid selection")
                except ValueError:
                    print("[ERR] Please enter a valid number")
        
        elif selected_area is None:
            # Area/Subrealm selection mode
            subrealms = Config.get_subrealms(selected_realm)
            
            if subrealms:
                print("\n" + "="*60)
                print(f"Realm: {selected_realm} - Select Area/Subrealm")
                print("="*60)
                print(f"\nAvailable subrealms:\n")
                
                for idx, subrealm in enumerate(subrealms, 1):
                    print(f"({idx}) {subrealm}")
                
                print(f"\n(0) No subrealm - use main realm only")
                print("\nEnter number to select (or 'back'):")
                
                choice_input = input("> ").strip()
                
                if choice_input.lower() == 'back':
                    selected_realm = None
                    continue
                
                try:
                    choice_idx = int(choice_input)
                    if choice_idx == 0:
                        selected_area = selected_realm
                    elif 0 < choice_idx <= len(subrealms):
                        selected_area = f"{selected_realm}/{subrealms[choice_idx - 1]}"
                    else:
                        print(f"[ERR] Invalid selection")
                        continue
                except ValueError:
                    print("[ERR] Please enter a valid number")
                    continue
            else:
                # No subrealms for this realm
                selected_area = selected_realm
        else:
            # Object selection and editing mode
            next_action = display_realm_create_page(realm_cmd, selected_realm, selected_area, pages_status)
            
            if next_action == 'create':
                # Create another object in same area
                continue
            elif next_action == 'realm':
                # Choose another realm
                selected_realm = None
                selected_area = None
                continue
            elif next_action == 'area':
                # Choose another area in same realm
                selected_area = None
                continue
            else:
                # Exit
                return


def get_area_from_object(realm_name: str, obj_data: dict) -> str:
    """Auto-detect area/subrealm from object's Section field"""
    section = obj_data.get('Section', '')
    if section:
        subrealm = Config.get_subrealm_from_section(section)
        if subrealm:
            return f"{realm_name}/{subrealm}"
    return realm_name


def display_realm_create_page(realm_cmd, realm_name: str, area_name: str, pages_status: dict) -> str:
    """Display realm objects for editing with page status. Returns 'create', 'realm', 'area', or 'exit'"""
    print("\n" + "="*60)
    print(f"Realm: {realm_name}")
    if area_name != realm_name:
        print(f"Area: {area_name}")
    print("Objects")
    print("="*60)
    
    # Load objects from JSON (already sorted alphabetically)
    objects = load_realm_objects(realm_name, Path(Config.REALMS_PATH))
    object_pages = check_object_pages(realm_name, Path(Config.REALMS_PATH))
    
    if not objects:
        print("\n[ERR] No objects found in realm JSON")
        return 'realm'
    
    print(f"\nObjects ({len(objects)}):\n")
    
    for idx, obj in enumerate(objects, 1):
        obj_name = obj.get('ObjectName', 'Unknown')
        difficulty = obj.get('Difficulty', 'Unknown')
        
        # Check if object has a wiki page
        status = object_pages.get(obj_name, "[x]")
        
        # Convert Unicode symbols to simple format
        if "✓" in status or "\u2713" in status:
            page_status = "[+]"
        else:
            page_status = "[x]"
        
        print(f"({idx}) {obj_name} {page_status}")
        print(f"    Difficulty: {difficulty}")
    
    # Count pages
    with_pages = sum(1 for v in object_pages.values() if "✓" in v or "\u2713" in v)
    without_pages = sum(1 for v in object_pages.values() if "[NO]" in v or "\u2717" in v or (v != "✓" and v != "\u2713" and "[NO]" not in v and "\u2717" not in v))
    
    print("\n" + "="*60)
    print(f"Total: {len(objects)} objects")
    print(f"  [+] WITH PAGE  : {with_pages}")
    print(f"  [x] NO PAGE    : {without_pages}")
    print("="*60)
    print("\nEnter object number to edit/create (or 'back'):")
    
    edit_input = input("> ").strip()
    
    if edit_input.lower() == 'back':
        # If we have subrealms, go back to area selection, otherwise go to realm selection
        subrealms = Config.get_subrealms(realm_name)
        if subrealms and area_name != realm_name:
            return 'area'
        return 'realm'
    
    try:
        obj_idx = int(edit_input) - 1
        if 0 <= obj_idx < len(objects):
            selected_obj = objects[obj_idx]
            # Auto-detect area from object's Section field
            detected_area = get_area_from_object(realm_name, selected_obj)
            return edit_object_page(realm_name, detected_area, selected_obj, object_pages)
        else:
            print(f"[ERR] Invalid object number")
            return 'create'
    except ValueError:
        print("[ERR] Please enter a valid number")
        return 'create'


if __name__ == "__main__":
    main()
