#!/usr/bin/env python3
"""
Create wiki pages from enriched metadata.

Scans objectjsons to find objects needing wiki pages.
Shows status of existing pages and generates new ones.
"""

import json
import pywikibot
from pathlib import Path
from typing import Dict, List, Tuple
import sys

class PageCreator:
    def __init__(self):
        """Initialize with PyWikiBot site connection."""
        try:
            self.site = pywikibot.Site(url='https://ftbc.fandom.com/api.php')
        except Exception as e:
            print(f"Error connecting to wiki: {e}")
            raise
        
        self.metadata_dir = Path('metadata/objectjsons')
    
    def list_realms(self) -> List[str]:
        """List all available realms."""
        realms = []
        for json_file in sorted(self.metadata_dir.glob('*.json')):
            realm_name = json_file.stem
            realms.append(realm_name)
        return realms
    
    def page_exists(self, object_name: str) -> bool:
        """Check if wiki page exists for an object."""
        try:
            page = pywikibot.Page(self.site, object_name)
            return page.exists()
        except:
            return False
    
    def scan_realm(self, realm_name: str) -> Tuple[List[str], List[str]]:
        """
        Scan a realm and check which objects have wiki pages.
        
        Returns:
            Tuple of (with_pages, without_pages) - lists of object names
        """
        json_file = self.metadata_dir / f"{realm_name}.json"
        
        if not json_file.exists():
            return [], []
        
        with open(json_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        with_pages = []
        without_pages = []
        
        total = len(objects)
        for idx, obj_name in enumerate(sorted(objects.keys()), 1):
            # Show progress
            progress = f"\r  Scanning... [{idx}/{total}]"
            print(progress, end='', flush=True)
            
            if self.page_exists(obj_name):
                with_pages.append(obj_name)
            else:
                without_pages.append(obj_name)
        
        print("\r" + " " * 50 + "\r", end='', flush=True)  # Clear progress line
        return with_pages, without_pages
    
    def display_realm_status(self, realm_name: str):
        """Scan and display status for a realm."""
        print(f"\n{'='*70}")
        print(f"Realm: {realm_name}")
        print(f"{'='*70}\n")
        
        with_pages, without_pages = self.scan_realm(realm_name)
        
        total = len(with_pages) + len(without_pages)
        coverage = (len(with_pages) / total * 100) if total > 0 else 0
        
        print(f"Pages exist: {len(with_pages)}/{total} ({coverage:.1f}%)\n")
        
        # Display with pages
        if with_pages:
            print("Pages that exist:")
            for obj_name in with_pages:
                print(f"  [+] {obj_name}")
        
        # Display without pages
        if without_pages:
            print("\nPages that need to be created:")
            for obj_name in without_pages:
                print(f"  [x] {obj_name}")
        
        print()
        return len(with_pages), len(without_pages)
    
    def interactive_mode(self):
        """Interactive mode to select and scan realms."""
        realms = self.list_realms()
        
        print(f"\n{'='*70}")
        print("Available Realms")
        print(f"{'='*70}\n")
        
        for idx, realm in enumerate(realms, 1):
            print(f"  ({idx:2d}) {realm}")
        
        print(f"\n{'='*70}")
        print("Enter realm number or name (or 'all' to scan all):")
        print(f"{'='*70}\n")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'all':
            selected_realms = realms
        elif user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(realms):
                selected_realms = [realms[idx]]
            else:
                print(f"Invalid number. Please choose 1-{len(realms)}")
                return
        else:
            # Try to match by name
            matching = [r for r in realms if user_input.lower() in r.lower()]
            if matching:
                selected_realms = matching
            else:
                print(f"No realm matching '{user_input}' found.")
                return
        
        # Scan selected realms
        total_with = 0
        total_without = 0
        
        for realm in selected_realms:
            with_pages, without_pages = self.display_realm_status(realm)
            total_with += with_pages
            total_without += without_pages
        
        # Summary
        print(f"{'='*70}")
        print("Summary")
        print(f"{'='*70}")
        print(f"Total pages exist: {total_with}")
        print(f"Total pages to create: {total_without}")
        total = total_with + total_without
        if total > 0:
            print(f"Coverage: {total_with/total*100:.1f}%")
        print(f"{'='*70}\n")

def main():
    try:
        creator = PageCreator()
        creator.interactive_mode()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
