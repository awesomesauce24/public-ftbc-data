#!/usr/bin/env python3
"""
Create/Edit Wiki Pages for FTBC Objects
Interactive script to create and save object pages to the Fandom wiki
"""

import json
import os
import sys
import re
from pathlib import Path
from .auth import get_wiki_client
import requests
from difflib import SequenceMatcher
from datetime import datetime, timedelta

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
METADATA_DIR = Path(__file__).parent.parent / "metadata"
CACHE_FILE = METADATA_DIR / "page_cache.json"

def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if sys.platform == "win32" else "clear")

def load_json(filepath):
    """Load JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_cache(cache_data):
    """Save page existence cache to file"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")

def load_cache():
    """Load page existence cache from file"""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load cache: {e}")
    return {"last_updated": None, "pages": {}}

def load_realms():
    """Load realms metadata"""
    return load_json(METADATA_DIR / "realms.json")

def load_subrealms():
    """Load subrealms metadata"""
    with open(METADATA_DIR / "realms.json") as f:
        data = json.load(f)
        return data.get("subrealms", {})

def load_difficulties():
    """Load difficulty metadata"""
    return load_json(METADATA_DIR / "difficulties.json")

def fuzzy_match(query, items, key=None):
    """Fuzzy match query against items, return sorted matches"""
    if key is None:
        key = lambda x: x
    
    matches = []
    query_lower = query.lower()
    
    for item in items:
        item_text = key(item).lower()
        # Calculate similarity ratio
        ratio = SequenceMatcher(None, query_lower, item_text).ratio()
        
        # Boost score if query matches start of string
        if item_text.startswith(query_lower):
            ratio = min(1.0, ratio + 0.3)
        
        # Only include if match is reasonable (>0.6)
        if ratio > 0.6:
            matches.append((item, ratio))
    
    # Sort by ratio (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    return [item for item, ratio in matches]

def display_realms():
    """Display all realms and subrealms, return selection"""
    realms = load_realms()
    subrealms = load_subrealms()
    
    choices = []
    
    print("\n" + "="*60)
    print("SELECT A REALM")
    print("="*60)
    print("Commands: 'back', 'exit', 'help'\n")
    
    # Display normal realms
    print("Normal Realms:")
    for i, realm in enumerate(realms["normal"], 1):
        print(f"  ({i}) {realm['label']}")
        choices.append(("realm", realm))
    
    # Display subrealms
    print("\nSub-Realms:")
    counter = len(realms["normal"]) + 1
    for parent, subs in subrealms.items():
        for sub in subs:
            print(f"  ({counter}) {sub['label']} [found in {parent}]")
            choices.append(("subrealm", sub, parent))
            counter += 1
    
    print(f"\n  (0) Back")
    
    while True:
        try:
            choice = input("\nEnter realm number: ").strip().lower()
            
            if choice == "back":
                return ("back", None)
            elif choice == "exit":
                return ("exit", None)
            elif choice == "help":
                print("\nEnter the number corresponding to a realm to select it.")
                continue
            
            if choice == "0":
                return ("back", None)
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(choices):
                return ("continue", choices[choice_idx])
            print("Invalid choice. Try again.")
        except ValueError:
            if choice not in ["back", "exit", "help"]:
                print("Please enter a number.")
            elif choice == "help":
                print("\nEnter the number corresponding to a realm to select it.")
            elif choice == "back":
                return ("back", None)
            elif choice == "exit":
                return ("exit", None)

def load_realm_objects(realm_label):
    """Load objects from realm JSON file"""
    # Convert label to folder name (spaces to spaces)
    folder_name = realm_label
    json_path = DATA_DIR / "realms" / folder_name / "objects.json"
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return None
    
    return load_json(json_path)

def load_subrealm_objects(realm_label, parent_label):
    """Load objects from subrealm JSON file"""
    # Subrealms are stored in data/subrealms/{parent}/{subrealm}/objects.json
    # Sanitize folder names by removing HTML tags and special characters
    def sanitize_folder_name(name):
        name = re.sub(r'<[^>]+>', '', name)  # Remove HTML tags
        name = re.sub(r'[<>:"/\\|?*]', '', name)  # Remove invalid characters
        return name.strip()
    
    sub_folder_name = sanitize_folder_name(realm_label)
    json_path = DATA_DIR / "subrealms" / parent_label / sub_folder_name / "objects.json"
    
    if not json_path.exists():
        print(f"Error: {json_path} not found")
        return None
    
    return load_json(json_path)

def display_objects(objects_data, realm_info, page_status=None):
    """Display objects and let user select one"""
    if not objects_data or not objects_data.get("objects"):
        print("No objects found in this realm.")
        return ("back", None)
    
    objects = sorted(objects_data["objects"], key=lambda x: x['name'].lower())
    realm_label = realm_info[1]["label"]
    
    print("\n" + "="*60)
    print(f"OBJECTS IN {realm_label.upper()}")
    print("="*60)
    print("Commands: 'back', 'exit', 'search [name]'\n")
    
    # Count pages on wiki
    pages_on_wiki = 0
    if page_status:
        pages_on_wiki = sum(1 for exists in page_status.values() if exists)
    
    for i, obj in enumerate(objects, 1):
        indicator = ""
        if page_status and obj['name'] in page_status:
            indicator = "[+]" if page_status[obj['name']] else "[x]"
        else:
            indicator = "[ ]"
        print(f"{indicator} ({i}) {obj['name']} | {obj['difficulty'].capitalize()}")
    
    # Show page count at bottom
    if page_status:
        total_pages = len(page_status)
        print(f"\n{pages_on_wiki}/{total_pages} pages on wiki")
    
    print(f"\n(0) Back")
    
    while True:
        choice = input("\nEnter object number or type name to search (or 'back'): ").strip()
        
        if choice.lower() == "back" or choice == "0":
            return ("back", None)
        elif choice.lower() == "exit":
            return ("exit", None)
        elif choice.lower() == "help":
            print("\nEnter the number of an object or type its name to search/select it.")
            continue
        
        # Try numeric choice first
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(objects):
                return ("continue", objects[idx])
        except ValueError:
            pass
        
        # Try exact match
        for obj in objects:
            if obj["name"].lower() == choice.lower():
                return ("continue", obj)
        
        # Try fuzzy matching
        matches = fuzzy_match(choice, objects, key=lambda x: x["name"])
        
        if matches:
            if len(matches) == 1:
                return ("continue", matches[0])
            
            # Show matching results
            print(f"\nResults for '{choice}':")
            for i, match in enumerate(matches[:10], 1):  # Show max 10 results
                indicator = ""
                if page_status and match['name'] in page_status:
                    indicator = "[+]" if page_status[match['name']] else "[x]"
                else:
                    indicator = "[ ]"
                print(f"{indicator} ({i}) {match['name']} | {match['difficulty'].capitalize()}")
            
            match_choice = input(f"\nEnter number to select (or press Enter to try again): ").strip()
            
            if match_choice:
                try:
                    match_idx = int(match_choice) - 1
                    if 0 <= match_idx < len(matches):
                        return ("continue", matches[match_idx])
                except ValueError:
                    pass
            
            print()
        else:
            print("Object not found. Try again.")

def check_wiki_page_exists(session, object_name, cache=None):
    """Check if a wiki page exists for this object (with caching)"""
    # Check cache first
    if cache and object_name in cache.get("pages", {}):
        return cache["pages"][object_name]
    
    url = "https://ftbc.fandom.com/api.php"
    params = {
        "action": "query",
        "titles": object_name,
        "format": "json"
    }
    
    try:
        response = session.get(url, params=params, timeout=5)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if "missing" not in page:
                return True
    except:
        pass
    
    return False

def check_realm_pages_batch(session, objects_data, realm_info=None):
    """Check existence of all pages in a realm using batch or individual API calls"""
    if not objects_data or not objects_data.get("objects"):
        return {}
    
    objects = objects_data["objects"]
    total = len(objects)
    
    # Load cache
    cache = load_cache()
    cached_pages = cache.get("pages", {})
    
    results = {}
    new_checks = {}
    processed_count = 0
    
    # Use individual requests for small realms (<100), batch for large ones
    use_individual_requests = total < 100
    
    if total >= 100:
        print(f"\n⚠️  Warning: This realm has {total} objects.")
        use_cache = input("Use cached results from previous checks? (yes/no) [default: yes]: ").strip().lower()
        if use_cache == "no":
            # Clear cache for this check to force fresh requests
            cached_pages = {}
        else:
            print("Loading cached results...")
    
    if use_individual_requests:
        # Individual request mode for <100 objects
        for obj in objects:
            obj_name = obj["name"]
            
            # Check cache first
            if obj_name in cached_pages:
                results[obj_name] = cached_pages[obj_name]
                processed_count += 1
                status_icon = "[+]" if cached_pages[obj_name] else "[x]"
                obj_display = obj_name[:40] + "..." if len(obj_name) > 40 else obj_name
                progress = processed_count / total * 100
                progress_text = f"({processed_count}/{total}) [{progress:.0f}%] {status_icon} {obj_display}"
                sys.stdout.write(f"\r\033[K{progress_text}")
                sys.stdout.flush()
                continue
            
            # Make individual request
            try:
                url = "https://ftbc.fandom.com/api.php"
                params = {
                    "action": "query",
                    "titles": obj_name,
                    "format": "json"
                }
                
                response = session.get(url, params=params, timeout=10)
                data = response.json()
                pages = data.get("query", {}).get("pages", {})
                
                exists = False
                for page_id, page_data in pages.items():
                    page_title = page_data.get("title", "")
                    # Check exact match (case-insensitive)
                    if page_title.lower() == obj_name.lower():
                        if "missing" not in page_data:
                            exists = True
                        break
                    # Also check for normalized versions (in case wiki uses different formatting)
                    if page_title.lower().replace("'", "") == obj_name.lower().replace("'", ""):
                        if "missing" not in page_data:
                            exists = True
                        break
                
                results[obj_name] = exists
                new_checks[obj_name] = exists
                
            except Exception as e:
                results[obj_name] = False
                new_checks[obj_name] = False
            
            processed_count += 1
            status_icon = "[+]" if results[obj_name] else "[x]"
            obj_display = obj_name[:40] + "..." if len(obj_name) > 40 else obj_name
            progress = processed_count / total * 100
            progress_text = f"({processed_count}/{total}) [{progress:.0f}%] {status_icon} {obj_display}"
            sys.stdout.write(f"\r\033[K{progress_text}")
            sys.stdout.flush()
    
    else:
        # Batch request mode for >=100 objects
        batch_size = 50  # Fandom API can handle this many titles per request
        
        for batch_start in range(0, total, batch_size):
            batch_end = min(batch_start + batch_size, total)
            batch_objects = objects[batch_start:batch_end]
            
            # Separate objects by whether we have them cached
            to_check = []
            for obj in batch_objects:
                obj_name = obj["name"]
                if obj_name in cached_pages:
                    results[obj_name] = cached_pages[obj_name]
                    processed_count += 1
                    # Show progress for cached items
                    status_icon = "[+]" if cached_pages[obj_name] else "[x]"
                    obj_display = obj_name[:40] + "..." if len(obj_name) > 40 else obj_name
                    progress = processed_count / total * 100
                    progress_text = f"[{processed_count}/{total}] {status_icon} {obj_display}... {progress:.0f}%"
                    sys.stdout.write(f"\r\033[K{progress_text}")
                    sys.stdout.flush()
                else:
                    to_check.append((obj_name, obj))
            
            # Check uncached items in this batch
            if to_check:
                try:
                    url = "https://ftbc.fandom.com/api.php"
                    object_names = [name for name, _ in to_check]
                    params = {
                        "action": "query",
                        "titles": "|".join(object_names),
                        "format": "json"
                    }
                    
                    response = session.get(url, params=params, timeout=10)
                    data = response.json()
                    pages = data.get("query", {}).get("pages", {})
                    
                    # Process results
                    for obj_name, obj in to_check:
                        exists = False
                        for page_id, page_data in pages.items():
                            page_title = page_data.get("title", "")
                            # Check exact match (case-insensitive)
                            if page_title.lower() == obj_name.lower():
                                if "missing" not in page_data:
                                    exists = True
                                break
                            # Also check for normalized versions (in case wiki uses different formatting)
                            if page_title.lower().replace("'", "") == obj_name.lower().replace("'", ""):
                                if "missing" not in page_data:
                                    exists = True
                                break
                        
                        results[obj_name] = exists
                        new_checks[obj_name] = exists
                        processed_count += 1
                        
                        # Show per-object progress
                        status_icon = "[+]" if exists else "[x]"
                        obj_display = obj_name[:40] + "..." if len(obj_name) > 40 else obj_name
                        progress = processed_count / total * 100
                        progress_text = f"[{processed_count}/{total}] {status_icon} {obj_display}... {progress:.0f}%"
                        sys.stdout.write(f"\r\033[K{progress_text}")
                        sys.stdout.flush()
                        
                except Exception as e:
                    # If batch check fails, mark all as False for this batch
                    for obj_name, _ in to_check:
                        results[obj_name] = False
                        new_checks[obj_name] = False
                        processed_count += 1
                        obj_display = obj_name[:40] + "..." if len(obj_name) > 40 else obj_name
                        progress = processed_count / total * 100
                        progress_text = f"[{processed_count}/{total}] [x] {obj_display}... {progress:.0f}%"
                        sys.stdout.write(f"\r\033[K{progress_text}")
                        sys.stdout.flush()
    
    # Update cache with new checks
    if new_checks:
        cached_pages.update(new_checks)
        cache["pages"] = cached_pages
        cache["last_updated"] = datetime.now().isoformat()
        save_cache(cache)
    
    print()  # New line after progress
    return results

def publish_to_wiki(session, page_title, markup_content):
    """Publish page to wiki using the bot account"""
    if not session:
        return False, "No session available"
    
    url = "https://ftbc.fandom.com/api.php"
    
    try:
        # Get CSRF token
        params_token = {
            "action": "query",
            "meta": "tokens",
            "type": "csrf",
            "format": "json"
        }
        
        response = session.get(url, params=params_token, timeout=10)
        response.raise_for_status()
        csrf_token = response.json()["query"]["tokens"]["csrftoken"]
        
        # Edit the page
        params_edit = {
            "action": "edit",
            "title": page_title,
            "text": markup_content,
            "summary": "Edited by Spongybot! :D",
            "bot": True,
            "format": "json",
            "token": csrf_token
        }
        
        response = session.post(url, data=params_edit, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if "edit" in result:
            if result["edit"]["result"] == "Success":
                return True, f"Page '{page_title}' successfully published"
            else:
                return False, f"Edit failed: {result['edit'].get('result', 'Unknown error')}"
        else:
            return False, f"Unexpected response: {result}"
    
    except Exception as e:
        return False, f"Publishing error: {str(e)}"

def prompt_multiline(prompt_text):
    """Prompt user for multiline input"""
    print(f"\n{prompt_text}")
    print("(Type lines of text, then press Enter twice to finish):")
    lines = []
    blank_count = 0
    
    while True:
        line = input()
        if line.strip() == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append("")
        else:
            blank_count = 0
            lines.append(line)
    
    return "\n".join(lines).strip()

def get_difficulty_hex(difficulties, difficulty_name):
    """Get hex color for difficulty"""
    for diff in difficulties["difficulties"]:
        if diff["name"].lower() == difficulty_name.lower():
            return diff["hex"]
    return "#ffffff"

def load_realm_gradients():
    """Load realm gradients metadata"""
    return load_json(METADATA_DIR / "realm_gradients.json")

def extract_gradient_value(gradient_string):
    """Extract gradient colors from -webkit-linear-gradient(colors) string"""
    # Remove the -webkit-linear-gradient( prefix and trailing )
    if gradient_string.startswith("-webkit-linear-gradient("):
        return gradient_string[24:-1]  # Remove prefix and closing paren
    return gradient_string

def get_realm_data(area_display):
    """Get realm data (image, gradient, accent) from metadata"""
    try:
        gradients = load_realm_gradients()
        # Check realms
        for realm in gradients.get("realms", []):
            if realm.get("label", "").lower() == area_display.lower():
                return {
                    "image": realm.get("image"),
                    "gradient": realm.get("gradient"),
                    "accent": realm.get("accent")
                }
        # Check subrealms
        for subrealm in gradients.get("subrealms", []):
            if subrealm.get("label", "").lower() == area_display.lower():
                return {
                    "image": subrealm.get("image"),
                    "gradient": subrealm.get("gradient"),
                    "accent": subrealm.get("accent")
                }
        # Check areas
        for area in gradients.get("areas", []):
            if area.get("label", "").lower() == area_display.lower():
                return {
                    "image": area.get("image"),
                    "gradient": area.get("gradient"),
                    "accent": area.get("accent")
                }
    except:
        pass
    
    # Return defaults if not found
    return {
        "image": f"{area_display} Sky.webp",
        "gradient": "-webkit-linear-gradient(#ffffff, #ffffff)",
        "accent": "#ffffff"
    }

def generate_wiki_markup(obj, info_text, obtaining_text, image_file, area, old_image, prev_difficulties, realm_info):
    """Generate wiki markup for the object"""
    difficulties = load_difficulties()
    
    # Get difficulty hex color and icon
    diff_hex = "#ffffff"
    diff_icon = "Missing_PNG"
    diff_priority = 0
    for diff in difficulties.get("difficulties", []):
        if diff["name"].lower() == obj["difficulty"].lower():
            diff_hex = diff.get("hex", "#ffffff")
            diff_icon = diff.get("icon", "Missing_PNG")
            diff_priority = diff.get("priority", 0)
            break
    
    # Get parent realm/subrealm category
    if realm_info[0] == "subrealm":
        parent_label = realm_info[2]
        area_category = f"{parent_label}/{realm_info[1]['label']}"
        area_display = realm_info[1]["label"]
    else:
        parent_label = realm_info[1]["label"]
        area_category = parent_label
        area_display = parent_label
    
    # Build the wiki markup
    bold_open = "<b>"
    bold_close = "</b>"
    
    # Get realm data (image, gradient, accent)
    realm_data = get_realm_data(area_display)
    realm_image = realm_data.get("image")
    realm_gradient = realm_data.get("gradient")
    gradient_value = extract_gradient_value(realm_gradient)
    
    # Format obtaining section - collapsible for Dreadful and above (priority > 11)
    if diff_priority > 11:
        formatted_obtaining = (f'{{| class="article-table mw-collapsible mw-collapsed" data-expandtext="&#9660;" data-collapsetext="&#9650;"\n'
                              f"!'''How to Find [SPOILERS]'''||\n"
                              f'|-\n'
                              f'|{obtaining_text}\n'
                              f'|}}')
    else:
        formatted_obtaining = obtaining_text
    
    # Build background file reference
    background_file = f'[[File:{realm_image}|2000px]]'
    
    markup = (f'<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;"> '
              f'{background_file} '
              f'</div>'
              f'\n<div style="--theme-accent-color:-webkit-linear-gradient({gradient_value}); --theme-accent-label-color:#ffffff;">'
              f'\n<div style="position:relative; z-index:1;">'
              f'{get_monochrome_overlay(area_display)}'
              f'\n{get_overlay_div(area_display)}'
              f'\n\n{{{{CharacterInfo'
              f'\n|name={obj["name"]}'
              f'\n|character=[[File:{image_file}]]'
              f'\n|difficulty=[[File:{diff_icon}]] <span style="color:{diff_hex}">\'\'\'<b>{obj["difficulty"].capitalize()}</b>\'\'\'</span>'
              f'\n|area=[[{area_category}]]'
              f'\n|hint={obj["description"]}'
              f'\n}}}}'
              f'\n\n== Info =='
              f'\n{info_text}'
              f'\n\n== Obtaining =='
              f'\n{formatted_obtaining}')
    
    # Add categories
    markup += f"\n\n[[Category:Objects]]"
    markup += f"\n[[Category:{obj['difficulty'].capitalize()} Objects]]"
    markup += f"\n[[Category:{area_category} Objects]]"
    markup += f"\n[[Category:{parent_label} Objects]]"
    markup += "\n\n</div>\n</div>"
    
    return markup

def get_monochrome_overlay(area_display):
    """Get monochrome overlay for Motionless realm"""
    if area_display.lower() == "motionless":
        return (f'\n<!-- Full-page monochrome overlay -->'
               f'\n<div style="'
               f'\n\tposition:fixed;'
               f'\n\ttop:0;'
               f'\n\tleft:0;'
               f'\n\tright:0;'
               f'\n\tbottom:0;'
               f'\n\tz-index:4;'
               f'\n\tpointer-events:none;'
               f'\n\tbackground:#000;'
               f'\n\tmix-blend-mode:saturation;'
               f'\n">'
               f'\n</div>')
    return ""

def get_overlay_div(area_display):
    """Get overlay image div if it exists for this realm/area"""
    try:
        gradients = load_realm_gradients()
        # Check realms
        for realm in gradients.get("realms", []):
            if realm.get("label", "").lower() == area_display.lower():
                overlay_image = realm.get("overlay_image")
                if overlay_image:
                    return (f'\n<!-- Overlay image on CharacterInfo -->'
                           f'\n<div style="'
                           f'\n\tposition:absolute;'
                           f'\n\ttop:0;'
                           f'\n\tleft:0;'
                           f'\n\tright:0;'
                           f'\n\tbottom:0;'
                           f'\n\tbackground-image:url([[File:{overlay_image}]]);'
                           f'\n\tbackground-size:cover;'
                           f'\n\tbackground-repeat:repeat;'
                           f'\n\topacity:0.3;'
                           f'\n\tpointer-events:none;'
                           f'\n\tz-index:2;'
                           f'\n">'
                           f'\n</div>')
        # Check subrealms
        for subrealm in gradients.get("subrealms", []):
            if subrealm.get("label", "").lower() == area_display.lower():
                overlay_image = subrealm.get("overlay_image")
                if overlay_image:
                    return (f'\n<!-- Overlay image on CharacterInfo -->'
                           f'\n<div style="'
                           f'\n\tposition:absolute;'
                           f'\n\ttop:0;'
                           f'\n\tleft:0;'
                           f'\n\tright:0;'
                           f'\n\tbottom:0;'
                           f'\n\tbackground-image:url([[File:{overlay_image}]]);'
                           f'\n\tbackground-size:cover;'
                           f'\n\tbackground-repeat:repeat;'
                           f'\n\topacity:0.3;'
                           f'\n\tpointer-events:none;'
                           f'\n\tz-index:2;'
                           f'\n">'
                           f'\n</div>')
        # Check areas
        for area in gradients.get("areas", []):
            if area.get("label", "").lower() == area_display.lower():
                overlay_image = area.get("overlay_image")
                if overlay_image:
                    return (f'\n<!-- Overlay image on CharacterInfo -->'
                           f'\n<div style="'
                           f'\n\tposition:absolute;'
                           f'\n\ttop:0;'
                           f'\n\tleft:0;'
                           f'\n\tright:0;'
                           f'\n\tbottom:0;'
                           f'\n\tbackground-image:url([[File:{overlay_image}]]);'
                           f'\n\tbackground-size:cover;'
                           f'\n\tbackground-repeat:repeat;'
                           f'\n\topacity:0.3;'
                           f'\n\tpointer-events:none;'
                           f'\n\tz-index:2;'
                           f'\n">'
                           f'\n</div>')
    except:
        pass
    return ""

def main(session=None):
    """Main interactive loop"""
    print("\n" + "="*60)
    print("FTBC WIKI PAGE CREATOR")
    print("="*60)
    
    while True:
        # Select realm
        realm_result = display_realms()
        status, realm_choice = realm_result
        
        if status == "exit":
            return "exit"
        if status == "back" or realm_choice is None:
            break
        
        # Load objects from selected realm
        if realm_choice[0] == "realm":
            realm_label = realm_choice[1]["label"]
            objects_data = load_realm_objects(realm_label)
        else:  # subrealm
            realm_label = realm_choice[1]["label"]
            parent_label = realm_choice[2]
            objects_data = load_subrealm_objects(realm_label, parent_label)
        
        if not objects_data:
            continue
        
        # Sort objects alphabetically
        if objects_data.get("objects"):
            objects_data["objects"] = sorted(objects_data["objects"], key=lambda x: x['name'].lower())
        
        # Check pages if session available
        page_status = None
        if session:
            page_status = check_realm_pages_batch(session, objects_data, realm_choice)
        
        # Inner loop for managing objects in this realm
        while True:
            # Clear screen before showing objects list
            clear_screen()
            
            # Select object
            obj_result = display_objects(objects_data, realm_choice, page_status)
            status, obj = obj_result
            
            if status == "exit":
                return "exit"
            if status == "back" or obj is None:
                break  # Break inner loop to go back to realm selection
            
            # Clear screen before showing object page
            clear_screen()
            
            # Check if page exists
            page_exists = False
            if session:
                page_exists = check_wiki_page_exists(session, obj["name"])
            
            mode = "EDIT" if page_exists else "CREATE"
            
            print("\n" + "="*60)
            print(f"Object: {obj['name']} [{mode}]")
            print("="*60)
            print("Commands: 'back', 'exit'\n")
            print(f"Difficulty: {obj['difficulty'].capitalize()}")
            print(f"Hint: {obj['description']}")
            
            # Get user input
            info_text = prompt_multiline("Enter INFO section (description).")
            if info_text.lower() in ["back", "exit"]:
                continue  # Back to object selection
            
            obtaining_text = prompt_multiline("Enter OBTAINING section (how to get it).")
            if obtaining_text.lower() in ["back", "exit"]:
                continue  # Back to object selection
            
            image_input = input("\nEnter image file name (press Enter to use default: " + obj['name'] + ".png): ").strip()
            image_file = image_input if image_input else f"{obj['name']}.png"
            
            old_image = input("\nDoes this object have an old image? (yes/no): ").strip().lower()
            old_image = old_image in ["yes", "y"]
            
            prev_difficulties = input("Enter previous difficulties (if any, e.g., 'Insane, Hard'): ").strip()
            
            # Generate markup
            markup = generate_wiki_markup(
                obj, info_text, obtaining_text, image_file,
                obj.get("area", "Unknown"), old_image, prev_difficulties, realm_choice
            )
            
            # Show preview
            print("\n" + "="*60)
            print("Source Editor Preview (Copy & Paste into Fandom):")
            print("="*60)
            print(markup)
            
            # Automatically save to .txt file
            if realm_choice[0] == "realm":
                realm_label = realm_choice[1]["label"]
                objects_folder = DATA_DIR / "realms" / realm_label / "Objects"
            else:  # subrealm
                realm_label = realm_choice[1]["label"]
                parent_label = realm_choice[2]
                # Sanitize folder names
                def sanitize_folder_name(name):
                    name = re.sub(r'<[^>]+>', '', name)  # Remove HTML tags
                    name = re.sub(r'[<>:"/\\|?*]', '', name)  # Remove invalid characters
                    return name.strip()
                
                sub_folder_name = sanitize_folder_name(realm_label)
                objects_folder = DATA_DIR / "subrealms" / parent_label / sub_folder_name / "Objects"
            
            # Create Objects folder if it doesn't exist
            objects_folder.mkdir(parents=True, exist_ok=True)
            
            # Save markup to .txt file
            txt_file = objects_folder / f"{obj['name']}.txt"
            txt_file.write_text(markup, encoding='utf-8')
            print(f"\n✓ Page saved to {txt_file}")
            
            # Ask about publishing to wiki
            publish = input("\nPublish to wiki using Spongybot? (yes/no/back): ").strip().lower()
            if publish in ["back", "b"]:
                continue  # Back to object selection
            elif publish in ["yes", "y"]:
                if session:
                    success, message = publish_to_wiki(session, obj["name"], markup)
                    if success:
                        print(f"✓ {message}")
                    else:
                        print(f"✗ {message}")
                else:
                    print("⚠️  Session not available. Cannot publish.")
            
            # Post-page menu
            menu_action = None
            while True:
                print("\n" + "="*60)
                print("What would you like to do?")
                print("="*60)
                print("(1) Create/edit another object in this realm")
                print("(2) Select a different realm")
                print("(3) Exit")
                print("(0) Back to realm selection")
                
                choice = input("\nEnter your choice (1-3 or 0): ").strip()
                
                if choice == "1":
                    menu_action = "continue_realm"
                    break
                elif choice == "2":
                    menu_action = "new_realm"
                    break
                elif choice == "3":
                    return "exit"
                elif choice == "0":
                    menu_action = "new_realm"
                    break
                else:
                    print("Invalid choice. Try again.")
            
            # Handle post-page menu result
            if menu_action == "continue_realm":
                continue  # Continue with object selection in same realm
            elif menu_action == "new_realm":
                break  # Go back to realm selection
        
        # If we exit the inner loop due to "back" from object selection, continue to next realm

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExit.")
        sys.exit(0)
