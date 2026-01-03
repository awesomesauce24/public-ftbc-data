#!/usr/bin/env python3
"""
FTBC Wiki Scraper using PyWikiBot

Fetches object data from FTBC Fandom wiki using PyWikiBot and populates
enriched objectjsons metadata with:
- Images (current and "New" variants)
- Previous difficulties
- Wiki content (Info and Obtaining sections)

Requires: pywikibot
Install: pip install pywikibot
"""

import pywikibot
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

class FTBCWikiScraper:
    """Scrape FTBC wiki using PyWikiBot."""
    
    def __init__(self):
        """Initialize scraper with PyWikiBot site."""
        try:
            # Connect to FTBC Fandom wiki
            self.site = pywikibot.Site(url='https://ftbc.fandom.com/api.php')
            print(f"Connected to: {self.site}")
        except Exception as e:
            print(f"Error connecting to wiki: {e}")
            raise
        
        self.metadata_dir = Path('metadata/objectjsons')
        
        # Load replacements mapping (rbxlx name -> official name)
        self.replacements = self._load_replacements()
    
    def _load_replacements(self) -> Dict[str, str]:
        """Load replacements.json mapping."""
        replacements_file = Path('metadata/replacements.json')
        if not replacements_file.exists():
            return {}
        
        try:
            with open(replacements_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load replacements: {e}")
            return {}
    
    def get_wiki_name(self, rbxlx_name: str) -> str:
        """
        Convert rbxlx object name to official wiki name using replacements.
        
        Args:
            rbxlx_name: Object name from rbxlx file
            
        Returns:
            Official wiki name (after applying replacements)
        """
        return self.replacements.get(rbxlx_name, rbxlx_name)
    
    def fetch_page_text(self, object_name: str) -> Optional[str]:
        """
        Fetch raw wiki markup for a page.
        
        Args:
            object_name: Name of the object/page
            
        Returns:
            Raw wiki markup or None if page doesn't exist
        """
        try:
            page = pywikibot.Page(self.site, object_name)
            
            if not page.exists():
                return None
            
            return page.get()
        
        except pywikibot.exceptions.NoPageError:
            return None
        except Exception as e:
            return None
    
    def extract_character_info(self, wikitext: str) -> Dict:
        """
        Extract CharacterInfo template data from wiki markup.
        
        Args:
            wikitext: Raw wiki markup
            
        Returns:
            Dictionary with extracted fields
        """
        data = {}
        
        # Find CharacterInfo template
        match = re.search(r'\{\{CharacterInfo(.*?)\}\}', wikitext, re.DOTALL)
        if not match:
            return data
        
        content = match.group(1)
        
        # Extract fields
        # Name
        name_match = re.search(r'\|name\s*=\s*([^\|]+)', content)
        if name_match:
            data['name'] = name_match.group(1).strip()
        
        # Difficulty - extract from '''...'''
        diff_match = re.search(r"'''([^']+)'''", content)
        if diff_match:
            data['difficulty'] = diff_match.group(1).strip()
        
        # Area
        area_match = re.search(r'\|area\s*=\s*\[\[([^\]]+)\]\]', content)
        if area_match:
            data['area'] = area_match.group(1).strip()
        
        # Hint
        hint_match = re.search(r'\|hint\s*=\s*([^\|]+)', content)
        if hint_match:
            data['hint'] = hint_match.group(1).strip()
        
        # Character/Images
        char_match = re.search(r'\|character\s*=\s*((?:(?!\n\|)[^\n]|\n(?!\|))*)', content, re.DOTALL)
        if char_match:
            data['character_raw'] = char_match.group(1).strip()
        
        # Previous difficulties
        prev_match = re.search(r'\|previousdifficulties\s*=\s*((?:(?!\n\|)[^\n]|\n(?!\|))*)', content, re.DOTALL)
        if prev_match:
            data['previousdifficulties_raw'] = prev_match.group(1).strip()
        
        return data
    
    def find_images_by_filename(self, object_name: str) -> List[Dict]:
        """
        Check for images on wiki by trying different filename variants.
        
        Tries:
        - ObjectName.{webp,png,jpg}
        - ObjectName New.{webp,png,jpg}
        
        Args:
            object_name: Name of the object
            
        Returns:
            List of dicts with {name, file} keys
        """
        images = []
        extensions = ['webp', 'png', 'jpg']
        variants = [
            (object_name, object_name),  # (filename_base, display_name)
            (f'{object_name} New', f'{object_name} New')
        ]
        
        for filename_base, display_name in variants:
            for ext in extensions:
                filename = f"{filename_base}.{ext}"
                
                try:
                    # Try to get the file page
                    file_page = pywikibot.FilePage(self.site, filename)
                    if file_page.exists():
                        images.append({
                            'name': display_name,
                            'file': filename
                        })
                        break  # Found this variant, move to next
                except Exception:
                    continue
        
        return images
    
    def parse_previous_difficulties(self, raw: str) -> List[str]:
        """
        Parse previous difficulties from raw markup.
        
        Args:
            raw: Raw previousdifficulties content
            
        Returns:
            List of difficulty names
        """
        difficulties = []
        
        # Find all '''Difficulty''' patterns
        for match in re.finditer(r"'''([^']+)'''", raw):
            difficulty = match.group(1).strip()
            if difficulty and difficulty not in difficulties:
                difficulties.append(difficulty)
        
        return difficulties
    
    def scrape_object(self, object_name: str) -> Optional[Dict]:
        """
        Scrape all wiki data for an object.
        
        Args:
            object_name: Name of the object
            
        Returns:
            Dictionary with scraped data or None if nothing found
        """
        result = {}
        
        # Always try to find images by filename (all objects should have them)
        images = self.find_images_by_filename(object_name)
        if images:
            result['images'] = images
        
        # Also try to get previous difficulties from wiki page
        wikitext = self.fetch_page_text(object_name)
        if wikitext:
            char_info = self.extract_character_info(wikitext)
            
            # Previous difficulties
            if 'previousdifficulties_raw' in char_info:
                prev_diffs = self.parse_previous_difficulties(char_info['previousdifficulties_raw'])
                if prev_diffs:
                    result['previousDifficulties'] = prev_diffs
        
        return result if result else None
    
    def process_realm(self, realm_name: str) -> Tuple[int, int]:
        """
        Process all objects in a realm using parallel scraping.
        
        Args:
            realm_name: Name of the realm
            
        Returns:
            Tuple of (updated_count, total_count)
        """
        json_file = self.metadata_dir / f"{realm_name}.json"
        
        if not json_file.exists():
            return 0, 0
        
        # Load metadata
        with open(json_file, 'r', encoding='utf-8') as f:
            objects = json.load(f)
        
        total_count = len(objects)
        object_names = list(objects.keys())
        
        # Scrape all objects in parallel
        # Map: rbxlx_name -> wiki_name (for scraping)
        wiki_results = {}
        with ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all scrape tasks using wiki names (after replacements)
            futures = {}
            for rbxlx_name in object_names:
                wiki_name = self.get_wiki_name(rbxlx_name)
                futures[executor.submit(self.scrape_object, wiki_name)] = rbxlx_name
            
            # Process results as they complete
            for future in as_completed(futures):
                rbxlx_name = futures[future]
                try:
                    wiki_data = future.result()
                    if wiki_data:  # Only store if we got data
                        wiki_results[rbxlx_name] = wiki_data
                        # Show both names if they're different
                        wiki_name = self.get_wiki_name(rbxlx_name)
                        if wiki_name != rbxlx_name:
                            print(f"  [OK] {rbxlx_name} ({wiki_name})")
                        else:
                            print(f"  [OK] {rbxlx_name}")
                except Exception as e:
                    pass
        
        # Update metadata only for objects that had wiki data
        updated_count = 0
        for obj_name, wiki_data in wiki_results.items():
            obj_data = objects[obj_name]
            
            # Update with images if found
            if 'images' in wiki_data:
                obj_data['images'] = wiki_data['images']
            
            # Update with previous difficulties if found
            if 'previousDifficulties' in wiki_data:
                obj_data['previousDifficulties'] = wiki_data['previousDifficulties']
            
            updated_count += 1
        
        # Save updated metadata
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(objects, f, indent=2, ensure_ascii=False)
        
        return updated_count, total_count
    
    def process_all(self, realm_filter: Optional[str] = None):
        """
        Process all realms or specific realm.
        
        Args:
            realm_filter: Optional specific realm name to process
        """
        if not self.metadata_dir.exists():
            print(f"Error: {self.metadata_dir} not found")
            return
        
        json_files = sorted(self.metadata_dir.glob('*.json'))
        total_updated = 0
        total_objects = 0
        
        print("Scraping FTBC wiki using PyWikiBot...\n")
        
        for json_file in json_files:
            realm_name = json_file.stem
            
            # Filter by realm if specified
            if realm_filter and realm_name != realm_filter:
                continue
            
            print(f">> {realm_name}:")
            updated, total = self.process_realm(realm_name)
            total_updated += updated
            total_objects += total
            print(f"  [{updated}/{total} updated]\n")
        
        print("=" * 70)
        print("[DONE] Wiki scraping complete!")
        print(f"  Total objects updated: {total_updated}/{total_objects}")
        print("=" * 70)

def main():
    """Main entry point."""
    import sys
    
    try:
        scraper = FTBCWikiScraper()
        
        # Get optional realm filter from command line
        realm_filter = sys.argv[1] if len(sys.argv) > 1 else None
        
        scraper.process_all(realm_filter)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
