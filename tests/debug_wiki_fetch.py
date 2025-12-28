#!/usr/bin/env python3
"""Debug wiki API fetching."""

import requests
import json

def test_fetch_method1(obj_name):
    """Test fetching using query/pages/wikitext."""
    wiki_url = "https://ftbc.fandom.com"
    api_url = f"{wiki_url}/api.php"
    
    print(f"\n[Method 1] Testing: {obj_name}")
    print("-" * 60)
    
    try:
        response = requests.get(
            api_url,
            params={
                "action": "query",
                "titles": obj_name,
                "prop": "wikitext",
                "format": "json",
            },
            timeout=5
        )
        response.raise_for_status()
        
        result = response.json()
        print(f"Full response: {json.dumps(result, indent=2)[:500]}")
        
        return False
    except Exception as e:
        print(f"[x] Error: {e}")
        return False


def test_fetch_method2(obj_name):
    """Test fetching using query/pages with revisions."""
    wiki_url = "https://ftbc.fandom.com"
    api_url = f"{wiki_url}/api.php"
    
    print(f"\n[Method 2] Testing with revisions: {obj_name}")
    print("-" * 60)
    
    try:
        response = requests.get(
            api_url,
            params={
                "action": "query",
                "titles": obj_name,
                "prop": "revisions",
                "rvprop": "content",
                "format": "json",
            },
            timeout=5
        )
        response.raise_for_status()
        
        result = response.json()
        pages = result.get("query", {}).get("pages", {})
        
        if pages:
            page = next(iter(pages.values()))
            print(f"Page keys: {list(page.keys())}")
            
            if "revisions" in page:
                print(f"[+] Has revisions: {len(page['revisions'])}")
                content = page["revisions"][0].get("*", "")
                print(f"[+] Content length: {len(content)} chars")
                print(f"[+] First 200 chars: {content[:200]}")
                return True
        
        return False
    except Exception as e:
        print(f"[x] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Test with known objects
    test_fetch_method1("Apple")
    test_fetch_method2("Apple")
