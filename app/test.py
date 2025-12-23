#!/usr/bin/env python3
"""
Quick test script to verify wiki system is working
Run: python app/test.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core.loader import RealmLoader, SubrealmLoader
from core.config import Config
from cli.commands import RealmCommands, SearchCommands, ExportCommands


def test_config():
    """Test config loading"""
    print("Testing Config...")
    color = Config.get_color("Hard")
    assert color == "#FF7700", f"Expected #FF7700, got {color}"
    
    realm_info = Config.get_realm_info("Main Realm")
    assert realm_info is not None, "Realm info is None"
    
    print("  ✓ Config works\n")


def test_loaders():
    """Test data loaders"""
    print("Testing Loaders...")
    
    loader = RealmLoader(Config.REALMS_PATH)
    realms = loader.get_all_realms()
    
    if realms:
        print(f"  ✓ Found {len(realms)} realms")
        
        # Test specific realm
        if "Main Realm" in realms:
            data = loader.get_realm_data("Main Realm")
            desc = loader.get_realm_description("Main Realm")
            subrealms = loader.get_subrealms("Main Realm")
            
            print(f"    - Main Realm has {len(subrealms)} subrealms")
            print(f"    - Data: {'loaded' if data else 'empty'}")
            print(f"    - Description: {'loaded' if desc else 'empty'}")
    else:
        print("  ✗ No realms found")
    
    print()


def test_commands():
    """Test CLI commands"""
    print("Testing Commands...")
    
    cmd = RealmCommands()
    realms = cmd.list_realms()
    
    if realms:
        print(f"  ✓ RealmCommands: {len(realms)} realms available")
        
        # Show first realm
        first_realm = realms[0]
        info = cmd.show_realm(first_realm)
        print(f"    - {first_realm}: {len(info.get('subrealms', []))} subrealms")
    
    search_cmd = SearchCommands()
    results = search_cmd.search_realms("forest")
    print(f"  ✓ SearchCommands: found {len(results)} results for 'forest'")
    
    export_cmd = ExportCommands()
    export_list = export_cmd.export_realm_list('text')
    print(f"  ✓ ExportCommands: exported realm list")
    
    print()


def test_structure():
    """Test data structure integrity"""
    print("Testing Data Structure...")
    
    loader = RealmLoader(Config.REALMS_PATH)
    realms = loader.get_all_realms()
    
    for realm in realms[:3]:  # Check first 3 realms
        realm_path = Config.REALMS_PATH / realm
        json_exists = (realm_path / f"{realm}.json").exists()
        txt_exists = (realm_path / "page.txt").exists()
        
        print(f"  {realm}:")
        print(f"    - JSON: {'✓' if json_exists else '✗'}")
        print(f"    - TXT:  {'✓' if txt_exists else '✗'}")
        
        subrealms = loader.get_subrealms(realm)
        if subrealms:
            print(f"    - Subrealms: {len(subrealms)}")
    
    print()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("FTBC Wiki System - Test Suite")
    print("="*60 + "\n")
    
    try:
        test_config()
        test_loaders()
        test_commands()
        test_structure()
        
        print("="*60)
        print("✓ All tests passed!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
