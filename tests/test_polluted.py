#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path

rbx_file = Path('extraction/rbx/Polluted Marshlands.rbxlx')
tree = ET.parse(rbx_file)
root = tree.getroot()

for item in root.findall('.//Item'):
    ws_name = item.find("Properties/string[@name='Name']")
    if ws_name is not None and ws_name.text == 'Workspace':
        print('[+] Found Workspace')
        for child in item.findall('Item'):
            child_name = child.find("Properties/string[@name='Name']")
            if child_name is not None:
                print(f'  - {child_name.text}')
                if child_name.text == 'Objects':
                    obj_items = list(child.findall('Item'))
                    print(f'[+] Objects folder has {len(obj_items)} direct children')
                    for obj in obj_items[:5]:
                        obj_name = obj.find("Properties/string[@name='Name']")
                        if obj_name is not None:
                            print(f'    - {obj_name.text}')

