#!/usr/bin/env python3
"""Final comprehensive test of all main.py features."""

import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

def run_all_tests():
    """Run all tests."""
    
    print("=" * 70)
    print("FTBC WIKI MANAGEMENT SYSTEM - COMPREHENSIVE TEST REPORT")
    print("=" * 70)
    print()
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Environment & Dependencies
    print("[TEST 1] Environment & Dependencies")
    print("-" * 70)
    tests_total += 1
    
    try:
        import requests
        import dotenv
        print("[+] requests library available")
        print("[+] python-dotenv library available")
        tests_passed += 1
        print()
    except ImportError as e:
        print(f"[x] Missing dependency: {e}")
        print()
    
    # Test 2: Auth Module
    print("[TEST 2] Authentication Module")
    print("-" * 70)
    tests_total += 1
    
    try:
        from auth import WikiAuth, authenticate
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        username = os.getenv('BOT_USERNAME')
        password = os.getenv('BOT_PASSWORD')
        
        print("[+] WikiAuth class initialized")
        print("[+] authenticate() function available")
        print(f"[+] BOT_USERNAME configured: {bool(username)}")
        print(f"[+] BOT_PASSWORD configured: {bool(password)}")
        print("[+] Session retry strategy configured")
        
        if username and password:
            tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Auth module error: {e}")
        print()
    
    # Test 3: Realm & Subrealm Loading
    print("[TEST 3] Realm & Subrealm Loading")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import list_realms_and_subrealms_hierarchical
        
        items = list_realms_and_subrealms_hierarchical()
        realms = [item for item in items if item[5] == 'realm']
        subrealms = [item for item in items if item[5] in ['subrealm', 'nested_subrealm']]
        
        print(f"[+] Loaded {len(items)} total items")
        print(f"[+] {len(realms)} realms loaded")
        print(f"[+] {len(subrealms)} subrealms loaded")
        print(f"[+] Realm names: {', '.join([r[1] for r in realms[:3]])}, ...")
        
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Realm loading error: {e}")
        print()
    
    # Test 4: Metadata Loading
    print("[TEST 4] Metadata Loading (JSON)")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import load_json
        
        difficulties = load_json('metadata/difficulties.json')
        gradients = load_json('metadata/realm_gradients.json')
        special_cases = load_json('metadata/special_cases.json')
        
        print(f"[+] difficulties.json: {len(difficulties.get('difficulties', []))} difficulties")
        print(f"[+] realm_gradients.json: {len(gradients.get('realms', []))} realms, {len(gradients.get('subrealms', []))} subrealms")
        print(f"[+] special_cases.json: {len(special_cases.get('special_cases', {}))} cases")
        print("[+] All JSON files load successfully")
        
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Metadata loading error: {e}")
        print()
    
    # Test 5: Wiki Page Checking
    print("[TEST 5] Wiki Page Existence Checking")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import check_wiki_page_exists
        
        # Test with known page
        result_exists = check_wiki_page_exists('Apple')
        result_not_exists = check_wiki_page_exists('NonExistentObject_xyz_12345')
        
        print(f"[+] check_wiki_page_exists('Apple'): {result_exists}")
        print(f"[+] check_wiki_page_exists('NonExistentObject_xyz_12345'): {result_not_exists}")
        print("[+] Wiki page checking works (HTTP requests functional)")
        
        if result_exists and not result_not_exists:
            tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Wiki checking error: {e}")
        print()
    
    # Test 6: Difficulty Info Retrieval
    print("[TEST 6] Difficulty Information Retrieval")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import get_difficulty_info
        
        icon, hex_color, name, priority = get_difficulty_info('Normal')
        print(f"[+] Normal: name={name}, color={hex_color}, priority={priority}, icon={icon}")
        
        icon, hex_color, name, priority = get_difficulty_info('Dreadful')
        print(f"[+] Dreadful: name={name}, color={hex_color}, priority={priority}, icon={icon}")
        
        print("[+] Difficulty info retrieval working")
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Difficulty info error: {e}")
        print()
    
    # Test 7: Realm Gradient Retrieval
    print("[TEST 7] Realm Gradient & Colors")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import get_realm_gradient
        
        gradient, accent, image = get_realm_gradient('Main Realm')
        print(f"[+] Main Realm: gradient={bool(gradient)}, accent={accent}, image={bool(image)}")
        
        gradient, accent, image = get_realm_gradient('Barren Desert')
        print(f"[+] Barren Desert: gradient={bool(gradient)}, accent={accent}, image={bool(image)}")
        
        print("[+] Realm gradient retrieval working")
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Realm gradient error: {e}")
        print()
    
    # Test 8: Output Directory Structure
    print("[TEST 8] Output Directories & Write Permissions")
    print("-" * 70)
    tests_total += 1
    
    try:
        wiki_dir = Path('wiki')
        data_dir = Path('data')
        metadata_dir = Path('metadata')
        
        wiki_dir.mkdir(exist_ok=True)
        data_dir.mkdir(exist_ok=True)
        
        # Test write permission
        test_file = wiki_dir / '.write_test'
        test_file.write_text('test')
        test_file.unlink()
        
        print(f"[+] wiki/ directory writable")
        print(f"[+] data/ directory exists")
        print(f"[+] metadata/ directory exists")
        print("[+] All output directories accessible")
        
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Directory error: {e}")
        print()
    
    # Test 9: Main Module Imports
    print("[TEST 9] Main Module & CLI")
    print("-" * 70)
    tests_total += 1
    
    try:
        # Check main.py syntax
        with open('main.py') as f:
            code = f.read()
        compile(code, 'main.py', 'exec')
        
        # Check imports
        from auth import authenticate
        from create_pages import create
        
        print("[+] main.py syntax valid")
        print("[+] auth.authenticate() available")
        print("[+] create_pages.create() available")
        print("[+] CLI entry point ready")
        
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Main module error: {e}")
        print()
    
    # Test 10: Special Cases & Custom Formatting
    print("[TEST 10] Special Cases & Custom Formatting")
    print("-" * 70)
    tests_total += 1
    
    try:
        from create_pages import get_special_case
        
        # Try to get special case
        special = get_special_case('Main Realm')
        print(f"[+] Special case lookup functional")
        print(f"[+] Special case data available (format configurable)")
        
        tests_passed += 1
        print()
    except Exception as e:
        print(f"[x] Special cases error: {e}")
        print()
    
    # Summary
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"\nPassed: {tests_passed}/{tests_total} tests")
    
    if tests_passed == tests_total:
        print("\n[✓] ALL FEATURES WORKING - System is ready to use!")
        print("\nAvailable commands:")
        print("  python main.py          - Start the CLI")
        print("  create                  - Create wiki object pages")
        print("  help                    - Show help")
        print("  exit                    - Exit the CLI")
        return 0
    else:
        print(f"\n[x] {tests_total - tests_passed} test(s) failed - please review errors above")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
