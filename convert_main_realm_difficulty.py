#!/usr/bin/env python3
"""
Convert remaining difficulty sections in Main_Realm.txt from bullet-point to ObjectDifficultyList format
"""

import re
from pathlib import Path

def extract_objects_from_section(section_text):
    """Extract object names from bullet-point format section"""
    # Pattern: *[[File:Icon.png|frameless|Name]] [[Object Name]]
    pattern = r'\*\[\[File:[^\]]*\]\] \[\[([^\]]+)\]\]'
    matches = re.findall(pattern, section_text)
    return matches

def create_gallery_entries(objects, icon_name):
    """Create gallery entries for ObjectDifficultyList format"""
    gallery_lines = []
    for obj in objects:
        # Handle special characters and spaces in filenames
        filename = obj.replace(' ', '_') + '.png'
        # Create the gallery entry
        entry = f"File:{filename}|[[File:{icon_name}.png|18px]] '''[[{obj}]]'''"
        gallery_lines.append(entry)
    return gallery_lines

def create_object_difficulty_list(name, icon, color, objects):
    """Create the ObjectDifficultyList template section"""
    gallery_entries = create_gallery_entries(objects, icon)
    gallery_content = '\n'.join(gallery_entries)
    
    template = f"""{{{{ObjectDifficultyList
|name = {name}
|icon = {icon}.png
|color = {color}
|total = {len(objects)}
|gallery =
<gallery widths="60" heights="60" mode="packed">
{gallery_content}
</gallery>
}}}}"""
    return template

def convert_main_realm():
    """Main conversion function"""
    file_path = Path('c:\\Users\\anony\\OneDrive\\Documentos\\GitHub\\public-ftbc-data\\pages\\realms\\Main_Realm.txt')
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Reading file...")
    print(f"File size: {len(content)} characters")
    
    # Define conversions with exact patterns to find
    conversions = [
        {
            'name': 'Intermediate',
            'icon': 'Intermediate FTBC',
            'color': '#ffb700',
            'search_pattern': r"====<span style=\"color:#ffb700\">\'\'\'Intermediate\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Hard',
            'icon': 'Hard',
            'color': '#ff7e21',
            'search_pattern': r"====<span style=\"color:#ff7e21\">\'\'\'Hard\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Difficult',
            'icon': 'Difficult',
            'color': '#f54f25',
            'search_pattern': r"====<span style=\"color:#f54f25\">\'\'\'Difficult\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Extreme',
            'icon': 'Extreme',
            'color': '#ED2727',
            'search_pattern': r"==== <span style=\"color:#ED2727\">\'\'\'Extreme\'\'\'</span> ====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Unforgiving',
            'icon': 'Unforgiving',
            'color': '#ff143f',
            'search_pattern': r"====<span style=\"color:#ff143f\">\'\'\'Unforgiving\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Insane',
            'icon': 'Insane',
            'color': '#FF1C95',
            'search_pattern': r"==== <span style=\"color:#FF1C95\">\'\'\'Insane\'\'\'</span> ====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Dreadful',
            'icon': 'Dreadful',
            'color': '#db25ff',
            'search_pattern': r"====<span style=\"color:#db25ff\">\'\'\'Dreadful\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Terrifying',
            'icon': 'Terrifying',
            'color': '#8b17ff',
            'search_pattern': r"====<span style=\"color:#8b17ff\">\'\'\'Terrifying\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Arduous',
            'icon': 'Arduous',
            'color': '#5d0cff',
            'search_pattern': r"====<span style=\"color:#5d0cff\">\'\'\'Arduous\'\'\'</span>====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Strenuous',
            'icon': 'Strenuous',
            'color': '#4048E5',
            'search_pattern': r"==== <span style=\"color:#4048E5\">\'\'\'Strenuous\'\'\'</span> ====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Remorseless',
            'icon': 'Remorseless',
            'color': '#2084FF',
            'search_pattern': r"==== <span style=\"color:#2084FF\">\'\'\'Remorseless\'\'\'</span> ====\n(.*?)\n-{10,}"
        },
        {
            'name': 'Horrifying',
            'icon': 'Horrifying',
            'color': '#2bd0fd; -webkit-text-stroke-width: 1px; -webkit-text-stroke-color: #72e1ff',
            'search_pattern': r"====<span style=\"color:#2bd0fd; -webkit-text-stroke-width: 1px; -webkit-text-stroke-color: #72e1ff font-size: 24px\">\'\'\'Horrifying\'\'\'</span>====\n(.*?)\n-{10,}"
        },
    ]
    
    # Process each difficulty
    for conversion in conversions:
        print(f"\nProcessing {conversion['name']}...")
        
        match = re.search(conversion['search_pattern'], content, re.DOTALL)
        if not match:
            print(f"  ERROR: Could not find section for {conversion['name']}")
            continue
        
        section_text = match.group(1)
        full_match = match.group(0)
        
        objects = extract_objects_from_section(section_text)
        print(f"  Found {len(objects)} objects")
        
        # Create the new template with separator
        new_template = create_object_difficulty_list(
            conversion['name'],
            conversion['icon'],
            conversion['color'],
            objects
        )
        
        # Replace with new template + separator
        replacement = new_template + '\n\n' + '-' * 60 + '\n'
        content = content.replace(full_match, replacement, 1)
        print(f"  ✓ Converted {conversion['name']}")
    
    # Write back to file
    print("\nWriting converted file...")
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Successfully converted all remaining difficulty sections!")
    return True

if __name__ == '__main__':
    try:
        convert_main_realm()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
