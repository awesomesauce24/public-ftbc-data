#!/usr/bin/env python3
"""
Fandom Wiki Authentication Module
Handles login and session management for the FTBC Fandom wiki
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables from .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

def get_wiki_client():
    """
    Authenticate and return a session to the Fandom wiki.
    
    Returns:
        requests.Session: Authenticated session with login cookie
        
    Raises:
        ValueError: If credentials are not found in .env
    """
    
    # Get credentials from environment
    username = os.getenv("BOT_USERNAME")
    password = os.getenv("BOT_PASSWORD")
    
    if not username or not password:
        raise ValueError("Missing BOT_USERNAME or BOT_PASSWORD in .env file")
    
    try:
        print("Connecting to ftbc.fandom.com...")
        
        # Create a session with retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Get login token
        print(f"Authenticating as {username}...")
        login_url = "https://ftbc.fandom.com/api.php"
        
        params_token = {
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }
        
        response = session.get(login_url, params=params_token)
        response.raise_for_status()
        login_token = response.json()["query"]["tokens"]["logintoken"]
        
        # Login
        params_login = {
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login_token,
            "format": "json"
        }
        
        response = session.post(login_url, data=params_login)
        response.raise_for_status()
        
        if response.json()["login"]["result"] == "Success":
            print("[OK] Successfully authenticated to Fandom wiki")
            return session
        else:
            raise Exception(f"Login failed: {response.json()['login']['result']}")
        
    except Exception as e:
        print(f"[ERROR] Authentication error: {e}")
        raise

if __name__ == "__main__":
    try:
        session = get_wiki_client()
        print("Bot ready for wiki operations")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
