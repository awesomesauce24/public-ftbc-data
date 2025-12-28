#!/usr/bin/env python3
"""
Wiki Page Management - Create, format, and manage wiki object pages.

This module handles:
- Creating new wiki pages (create_object_in_realm)
- Formatting pages to new template (update_realm_format, reformat_and_stub_all_realms)
- Fetching and parsing wiki content (fetch_wiki_source, parse_old_format)
- Batch operations on realms
- Stub creation for missing/incomplete pages

PUBLIC API (called from main.py):
  - create(session)         : Create a new wiki object page
  - update_realm(session)   : Update realm pages from wiki
  - update_realm_format(session) : Format pages + create stubs
"""

import json
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from difflib import SequenceMatcher


# ============================================================================
# UTILITY FUNCTIONS - Data loading and configuration
# ============================================================================

def load_json(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[x] Error loading {filepath}: {e}")
        return {}


def get_special_case(realm_name):
    """Get special case formatting for a realm."""
    special_cases = load_json('metadata/special_cases.json')
    
    for realm, config in special_cases.get('special_cases', {}).items():
        if realm.lower() == realm_name.lower():
            return config
    
    return {}


def list_realms_and_subrealms_hierarchical():
    """List all realms and subrealms with hierarchy."""
    realms_dir = Path('metadata/realms')
    subrealms_dir = Path('metadata/subrealms')
    
    # Items that should only appear as subrealms, not realms
    subrealm_only = {'Zombie Apocalypse', 'nihilism', 'stairwell'}
    
    items = []  # List of (number, name, path, is_subrealm, parent, item_type)
    counter = 1
    
    # Collect all subrealm names to avoid duplicates
    all_subrealm_names = set()
    
    # First, get all realms sorted with Main Realm first
    all_realms = []
    if realms_dir.exists():
        for realm_dir in sorted(realms_dir.iterdir()):
            if realm_dir.is_dir():
                all_realms.append(realm_dir.name)
    
    # Collect subrealm names from Main Realm (Goiky)
    main_realm_goiky_dir = realms_dir / 'Main Realm (Goiky)'
    if main_realm_goiky_dir.exists():
        for sub_dir in main_realm_goiky_dir.iterdir():
            if sub_dir.is_dir():
                all_subrealm_names.add(sub_dir.name)
    
    # Collect from The Backrooms nested subrealms
    backrooms_dir = Path('metadata/subrealms/subrealms/The Backrooms')
    if backrooms_dir.exists():
        for sub_dir in backrooms_dir.iterdir():
            if sub_dir.is_dir():
                all_subrealm_names.add(sub_dir.name)
    
    # Collect from other top-level subrealms in metadata/subrealms
    if subrealms_dir.exists():
        for item in subrealms_dir.iterdir():
            if item.is_dir() and item.name != 'subrealms':
                all_subrealm_names.add(item.name)
    
    # Filter out Backrooms variants and subrealm-only names (not in realms directory)
    backrooms_variants = [r for r in all_realms if r.startswith('The Backrooms')]
    backrooms_levels = [r for r in backrooms_variants if r != 'The Backrooms Level']
    for variant in backrooms_variants:
        all_realms.remove(variant)
    
    # Remove ONLY subrealm-only names (those not actually in realms directory)
    # Keep realms that happen to also have subrealms
    subrealm_only_names = all_subrealm_names - set(all_realms)
    all_realms = [r for r in all_realms if r not in subrealm_only_names and r not in subrealm_only]
    
    if 'Main Realm' in all_realms:
        all_realms.remove('Main Realm')
        all_realms = ['Main Realm'] + sorted(all_realms)
    else:
        all_realms = sorted(all_realms)
    
    # Add realms and their subrealms
    for realm_name in all_realms:
        items.append((counter, realm_name, f'metadata/realms/{realm_name}', False, None, 'realm'))
        counter += 1
        
        # Check for subrealms in this realm
        realm_subrealms_dir = realms_dir / realm_name
        if realm_subrealms_dir.exists():
            subrealms_in_realm = []
            for sub_dir in sorted(realm_subrealms_dir.iterdir()):
                if sub_dir.is_dir():
                    subrealms_in_realm.append(sub_dir.name)
            
            for subrealm_name in sorted(subrealms_in_realm):
                items.append((counter, f"  → {subrealm_name}", f'metadata/realms/{realm_name}/{subrealm_name}', True, realm_name, 'nested_subrealm'))
                counter += 1
    
    # Mark where subrealms section begins
    subrealms_start = counter
    
    # Handle The Backrooms specially - use A1, A2, A3 format
    subrealm_letter = 'A'
    subrealm_counter = 1
    
    # Create display label for The Backrooms
    backrooms_label = f'{subrealm_letter}{subrealm_counter}'
    items.append((backrooms_label, 'The Backrooms', f'metadata/subrealms/The Backrooms/The Backrooms', False, None, 'subrealm'))
    subrealm_counter += 1
    
    # Add Backrooms levels from subrealms directory
    backrooms_levels_dir = subrealms_dir / 'The Backrooms' / 'The Backrooms'
    if backrooms_levels_dir.exists():
        for level_dir in sorted(backrooms_levels_dir.iterdir()):
            if level_dir.is_dir():
                level_name = level_dir.name
                items.append((f'{subrealm_letter}{subrealm_counter}', f"  → {level_name}", f'metadata/subrealms/The Backrooms/The Backrooms/{level_name}', True, 'The Backrooms', 'nested_subrealm'))
                subrealm_counter += 1
    
    # Move to next letter for next subrealm
    subrealm_letter = chr(ord(subrealm_letter) + 1)
    subrealm_counter = 1
    
    # Also check for subrealms directory structure
    if subrealms_dir.exists():
        for top_level in sorted(subrealms_dir.iterdir()):
            if not top_level.is_dir():
                continue
            
            # Skip if it's just a single folder named 'subrealms'
            if top_level.name == 'subrealms':
                # Handle nested structure - these are sub-subrealms
                for nested in sorted(top_level.iterdir()):
                    if nested.is_dir():
                        # Skip The Backrooms if already added
                        if nested.name == 'The Backrooms':
                            continue
                        
                        items.append((f'{subrealm_letter}{subrealm_counter}', nested.name, f'metadata/subrealms/subrealms/{nested.name}', False, None, 'subrealm'))
                        subrealm_counter += 1
                        
                        # Add sub-subrealms
                        for sub_nested in sorted(nested.iterdir()):
                            if sub_nested.is_dir():
                                items.append((f'{subrealm_letter}{subrealm_counter}', f"  → {sub_nested.name}", f'metadata/subrealms/subrealms/{nested.name}/{sub_nested.name}', True, nested.name, 'nested_subrealm'))
                                subrealm_counter += 1
                        
                        # Move to next letter
                        subrealm_letter = chr(ord(subrealm_letter) + 1)
                        subrealm_counter = 1
                continue
            
            # For other top-level subrealms not in realms and not already added
            if top_level.name not in all_realms and top_level.name != 'The Backrooms':
                items.append((f'{subrealm_letter}{subrealm_counter}', top_level.name, f'metadata/subrealms/{top_level.name}', False, None, 'subrealm'))
                subrealm_counter += 1
                
                for sub in sorted(top_level.iterdir()):
                    if sub.is_dir():
                        items.append((f'{subrealm_letter}{subrealm_counter}', f"  → {sub.name}", f'metadata/subrealms/{top_level.name}/{sub.name}', True, top_level.name, 'nested_subrealm'))
                        subrealm_counter += 1
                
                # Move to next letter
                subrealm_letter = chr(ord(subrealm_letter) + 1)
                subrealm_counter = 1
    
    return items


def check_wiki_page_exists(obj_name):
    """Check if a wiki page exists for an object."""
    url = f"https://ftbc.fandom.com/wiki/{obj_name.replace(' ', '_')}"
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def get_difficulty_info(difficulty_name):
    """Get icon, hex color, proper capitalization, and priority for a difficulty."""
    difficulties = load_json('metadata/difficulties.json')
    
    for diff in difficulties.get('difficulties', []):
        if diff.get('name', '').lower() == difficulty_name.lower():
            return (diff.get('icon', ''), 
                    diff.get('hex', '#000000'), 
                    diff.get('name', difficulty_name),
                    diff.get('priority', 0))
    
    return '', '#000000', difficulty_name, 0


def get_realm_gradient(realm_name):
    """Get gradient and accent color for a realm."""
    gradients = load_json('metadata/realm_gradients.json')
    
    # Search in realms
    for realm in gradients.get('realms', []):
        if realm.get('label', '') == realm_name:
            return realm.get('gradient', ''), realm.get('accent', '#ffffff'), realm.get('image', '')
    
    # Search in subrealms
    for subrealm in gradients.get('subrealms', []):
        if subrealm.get('label', '') == realm_name:
            return subrealm.get('gradient', ''), subrealm.get('accent', '#ffffff'), subrealm.get('image', '')
    
    return '', '#ffffff', ''


def find_fuzzy_matches(user_input, available_objects, threshold=0.6):
    """Find fuzzy matches for user input from available objects."""
    if not user_input or not available_objects:
        return []
    
    matches = []
    for obj_name in available_objects:
        # Case-insensitive comparison
        ratio = SequenceMatcher(None, user_input.lower(), obj_name.lower()).ratio()
        if ratio >= threshold:
            matches.append((obj_name, ratio))
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x[1], reverse=True)
    return [obj_name for obj_name, _ in matches[:10]]  # Return top 10 matches


# ============================================================================
# WIKI INTERACTION - Fetching and uploading content
# ============================================================================

def upload_wiki_page(session, obj_name, wiki_markup):
    """Upload wiki page content using the authenticated session."""
    wiki_url = "https://ftbc.fandom.com"
    api_url = f"{wiki_url}/api.php"
    
    try:
        print(f"\n[*] Uploading '{obj_name}' to wiki...", end=" ", flush=True)
        
        # Get CSRF token for editing
        response = session.get(
            api_url,
            params={
                "action": "query",
                "meta": "tokens",
                "type": "csrf",
                "format": "json",
            },
            timeout=10
        )
        response.raise_for_status()
        csrf_token = response.json()["query"]["tokens"]["csrftoken"]
        
        # Upload the page
        response = session.post(
            api_url,
            data={
                "action": "edit",
                "title": obj_name,
                "text": wiki_markup,
                "summary": "Edited by Spongybot v7.0!",
                "token": csrf_token,
                "format": "json",
            },
            timeout=10
        )
        response.raise_for_status()
        
        result = response.json()
        if "edit" in result and result["edit"].get("result") == "Success":
            print("✓ Upload successful!")
            print(f"[+] Page live at: {wiki_url}/wiki/{obj_name.replace(' ', '_')}")
            return True
        else:
            error_msg = result.get("edit", {}).get("result", "Unknown error")
            print(f"✗ Upload failed: {error_msg}")
            return False
    
    except requests.RequestException as e:
        print(f"✗ Network error: {e}")
        return False
    except (KeyError, ValueError) as e:
        print(f"✗ API error: {e}")
        return False


def fetch_wiki_source(obj_name):
    """Fetch the wiki source code (wikitext) for an object.
    
    Returns tuple of (content, actual_title) where actual_title is the proper case from wiki.
    Uses multiple retry strategies for robustness.
    """
    wiki_url = "https://ftbc.fandom.com"
    api_url = f"{wiki_url}/api.php"
    
    # Try the exact name first, then variations
    names_to_try = [
        obj_name,
        obj_name.replace(' ', '_'),
        obj_name.title(),
    ]
    
    for attempt_name in names_to_try:
        try:
            response = requests.get(
                api_url,
                params={
                    "action": "query",
                    "titles": attempt_name,
                    "prop": "revisions",
                    "rvprop": "content",
                    "format": "json",
                },
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            pages = result.get("query", {}).get("pages", {})
            
            if pages:
                # Get first page (should only be one)
                page = next(iter(pages.values()))
                
                # Check if page exists (no "missing" key)
                if "missing" not in page and "revisions" in page:
                    # Get the content from the first (most recent) revision
                    content = page["revisions"][0].get("*", "")
                    actual_title = page.get("title", obj_name)  # Get actual case from wiki
                    if content:
                        return content, actual_title
        except Exception:
            continue
    
    return None, obj_name


def update_realm(session):
    """Update all object pages from a realm by fetching wiki source."""
    print()
    print("=" * 60)
    print("UPDATE REALM PAGES")
    print("=" * 60)
    
    # Step 1: Select realm/subrealm
    items = list_realms_and_subrealms_hierarchical()
    
    print("\nREALMS:")
    print()
    
    # Find where subrealms start
    first_subrealm_idx = None
    for i, item in enumerate(items):
        if isinstance(item[0], str) and item[0][0].isalpha():
            first_subrealm_idx = i
            break
    
    print("(@) Update ALL realms (batch mode)")
    print()
    
    for i, item in enumerate(items):
        number, name, path, is_subrealm, parent, item_type = item
        
        if first_subrealm_idx and i == first_subrealm_idx:
            print()
            print("-" * 60)
            print()
            print("SUBREALMS:")
            print()
        
        print(f"  ({number}) {name}")
    
    try:
        choice = input("\nEnter number or label (or @ for all): ").strip()
        
        # Check for @ option (all realms)
        if choice == "@":
            return update_all_realms(session)
        
        # Find matching item
        selected_item = None
        for item in items:
            if str(item[0]) == choice:
                selected_item = item
                break
        
        if not selected_item:
            print("[x] Invalid selection")
            return False
        
        selected_number, selected_realm, selected_path, is_subrealm, parent_realm, item_type = selected_item
    except (ValueError, IndexError):
        print("[x] Invalid selection")
        return False
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    print(f"\n[+] Selected: {selected_realm.lstrip('→ ')}")
    
    # Step 2: Get objects from metadata
    realm_dir = Path(selected_path)
    
    if not realm_dir.exists():
        print(f"[x] Directory not found: {realm_dir}")
        return False
    
    objects = []
    for obj_file in sorted(realm_dir.glob('*.json')):
        objects.append(obj_file.stem)
    
    if not objects:
        print(f"[!] No objects found in {realm_dir}")
        return False
    
    print(f"\n[+] Found {len(objects)} objects")
    print("    Fetching from wiki...")
    
    # Step 3: Fetch and save each page
    output_dir = Path(selected_path.replace('metadata', 'data'))
    output_dir.mkdir(parents=True, exist_ok=True)
    
    completed = 0
    saved = 0
    failed = 0
    
    for obj_name in objects:
        completed += 1
        percent = int((completed / len(objects)) * 100)
        progress_text = f"[{completed}/{len(objects)}] ({percent}%) fetching {obj_name}..."
        sys.stdout.write(f"\r\033[K{progress_text}")
        sys.stdout.flush()
        
        # Fetch from wiki
        source = fetch_wiki_source(obj_name)
        
        if source:
            # Save to file
            try:
                output_file = output_dir / f'{obj_name}.txt'
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(source)
                saved += 1
            except Exception:
                failed += 1
        else:
            failed += 1
    
    # Clear progress line
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    
    # Summary
    print()
    print(f"[+] Completed: {saved} saved, {failed} failed")
    
    if failed > 0:
        print(f"[!] {failed} pages could not be fetched (may not exist)")
    
    return True



    """Prompt for multiline input."""
    print(f"\n{prompt_text}")
    print("(Type lines of text, then press Enter twice to finish):")
    
    lines = []
    empty_count = 0
    
    try:
        while True:
            line = input("")
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append(line)
            else:
                empty_count = 0
                lines.append(line)
    except KeyboardInterrupt:
        return None
    
    # Remove trailing empty lines
    while lines and lines[-1] == "":
        lines.pop()
    
    return "\n".join(lines)


def update_all_realms(session):
    """Update all objects from all realms using parallel fetching."""
    print()
    print("=" * 60)
    print("UPDATING ALL REALMS (BATCH MODE)")
    print("=" * 60)
    
    # Get all realm directories from metadata
    realms_dir = Path('metadata/realms')
    if not realms_dir.exists():
        print("[x] metadata/realms directory not found")
        return False
    
    all_realms = sorted([d.name for d in realms_dir.iterdir() if d.is_dir()])
    print(f"\n[+] Found {len(all_realms)} realms to update")
    print()
    
    total_saved = 0
    total_failed = 0
    
    for realm_name in all_realms:
        realm_metadata_dir = realms_dir / realm_name
        output_dir = Path('data/realms') / realm_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get objects
        objects = sorted([obj.stem for obj in realm_metadata_dir.glob('*.json')])
        
        if not objects:
            print(f"[-] {realm_name}: 0 objects")
            continue
        
        print(f"[*] {realm_name} ({len(objects)} objects)")
        
        # Use ThreadPoolExecutor for parallel fetching
        completed = 0
        saved = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_name = {executor.submit(fetch_wiki_source, obj_name): obj_name for obj_name in objects}
            
            for future in as_completed(future_to_name):
                obj_name = future_to_name[future]
                completed += 1
                
                try:
                    source = future.result()
                except Exception:
                    source = None
                
                # Show progress
                percent = int((completed / len(objects)) * 100)
                sys.stdout.write(f"\r    [{completed}/{len(objects)}] ({percent}%) {obj_name:<40}")
                sys.stdout.flush()
                
                if source:
                    try:
                        output_file = output_dir / f'{obj_name}.txt'
                        with open(output_file, 'w', encoding='utf-8') as f:
                            f.write(source)
                        saved += 1
                    except Exception:
                        failed += 1
                else:
                    failed += 1
        
        # Clear progress line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
        
        print(f"    [+] {saved} saved, [!] {failed} failed")
        total_saved += saved
        total_failed += failed
    
    print()
    print("=" * 60)
    print(f"[+] BATCH UPDATE COMPLETE: {total_saved} saved, {total_failed} failed")
    print("=" * 60)
    
    return True


def create_object_page(session):
    """Main create object page workflow."""
    while True:
        if not create_object_in_realm(session):
            break


def create_object_in_realm(session):
    """Create a single object in a realm. Returns True to continue, False to exit."""
    print()
    print("=" * 60)
    print("CREATE WIKI OBJECT PAGE")
    print("=" * 60)
    
    # Step 1: Select realm/subrealm
    items = list_realms_and_subrealms_hierarchical()
    
    print("\nREALMS:")
    print()
    
    # Find where subrealms start (first item with string label like "A1")
    first_subrealm_idx = None
    for i, item in enumerate(items):
        if isinstance(item[0], str) and item[0][0].isalpha():
            first_subrealm_idx = i
            break
    
    for i, item in enumerate(items):
        number, name, path, is_subrealm, parent, item_type = item
        
        if first_subrealm_idx and i == first_subrealm_idx:
            print()
            print("-" * 60)
            print()
            print("SUBREALMS:")
            print()
        
        print(f"  ({number}) {name}")
    
    try:
        choice = input("\nEnter number or label: ").strip()
        
        # Find matching item
        selected_item = None
        for item in items:
            if str(item[0]) == choice:
                selected_item = item
                break
        
        if not selected_item:
            print("[x] Invalid selection")
            return False
        
        selected_number, selected_realm, selected_path, is_subrealm, parent_realm, item_type = selected_item
    except (ValueError, IndexError):
        print("[x] Invalid selection")
        return False
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    print(f"\n[+] Selected: {selected_realm.lstrip('→ ')}")
    
    # Step 2: List objects in selected realm/subrealm
    realm_dir = Path(selected_path)
    
    if not realm_dir.exists():
        print(f"[x] Directory not found: {realm_dir}")
        return False
    
    objects = []
    for obj_file in sorted(realm_dir.glob('*.json')):
        objects.append(obj_file.stem)
    
    # If no direct objects, check for Objects subdirectory
    if not objects:
        objects_subdir = realm_dir / 'Objects'
        if objects_subdir.exists():
            for obj_file in sorted(objects_subdir.glob('*.json')):
                objects.append(obj_file.stem)
    
    # If still no objects, check objects.json file
    if not objects:
        objects_file = realm_dir / 'objects.json'
        if objects_file.exists():
            try:
                objects_data = load_json(objects_file)
                if isinstance(objects_data.get('objects'), list):
                    objects = [obj.get('name', '') for obj in objects_data.get('objects', []) if obj.get('name')]
            except:
                pass
    
    print(f"\n[+] Found {len(objects)} objects")
    if not objects:
        print("    [!] No objects found in metadata")
        print("    [!] You may need to:")
        print("        - Populate the metadata/objects folder with object JSON files")
        print("        - Or provide the object name manually below")
    print("    Checking wiki pages (parallel requests)...")
    
    # Check which pages exist on wiki using parallel requests
    existing_pages = []
    new_pages = []
    
    total_objects = len(objects)
    completed = 0
    
    # Use ThreadPoolExecutor for parallel requests (up to 8 concurrent)
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all tasks
        future_to_name = {executor.submit(check_wiki_page_exists, obj_name): obj_name for obj_name in objects}
        
        # Process completed tasks
        for future in as_completed(future_to_name):
            obj_name = future_to_name[future]
            completed += 1
            
            try:
                exists = future.result()
            except Exception:
                exists = False
            
            # Update on same line with proper clearing
            percent = int((completed / total_objects) * 100) if total_objects > 0 else 0
            progress_text = f"[{completed}/{total_objects}] ({percent}%) checking {obj_name}..."
            # Use ANSI escape to clear line, then carriage return
            sys.stdout.write(f"\r\033[K{progress_text}")
            sys.stdout.flush()
            
            if exists:
                existing_pages.append(obj_name)
            else:
                new_pages.append(obj_name)
    
    # Clear the progress line and print results
    if total_objects > 0:
        sys.stdout.write("\r\033[K")  # Clear the progress line
        sys.stdout.flush()
    
    # Sort results: existing pages first, then new pages, both alphabetically (case-insensitive)
    existing_pages.sort(key=str.lower)
    new_pages.sort(key=str.lower)
    
    # Print summary with symbols
    print()
    for obj_name in existing_pages:
        print(f"    [+] {obj_name}")
    for obj_name in new_pages:
        print(f"    [x] {obj_name}")
    
    if existing_pages:
        print(f"\n    [+] {len(existing_pages)} pages already on wiki")
    if new_pages:
        print(f"    [+] {len(new_pages)} pages need to be created")
    
    # Step 3: Get object name
    print()
    if not objects:
        print("[!] No objects found in metadata for this location")
        print("[!] You can still create a page by entering the object name manually")
        print()
    
    try:
        obj_name = input("Object name to edit/create: ").strip()
        if not obj_name:
            print("[x] Object name required")
            return False
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    # Check for exact match first
    exact_match = None
    for obj in objects:
        if obj.lower() == obj_name.lower():
            exact_match = obj
            break
    
    # If no exact match, try fuzzy matching
    if not exact_match and objects:
        fuzzy_matches = find_fuzzy_matches(obj_name, objects, threshold=0.5)
        
        if fuzzy_matches:
            print(f"\n[!] No exact match for '{obj_name}'. Did you mean:")
            print()
            for i, match in enumerate(fuzzy_matches, 1):
                print(f"  ({i}) {match}")
            print(f"  ({len(fuzzy_matches) + 1}) Use '{obj_name}' as-is")
            print()
            
            try:
                choice = input("Select number: ").strip()
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(fuzzy_matches):
                        obj_name = fuzzy_matches[choice_num - 1]
                    elif choice_num == len(fuzzy_matches) + 1:
                        pass  # Use obj_name as-is
                    else:
                        print("[x] Invalid selection")
                        return False
            except KeyboardInterrupt:
                print("\nCancelled")
                return False
    
    # Capitalize object name properly (title case) for wiki lookup
    # This ensures "not canon" becomes "Not Canon" for wiki searches
    obj_name_for_wiki = obj_name.title() if not any(c.isupper() for c in obj_name) else obj_name
    
    # Step 4: Find or create object metadata
    obj_file = realm_dir / f'{obj_name}.json'
    
    # If object file doesn't exist, check Objects subdirectory
    if not obj_file.exists():
        objects_subdir = realm_dir / 'Objects'
        if objects_subdir.exists():
            obj_file = objects_subdir / f'{obj_name}.json'
    
    # If still not found, allow creating new
    if not obj_file.exists():
        print(f"[!] Object '{obj_name}' not found in metadata")
        print("[+] Will create new page (metadata can be created/updated later)")
    
    if check_wiki_page_exists(obj_name_for_wiki):
        print(f"[!] Wiki page already exists at https://ftbc.fandom.com/wiki/{obj_name_for_wiki.replace(' ', '_')}")
    else:
        print(f"[+] No wiki page found - this is a new object")
    
    # Load object data if it exists
    if obj_file.exists():
        obj_data = load_json(obj_file)
        print(f"[+] Found metadata for '{obj_name}'")
    else:
        obj_data = {}
        print(f"[!] No metadata file for '{obj_name}' - will use defaults")
    
    difficulty = obj_data.get('difficulty', 'Normal')
    area = selected_realm.lstrip('→ ')  # Remove arrow if subrealm
    hint = obj_data.get('description', '')
    
    # Determine location type for saving
    if selected_path.startswith('metadata/realms/'):
        location_type = 'realm'
    else:
        location_type = 'subrealm'
    
    # Step 5: Display object info
    print()
    print("=" * 60)
    print(f"Object: {obj_name} [CREATE]")
    print("=" * 60)
    print(f"Difficulty: {difficulty}")
    print(f"Area: {area}")
    print(f"Hint: {hint}")
    
    # Step 6: Get difficulty icon and color
    diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
    
    # Step 7: Get realm/subrealm gradient and image (use parent realm if subrealm)
    lookup_realm = parent_realm if parent_realm else area
    gradient, accent, bg_image = get_realm_gradient(lookup_realm)
    special_case = get_special_case(lookup_realm)
    # Step 6: Get difficulty icon and color
    diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
    
    # Step 7: Get realm/subrealm gradient and image
    gradient, accent, bg_image = get_realm_gradient(selected_realm)
    special_case = get_special_case(selected_realm)
    
    # Override with special case if applicable
    if special_case.get('custom_gradient'):
        gradient = special_case['custom_gradient']
    if special_case.get('custom_bg_image'):
        bg_image = special_case['custom_bg_image']
    
    # Step 8: Prompt for sections
    info = prompt_multiline("Enter INFO section (description).")
    if info is None:
        print("\nCancelled")
        return
    
    obtaining = prompt_multiline("Enter OBTAINING section (how to get it).")
    if obtaining is None:
        print("\nCancelled")
        return
    
    # Step 9: Image filename
    default_image = f"{obj_name}.png"
    try:
        image_input = input(f"\nEnter image file name (press Enter to use default: {default_image}): ").strip()
        image_filename = image_input if image_input else default_image
    except KeyboardInterrupt:
        print("\nCancelled")
        return
    
    # Step 10: Old image?
    try:
        old_image_input = input("\nDoes this object have an old image? (yes/no): ").strip().lower()
        has_old_image = old_image_input in ['yes', 'y']
    except KeyboardInterrupt:
        print("\nCancelled")
        return
    
    # Step 11: Previous difficulties
    try:
        prev_diff_input = input("\nEnter previous difficulties (if any, e.g., 'Insane, Hard'): ").strip()
        previous_difficulties = prev_diff_input if prev_diff_input else ""
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    # Step 12: Generate wiki markup
    print()
    print("=" * 60)
    print("Source Editor Preview (Copy & Paste into Fandom):")
    print("=" * 60)
    
    # Build character gallery
    gallery_markup = f"[[File:{image_filename}]]"
    if has_old_image:
        old_filename = image_filename.replace(".png", "") + " Old.png"
        gallery_markup += f"\n[[File:{old_filename}]]"
    
    # Build previous difficulties
    prev_diff_markup = ""
    if previous_difficulties:
        prev_diffs = [d.strip() for d in previous_difficulties.split(',')]
        for prev_diff in prev_diffs:
            prev_icon, prev_hex, prev_diff_proper, _ = get_difficulty_info(prev_diff)
            prev_diff_markup += f"\n[[File:{prev_icon}|link=]] <span style=\"color:{prev_hex}\">'''<b>{prev_diff_proper}</b>'''</span>"
    
    # Build categories
    categories = [
        f"[[Category:{difficulty_proper} Objects]]",
        "[[Category:Objects]]",
        f"[[Category:{area} Objects]]",
    ]
    
    # Build obtaining section (with collapsible if Dreadful or above)
    obtaining_markup = ""
    if difficulty_priority >= 11:  # Dreadful or above
        obtaining_markup = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
{obtaining}
</div>
</div>"""
    else:
        obtaining_markup = f"""== Obtaining ==
{obtaining}"""
    
    # Build static overlay if special case
    static_overlay = ""
    if special_case.get('static_overlay'):
        static_img = special_case.get('static_image', 'Staticbg.gif')
        static_opacity = special_case.get('static_opacity', 0.05)
        static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
    
    wiki_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{area}]]
|hint={hint}{prev_diff_markup}
}}}}

== Info ==
{info}

{obtaining_markup}

{chr(10).join(categories)}
</div>
</div>"""
    
    print(wiki_markup)
    
    # Step 13: Auto-save to file
    print()
    print("=" * 60)
    
    # Determine output directory based on selected path
    output_dir = Path(selected_path.replace('metadata', 'data'))
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f'{obj_name}.txt'
    
    # Save the wiki markup automatically
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(wiki_markup)
        
        print(f"[+] Page saved to: {output_file}")
    except Exception as e:
        print(f"[x] Error saving page: {e}")
        return False
    
    # Step 14: Offer to upload to wiki
    print()
    try:
        upload = input("Upload to wiki? (y/n): ").strip().lower()
        if upload == 'y':
            success = upload_wiki_page(session, obj_name, wiki_markup)
            if not success:
                print("[!] Page saved locally but upload failed. You can upload manually later.")
    except KeyboardInterrupt:
        print("\n[!] Upload cancelled. Page is saved locally.")
    
    # Step 15: Show continue menu
    print()
    print("=" * 60)
    print("What would you like to do next?")
    print("=" * 60)
    print("  (1) Create/edit another object in this realm")
    print("  (2) Choose another realm")
    print("  (3) Exit")
    print()
    
    try:
        choice = input("Select option (1-3): ").strip()
        
        if choice == '1':
            # Restart with same realm
            return True
        elif choice == '2':
            # Restart to choose new realm
            return True
        elif choice == '3':
            # Exit
            print("Exiting...")
            return False
        else:
            print("[x] Invalid choice, exiting...")
            return False
    except KeyboardInterrupt:
        print("\nExiting...")
        return False


# ============================================================================
# PARSING - Extract info from wiki content
# ============================================================================

def parse_old_format(content):
    """Parse old format .txt file and extract Info and Obtaining sections.
    
    Handles multiple formats:
    - Traditional: == Info == and == Obtaining ==
    - CharacterInfo template: extracts hint as info ONLY if no == Info == section
    - CharacterInfo template with == Info == section: uses the section (priority)
    """
    info = ""
    obtaining = ""
    hint_as_fallback = ""
    
    lines = content.split('\n')
    in_info = False
    in_obtaining = False
    has_info_section = False
    
    # First pass: check if there's an == Info == section
    for line in lines:
        lower_line = line.lower().strip()
        if any(x in lower_line for x in ['== character ==', '== info ==', '==info==', '== appearance ==', '==appearance==']):
            has_info_section = True
            break
    
    # First, try to extract hint from CharacterInfo as FALLBACK only
    if not has_info_section:
        for line in lines:
            if '|hint' in line.lower() and '=' in line:
                hint_match = line.split('|hint', 1)
                if len(hint_match) > 1:
                    hint_part = hint_match[1].strip()
                    if hint_part.startswith('='):
                        hint_part = hint_part[1:].strip()
                    # Remove closing brackets if present
                    hint_part = hint_part.rstrip('}').strip()
                    if hint_part and hint_part != '}}':
                        hint_as_fallback = hint_part
                        break
    
    # Then parse sections normally (this takes priority)
    for i, line in enumerate(lines):
        lower_line = line.lower().strip()
        
        # Stop if we hit a category or closing div
        if lower_line.startswith('[[category:') or line.strip().startswith('</'):
            in_info = False
            in_obtaining = False
            continue
        
        # Check for info section (multiple variations - with and without spaces)
        if any(x in lower_line for x in ['== character ==', '== info ==', '==info==', '== appearance ==', '==appearance==']):
            in_info = True
            in_obtaining = False
            info = ""  # Clear any fallback
            continue
        
        # Check for obtaining section (including misspellings and spacing variations)
        if any(x in lower_line for x in ['== obtaining ==', '==obtaining==', '== obataining ==', '==obataining==', '== obataining==', '==obataining ==']):
            in_info = False
            in_obtaining = True
            continue
        
        # Check if we've hit a new section (any == ... ==)
        if '==' in line and line.count('==') >= 2:
            if in_info or in_obtaining:
                in_info = False
                in_obtaining = False
        
        if in_info:
            info += line + '\n'
        elif in_obtaining:
            obtaining += line + '\n'
    
    # Clean up: strip closing divs and extra whitespace
    info = info.strip()
    obtaining = obtaining.strip()
    
    # Use fallback hint if no info section was found
    if not info and hint_as_fallback:
        info = hint_as_fallback
    
    # Remove trailing </div> tags
    while obtaining.endswith('</div>'):
        obtaining = obtaining[:-6].strip()
    
    return info, obtaining


# ============================================================================
# MAIN WORKFLOWS - Single realm operations
# ============================================================================

def update_realm_format(session):
    """Fetch pages from wiki, reformat to new template, and save as .txt files."""
    print()
    print("=" * 60)
    print("REFORMAT REALM PAGES (FROM WIKI)")
    print("=" * 60)
    
    # Step 1: Select realm/subrealm
    items = list_realms_and_subrealms_hierarchical()
    
    print("\nSelect realm/subrealm to reformat:")
    print()
    print("  (@) Reformat ALL realms")
    print()
    
    # Find where subrealms start
    first_subrealm_idx = None
    for i, item in enumerate(items):
        if isinstance(item[0], str) and item[0][0].isalpha():
            first_subrealm_idx = i
            break
    
    for i, item in enumerate(items):
        number, name, path, is_subrealm, parent, item_type = item
        
        if first_subrealm_idx and i == first_subrealm_idx:
            print()
            print("-" * 60)
            print()
        
        print(f"  ({number}) {name}")
    
    try:
        choice = input("\nEnter number, label, or @: ").strip()
        
        if choice == "@":
            return reformat_all_realms_from_wiki(session)
        
        # Find matching item
        selected_item = None
        for item in items:
            if str(item[0]) == choice:
                selected_item = item
                break
        
        if not selected_item:
            print("[x] Invalid selection")
            return False
        
        selected_number, selected_realm, selected_path, is_subrealm, parent_realm, item_type = selected_item
    except (ValueError, IndexError):
        print("[x] Invalid selection")
        return False
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    print(f"\n[+] Selected: {selected_realm.lstrip('→ ')}")
    
    # Step 2: Get objects from metadata
    metadata_dir = Path(selected_path)
    data_dir = Path(selected_path.replace('metadata', 'data'))
    
    if not metadata_dir.exists():
        print(f"[!] Metadata directory not found: {metadata_dir}")
        return False
    
    objects = sorted([obj.stem for obj in metadata_dir.glob('*.json')])
    
    if not objects:
        print(f"[!] No objects found in {metadata_dir}")
        return False
    
    # Step 3: Delete existing .txt files
    data_dir.mkdir(parents=True, exist_ok=True)
    existing_files = list(data_dir.glob('*.txt'))
    if existing_files:
        print(f"\n[*] Deleting {len(existing_files)} existing .txt files...")
        for f in existing_files:
            try:
                f.unlink()
            except Exception as e:
                print(f"[!] Could not delete {f.name}: {e}")
    
    print(f"\n[+] Found {len(objects)} objects")
    print("    Fetching from wiki and reformatting...")
    
    # Step 4: Fetch, reformat, and save each page
    completed = 0
    saved = 0
    failed = 0
    failed_files = []
    
    realm_name = selected_realm.lstrip('→ ')
    
    for obj_name in objects:
        completed += 1
        
        percent = int((completed / len(objects)) * 100)
        sys.stdout.write(f"\r[{completed}/{len(objects)}] ({percent}%) {obj_name:<40}")
        sys.stdout.flush()
        
        try:
            # Fetch from wiki
            source, actual_name = fetch_wiki_source(obj_name)
            
            if not source:
                failed += 1
                failed_files.append((obj_name, "Page not found on wiki"))
                continue
            
            # Use the actual name from wiki (handles case differences)
            obj_name = actual_name
            
            # Parse fetched content
            info, obtaining = parse_old_format(source)
            
            if not info:
                failed += 1
                failed_files.append((obj_name, "No info section in wiki page"))
                continue
            
            # Get metadata
            metadata_file = metadata_dir / f'{obj_name}.json'
            difficulty = 'Normal'
            hint = ''
            
            if metadata_file.exists():
                try:
                    obj_data = load_json(metadata_file)
                    difficulty = obj_data.get('difficulty', 'Normal')
                    hint = obj_data.get('description', '')
                except:
                    pass
            
            # Get difficulty info
            diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
            
            # Get realm info
            gradient, accent, bg_image = get_realm_gradient(realm_name)
            special_case = get_special_case(realm_name)
            
            if special_case.get('custom_gradient'):
                gradient = special_case['custom_gradient']
            if special_case.get('custom_bg_image'):
                bg_image = special_case['custom_bg_image']
            
            # Build categories
            categories = [
                f"[[Category:{difficulty_proper} Objects]]",
                "[[Category:Objects]]",
                f"[[Category:{realm_name} Objects]]",
            ]
            
            # Build obtaining section
            if difficulty_priority >= 11:  # Dreadful or above
                obtaining_markup = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
{obtaining}
</div>
</div>"""
            else:
                obtaining_markup = f"""== Obtaining ==
{obtaining}"""
            
            # Build static overlay
            static_overlay = ""
            if special_case.get('static_overlay'):
                static_img = special_case.get('static_image', 'Staticbg.gif')
                static_opacity = special_case.get('static_opacity', 0.05)
                static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
            
            # Build new format
            gallery_markup = f"[[File:{obj_name}.png]]"
            
            wiki_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
{info}

{obtaining_markup}

{chr(10).join(categories)}
</div>
</div>"""
            
            # Save reformatted file
            output_file = data_dir / f'{obj_name}.txt'
            output_file.write_text(wiki_markup, encoding='utf-8')
            saved += 1
            
        except Exception as e:
            failed += 1
            failed_files.append((obj_name, str(e)))
    
    # Clear progress line
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()
    
    # Summary
    print()






def reformat_all_realms_from_wiki(session):
    """Fetch and reformat all pages from all realms."""
    print()
    print("=" * 60)
    print("REFORMATTING ALL REALMS (FROM WIKI)")
    print("=" * 60)
    
    realms_dir = Path('metadata/realms')
    if not realms_dir.exists():
        print("[x] metadata/realms not found")
        return False
    
    all_realms = sorted([d.name for d in realms_dir.iterdir() if d.is_dir()])
    print(f"\n[+] Found {len(all_realms)} realms")
    print()
    
    total_saved = 0
    total_failed = 0
    
    for realm_name in all_realms:
        metadata_dir = realms_dir / realm_name
        data_dir = Path('data/realms') / realm_name
        
        # Get objects
        objects = sorted([obj.stem for obj in metadata_dir.glob('*.json')])
        
        if not objects:
            print(f"[-] {realm_name}: 0 objects")
            continue
        
        # Delete existing .txt files
        data_dir.mkdir(parents=True, exist_ok=True)
        existing_files = list(data_dir.glob('*.txt'))
        for f in existing_files:
            try:
                f.unlink()
            except:
                pass
        
        print(f"[*] {realm_name} ({len(objects)} objects)")
        
        # Use ThreadPoolExecutor for parallel fetching
        completed = 0
        saved = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_name = {executor.submit(fetch_wiki_source, obj_name): obj_name for obj_name in objects}
            
            for future in as_completed(future_to_name):
                original_obj_name = future_to_name[future]
                completed += 1
                
                try:
                    source, actual_name = future.result()
                    obj_name = actual_name  # Use corrected name from wiki
                except Exception:
                    source = None
                    obj_name = original_obj_name
                
                # Show progress
                percent = int((completed / len(objects)) * 100)
                sys.stdout.write(f"\r    [{completed}/{len(objects)}] ({percent}%) {obj_name:<40}")
                sys.stdout.flush()
                
                if source:
                    try:
                        # Parse fetched content
                        info, obtaining = parse_old_format(source)
                        
                        if not info:
                            failed += 1
                            continue
                        
                        # Get metadata
                        metadata_file = metadata_dir / f'{obj_name}.json'
                        difficulty = 'Normal'
                        hint = ''
                        
                        if metadata_file.exists():
                            try:
                                obj_data = load_json(metadata_file)
                                difficulty = obj_data.get('difficulty', 'Normal')
                                hint = obj_data.get('description', '')
                            except:
                                pass
                        
                        # Get difficulty info
                        diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
                        
                        # Get realm info
                        gradient, accent, bg_image = get_realm_gradient(realm_name)
                        special_case = get_special_case(realm_name)
                        
                        if special_case.get('custom_gradient'):
                            gradient = special_case['custom_gradient']
                        if special_case.get('custom_bg_image'):
                            bg_image = special_case['custom_bg_image']
                        
                        # Build categories
                        categories = [
                            f"[[Category:{difficulty_proper} Objects]]",
                            "[[Category:Objects]]",
                            f"[[Category:{realm_name} Objects]]",
                        ]
                        
                        # Build obtaining section
                        if difficulty_priority >= 11:
                            obtaining_markup = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
{obtaining}
</div>
</div>"""
                        else:
                            obtaining_markup = f"""== Obtaining ==
{obtaining}"""
                        
                        # Build static overlay
                        static_overlay = ""
                        if special_case.get('static_overlay'):
                            static_img = special_case.get('static_image', 'Staticbg.gif')
                            static_opacity = special_case.get('static_opacity', 0.05)
                            static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
                        
                        # Build new format
                        gallery_markup = f"[[File:{obj_name}.png]]"
                        
                        wiki_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
{info}

{obtaining_markup}

{chr(10).join(categories)}
</div>
</div>"""
                        
                        # Save reformatted file
                        output_file = data_dir / f'{obj_name}.txt'
                        output_file.write_text(wiki_markup, encoding='utf-8')
                        saved += 1
                    except Exception:
                        failed += 1
                else:
                    failed += 1
        
        # Clear progress line
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()
        
        print(f"    [+] {saved} saved, [!] {failed} failed")
        total_saved += saved
        total_failed += failed
    
    print()
    print("=" * 60)
    print(f"[+] BATCH REFORMAT COMPLETE: {total_saved} saved, {total_failed} failed")
    print("=" * 60)
    
    return True


# ============================================================================
# PUBLIC API - Entry points called from main.py
# ============================================================================

def create(session):
    """Entry point for create command."""
    try:
        create_object_page(session)
    except Exception as e:
        print(f"[x] Error: {e}")


# ============================================================================
# BATCH OPERATIONS - All realms at once
# ============================================================================

def reformat_and_stub_all_realms(session):
    """Format & create stubs for all realms at once."""
    print()
    print("=" * 60)
    print("FORMATTING ALL REALMS (+ CREATING STUBS)")
    print("=" * 60)
    
    realms_dir = Path('metadata/realms')
    if not realms_dir.exists():
        print("[x] metadata/realms not found")
        return False
    
    all_realms = sorted([d.name for d in realms_dir.iterdir() if d.is_dir()])
    print(f"\n[+] Found {len(all_realms)} realms\n")
    
    for realm_name in all_realms:
        metadata_dir = realms_dir / realm_name
        data_dir = Path('data/realms') / realm_name
        
        all_objects = sorted([obj.stem for obj in metadata_dir.glob('*.json')])
        
        if not all_objects:
            print(f"[-] {realm_name}: no objects")
            continue
        
        # Delete existing files
        data_dir.mkdir(parents=True, exist_ok=True)
        existing_files = list(data_dir.glob('*.txt')) + list(data_dir.glob('[x]*.txt'))
        for f in existing_files:
            try:
                f.unlink()
            except:
                pass
        
        print(f"[*] {realm_name} ({len(all_objects)} objects)")
        
        saved = 0
        stubbed = 0
        failed = 0
        
        for obj_name in all_objects:
            try:
                source, actual_name = fetch_wiki_source(obj_name)
                obj_name = actual_name
                
                if not source:
                    # Create stub
                    try:
                        metadata_file = metadata_dir / f'{obj_name}.json'
                        if not metadata_file.exists():
                            for orig in all_objects:
                                if orig.lower() == obj_name.lower():
                                    metadata_file = metadata_dir / f'{orig}.json'
                                    break
                        
                        obj_data = load_json(metadata_file)
                        difficulty = obj_data.get('difficulty', 'Normal')
                        hint = obj_data.get('description', '')
                        
                        diff_icon, diff_hex, difficulty_proper, _ = get_difficulty_info(difficulty)
                        gradient, accent, bg_image = get_realm_gradient(realm_name)
                        special_case = get_special_case(realm_name)
                        
                        if special_case.get('custom_gradient'):
                            gradient = special_case['custom_gradient']
                        if special_case.get('custom_bg_image'):
                            bg_image = special_case['custom_bg_image']
                        
                        categories = [
                            f"[[Category:{difficulty_proper} Objects]]",
                            "[[Category:Objects]]",
                            f"[[Category:{realm_name} Objects]]",
                        ]
                        
                        static_overlay = ""
                        if special_case.get('static_overlay'):
                            static_img = special_case.get('static_image', 'Staticbg.gif')
                            static_opacity = special_case.get('static_opacity', 0.05)
                            static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
                        
                        gallery_markup = f"[[File:{obj_name}.png]]"
                        
                        stub_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
[TODO: Add info description here]

== Obtaining ==
[TODO: Add obtaining instructions here]

{chr(10).join(categories)}
</div>
</div>"""
                        
                        stub_file = data_dir / f'[x] {obj_name}.txt'
                        stub_file.write_text(stub_markup, encoding='utf-8')
                        stubbed += 1
                    except Exception:
                        failed += 1
                    continue
                
                # Reformat existing page
                info, obtaining = parse_old_format(source)
                
                if not info:
                    failed += 1
                    continue
                
                metadata_file = metadata_dir / f'{obj_name}.json'
                if not metadata_file.exists():
                    for orig in all_objects:
                        if orig.lower() == obj_name.lower():
                            metadata_file = metadata_dir / f'{orig}.json'
                            break
                
                obj_data = load_json(metadata_file)
                difficulty = obj_data.get('difficulty', 'Normal')
                hint = obj_data.get('description', '')
                
                diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
                gradient, accent, bg_image = get_realm_gradient(realm_name)
                special_case = get_special_case(realm_name)
                
                if special_case.get('custom_gradient'):
                    gradient = special_case['custom_gradient']
                if special_case.get('custom_bg_image'):
                    bg_image = special_case['custom_bg_image']
                
                categories = [
                    f"[[Category:{difficulty_proper} Objects]]",
                    "[[Category:Objects]]",
                    f"[[Category:{realm_name} Objects]]",
                ]
                
                if difficulty_priority >= 11:
                    obtaining_markup = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
{obtaining}
</div>
</div>"""
                else:
                    obtaining_markup = f"""== Obtaining ==
{obtaining}"""
                
                static_overlay = ""
                if special_case.get('static_overlay'):
                    static_img = special_case.get('static_image', 'Staticbg.gif')
                    static_opacity = special_case.get('static_opacity', 0.05)
                    static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
                
                gallery_markup = f"[[File:{obj_name}.png]]"
                
                wiki_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
{info}

{obtaining_markup}

{chr(10).join(categories)}
</div>
</div>"""
                
                output_file = data_dir / f'{obj_name}.txt'
                output_file.write_text(wiki_markup, encoding='utf-8')
                saved += 1
                
            except Exception:
                failed += 1
        
        print(f"    [+] {saved} saved, [+] {stubbed} stubbed, [!] {failed} failed")
    
    print()
    print("=" * 60)
    print("[+] BATCH FORMAT COMPLETE")
    print("=" * 60)
    
    return True



    """Create stub .txt files for missing objects."""
    print()
    print("=" * 60)
    print("CREATE STUB FILES FOR MISSING PAGES")
    print("=" * 60)
    
    # Step 1: Select realm/subrealm
    items = list_realms_and_subrealms_hierarchical()
    
    print("\nSelect realm/subrealm:")
    print()
    print("  (@) Create stubs for ALL realms")
    print()
    
    # Find where subrealms start
    first_subrealm_idx = None
    for i, item in enumerate(items):
        if isinstance(item[0], str) and item[0][0].isalpha():
            first_subrealm_idx = i
            break
    
    for i, item in enumerate(items):
        number, name, path, is_subrealm, parent, item_type = item
        
        if first_subrealm_idx and i == first_subrealm_idx:
            print()
            print("-" * 60)
            print()
        
        print(f"  ({number}) {name}")
    
    try:
        choice = input("\nEnter number, label, or @: ").strip()
        
        if choice == "@":
            return create_stubs_all_realms(session)
        
        # Find matching item
        selected_item = None
        for item in items:
            if str(item[0]) == choice:
                selected_item = item
                break
        
        if not selected_item:
            print("[x] Invalid selection")
            return False
        
        selected_number, selected_realm, selected_path, is_subrealm, parent_realm, item_type = selected_item
    except (ValueError, IndexError):
        print("[x] Invalid selection")
        return False
    except KeyboardInterrupt:
        print("\nCancelled")
        return False
    
    print(f"\n[+] Selected: {selected_realm.lstrip('→ ')}")
    
    # Step 2: Get metadata and data directories
    metadata_dir = Path(selected_path)
    data_dir = Path(selected_path.replace('metadata', 'data'))
    realm_name = selected_realm.lstrip('→ ')
    
    if not metadata_dir.exists():
        print(f"[!] Metadata directory not found: {metadata_dir}")
        return False
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Get all objects from metadata
    all_objects = sorted([obj.stem for obj in metadata_dir.glob('*.json')])
    
    # Get objects that already have .txt files
    existing_files = set(f.stem for f in data_dir.glob('*.txt'))
    existing_files.update(f.stem.lstrip('[x] ') for f in data_dir.glob('[x]*.txt'))
    
    # Find missing objects
    missing_objects = [obj for obj in all_objects if obj not in existing_files]
    
    if not missing_objects:
        print(f"\n[+] All objects already have files!")
        return True
    
    print(f"\n[+] Found {len(missing_objects)} missing objects")
    print("    Creating stub files...")
    
    # Step 3: Create stub files
    created = 0
    failed = 0
    
    for obj_name in missing_objects:
        try:
            # Get metadata
            metadata_file = metadata_dir / f'{obj_name}.json'
            obj_data = load_json(metadata_file)
            
            difficulty = obj_data.get('difficulty', 'Normal')
            hint = obj_data.get('description', '')
            
            # Get difficulty info
            diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
            
            # Get realm info
            gradient, accent, bg_image = get_realm_gradient(realm_name)
            special_case = get_special_case(realm_name)
            
            if special_case.get('custom_gradient'):
                gradient = special_case['custom_gradient']
            if special_case.get('custom_bg_image'):
                bg_image = special_case['custom_bg_image']
            
            # Build categories
            categories = [
                f"[[Category:{difficulty_proper} Objects]]",
                "[[Category:Objects]]",
                f"[[Category:{realm_name} Objects]]",
            ]
            
            # Build stub content
            static_overlay = ""
            if special_case.get('static_overlay'):
                static_img = special_case.get('static_image', 'Staticbg.gif')
                static_opacity = special_case.get('static_opacity', 0.05)
                static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
            
            gallery_markup = f"[[File:{obj_name}.png]]"
            
            stub_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
[TODO: Add info description here]

== Obtaining ==
[TODO: Add obtaining instructions here]

{chr(10).join(categories)}
</div>
</div>"""
            
            # Save stub file with [x] prefix
            stub_file = data_dir / f'[x] {obj_name}.txt'
            stub_file.write_text(stub_markup, encoding='utf-8')
            created += 1
            
        except Exception as e:
            failed += 1
            print(f"\n[!] Failed to create stub for {obj_name}: {e}")
    
    print(f"\n[+] Created {created} stub files")
    if failed > 0:
        print(f"[!] Failed: {failed}")
    
    return True


def create_stubs_all_realms(session):
    """Create stub files for all missing objects in all realms."""
    print()
    print("=" * 60)
    print("CREATING STUBS FOR ALL REALMS")
    print("=" * 60)
    
    realms_dir = Path('metadata/realms')
    if not realms_dir.exists():
        print("[x] metadata/realms not found")
        return False
    
    all_realms = sorted([d.name for d in realms_dir.iterdir() if d.is_dir()])
    print(f"\n[+] Found {len(all_realms)} realms\n")
    
    total_created = 0
    total_failed = 0
    
    for realm_name in all_realms:
        metadata_dir = realms_dir / realm_name
        data_dir = Path('data/realms') / realm_name
        
        # Get objects
        all_objects = sorted([obj.stem for obj in metadata_dir.glob('*.json')])
        
        # Get existing files
        data_dir.mkdir(parents=True, exist_ok=True)
        existing_files = set(f.stem for f in data_dir.glob('*.txt'))
        existing_files.update(f.stem.lstrip('[x] ') for f in data_dir.glob('[x]*.txt'))
        
        # Find missing objects
        missing_objects = [obj for obj in all_objects if obj not in existing_files]
        
        if not missing_objects:
            print(f"[-] {realm_name}: no missing objects")
            continue
        
        print(f"[*] {realm_name} ({len(missing_objects)} missing)")
        
        created = 0
        failed = 0
        
        for obj_name in missing_objects:
            try:
                # Get metadata
                metadata_file = metadata_dir / f'{obj_name}.json'
                obj_data = load_json(metadata_file)
                
                difficulty = obj_data.get('difficulty', 'Normal')
                hint = obj_data.get('description', '')
                
                # Get difficulty info
                diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
                
                # Get realm info
                gradient, accent, bg_image = get_realm_gradient(realm_name)
                special_case = get_special_case(realm_name)
                
                if special_case.get('custom_gradient'):
                    gradient = special_case['custom_gradient']
                if special_case.get('custom_bg_image'):
                    bg_image = special_case['custom_bg_image']
                
                # Build categories
                categories = [
                    f"[[Category:{difficulty_proper} Objects]]",
                    "[[Category:Objects]]",
                    f"[[Category:{realm_name} Objects]]",
                ]
                
                # Build stub
                static_overlay = ""
                if special_case.get('static_overlay'):
                    static_img = special_case.get('static_image', 'Staticbg.gif')
                    static_opacity = special_case.get('static_opacity', 0.05)
                    static_overlay = f"""<!-- Subtle static + vignette overlays -->
<div style="opacity:{static_opacity}; pointer-events:none; position:fixed; z-index:3; top:0; left:0; right:0; bottom:0;">
[[File:{static_img}|1500px]]
</div>

"""
                
                gallery_markup = f"[[File:{obj_name}.png]]"
                
                stub_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={obj_name}
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm_name}]]
|hint={hint}
}}}}

== Info ==
[TODO: Add info description here]

== Obtaining ==
[TODO: Add obtaining instructions here]

{chr(10).join(categories)}
</div>
</div>"""
                
                # Save stub file with [x] prefix
                stub_file = data_dir / f'[x] {obj_name}.txt'
                stub_file.write_text(stub_markup, encoding='utf-8')
                created += 1
                
            except Exception:
                failed += 1
        
        print(f"    [+] {created} created, [!] {failed} failed")
        total_created += created
        total_failed += failed
    
    print()
    print("=" * 60)
    print(f"[+] STUB CREATION COMPLETE: {total_created} created")
    print("=" * 60)
    
    return True

