#!/usr/bin/env python3
"""
Wiki page template generator with realm styling.

Generates properly styled wiki pages using realm data from realms.json.
"""

import json
from pathlib import Path
from typing import Dict, Optional

class WikiTemplateGenerator:
    def __init__(self):
        """Initialize with realm and difficulty data."""
        self.realms_path = Path('metadata/realms.json')
        self.difficulties_path = Path('metadata/difficulties.json')
        
        with open(self.realms_path, 'r', encoding='utf-8') as f:
            realms_data = json.load(f)
        
        # Flatten realms
        self.realms_map = {}
        for realm_list in realms_data.get('normal', []):
            if isinstance(realm_list, dict):
                label = realm_list.get('label', '')
                if label:
                    self.realms_map[label] = realm_list
        
        # Add subrealms
        for subrealm_type, subrealm_list in realms_data.get('subrealms', {}).items():
            if isinstance(subrealm_list, list):
                for realm in subrealm_list:
                    if isinstance(realm, dict):
                        label = realm.get('label', '')
                        if label:
                            self.realms_map[label] = realm
        
        # Load difficulties
        with open(self.difficulties_path, 'r', encoding='utf-8') as f:
            difficulties_data = json.load(f)
        
        self.difficulties_map = {}
        for diff in difficulties_data.get('difficulties', []):
            name = diff.get('name', '')
            if name:
                self.difficulties_map[name] = {
                    'icon': diff.get('icon', f'{name}.png'),
                    'color': diff.get('hex', '#ffffff')  # Use 'hex' field from difficulties.json
                }
    
    def generate_page_header(self, realm_name: str) -> str:
        """Generate styled page header from realm data."""
        # Handle Basement specially - it's under Yoyle Factory subrealm
        lookup_realm = realm_name
        if realm_name == "The Basement":
            lookup_realm = "Basement"
        
        realm_info = self.realms_map.get(lookup_realm, {})
        
        image = realm_info.get('image', 'Main Realm Sky.webp')
        gradient = realm_info.get('gradient', '-webkit-linear-gradient(#78ff78, #00ff00)')
        accent = realm_info.get('accent', '#ffffff')
        
        header = f'''<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
 [[File:{image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">
'''
        return header
    
    def generate_character_info(self, object_name: str, obj_data: Dict, 
                               info: str = '', obtaining: str = '', 
                               prev_diffs: list = None, old_image: Optional[str] = None) -> str:
        """Generate CharacterInfo template section."""
        if prev_diffs is None:
            prev_diffs = []
        
        difficulty = obj_data.get('difficulty', '')
        realm = obj_data.get('realm', '')
        images = obj_data.get('images', [])
        description = obj_data.get('description', '')
        
        # Start CharacterInfo inline
        char_info = f"{{{{CharacterInfo|name={object_name}\n"
        
        # Add images in gallery format
        if images or old_image:
            char_info += "|character=<gallery>\n"
            if images:
                for img in images:
                    filename = img['file']
                    if 'New' in filename:
                        char_info += f"{filename}|{img['name']} New\n"
                    else:
                        char_info += f"{filename}|{img['name']}\n"
            if old_image:
                char_info += f"{old_image}|{object_name} Old\n"
            char_info += "</gallery>\n"
        
        # Add difficulty with icon and color
        diff_info = self.difficulties_map.get(difficulty, {})
        diff_icon = diff_info.get('icon', f'{difficulty}.png')
        diff_color = diff_info.get('color', '#ffffff')
        char_info += f"|difficulty= [[File:{diff_icon}]] <span style=\"color:{diff_color}\">'''{difficulty}'''</span>\n"
        
        # Add area (realm) - special handling for Basement
        area_link = realm
        if realm == "The Basement":
            area_link = "Basement"  # Just "Basement", not "The Basement"
        char_info += f"|area=[[{area_link}]]\n"
        
        # Add hint/description
        if description:
            char_info += f"|hint={description}\n"
        
        # Add additional info if provided
        if info:
            char_info += "|additionalinfo\n"
        
        # Add previous difficulties with icons and colors
        all_prev_diffs = obj_data.get('previousDifficulties', []) + prev_diffs
        if all_prev_diffs:
            char_info += "|previousdifficulties = \n"
            for prev_diff in all_prev_diffs:
                prev_info = self.difficulties_map.get(prev_diff, {})
                prev_icon = prev_info.get('icon', f'{prev_diff}.png')
                prev_color = prev_info.get('color', '#ffffff')
                char_info += f"[[File:{prev_icon}]] <span style=\"color:{prev_color}\">'''{prev_diff}'''</span>\n"
        
        char_info += "}}\n"
        
        return char_info
    
    def generate_complete_page(self, object_name: str, obj_data: Dict,
                              info: str = '', obtaining: str = '',
                              prev_diffs: list = None, old_image: Optional[str] = None) -> str:
        """Generate complete wiki page with header, CharacterInfo, and sections."""
        if prev_diffs is None:
            prev_diffs = []
        
        realm = obj_data.get('realm', '')
        
        # Start with styled header
        page = self.generate_page_header(realm)
        page += "\n"
        
        # Add CharacterInfo
        page += self.generate_character_info(object_name, obj_data, info, obtaining, prev_diffs, old_image)
        page += "\n"
        
        # Add Info section
        if info:
            page += "== Info ==\n"
            page += info + "\n\n"
        
        # Add Obtaining section
        if obtaining:
            page += "== Obtaining ==\n"
            page += obtaining + "\n\n"
        
        # Close styled div
        page += "</div>\n</div>\n\n"
        
        # Add categories
        difficulty = obj_data.get('difficulty', '')
        page += f"[[Category:{difficulty} Objects]]\n"
        page += f"[[Category:{realm} Objects]]\n"
        page += f"[[Category:Objects]]\n"
        
        return page

def main():
    """Test the template generator."""
    generator = WikiTemplateGenerator()
    
    # Test with example data
    test_data = {
        'name': 'American Flag',
        'difficulty': 'Effortless',
        'realm': 'Barren Desert',
        'description': 'this donut shop is america-certified. LAND OF THE FREE BABY!!!!!!!!',
        'images': [
            {'name': 'American Flag', 'file': 'American Flag New.png'},
            {'name': 'American Flag', 'file': 'American Flag.png'}
        ],
        'previousDifficulties': ['Easy']
    }
    
    page = generator.generate_complete_page(
        'American Flag',
        test_data,
        info='This is the info section.',
        obtaining='This is the obtaining section.',
        prev_diffs=['Event']
    )
    
    print(page)

if __name__ == '__main__':
    main()
