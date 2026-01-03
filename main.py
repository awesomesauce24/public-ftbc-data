#!/usr/bin/env python3
"""
FTBC Data Manager - Central hub for all data and wiki management tools.

Provides interactive menu to access:
- Wiki page creation
- Metadata enrichment
- Difficulty change application
- Wiki scraping
- And more
"""

import subprocess
import sys
from pathlib import Path

def main_menu():
    """Display main menu and handle user selection."""
    while True:
        print("\n" + "="*70)
        print("FTBC DATA MANAGER")
        print("="*70)
        print("\n  WIKI PAGE CREATION")
        print("    (1) Create/edit wiki pages (interactive)")
        print("    (2) Scan realms for page status")
        print("\n  METADATA MANAGEMENT")
        print("    (3) Enrich objectjsons metadata")
        print("    (4) Apply difficulty changes")
        print("\n  WIKI INTEGRATION")
        print("    (5) Scrape wiki (images, previous difficulties)")
        print("\n  UTILITIES")
        print("    (6) Show metadata stats")
        print("    (7) Filter Main Realm")
        print("\n  OTHER")
        print("    (q) Quit")
        print("\n" + "="*70)
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == 'q':
            print("\nGoodbye!")
            break
        elif choice == '1':
            run_interactive_create_pages()
        elif choice == '2':
            run_scan_pages()
        elif choice == '3':
            run_enrich_metadata()
        elif choice == '4':
            run_apply_difficulties()
        elif choice == '5':
            run_wiki_scraper()
        elif choice == '6':
            show_stats()
        elif choice == '7':
            run_filter_main_realm()
        else:
            print("\nInvalid option. Please try again.")

def run_interactive_create_pages():
    """Run interactive wiki page creator."""
    print("\n" + "="*70)
    print("WIKI PAGE CREATOR - INTERACTIVE MODE")
    print("="*70)
    print("Starting interactive wiki page creator...\n")
    
    scripts_dir = Path(__file__).parent / 'scripts'
    script = scripts_dir / 'interactive_create_pages.py'
    
    if not script.exists():
        print(f"Error: Script not found at {script}")
        return
    
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error running script: {e}")

def run_scan_pages():
    """Run page status scanner."""
    print("\n" + "="*70)
    print("PAGE STATUS SCANNER")
    print("="*70)
    print("Starting page scanner...\n")
    
    scripts_dir = Path(__file__).parent / 'scripts'
    script = scripts_dir / 'create_pages.py'
    
    if not script.exists():
        print(f"Error: Script not found at {script}")
        return
    
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error running script: {e}")

def run_enrich_metadata():
    """Run metadata enrichment."""
    print("\n" + "="*70)
    print("METADATA ENRICHMENT")
    print("="*70)
    print("Starting metadata enrichment...\n")
    
    scripts_dir = Path(__file__).parent / 'scripts'
    script = scripts_dir / 'enrich_objectjsons.py'
    
    if not script.exists():
        print(f"Error: Script not found at {script}")
        return
    
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error running script: {e}")

def run_apply_difficulties():
    """Run difficulty change application."""
    print("\n" + "="*70)
    print("APPLY DIFFICULTY CHANGES")
    print("="*70)
    print("Starting difficulty change application...\n")
    
    scripts_dir = Path(__file__).parent / 'scripts'
    script = scripts_dir / 'apply_difficulty_changes.py'
    
    if not script.exists():
        print(f"Error: Script not found at {script}")
        return
    
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error running script: {e}")

def run_wiki_scraper():
    """Run wiki scraper."""
    print("\n" + "="*70)
    print("WIKI SCRAPER")
    print("="*70)
    print("Starting wiki scraper...\n")
    
    scripts_dir = Path(__file__).parent / 'scripts'
    script = scripts_dir / 'wiki_scraper_pywikibot.py'
    
    if not script.exists():
        print(f"Error: Script not found at {script}")
        return
    
    try:
        subprocess.run([sys.executable, str(script)], check=False)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"Error running script: {e}")

def show_stats():
    """Show metadata statistics."""
    import json
    from pathlib import Path
    
    print("\n" + "="*70)
    print("METADATA STATISTICS")
    print("="*70 + "\n")
    
    metadata_dir = Path('metadata/objectjsons')
    
    total_objects = 0
    total_realms = 0
    realms_data = {}
    
    for json_file in sorted(metadata_dir.glob('*.json')):
        realm_name = json_file.stem
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                objects = json.load(f)
            
            count = len(objects)
            total_objects += count
            total_realms += 1
            realms_data[realm_name] = count
        except Exception as e:
            print(f"Error reading {realm_name}: {e}")
    
    print(f"Total realms: {total_realms}")
    print(f"Total objects: {total_objects}\n")
    
    print("Objects per realm:")
    for realm, count in realms_data.items():
        print(f"  {realm:<40} {count:4d}")
    
    print("\n" + "="*70)

def run_filter_main_realm():
    """Run Main Realm filter."""
    print("\n" + "="*70)
    print("FILTER MAIN REALM")
    print("="*70)
    print("This would filter Main Realm.json to only actual Main Realm objects.")
    print("Already completed in previous session.")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
