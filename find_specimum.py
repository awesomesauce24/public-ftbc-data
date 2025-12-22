#!/usr/bin/env python3
"""Find which realm has Specimum Sandwich"""
import json
import os
from pathlib import Path

realms_dir = Path('Realms')
found_in = []

for realm_dir in sorted(realms_dir.iterdir()):
    if realm_dir.is_dir() and realm_dir.name != '.cache':
        realm_file = realm_dir / f"{realm_dir.name}.json"
        if realm_file.exists():
            try:
                with open(realm_file, encoding='utf-8') as f:
                    data = json.load(f)
                
                objs = data if isinstance(data, list) else data.get('objects', [])
                
                for obj in objs:
                    obj_name = obj.get('ObjectName', '') if isinstance(obj, dict) else str(obj)
                    if 'Specimum' in obj_name:
                        found_in.append((realm_dir.name, obj_name))
            except Exception as e:
                print(f"Error reading {realm_file}: {e}")

if found_in:
    print("Found in realms:")
    for realm, obj_name in found_in:
        print(f"  {realm}: {obj_name}")
else:
    print("Specimum Sandwich NOT FOUND IN ANY REALM!")
