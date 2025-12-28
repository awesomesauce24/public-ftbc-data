#!/usr/bin/env python3
"""
Fetch object descriptions from wiki and create individual JSON files.
Creates object_descriptions/ folder with one file per object.
"""

import json
import re
import requests
import time
from pathlib import Path
from collections import defaultdict
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warning for requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DIFFICULTY_MAP = {
    "Effortless": "effortless",
    "Easy": "easy",
    "Moderate": "moderate",
    "Normal": "normal",
    "Intermediate": "intermediate",
    "Hard": "hard",
    "Difficult": "difficult",
    "Extreme": "extreme",
    "Unforgiving": "unforgiving",
    "Insane": "insane",
    "Dreadful": "dreadful",
    "Terrifying": "terrifying",
    "Arduous": "arduous",
    "Strenuous": "strenuous",
    "Remorseless": "remorseless",
    "Horrifying": "horrifying",
}

def fetch_object_page(object_name, retries=3):
    """Fetch wiki page for an object with retry logic."""
    url = "https://ftbc.fandom.com/api.php"
    
    params = {
        "action": "query",
        "titles": object_name,
        "prop": "revisions",
        "rvprop": "content",
        "format": "json",
    }
    
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, timeout=20, verify=False)
            response.raise_for_status()
            
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            
            for page_id, page_data in pages.items():
                if "missing" in page_data:
                    return None
                    
                revisions = page_data.get("revisions", [])
                if revisions:
                    return revisions[0].get("*", "")
            
            return None
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            else:
                return None
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            else:
                return None

def parse_character_info(content, object_name, area, difficulty):
    """Parse CharacterInfo template to extract object data."""
    # Find the CharacterInfo template
    char_info_pattern = r'\{\{CharacterInfo\s*\|([^}]+)\}\}'
    match = re.search(char_info_pattern, content, re.DOTALL)
    
    obj_data = {
        "name": object_name,
        "area": area,
        "difficulty": difficulty,
        "description": "",
        "hint": "",
        "previous_difficulties": [],
        "wiki_markup": ""
    }
    
    if not match:
        return obj_data
    
    template_content = match.group(1)
    
    # Extract description/hint
    hint_match = re.search(r'\|hint\s*=\s*([^\n|]+)', template_content)
    if hint_match:
        hint_text = hint_match.group(1).strip()
        # Clean up wiki markup
        hint_text = re.sub(r'\[\[([^\|\]]+)(?:\|([^\]]+))?\]\]', r'\2' if r'\2' else r'\1', hint_text)
        obj_data["hint"] = hint_text
        obj_data["description"] = hint_text  # Use hint as description
    
    # Extract previous difficulties
    prev_diff_pattern = r'\|previousdifficulties\s*=\s*(?:.*?<span[^>]*>\'\'\'([^\']+)\'\'\'</span>|([^|\n]+))'
    prev_match = re.search(prev_diff_pattern, template_content)
    if prev_match:
        prev_text = (prev_match.group(1) or prev_match.group(2)).strip()
        if prev_text:
            obj_data["previous_difficulties"].append(prev_text)
    
    # Store raw template for reference
    obj_data["wiki_markup"] = template_content[:500]  # First 500 chars
    
    return obj_data

def collect_all_objects():
    """Collect all objects from current data structure."""
    objects = {}  # object_name -> {area, difficulty, location}
    
    # From realms
    realms_dir = Path('data/realms')
    for realm_dir in realms_dir.iterdir():
        if not realm_dir.is_dir():
            continue
        
        # Check for direct objects.json
        obj_file = realm_dir / 'objects.json'
        if obj_file.exists():
            try:
                with open(obj_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for obj in data.get('objects', []):
                    obj_name = obj.get('name', '').strip()
                    if obj_name and len(obj_name) > 1 and not obj_name.isdigit():
                        objects[obj_name] = {
                            "area": obj.get('area', realm_dir.name),
                            "difficulty": obj.get('difficulty', ''),
                            "location": f"realm:{realm_dir.name}"
                        }
            except Exception as e:
                print(f"ERROR reading {obj_file}: {e}")
        
        # Check for sub-areas
        for area_dir in realm_dir.iterdir():
            if area_dir.is_dir():
                obj_file = area_dir / 'objects.json'
                if obj_file.exists():
                    try:
                        with open(obj_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        for obj in data.get('objects', []):
                            obj_name = obj.get('name', '').strip()
                            if obj_name and len(obj_name) > 1 and not obj_name.isdigit():
                                objects[obj_name] = {
                                    "area": obj.get('area', area_dir.name),
                                    "difficulty": obj.get('difficulty', ''),
                                    "location": f"realm:{realm_dir.name}/{area_dir.name}"
                                }
                    except Exception as e:
                        print(f"ERROR reading {obj_file}: {e}")
    
    # From subrealms
    subrealms_dir = Path('data/subrealms')
    if subrealms_dir.exists():
        for parent_dir in subrealms_dir.iterdir():
            if parent_dir.is_dir():
                for subrealm_dir in parent_dir.iterdir():
                    if subrealm_dir.is_dir():
                        obj_file = subrealm_dir / 'objects.json'
                        if obj_file.exists():
                            try:
                                with open(obj_file, 'r', encoding='utf-8') as f:
                                    data = json.load(f)
                                for obj in data.get('objects', []):
                                    obj_name = obj.get('name', '').strip()
                                    if obj_name and len(obj_name) > 1 and not obj_name.isdigit():
                                        objects[obj_name] = {
                                            "area": obj.get('area', subrealm_dir.name),
                                            "difficulty": obj.get('difficulty', ''),
                                            "location": f"subrealm:{parent_dir.name}/{subrealm_dir.name}"
                                        }
                            except Exception as e:
                                print(f"ERROR reading {obj_file}: {e}")
    
    return objects

def main():
    print("=" * 80)
    print("FETCHING OBJECT DESCRIPTIONS FROM WIKI")
    print("=" * 80)
    print()
    
    # Create output directory
    output_dir = Path('object_descriptions')
    output_dir.mkdir(exist_ok=True)
    
    print(f"Output directory: {output_dir.absolute()}")
    print()
    
    # Collect all objects
    print("Collecting all objects from data/realms and data/subrealms...")
    objects = collect_all_objects()
    print(f"Found {len(objects)} unique objects\n")
    
    # Fetch data for each object
    fetched = 0
    skipped = 0
    failed = 0
    
    for i, (obj_name, obj_info) in enumerate(sorted(objects.items()), 1):
        # Skip invalid names
        if not obj_name or obj_name.isdigit() or len(obj_name) < 2:
            skipped += 1
            continue
        
        # Create filename
        filename = obj_name.replace('/', '_').replace('\\', '_') + '.json'
        output_file = output_dir / filename
        
        # Skip if already exists
        if output_file.exists():
            skipped += 1
            if i % 100 == 0:
                print(f"  [{i:4}/{len(objects)}] Progress: {fetched} fetched, {skipped} skipped, {failed} failed")
            continue
        
        try:
            # Fetch from wiki (with longer timeout)
            content = fetch_object_page(obj_name)
            
            if content:
                # Parse data
                obj_data = parse_character_info(
                    content,
                    obj_name,
                    obj_info['area'],
                    obj_info['difficulty']
                )
                
                # Add location info
                obj_data['location'] = obj_info['location']
                
                # Save to file
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(obj_data, f, indent=2, ensure_ascii=False)
                
                fetched += 1
                
                if i % 100 == 0:
                    print(f"  [{i:4}/{len(objects)}] Progress: {fetched} fetched, {skipped} skipped, {failed} failed")
            else:
                failed += 1
        
        except KeyboardInterrupt:
            print(f"\n\nInterrupted at object {i}/{len(objects)}: {obj_name}")
            print(f"Progress: Fetched {fetched}, Skipped {skipped}, Failed {failed}")
            print("Run again to resume (already-fetched files are cached)\n")
            break
        except Exception as e:
            failed += 1
    
    print()
    print("=" * 80)
    print(f"✓ COMPLETE")
    print(f"  Fetched: {fetched}")
    print(f"  Skipped: {skipped}")
    print(f"  Failed:  {failed}")
    print(f"  Total:   {len(objects)}")
    print(f"  Output:  {output_dir.absolute()}")
    print("=" * 80)

if __name__ == "__main__":
    main()
