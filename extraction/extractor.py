#!/usr/bin/env python3
"""
Extract realm data from Roblox .rbxlx files (plain XML format).

.rbxlx files are XML files that describe Roblox places.
This script extracts object lists and creates JSON files.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path


# Mapping of Roblox usernames to actual object names
# Format: {"username": "actual_object_name"}
USERNAME_TO_OBJECT = {
    "Present": "Gifty",
    "Brick Wall": "Mortar",
    "Building Tools": "ReplicatedStorage",
    "Crystal": "Morganite",
    "Evil Blocky": "B.O.D",
    "Kebab": "Kabab",
    "CrystalBallOSC": "Dynamite",
    "megapidragon": "gas can",
    "Just_Summa": "Pizza",
    "Dirty Bubble": "Trash Can",
    "scenerycloud": "Blob of Syrup",
    "AndrewRoblox3333": "Pink Lemonade",
    "Redstrike8k": "Soul Cube",
    "BFDI_BIGFAN": "Cheddary",
    "blOckHeAdFORLiFyes": "Cuber",
    "Supermario432158": "Autumn Leaf",
    "HaydounDO": "Locket",
    "dragonboy010814": "Beehive",
    "Baba_Booey5875": "Yoyle Soda",
    "119WildUpdate": "Pill",
    "ibbyiscool26": "Pearl",
    "calolmeeeee3": "Lotus Flower",
    "FredsterYT10": "Jetpacky",
    "N_Gu1d2010": "Watermelon Slice",
    "TeardropIsAwesome": "Fronk",
    "Fourbfdi2468": "Geode",
    "MishkaVal": "Filler",
    "Kokodore": "Storm Ball",
    "DrPepperHeinz": "Rollarskate",
    "austin51278741": "Tombstone",
    "EpicHatesAbba": "Stool",
    "RoboNickoli20": "cheese",
    "Strawberri": "Cartridge",
    "darkwolf9854": "Duffel Bag",
}


def extract_rbxlx(rbxlx_path):
    """
    Extract object data from a .rbxlx file.
    
    .rbxlx files are plain XML files.
    
    Args:
        rbxlx_path: Path to the .rbxlx file
        
    Returns:
        List of dicts with 'name', 'difficulty', and 'description' keys
    """
    objects = []
    
    def is_valid_object_name(name):
        """Filter out Roblox IDs and junk entries."""
        if not name or len(name) < 2:
            return False
        # Skip pure numbers and scientific notation (Roblox IDs)
        if name.replace('.', '').replace('-', '').replace('+', '').replace('e', '').isdigit():
            return False
        # Skip names that are just numbers or look like IDs
        try:
            float(name)
            return False  # It's a number
        except ValueError:
            pass
        # Skip empty or whitespace-only names
        if not name.strip():
            return False
        return True
    
    try:
        # Read as plain XML file
        tree = ET.parse(rbxlx_path)
        root = tree.getroot()
        
        # Navigate to Workspace > Objects to get only actual objects
        # Find the Workspace item
        for item in root.findall('.//Item'):
            workspace_name = item.find("Properties/string[@name='Name']")
            if workspace_name is not None and workspace_name.text == 'Workspace':
                # Found Workspace, now look for Objects folder inside it (direct children only)
                for child in item.findall('Item'):
                    objects_name = child.find("Properties/string[@name='Name']")
                    if objects_name is not None and objects_name.text == 'Objects':
                        # Found Objects folder, extract only direct children as objects
                        for obj_item in child.findall('Item'):
                            name_elem = obj_item.find("Properties/string[@name='Name']")
                            if name_elem is not None and name_elem.text:
                                obj_name = name_elem.text.strip()
                                
                                # Filter out junk entries
                                if not is_valid_object_name(obj_name):
                                    continue
                                
                                # Apply username-to-object mapping if available
                                if obj_name in USERNAME_TO_OBJECT:
                                    obj_name = USERNAME_TO_OBJECT[obj_name]
                                
                                # Extract Difficulty and Description from nested Items (StringValues)
                                difficulty = ""
                                description = ""
                                
                                # Iterate through all child items to find StringValues
                                for nested_item in obj_item.findall('Item'):
                                    nested_name = nested_item.find("Properties/string[@name='Name']")
                                    nested_value = nested_item.find("Properties/string[@name='Value']")
                                    
                                    if nested_name is not None and nested_name.text:
                                        # Check case-insensitive
                                        name_lower = nested_name.text.lower()
                                        if name_lower == 'difficulty' and nested_value is not None and nested_value.text:
                                            difficulty = nested_value.text
                                        elif name_lower == 'description' and nested_value is not None and nested_value.text:
                                            description = nested_value.text
                                
                                # Skip objects with "[Hidden in..." or "[Start in..." - these are references, not actual objects
                                if description and description.startswith('['):
                                    continue
                                
                                objects.append({
                                    "name": obj_name,
                                    "difficulty": difficulty,
                                    "description": description
                                })
                        return objects  # Found and processed Objects, exit
        
    except ET.ParseError as e:
        print(f"[x] XML parse error in {rbxlx_path.name}: {e}")
        return objects
    except Exception as e:
        print(f"[x] Error processing {rbxlx_path.name}: {e}")
        return objects
    
    return objects


def main():
    """Main extraction process."""
    print("=" * 70)
    print("ROBLOX .rbxlx EXTRACTION")
    print("=" * 70)
    print()
    
    # Look for rbx folder in parent directory (outside the repo)
    rbx_dir = Path(__file__).parent.parent.parent / '.rbx'
    
    if not rbx_dir.exists():
        # Fallback to old location if parent doesn't exist
        rbx_dir = Path(__file__).parent / 'rbx'
    
    if not rbx_dir.exists():
        print(f"[x] Directory not found: {rbx_dir}")
        return
    
    # Find all .rbxlx files
    rbxlx_files = list(rbx_dir.glob('*.rbxlx'))
    
    if not rbxlx_files:
        print(f"[x] No .rbxlx files found in {rbx_dir}")
        return
    
    print(f"[+] Found {len(rbxlx_files)} .rbxlx files")
    print()
    
    # Process each file
    extracted_count = 0
    failed_count = 0
    total_objects = 0
    
    for rbxlx_file in sorted(rbxlx_files):
        print(f"[~] Processing: {rbxlx_file.name}", end=" ... ", flush=True)
        
        objects = extract_rbxlx(rbxlx_file)
        
        if objects:
            # Determine realm/subrealm from filename
            realm_name = rbxlx_file.stem  # Remove .rbxlx extension
            
            # Create output directory in metadata/realms (already extracted)
            output_dir = Path('metadata/realms') / realm_name
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save each object as individual JSON file
            for obj in objects:
                obj_name = obj.get('name', 'Unknown')
                # Sanitize filename (remove/replace invalid characters)
                safe_name = obj_name
                # Replace invalid filename characters
                for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
                    safe_name = safe_name.replace(char, '_')
                # Remove non-ASCII characters that might cause issues
                safe_name = safe_name.encode('ascii', errors='ignore').decode('ascii')
                # Limit length
                if len(safe_name) > 200:
                    safe_name = safe_name[:200]
                
                output_file = output_dir / f'{safe_name}.json'
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(obj, f, indent=2, ensure_ascii=False)
            
            print(f"[+] {len(objects)} objects extracted")
            extracted_count += 1
            total_objects += len(objects)
        else:
            print(f"[x] No objects found")
            failed_count += 1
    
    print()
    print("=" * 70)
    print(f"[+] EXTRACTION COMPLETE")
    print(f"    Realms processed: {extracted_count}")
    print(f"    Failed: {failed_count}")
    print(f"    Total objects: {total_objects}")
    print(f"    Output: metadata/realms/{{RealmName}}/ObjectName.json")
    print("=" * 70)


if __name__ == "__main__":
    main()
