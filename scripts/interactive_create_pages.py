#!/usr/bin/env python3
"""
Interactive wiki page creator for FTBC objects.

Allows users to:
1. Select a realm and object
2. Auto-populate CharacterInfo with metadata
3. Edit Info and Obtaining sections
4. Upload to wiki

Features:
- Auto-fills difficulty, area, realm data
- Proper styled page with realm background/gradient
- Handles image variants (New/Old)
- Tracks previous difficulties
"""

import json
import pywikibot
from pathlib import Path
from typing import Dict, Optional, Tuple
import sys
from wiki_template_generator import WikiTemplateGenerator

class WikiPageCreator:
    def __init__(self):
        """Initialize with PyWikiBot site connection."""
        try:
            self.site = pywikibot.Site(url='https://ftbc.fandom.com/api.php')
            print("✓ Connected to FTBC wiki\n")
        except Exception as e:
            print(f"Error connecting to wiki: {e}")
            raise
        
        self.metadata_dir = Path('metadata/objectjsons')
        self.current_realm = None
        self.objects_list = {}
        self.template_generator = WikiTemplateGenerator()
    
    def list_realms(self) -> list:
        """List all realms."""
        return sorted([f.stem for f in self.metadata_dir.glob('*.json')])
    
    def select_realm(self) -> Optional[str]:
        """Interactive realm selection."""
        realms = self.list_realms()
        
        print(f"\n{'='*70}")
        print("SELECT REALM")
        print(f"{'='*70}\n")
        
        for idx, realm in enumerate(realms, 1):
            print(f"  ({idx:2d}) {realm}")
        
        print(f"\n{'='*70}")
        print("Enter realm number or name (or 'q' to quit):")
        print(f"{'='*70}\n")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'q':
            return None
        
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(realms):
                return realms[idx]
        else:
            matching = [r for r in realms if user_input.lower() in r.lower()]
            if matching:
                return matching[0]
        
        print(f"\nInvalid input.")
        return self.select_realm()
    
    def load_realm_objects(self, realm_name: str):
        """Load objects for a realm."""
        json_file = self.metadata_dir / f"{realm_name}.json"
        
        if not json_file.exists():
            print(f"Realm file not found: {realm_name}")
            return False
        
        with open(json_file, 'r', encoding='utf-8') as f:
            self.objects_list = json.load(f)
        
        self.current_realm = realm_name
        return True
    
    def page_exists(self, object_name: str) -> bool:
        """Check if wiki page exists."""
        try:
            page = pywikibot.Page(self.site, object_name)
            return page.exists()
        except:
            return False
    
    def select_object(self) -> Optional[str]:
        """Interactive object selection."""
        print(f"\n{'='*70}")
        print(f"REALM: {self.current_realm}")
        print(f"{'='*70}\n")
        
        objects = sorted(self.objects_list.keys())
        
        for idx, obj_name in enumerate(objects, 1):
            status = "[+]" if self.page_exists(obj_name) else "[x]"
            print(f"  {status} ({idx:3d}) {obj_name}")
        
        print(f"\n{'='*70}")
        print("Select object number or name (or 'q' to change realm):")
        print(f"{'='*70}\n")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'q':
            return None
        
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(objects):
                return objects[idx]
        else:
            matching = [o for o in objects if user_input.lower() in o.lower()]
            if matching:
                return matching[0]
        
        print(f"\nInvalid input.")
        return self.select_object()
    
    def edit_object(self, object_name: str) -> Optional[Dict]:
        """Interactive object editor."""
        obj_data = self.objects_list[object_name]
        
        print(f"\n{'='*70}")
        print(f"OBJECT: {object_name}")
        print(f"{'='*70}\n")
        
        # Display auto-populated fields
        print("Auto-populated fields:")
        print(f"  Name: {object_name}")
        print(f"  Difficulty: {obj_data.get('difficulty', 'Unknown')}")
        print(f"  Realm: {obj_data.get('realm', 'Unknown')}")
        if 'images' in obj_data and obj_data['images']:
            print(f"  Images: {[img['file'] for img in obj_data['images']]}")
        print()
        
        # Prompt for Info
        print("=" * 70)
        print("Enter INFO section (or press Enter to skip):")
        print("=" * 70)
        info_content = input_multiline()
        
        # Prompt for Obtaining
        print("\n" + "=" * 70)
        print("Enter OBTAINING section (or press Enter to skip):")
        print("=" * 70)
        obtaining_content = input_multiline()
        
        # Prompt for previous difficulties
        print("\n" + "=" * 70)
        print("Enter additional previous difficulties (comma-separated, or press Enter to skip):")
        print("=" * 70)
        prev_diffs_input = input("> ").strip()
        prev_diffs = [d.strip() for d in prev_diffs_input.split(',') if d.strip()] if prev_diffs_input else []
        
        # Prompt for old image
        print("\n" + "=" * 70)
        print("Enter old image filename (or press Enter to skip):")
        print("=" * 70)
        old_image = input("> ").strip() or None
        
        # Build wiki page
        wiki_markup = self.generate_wiki_page(object_name, obj_data, info_content, obtaining_content, prev_diffs, old_image)
        
        # Preview
        print("\n" + "=" * 70)
        print("WIKI PAGE PREVIEW")
        print("=" * 70)
        print(wiki_markup)
        print("=" * 70)
        
        # Confirm upload
        print("\nUpload this page? (y/n)")
        if input("> ").strip().lower() == 'y':
            self.upload_page(object_name, wiki_markup)
            return {'uploaded': True}
        else:
            print("Page not uploaded.")
            return {'uploaded': False}
    
    def generate_wiki_page(self, object_name: str, obj_data: Dict, info: str, obtaining: str, prev_diffs: list, old_image: Optional[str]) -> str:
        """Generate wiki page using template generator."""
        return self.template_generator.generate_complete_page(
            object_name,
            obj_data,
            info=info,
            obtaining=obtaining,
            prev_diffs=prev_diffs,
            old_image=old_image
        )
    
    def upload_page(self, object_name: str, wiki_markup: str):
        """Upload page to wiki."""
        try:
            page = pywikibot.Page(self.site, object_name)
            page.text = wiki_markup
            page.save(summary="Created/updated via wiki page creator script")
            print(f"\n✓ Page uploaded: {object_name}")
        except Exception as e:
            print(f"\n✗ Error uploading page: {e}")
    
    def run(self):
        """Main interactive loop."""
        while True:
            # Select realm
            realm = self.select_realm()
            if realm is None:
                print("\nGoodbye!")
                break
            
            if not self.load_realm_objects(realm):
                continue
            
            # Object selection loop
            while True:
                obj = self.select_object()
                if obj is None:
                    break  # Change realm
                
                result = self.edit_object(obj)
                
                if result and result.get('uploaded'):
                    # Show menu
                    print(f"\n{'='*70}")
                    print("NEXT:")
                    print(f"{'='*70}")
                    print("  (1) Choose another object (in this realm)")
                    print("  (2) Choose another realm")
                    print("  (3) Quit")
                    print(f"{'='*70}\n")
                    
                    choice = input("> ").strip()
                    
                    if choice == '2':
                        break  # Change realm
                    elif choice == '3':
                        print("\nGoodbye!")
                        return
                    # else: continue with same realm

def input_multiline() -> str:
    """Get multi-line input from user."""
    print("(Enter text, then press Ctrl+D or type 'END' on a new line to finish)")
    lines = []
    try:
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
    except EOFError:
        pass
    return '\n'.join(lines)

def main():
    try:
        creator = WikiPageCreator()
        creator.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
