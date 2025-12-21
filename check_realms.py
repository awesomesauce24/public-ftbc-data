import re
from pathlib import Path

realms = ['Backrooms', 'Barren Desert', 'Cherry Grove', 'Classic Paradise', 'Evil Forest', 'Frozen World', 'Inverted', 'Magma Canyon', 'Main Realm', 'Midnight Rooftops', 'Polluted Marshlands', 'Sakura Serenity', 'Timber Peaks', 'Yoyleland']

for f in sorted(Path('.').glob('*.txt')):
    try:
        content = f.read_text(encoding='utf-8', errors='ignore').lower()
        found = None
        for realm in realms:
            if realm.lower() in content:
                found = realm
                break
        status = found if found else "[Unknown]"
        print(f'{f.name}: {status}')
    except:
        print(f'{f.name}: [Error]')
