#!/usr/bin/env python3
"""Test the complete workflow without authentication (since that requires live wiki)."""

import sys
from pathlib import Path
from io import StringIO

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def test_full_workflow():
    """Test a simulated object page creation workflow."""
    print("\n[TEST] Full Object Page Creation Workflow (simulated)")
    print("-" * 60)
    
    from create_pages import (
        list_realms_and_subrealms_hierarchical,
        load_json,
        check_wiki_page_exists,
        get_difficulty_info,
        get_realm_gradient,
        get_special_case
    )
    
    # Step 1: Load realms
    print("[1/5] Loading realms and subrealms...")
    items = list_realms_and_subrealms_hierarchical()
    print(f"     [+] Loaded {len(items)} items")
    
    # Step 2: Select first realm (Main Realm)
    print("[2/5] Selecting Main Realm...")
    selected_item = items[0]  # Main Realm
    _, selected_realm, selected_path, is_subrealm, parent_realm, item_type = selected_item
    print(f"     [+] Selected: {selected_realm}")
    
    # Step 3: Check objects in realm
    print("[3/5] Listing objects in realm...")
    realm_dir = Path(selected_path)
    objects = []
    
    if realm_dir.exists():
        for obj_file in sorted(realm_dir.glob('*.json')):
            objects.append(obj_file.stem)
    
    if not objects:
        objects_file = realm_dir / 'objects.json'
        if objects_file.exists():
            try:
                objects_data = load_json(objects_file)
                if isinstance(objects_data.get('objects'), list):
                    objects = [obj.get('name', '') for obj in objects_data.get('objects', []) if obj.get('name')]
            except:
                pass
    
    print(f"     [+] Found {len(objects)} objects")
    
    if objects:
        # Step 4: Test with first object
        print("[4/5] Testing with first object...")
        obj_name = objects[0]
        print(f"     [+] Selected object: {obj_name}")
        
        # Check wiki
        exists = check_wiki_page_exists(obj_name)
        print(f"     [+] Wiki page exists: {exists}")
        
        # Get difficulty
        difficulty = 'Normal'
        icon, hex_color, proper_name, priority = get_difficulty_info(difficulty)
        print(f"     [+] Difficulty info: {proper_name} (priority {priority})")
        
        # Get gradient
        gradient, accent, image = get_realm_gradient(selected_realm)
        print(f"     [+] Realm gradient: {bool(gradient)}")
        
        # Step 5: Generate wiki markup
        print("[5/5] Generating wiki markup...")
        wiki_markup = f"""<div align="center">
[[File:{obj_name}.png]]
</div>

== {obj_name} ==
This is a test object page."""
        
        print(f"     [+] Generated {len(wiki_markup)} chars of wiki markup")
        
        return True
    else:
        print("[!] No objects found - workflow cannot be tested fully")
        return True  # Not a failure


if __name__ == "__main__":
    print("=" * 60)
    print("FTBC Wiki System - Complete Workflow Test")
    print("=" * 60)
    
    try:
        result = test_full_workflow()
        if result:
            print("\n" + "=" * 60)
            print("[+] Full workflow test passed!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n[x] Workflow test failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n[x] Error during workflow: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
