#!/usr/bin/env python3
"""Test all features of the system."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def test_realm_loading():
    """Test realm and subrealm loading."""
    print("\n[TEST 1] Realm & Subrealm Loading")
    print("-" * 60)
    
    from create_pages import list_realms_and_subrealms_hierarchical
    
    items = list_realms_and_subrealms_hierarchical()
    print(f"[+] Loaded {len(items)} realm/subrealm items")
    
    # Count by type
    realms = [item for item in items if item[5] == 'realm']
    subrealms = [item for item in items if item[5] in ['subrealm', 'nested_subrealm']]
    
    print(f"[+] {len(realms)} realms")
    print(f"[+] {len(subrealms)} subrealms/nested subrealms")
    
    return True


def test_json_loading():
    """Test JSON loading for metadata."""
    print("\n[TEST 2] JSON Metadata Loading")
    print("-" * 60)
    
    from create_pages import load_json
    
    # Test loading difficulties
    difficulties = load_json('metadata/difficulties.json')
    print(f"[+] Loaded difficulties.json: {len(difficulties.get('difficulties', []))} difficulties")
    
    # Test loading gradients
    gradients = load_json('metadata/realm_gradients.json')
    print(f"[+] Loaded realm_gradients.json: {len(gradients.get('realms', []))} realms, {len(gradients.get('subrealms', []))} subrealms")
    
    # Test loading special cases
    special_cases = load_json('metadata/special_cases.json')
    print(f"[+] Loaded special_cases.json: {len(special_cases.get('special_cases', {}))} special cases")
    
    return True


def test_wiki_page_checking():
    """Test wiki page existence checking."""
    print("\n[TEST 3] Wiki Page Existence Checking")
    print("-" * 60)
    
    from create_pages import check_wiki_page_exists
    
    # Test with a known object
    result = check_wiki_page_exists('Apple')
    print(f"[+] check_wiki_page_exists('Apple'): {result}")
    
    # Test with unknown object
    result = check_wiki_page_exists('NonExistentObject_xyz_123')
    print(f"[+] check_wiki_page_exists('NonExistentObject_xyz_123'): {result}")
    
    return True


def test_difficulty_info():
    """Test difficulty info retrieval."""
    print("\n[TEST 4] Difficulty Info Retrieval")
    print("-" * 60)
    
    from create_pages import get_difficulty_info
    
    # Test getting difficulty info
    icon, hex_color, proper_name, priority = get_difficulty_info('Normal')
    print(f"[+] Normal: icon={icon}, color={hex_color}, name={proper_name}, priority={priority}")
    
    icon, hex_color, proper_name, priority = get_difficulty_info('Dreadful')
    print(f"[+] Dreadful: icon={icon}, color={hex_color}, name={proper_name}, priority={priority}")
    
    return True


def test_realm_gradient():
    """Test realm gradient retrieval."""
    print("\n[TEST 5] Realm Gradient Retrieval")
    print("-" * 60)
    
    from create_pages import get_realm_gradient
    
    # Test getting gradient
    gradient, accent, image = get_realm_gradient('Main Realm')
    print(f"[+] Main Realm: gradient={gradient}, accent={accent}, image={bool(image)}")
    
    gradient, accent, image = get_realm_gradient('Barren Desert')
    print(f"[+] Barren Desert: gradient={gradient}, accent={accent}, image={bool(image)}")
    
    return True


def test_auth_setup():
    """Test authentication setup."""
    print("\n[TEST 6] Authentication Setup")
    print("-" * 60)
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    username = os.getenv('BOT_USERNAME')
    password = os.getenv('BOT_PASSWORD')
    
    print(f"[+] BOT_USERNAME configured: {bool(username)}")
    print(f"[+] BOT_PASSWORD configured: {bool(password)}")
    
    if not username or not password:
        print("[x] Missing credentials in .env")
        return False
    
    return True


def test_create_pages_import():
    """Test that main.py can import everything."""
    print("\n[TEST 7] Module Imports")
    print("-" * 60)
    
    try:
        from auth import authenticate
        print("[+] Successfully imported authenticate from auth")
        
        from create_pages import create
        print("[+] Successfully imported create from create_pages")
        
        return True
    except Exception as e:
        print(f"[x] Import error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("FTBC Wiki Management System - Feature Tests")
    print("=" * 60)
    
    tests = [
        test_realm_loading,
        test_json_loading,
        test_wiki_page_checking,
        test_difficulty_info,
        test_realm_gradient,
        test_auth_setup,
        test_create_pages_import,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            print(f"[x] Test failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test.__name__, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[+]" if result else "[x]"
        print(f"{status} {test_name}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n[+] All features working!")
        sys.exit(0)
    else:
        print(f"\n[x] {total - passed} test(s) failed")
        sys.exit(1)
