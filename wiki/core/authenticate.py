#!/usr/bin/env python3
"""
Bot Authentication Script for FTBC Wiki
Simple script to login and authenticate the bot
"""

import os
import requests
import http.cookiejar
from dotenv import load_dotenv

def authenticate():
    """Login and authenticate the bot with direct API calls"""
    # Load environment variables
    load_dotenv()
    
    username = os.getenv('WIKI_USERNAME')
    password = os.getenv('WIKI_PASSWORD')
    wiki_url = os.getenv('WIKI_URL', 'https://ftbc.fandom.com')
    
    if not username or not password:
        print("ERROR: WIKI_USERNAME or WIKI_PASSWORD not found in .env")
        return None
    
    try:
        print(f"Attempting to login as: {username}")
        print(f"Connecting to: {wiki_url}")
        
        # Use requests session for cookie handling
        session = requests.Session()
        
        # Step 1: Get login token
        params = {
            'action': 'query',
            'meta': 'tokens',
            'type': 'login',
            'format': 'json'
        }
        
        response = session.get(f'{wiki_url}/api.php', params=params)
        if response.status_code != 200:
            print(f"ERROR: Failed to get login token - {response.status_code}")
            return None
            
        token = response.json()['query']['tokens']['logintoken']
        
        # Step 2: Login
        login_params = {
            'action': 'login',
            'lgname': username,
            'lgpassword': password,
            'lgtoken': token,
            'format': 'json'
        }
        
        response = session.post(f'{wiki_url}/api.php', data=login_params)
        login_result = response.json()
        
        if login_result['login']['result'] != 'Success':
            print(f"ERROR: Login failed - {login_result['login'].get('reason', 'Unknown error')}")
            return None
        
        # Step 3: Verify login
        params = {
            'action': 'query',
            'meta': 'userinfo',
            'format': 'json'
        }
        
        response = session.get(f'{wiki_url}/api.php', params=params)
        userinfo = response.json()['query']['userinfo']
        
        print("[OK] Successfully authenticated!")
        print(f"[OK] Connected to: {wiki_url}")
        print(f"[OK] User: {userinfo.get('name', username)}")
        
        # Return session as our "site" object
        session.wiki_url = wiki_url
        session.username = userinfo.get('name', username)
        return session
    
    except Exception as e:
        print(f"ERROR: Authentication failed - {str(e)}")
        return None

if __name__ == "__main__":
    site = authenticate()
    if site:
        print("\nBot is ready to use!")
    else:
        print("\nAuthentication failed. Check your credentials in .env")
