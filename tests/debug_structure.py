#!/usr/bin/env python3
import xml.etree.ElementTree as ET
from pathlib import Path

rbx_file = Path('extraction/rbx/Polluted Marshlands.rbxlx')
tree = ET.parse(rbx_file)
root = tree.getroot()

for item in root.findall('.//Item'):
    ws_name = item.find("Properties/string[@name='Name']")
    if ws_name is not None and ws_name.text == 'Workspace':
        for child in item.findall('Item'):
            obj_name = child.find("Properties/string[@name='Name']")
            if obj_name is not None and obj_name.text == 'Objects':
                obj_items = list(child.findall('Item'))
                if len(obj_items) > 0:
                    # Check first object
                    first_obj = obj_items[0]
                    first_name = first_obj.find("Properties/string[@name='Name']")
                    print(f"First object: {first_name.text if first_name is not None else 'N/A'}")
                    print(f"Has {len(list(first_obj))} child elements")
                    
                    # Show all children and their structure
                    for i, child_elem in enumerate(first_obj):
                        print(f"\nChild {i}: tag={child_elem.tag}, attrib={child_elem.attrib}")
                        # Check if it has Properties
                        props = child_elem.find("Properties")
                        if props is not None:
                            print(f"  Has Properties")
                            for prop in props:
                                if prop.tag == 'string':
                                    attr_name = prop.get('name')
                                    text = prop.text
                                    print(f"    - string[@name='{attr_name}'] = {text}")
                break
        break

