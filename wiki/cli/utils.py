#!/usr/bin/env python3
"""
Utility functions for FTBC Wiki Bot
Handles clipboard operations and wiki page editing
"""

import os
import sys
import subprocess


def copy_to_clipboard(text):
    """
    Copy text to clipboard (Windows compatible)
    
    Args:
        text (str): Text to copy to clipboard
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        process = subprocess.Popen(
            ['powershell', '-Command', 'Set-Clipboard -Value $input'], 
            stdin=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(text.encode('utf-8'))
        return process.returncode == 0
    except Exception as e:
        print(f"Could not copy to clipboard: {e}")
        return False


def open_browser(page_name):
    """
    Open wiki page in default browser
    
    Args:
        page_name (str): Name of the wiki page to open
    """
    url = f"https://ftbc.fandom.com/wiki/{page_name}"
    try:
        if os.name == 'nt':  # Windows
            os.startfile(url)
        elif os.name == 'posix':  # macOS, Linux
            cmd = f'open "{url}"' if sys.platform == 'darwin' else f'xdg-open "{url}"'
            os.system(cmd)
        print(f"[OK] Opening {url}")
    except Exception as e:
        print(f"[FAIL] Could not open browser: {e}")
        print(f"Visit: {url}")


def edit_wiki_page(session, page_name, content, summary="Updated by Spongybot v4"):
    """
    Edit or create a wiki page using the authenticated session
    
    Args:
        session: Authenticated wiki session
        page_name (str): Name of the page to edit
        content (str): Content to post
        summary (str): Edit summary
        
    Returns:
        bool: True if successful, False otherwise
    """
    wiki_url = session.wiki_url
    
    try:
        print(f"Uploading page: {page_name}...")
        
        # Get CSRF token
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'csrf',
            'format': 'json'
        }
        
        response = session.get(f"{wiki_url}/api.php", params=params)
        token_data = response.json()
        
        if 'batchcomplete' not in token_data:
            return False
        
        csrf_token = token_data['query']['tokens']['csrftoken']
        
        # Edit the page
        edit_params = {
            'action': 'edit',
            'title': page_name,
            'text': content,
            'summary': summary,
            'token': csrf_token,
            'format': 'json'
        }
        
        response = session.post(f"{wiki_url}/api.php", data=edit_params)
        result = response.json()
        
        if 'edit' in result:
            edit_result = result['edit']
            if 'pageid' in edit_result or ('result' in edit_result and edit_result['result'] == 'Success'):
                return True
        
        return False
        
    except Exception as e:
        print(f"Error editing wiki page: {e}")
        return False
