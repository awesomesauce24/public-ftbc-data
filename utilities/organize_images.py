#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

# Base directories
base_dir = Path(".")
characters_dir = base_dir / "FTBC Characters"
realms_dir = base_dir / "Realms"
subrealms_dir = base_dir / "Subrealms"

# Dictionary to store character -> realm/subrealm mapping
character_locations = {}

# Parse realm files
for realm_file in realms_dir.glob("*.txt"):
    realm_name = realm_file.stem
    with open(realm_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Extract character names from lines like "Name | difficulty | location"
        for line in content.split('\n'):
            if '|' in line and not line.strip().startswith('='):
                parts = [p.strip() for p in line.split('|')]
                if parts:
                    char_name = parts[0]
                    if char_name and not char_name.startswith('http'):
                        character_locations[char_name] = realm_name

# Parse subrealm files
for subrealm_file in subrealms_dir.glob("*.txt"):
    subrealm_name = subrealm_file.stem
    with open(subrealm_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Extract character names
        for line in content.split('\n'):
            if '|' in line and not line.strip().startswith('='):
                parts = [p.strip() for p in line.split('|')]
                if parts:
                    char_name = parts[0]
                    if char_name and not char_name.startswith('http'):
                        # Subrealms take priority
                        character_locations[char_name] = subrealm_name

# Create directories and move files
for char_name, location in character_locations.items():
    # Find matching image file (case-insensitive)
    for img_file in characters_dir.glob("*.png"):
        if img_file.name.replace(".png", "").lower() == char_name.lower():
            target_dir = characters_dir / location
            target_dir.mkdir(parents=True, exist_ok=True)
            target_path = target_dir / img_file.name
            
            # Move file
            if img_file.exists() and not target_path.exists():
                shutil.move(str(img_file), str(target_path))
                print(f"Moved: {img_file.name} -> {location}/")

# Move remaining unorganized subdirectories into appropriate realms
special_dirs = {
    "Evil Forest": "EvilForest",
    "Cherry Grove": "CherryGrove",
    "Frozen World": "FrozenWorld",
}

for old_name, realm_name in special_dirs.items():
    old_path = characters_dir / old_name
    if old_path.exists() and old_path.is_dir():
        # Move all files from this directory into the realm directory
        target_dir = characters_dir / realm_name
        target_dir.mkdir(parents=True, exist_ok=True)
        
        for file in old_path.glob("*"):
            if file.is_file():
                target_file = target_dir / file.name
                if not target_file.exists():
                    shutil.move(str(file), str(target_file))
                    print(f"Moved: {file.name} -> {realm_name}/")
        
        # Remove empty directory
        try:
            old_path.rmdir()
            print(f"Removed empty directory: {old_name}")
        except:
            pass

print("✅ Image organization complete!")
print(f"Organized {len(character_locations)} characters")
