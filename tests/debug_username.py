#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path

rbx_file = Path('extraction/rbx/CLASSIC EXPANSION Find the BFB Characters.rbxlx')
tree = ET.parse(rbx_file)
root = tree.getroot()

for item in root.findall('.//Item'):
    ws_name = item.find("Properties/string[@name='Name']")
    if ws_name is not None and ws_name.text == 'Workspace':
        for child in item.findall('Item'):
            obj_name = child.find("Properties/string[@name='Name']")
            if obj_name is not None and obj_name.text == 'Objects':
                print("First 20 items in Objects folder:")
                obj_items = list(child.findall('Item'))[:20]
                for obj in obj_items:
                    obj_name_elem = obj.find("Properties/string[@name='Name']")
                    if obj_name_elem is not None:
                        print(f"  - {obj_name_elem.text}")
                break
        break


