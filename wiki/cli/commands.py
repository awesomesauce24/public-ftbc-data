#!/usr/bin/env python3
"""
Commands for FTBC Wiki Bot
Implements interactive commands
"""

import sys
import json
import urllib.request
import urllib.error
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .ui import display_help, display_header, display_footer
from .search import search_objects
from wiki.core.object_formatter import check_page_exists

# Cache for wiki page existence checks
_wiki_page_cache = {}
# Track created pages for export
_created_pages_log = []


# ==================== BASIC COMMANDS ====================

def cmd_help():
    """Display help information"""
    display_help()


def cmd_exit():
    """Exit the bot"""
    print("Goodbye!")
    sys.exit(0)


# ==================== PAGE TRACKING & EXPORT ====================

def _log_page_creation(object_name, realm_name, success=True, error_msg=None):
    """Log a page creation attempt for export"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'object_name': object_name,
        'realm': realm_name,
        'success': success,
        'error': error_msg
    }
    _created_pages_log.append(entry)


def _export_pages_csv():
    """Export created pages log to CSV"""
    if not _created_pages_log:
        print("No pages logged yet.")
        return
    
    import csv
    filepath = Path(__file__).parent.parent.parent / "wiki_pages_created.csv"
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['timestamp', 'object_name', 'realm', 'success', 'error'])
            writer.writeheader()
            writer.writerows(_created_pages_log)
        
        print(f"✓ Exported {len(_created_pages_log)} entries to: {filepath}")
    except Exception as e:
        print(f"✗ Export failed: {e}")


def _export_pages_json():
    """Export created pages log to JSON"""
    if not _created_pages_log:
        print("No pages logged yet.")
        return
    
    filepath = Path(__file__).parent.parent.parent / "wiki_pages_created.json"
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(_created_pages_log, f, indent=2)
        
        print(f"✓ Exported {len(_created_pages_log)} entries to: {filepath}")
    except Exception as e:
        print(f"✗ Export failed: {e}")


def _preview_wiki_page(object_name):
    """
    Fetch and display how a wiki page looks
    
    Args:
        object_name (str): Name of the object/page
        
    Returns:
        str: HTML content or None if failed
    """
    try:
        wiki_name = object_name.replace(" ", "_")
        url = f"https://ftbc.fandom.com/wiki/{wiki_name}"
        
        print(f"\n📄 Fetching preview: {url}")
        
        response = urllib.request.urlopen(f"{url}?action=render", timeout=10)
        html_content = response.read().decode('utf-8')
        
        # Extract just the main content (simplified)
        if '<div id="mw-content-text"' in html_content:
            start = html_content.find('<div id="mw-content-text"')
            end = html_content.find('</div>', start) + 6
            content = html_content[start:end]
            
            # Remove HTML tags for terminal display
            import re
            text = re.sub('<[^<]+?>', '', content)
            text = text[:500] + "..." if len(text) > 500 else text
            
            print("\n--- Wiki Preview (first 500 chars) ---")
            print(text)
            print("--- End Preview ---\n")
            
            return True
        else:
            print("Could not parse page content.")
            return False
    
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("✗ Page not found on wiki (404)")
        else:
            print(f"✗ HTTP Error {e.code}")
        return False
    except Exception as e:
        print(f"✗ Preview failed: {e}")
        return False


# ==================== SEARCH COMMAND ====================

def cmd_search(query):
    """
    Search for objects matching a query
    
    Args:
        query (str): Search term
    """
    if not query:
        print("Usage: search <query>")
        print("Example: search Firey")
        return
    
    results = search_objects(query)
    
    if not results:
        print(f"No results found for '{query}'")
        return
    
    display_header(f"Search Results for '{query}'")
    for i, obj in enumerate(results, 1):
        print(f"({i}) ({obj['realm']}) {obj['name']} | {obj['difficulty']} | {obj['description'][:50]}...")
    display_footer()


# ==================== REALM LISTING COMMANDS ====================

def cmd_realms():
    """Display all main realms"""
    realms_path = Path(__file__).parent.parent.parent / "Realms"
    
    if not realms_path.exists():
        print("Realms directory not found!")
        return
    
    # Get main realms (JSON files in Realms/) - sorted alphabetically (case-insensitive)
    main_realms = sorted([f.stem for f in realms_path.glob("*.json")], key=str.lower)
    
    if not main_realms:
        print("No realms found!")
        return
    
    display_header(f"All Main Realms ({len(main_realms)})")
    for i, realm in enumerate(main_realms, 1):
        print(f"({i:2d}) {realm}")
    display_footer()


def cmd_subrealms():
    """Display all subrealms"""
    realms_path = Path(__file__).parent.parent.parent / "Realms"
    subrealms_path = realms_path / "Sub-realms"
    
    if not subrealms_path.exists():
        print("Sub-realms directory not found!")
        return
    
    # Get subrealms - sorted alphabetically (case-insensitive)
    subrealms = sorted([f.stem for f in subrealms_path.glob("*.json")], key=str.lower)
    
    if not subrealms:
        print("No subrealms found!")
        return
    
    display_header(f"All Subrealms ({len(subrealms)})")
    for i, subrealm in enumerate(subrealms, 1):
        print(f"({i:2d}) {subrealm}")
    display_footer()


# ==================== CREATE PAGE COMMAND ====================

def _check_wiki_page_exists(object_name):
    """
    Check if a wiki page exists for an object (cached)
    
    Args:
        object_name (str): Name of the object
        
    Returns:
        bool: True if page exists
    """
    # Check cache first
    if object_name in _wiki_page_cache:
        return _wiki_page_cache[object_name]
    
    # Replace spaces with underscores for wiki URL
    wiki_name = object_name.replace(" ", "_")
    url = f"https://ftbc.fandom.com/wiki/{wiki_name}"
    
    try:
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        response = urllib.request.urlopen(request, timeout=2)  # Reduced timeout from 5 to 2 seconds
        result = response.status == 200
    except (urllib.error.HTTPError, urllib.error.URLError, Exception):
        result = False
    
    # Cache the result
    _wiki_page_cache[object_name] = result
    return result


def _check_wiki_pages_concurrent(object_names, max_workers=10):
    """
    Check multiple wiki pages concurrently (much faster than sequential)
    
    Args:
        object_names (list): List of object names to check
        max_workers (int): Number of concurrent threads
        
    Returns:
        dict: Mapping of object_name -> has_page boolean
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_name = {executor.submit(_check_wiki_page_exists, name): name for name in object_names}
        
        # Process completed tasks as they finish
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                results[name] = future.result()
            except Exception:
                results[name] = False
    
    return results


def _load_realm_objects(realm_name, is_subrealm=False):
    """
    Load objects from a specific realm
    
    Args:
        realm_name (str): Name of the realm
        is_subrealm (bool): Whether this is a subrealm
        
    Returns:
        list: List of objects
    """
    realms_path = Path(__file__).parent.parent.parent / "Realms"
    
    if is_subrealm:
        realm_file = realms_path / "Sub-realms" / f"{realm_name}.json"
    else:
        realm_file = realms_path / f"{realm_name}.json"
    
    if not realm_file.exists():
        return []
    
    try:
        with open(realm_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Handle both array and object formats
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'objects' in data:
                return data['objects']
    except Exception as e:
        print(f"Error loading realm: {e}")
    
    return []


def _get_realm_styling(realm_name):
    """
    Get background and styling for a realm
    
    Args:
        realm_name (str): Name of the realm
        
    Returns:
        dict: Styling information
    """
    template_path = Path(__file__).parent.parent / "templates" / "object_template.json"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
            if realm_name in template.get('realms', {}):
                return template['realms'][realm_name]
    except Exception:
        pass
    
    # Default styling
    return {
        "background_file": "Main Realm Sky.webp",
        "theme_accent_color": "-webkit-linear-gradient(#23bd1c,#188a13)",
        "theme_accent_label_color": "#ffffff",
        "text_color": "#000000"
    }


def _generate_wiki_markup(obj, realm_name, info, obtaining, trivia):
    """
    Generate wiki markup for an object
    
    Args:
        obj (dict): Object data
        realm_name (str): Name of the realm
        info (str): Info section
        obtaining (str): Obtaining section
        trivia (str): Trivia section
        
    Returns:
        str: Wiki markup
    """
    styling = _get_realm_styling(realm_name)
    background_file = styling.get('background_file', 'Main Realm Sky.webp')
    background_size = styling.get('background_size', '2000px')
    theme_accent = styling.get('theme_accent_color', '-webkit-linear-gradient(#23bd1c,#188a13)')
    theme_label_color = styling.get('theme_accent_label_color', '#ffffff')
    text_color = styling.get('text_color', '#000000')
    
    object_name = obj.get('ObjectName', '')
    difficulty = obj.get('Difficulty', '')
    description = obj.get('Description', '')
    
    # Build the wiki markup
    markup = f"""<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{{{{{background_file}|{background_size}}}}}]]
</div>
<div style="--theme-accent-color:{theme_accent}; --theme-accent-label-color:{theme_label_color};">
<div style="position:relative; z-index:1;">

== {object_name} ==

'''Difficulty:''' [[File:{difficulty}.png]] <span style="color:{_get_difficulty_color(difficulty)}">'''{difficulty}'''</span>

'''Location:''' [[{realm_name}]]

'''Hint:''' {description}

== Info ==
{info if info and info.lower() != 'tbd' else 'TBD'}

== Obtaining ==
{obtaining if obtaining and obtaining.lower() != 'tbd' else 'TBD'}
"""
    
    if trivia and trivia.lower() != 'tbd':
        markup += f"\n== Trivia ==\n* {trivia}\n"
    
    markup += "\n</div>\n</div>"
    
    return markup


def _get_difficulty_color(difficulty):
    """Get hex color for difficulty"""
    template_path = Path(__file__).parent.parent / "templates" / "object_template.json"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = json.load(f)
            difficulties = template.get('difficulties', {})
            return difficulties.get(difficulty, '#000000')
    except Exception:
        pass
    
    return '#000000'


def _get_csrf_token(session):
    """
    Get CSRF token from wiki API
    
    Args:
        session: Authenticated requests session
        
    Returns:
        str: CSRF token or None
    """
    try:
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'csrf',
            'format': 'json'
        }
        
        wiki_url = getattr(session, 'wiki_url', 'https://ftbc.fandom.com')
        response = session.get(f'{wiki_url}/api.php', params=params)
        
        if response.status_code == 200:
            return response.json()['query']['tokens']['csrftoken']
    except Exception as e:
        print(f"Error getting CSRF token: {e}")
    
    return None


def _upload_page_to_wiki(session, page_title, page_content, is_edit=False):
    """
    Upload or edit a page directly to the wiki
    
    Args:
        session: Authenticated requests session
        page_title (str): Title of the page
        page_content (str): Wiki markup content
        is_edit (bool): Whether this is an edit (vs new page)
        
    Returns:
        tuple: (success, message)
    """
    if not session:
        return False, "Not authenticated with wiki"
    
    try:
        # Get CSRF token
        token = _get_csrf_token(session)
        if not token:
            return False, "Failed to get CSRF token"
        
        # Prepare edit parameters
        wiki_url = getattr(session, 'wiki_url', 'https://ftbc.fandom.com')
        
        # Always use "Spongybot" for edit reason
        if is_edit:
            edit_reason = "edited by Spongybot"
        else:
            edit_reason = "created by Spongybot"
        
        edit_params = {
            'action': 'edit',
            'title': page_title,
            'text': page_content,
            'summary': edit_reason,
            'token': token,
            'format': 'json'
        }
        
        # Send edit request
        response = session.post(f'{wiki_url}/api.php', data=edit_params)
        
        if response.status_code == 200:
            result = response.json()
            
            if 'edit' in result:
                edit_result = result['edit']
                
                if 'pageid' in edit_result or edit_result.get('result') == 'Success':
                    page_id = edit_result.get('pageid', '?')
                    if is_edit:
                        return True, f"✓ Page updated successfully (ID: {page_id})"
                    else:
                        return True, f"✓ Page created successfully (ID: {page_id})"
                elif 'error' in edit_result:
                    error_msg = edit_result['error'].get('info', 'Unknown error')
                    return False, f"✗ Edit failed: {error_msg}"
            
            return False, f"✗ Unexpected response: {result}"
        else:
            return False, f"✗ HTTP Error {response.status_code}"
    
    except Exception as e:
        return False, f"✗ Upload failed: {str(e)}"


def _fuzzy_match(search_term, text):
    """
    Calculate fuzzy match score (0-100, higher is better)
    Prioritizes: exact match > starts with > contains > fuzzy char match
    
    Args:
        search_term (str): Search term (lowercase)
        text (str): Text to match against (lowercase)
        
    Returns:
        int: Match score (0 = no match, 100 = exact match)
    """
    if search_term == text:
        return 100  # Exact match
    
    if text.startswith(search_term):
        return 90  # Starts with
    
    if search_term in text:
        return 80  # Contains (substring)
    
    # Fuzzy: all characters appear in order, but require higher confidence
    # Only allow if matches are relatively close together
    search_idx = 0
    last_match_pos = -1
    match_positions = []
    
    for pos, char in enumerate(text):
        if search_idx < len(search_term) and char == search_term[search_idx]:
            match_positions.append(pos)
            last_match_pos = pos
            search_idx += 1
    
    if search_idx == len(search_term):
        # All chars found in order
        # Calculate score based on how compact the matches are
        # Matches must be relatively close (within ~5 char distance per search char)
        max_spread = (match_positions[-1] - match_positions[0]) if len(match_positions) > 1 else 0
        acceptable_spread = len(search_term) * 5  # Allow up to 5 chars per search letter
        
        if max_spread <= acceptable_spread:
            # Good match - score decreases with spread
            score = max(40, 70 - (max_spread // 2))
            return score
    
    return 0  # No match


def _select_from_list(items, item_key='name', prompt="Enter choice"):
    """
    Helper to select from a list by number or name (with fuzzy matching)
    
    Args:
        items (list): List of dicts to select from
        item_key (str): Key to use for name matching (default: 'name')
        prompt (str): Prompt text
        
    Returns:
        tuple: (selected_item, index) or (None, None) if cancelled
    """
    user_input = input(f"{prompt}: ").strip()
    
    if not user_input:
        return None, None
    
    # Try numeric input first
    try:
        choice_num = int(user_input)
        cancel_num = len(items) + 1
        
        if choice_num == cancel_num:
            return None, None
        
        if 1 <= choice_num <= len(items):
            return items[choice_num - 1], choice_num - 1
        
        print("Invalid number. Try again.")
        return None, None
    except ValueError:
        pass
    
    # Try fuzzy name-based search
    search_term = user_input.lower()
    matches = []
    
    for i, item in enumerate(items):
        item_name = str(item.get(item_key, '')).lower()
        score = _fuzzy_match(search_term, item_name)
        
        if score > 0:
            matches.append((score, item, i))
    
    # Sort by score (descending), then by name
    matches.sort(key=lambda x: (-x[0], x[1].get(item_key, '').lower()))
    
    if len(matches) == 0:
        print(f"No matches found for '{user_input}'. Try again.")
        return None, None
    
    # If best match is an exact match, use it directly
    if matches[0][0] == 100:
        return matches[0][1], matches[0][2]
    
    # If exactly one match, use it
    if len(matches) == 1:
        return matches[0][1], matches[0][2]
    
    # For all other cases (including "starts with"), show matches and ask
    print(f"\n✓ Found {len(matches)} similar matches:")
    for j, (score, match, _) in enumerate(matches[:15], 1):  # Show max 15
        display_score = f"({score}%)" if score < 100 else ""
        print(f"  {j}. {match.get(item_key, '')} {display_score}")
    if len(matches) > 15:
        print(f"  ... and {len(matches) - 15} more")
    print(f"  {len(matches) + 1}. None of these, try again")
    
    # Ask which one they meant
    while True:
        choice = input("\nWhich one did you mean? (enter number): ").strip()
        try:
            choice_num = int(choice)
            if choice_num == len(matches) + 1:
                return None, None
            if 1 <= choice_num <= len(matches):
                _, selected_item, original_index = matches[choice_num - 1]
                return selected_item, original_index
            print("Invalid choice.")
        except ValueError:
            print("Please enter a valid number.")



def _select_realm():
    """
    Interactive prompt to select a realm
    
    Returns:
        tuple: (realm_name, is_subrealm) or (None, None) if cancelled
    """
    realms_path = Path(__file__).parent.parent.parent / "Realms"
    
    # Get main realms and subrealms - sorted alphabetically
    main_realms = sorted([f.stem for f in realms_path.glob("*.json")], key=str.lower)
    subrealms_path = realms_path / "Sub-realms"
    subrealms = sorted([f.stem for f in subrealms_path.glob("*.json")], key=str.lower) if subrealms_path.exists() else []
    
    # Main realms first, then subrealms
    all_realms = [(r, False) for r in main_realms] + [(s, True) for s in subrealms]
    
    display_header("Select a Realm")
    for i, (realm, is_sub) in enumerate(all_realms, 1):
        realm_type = "[SUB]" if is_sub else "[MAIN]"
        print(f"({i:2d}) {realm_type} {realm}")
    print(f"({len(all_realms) + 1:2d}) Cancel")
    
    while True:
        try:
            choice = input("\nEnter choice: ").strip()
            choice_num = int(choice)
            
            if choice_num == len(all_realms) + 1:
                return None, None
            
            if 1 <= choice_num <= len(all_realms):
                realm_name, is_subrealm = all_realms[choice_num - 1]
                return realm_name, is_subrealm
            
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def cmd_create_page(session=None):
    """Interactive command to create wiki pages for objects"""
    display_header("Wiki Page Creator")
    
    while True:
        realm_name, is_subrealm = _select_realm()
        if realm_name is None:
            return
        
        print(f"\nLoading objects from {realm_name}...")
        objects = _load_realm_objects(realm_name, is_subrealm)
        
        if not objects:
            print(f"No objects found in {realm_name}")
            continue
        
        # Check which objects have pages - using concurrent requests
        print(f"Checking wiki pages ({len(objects)} objects, this may take a moment)...")
        object_names = [obj.get('ObjectName', '') for obj in objects]
        pages_check = _check_wiki_pages_concurrent(object_names, max_workers=15)
        
        pages_status = []
        for obj in objects:
            obj_name = obj.get('ObjectName', '')
            has_page = pages_check.get(obj_name, False)
            pages_status.append({
                'object': obj,
                'has_page': has_page,
                'name': obj_name
            })
        
        with_pages = [p for p in pages_status if p['has_page']]
        without_pages = [p for p in pages_status if not p['has_page']]
        
        # Display results
        display_header("Page Status Report")
        print(f"\nObjects with Pages: {len(with_pages)}")
        print(f"Objects without Pages: {len(without_pages)}")
        
        if without_pages:
            print("\n--- Objects without Pages ---")
            for i, p in enumerate(without_pages, 1):
                print(f"  {i}. {p['name']}")
        
        display_footer()
        
        # Realm menu loop
        while True:
            print("\n--- Options ---")
            print("(1) Create/Edit Object Page")
            print("(2) Choose Another Realm")
            print("(3) Return to Main Menu")
            
            choice = input("\nEnter choice (1-3): ").strip()
            
            if choice == "1":
                # Select object to create/edit - sorted alphabetically
                print("\n--- Select Object to Create/Edit ---")
                sorted_objects = sorted(pages_status, key=lambda p: p['name'].lower())
                for i, p in enumerate(sorted_objects, 1):
                    status = "✓" if p['has_page'] else "✗"
                    print(f"({i}) {p['name']} [{status}]")
                print(f"({len(sorted_objects) + 1}) Cancel")
                
                selected, obj_index = _select_from_list(sorted_objects, 'name', "Enter choice (number or name)")
                
                if selected is None:
                    continue
                
                result = _create_object_interactive(selected['object'], realm_name, session)
                
                # Handle result from interactive creation
                if result == "another":
                    # Stay in realm menu to select another object
                    continue
                elif result == "realm":
                    # Break to select new realm
                    break
                elif result == "exit":
                    # Stay in realm menu
                    continue
            
            elif choice == "2":
                # Break to outer loop to select new realm
                break
            
            elif choice == "3":
                return
            
            else:
                print("Invalid choice.")


def _handle_page_submission(object_name, markup, realm_name, session=None):
    """
    Handle page submission/editing - Direct upload to wiki
    
    Args:
        object_name (str): Name of the object
        markup (str): Wiki markup
        realm_name (str): Name of the realm
        session: Authenticated wiki session (optional)
        
    Returns:
        str: "created", "updated", or "cancelled"
    """
    wiki_name = object_name.replace(" ", "_")
    page_url = f"https://ftbc.fandom.com/wiki/{wiki_name}"
    
    print(f"\nChecking page status: {page_url}")
    
    page_exists = _check_wiki_page_exists(object_name)
    
    if page_exists:
        print(f"✓ Page already exists at: {page_url}")
        print("\nWould you like to:")
        print("  (1) Update existing page with new content")
        print("  (2) Cancel")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        if choice == "1":
            if session:
                print("\n⏳ Uploading updated page...")
                success, message = _upload_page_to_wiki(session, wiki_name, markup, is_edit=True)
                print(message)
                
                if success:
                    return "updated"
                else:
                    print("\n✓ Markup is ready below if you want to copy and paste manually:")
                    print("\n=== Markup for Manual Update ===")
                    print(markup)
                    return "updated"
            else:
                print("\n=== Markup for Update ===")
                print(markup)
                print("\n✓ Copy the markup above and paste it into the existing page.")
                print(f"Edit URL: {page_url}?action=edit")
                return "updated"
        else:
            return "cancelled"
    else:
        print(f"✗ Page does not exist yet.")
        print(f"  URL: {page_url}\n")
        
        if session:
            print("⏳ Creating new page...")
            success, message = _upload_page_to_wiki(session, wiki_name, markup, is_edit=False)
            print(message)
            
            if success:
                print(f"\n✓ Page created and uploaded to wiki!")
                print(f"View at: {page_url}")
                return "created"
            else:
                print("\n✓ Markup is ready below if you want to copy and paste manually:")
                print("\n=== Markup for Manual Creation ===")
                print(markup)
                print(f"\nTo create manually:")
                print("  1. Go to: " + page_url)
                print("  2. Click 'Create this page'")
                print("  3. Paste the markup above")
                print("  4. Click 'Publish'")
                return "created"
        else:
            print("Creating new page markup for:")
            print(f"  URL: {page_url}")
            print("\nFollow these steps:")
            print("  1. Go to the URL above")
            print("  2. Click 'Create this page'")
            print("  3. Paste the markup below into the editor")
            print("  4. Fill in any additional sections (images, categories)")
            print("  5. Click 'Publish'")
            
            print("\n=== Markup for New Page ===")
            print(markup)
            print("\n✓ Markup is ready. Go to the URL above to create the page.")
            return "created"


def _copy_to_clipboard(text):
    """
    Copy text to clipboard
    
    Args:
        text (str): Text to copy
        
    Returns:
        bool: True if successful
    """
    try:
        import subprocess
        
        # Windows: Use clip.exe
        process = subprocess.Popen(['clip.exe'], stdin=subprocess.PIPE, shell=True)
        process.communicate(input=text.encode('utf-8'))
        
        if process.returncode == 0:
            print("✓ Markup copied to clipboard!")
            return True
        else:
            print("✗ Failed to copy to clipboard")
            return False
    except Exception as e:
        print(f"✗ Clipboard copy failed: {e}")
        print("  (You can manually select and copy the markup above)")
        return False


def _input_multiline(prompt, allow_blank=False):
    """
    Collect multi-line input from user
    Press Enter twice (empty line) to finish, or Ctrl+D
    
    Args:
        prompt (str): Display prompt
        allow_blank (bool): If False, require at least some input
        
    Returns:
        str: Collected text, stripped
    """
    print(f"{prompt} (Press Enter twice to finish):")
    lines = []
    blank_count = 0
    
    while True:
        try:
            line = input()
            
            if line == '':
                blank_count += 1
                if blank_count >= 2:
                    break
                lines.append(line)
            else:
                blank_count = 0
                lines.append(line)
        
        except EOFError:
            # Handle Ctrl+D
            break
    
    # Remove trailing blank lines
    while lines and lines[-1] == '':
        lines.pop()
    
    text = '\n'.join(lines).strip()
    
    if not allow_blank and not text:
        return "TBD"
    
    return text if text else "TBD"


def _create_object_interactive(obj, realm_name, session=None):
    """
    Interactive interface to create an object page
    
    Args:
        obj (dict): Object data
        realm_name (str): Name of the realm
        session: Authenticated wiki session (optional)
        
    Returns:
        str: Menu choice ("another", "realm", "exit") or None
    """
    object_name = obj.get('ObjectName', '')
    difficulty = obj.get('Difficulty', '')
    description = obj.get('Description', '')
    
    print(f"\n=== Creating Page for: {object_name} ===")
    print(f"Difficulty: {difficulty}")
    print(f"Description: {description}\n")
    
    # Input Validation: Check if page already exists
    print("Checking wiki for existing page...")
    page_exists = check_page_exists(object_name)
    
    if page_exists is True:
        print(f"⚠ WARNING: Page '{object_name}' already exists on the wiki!")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Cancelled.")
            return "exit"
    elif page_exists is None:
        print("⚠ Could not verify page status (connection issue)")
    
    print("\nEnter the following information (leave blank or type 'TBD' for blank sections):\n")
    
    # Use multi-line input for Info and Obtaining
    info = _input_multiline("Info") or "TBD"
    obtaining = _input_multiline("Obtaining") or "TBD"
    
    # Collect trivia items (one per line, leave blank to finish)
    print("Trivia (enter one item at a time, leave blank to skip):")

    trivia_list = []
    while True:
        trivia_item = input("  * ").strip()
        if not trivia_item:
            break
        trivia_list.append(trivia_item)
    
    # Collect previous difficulties (blank to skip)
    print("\nPrevious Difficulties (enter one at a time, leave blank to skip):")
    previous_difficulties = []
    while True:
        prev_diff = input("  - ").strip()
        if not prev_diff:
            break
        previous_difficulties.append(prev_diff)
    
    # Generate markup using the new formatter
    from wiki.core.object_formatter import create_object_with_autofill
    
    # Use object name as image filename
    character_images = [(f'{object_name}.png', '')]
    
    markup = create_object_with_autofill(
        name=object_name,
        realm_name=realm_name,
        character_images=character_images,
        info=info if info and info.lower() != 'tbd' else None,
        obtaining=obtaining if obtaining and obtaining.lower() != 'tbd' else None,
        trivia=trivia_list,
        previous_difficulties=previous_difficulties if previous_difficulties else None
    )
    
    # Display for review
    print("\n=== Generated Wiki Markup ===")
    print(markup)
    
    # Post-generation menu loop
    while True:
        print("\n--- Actions ---")
        print("(1) Submit/Edit the page")
        print("(2) Copy to clipboard")
        print("(3) Create another object in this realm")
        print("(4) Choose another realm")
        print("(5) Exit to main menu")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            result = _handle_page_submission(object_name, markup, realm_name, session)
            if result != "cancelled":
                print("\n→ What would you like to do next?")
                print("  (1) Create another object")
                print("  (2) Choose another realm")
                print("  (3) Exit to main menu")
                
                next_choice = input("\nEnter choice (1-3): ").strip()
                if next_choice == "1":
                    return "another"
                elif next_choice == "2":
                    return "realm"
                else:
                    return "exit"
        
        elif choice == "2":
            _copy_to_clipboard(markup)
            print("\n→ What would you like to do next?")
            print("  (1) Create another object")
            print("  (2) Choose another realm")
            print("  (3) Exit to main menu")
            
            next_choice = input("\nEnter choice (1-3): ").strip()
            if next_choice == "1":
                return "another"
            elif next_choice == "2":
                return "realm"
            else:
                return "exit"
        
        elif choice == "3":
            return "another"
        
        elif choice == "4":
            return "realm"
        
        elif choice == "5":
            return "exit"
        
        else:
            print("Invalid choice. Please try again.")
