import json
from pathlib import Path

print("REALM OBJECTS:")
total_realms = 0
for realm_dir in sorted(Path('data/realms').iterdir()):
    if realm_dir.is_dir():
        # Check if realm_dir has direct objects.json
        obj_file = realm_dir / 'objects.json'
        if obj_file.exists():
            with open(obj_file, 'r', encoding='utf-8') as f:
                d = json.load(f)
            count = len(d.get('objects', []))
            total_realms += count
            print(f'  {realm_dir.name:25} {count:3} objects')
        # Check if realm_dir has sub-areas
        else:
            realm_total = 0
            for area_dir in sorted(realm_dir.iterdir()):
                if area_dir.is_dir():
                    area_obj_file = area_dir / 'objects.json'
                    if area_obj_file.exists():
                        with open(area_obj_file, 'r', encoding='utf-8') as f:
                            d = json.load(f)
                        count = len(d.get('objects', []))
                        realm_total += count
            if realm_total > 0:
                total_realms += realm_total
                print(f'  {realm_dir.name:25} {realm_total:3} objects (14 areas)')

print(f"\nREALM TOTAL: {total_realms}")

print("\nSUBREALM OBJECTS:")
total_subrealms = 0
for parent_dir in sorted(Path('data/subrealms').iterdir()):
    if parent_dir.is_dir():
        for subrealm_dir in sorted(parent_dir.iterdir()):
            if subrealm_dir.is_dir():
                obj_file = subrealm_dir / 'objects.json'
                if obj_file.exists():
                    with open(obj_file, 'r', encoding='utf-8') as f:
                        d = json.load(f)
                    count = len(d.get('objects', []))
                    total_subrealms += count
                    print(f'  {parent_dir.name}/{subrealm_dir.name:25} {count:3} objects')

print(f"\nSUBREALM TOTAL: {total_subrealms}")
print(f"\nGRAND TOTAL: {total_realms + total_subrealms}")
