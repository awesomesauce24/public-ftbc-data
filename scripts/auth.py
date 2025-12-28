"""
Authentication module for Fandom wiki access.
Handles login and session management.
"""

import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Load environment variables
load_dotenv()

# Wiki configuration
WIKI_URL = "https://ftbc.fandom.com"
API_URL = f"{WIKI_URL}/api.php"


class WikiAuth:
    """Handle authentication with Fandom wiki."""
    
    def __init__(self):
        self.session = requests.Session()
        # Setup retry strategy for resilience
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.authenticated = False
        self.username = None
    
    def login(self):
        """Authenticate with the wiki using credentials from .env"""
        username = os.getenv("BOT_USERNAME")
        password = os.getenv("BOT_PASSWORD")
        
        if not username or not password:
            raise ValueError(
                "Missing wiki credentials. Please set BOT_USERNAME and BOT_PASSWORD in .env"
            )
        
        print(f"Authenticating as {username}...", end=" ", flush=True)
        
        try:
            # Get login token
            response = self.session.get(
                API_URL,
                params={
                    "action": "query",
                    "meta": "tokens",
                    "type": "login",
                    "format": "json",
                },
                timeout=10
            )
            response.raise_for_status()
            
            login_token = response.json()["query"]["tokens"]["logintoken"]
            
            # Perform login
            response = self.session.post(
                API_URL,
                data={
                    "action": "login",
                    "lgname": username,
                    "lgpassword": password,
                    "lgtoken": login_token,
                    "format": "json",
                },
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()["login"]["result"]
            
            if result == "Success":
                self.authenticated = True
                self.username = username
                
                print(f"✓ Logged in as {username}")
                return self.session
            else:
                print(f"✗ Login failed: {result}")
                raise RuntimeError(f"Wiki login failed: {result}")
                
        except requests.RequestException as e:
            print(f"✗ Network error: {e}")
            raise RuntimeError(f"Failed to connect to wiki: {e}")
        except KeyError as e:
            print(f"✗ Invalid response format: {e}")
            raise RuntimeError(f"Unexpected wiki response: {e}")
    
    def is_authenticated(self):
        """Check if currently authenticated."""
        return self.authenticated
    
    def get_session(self):
        """Get the authenticated session."""
        if not self.authenticated:
            raise RuntimeError("Not authenticated. Call login() first.")
        return self.session


def authenticate():
    """Main authentication function called by main.py"""
    auth = WikiAuth()
    auth.login()
    return auth.get_session()


if __name__ == "__main__":
    try:
        session = authenticate()
        print("\nAuthentication successful!")
    except Exception as e:
        print(f"\nAuthentication failed: {e}", file=sys.stderr)
        sys.exit(1)
