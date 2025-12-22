"""Fandom Wiki Publisher - Auto-publish pages to ftbc.fandom.com"""

import requests
import json
from typing import Tuple, Optional
from pathlib import Path


class FandomPublisher:
    """Handle publishing pages to Fandom wiki"""
    
    BASE_URL = "https://ftbc.fandom.com/api.php"
    
    def __init__(self, username: str, password: str):
        """Initialize with Fandom credentials"""
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FTBC-Wiki-Publisher/1.0'
        })
        self.logged_in = False
    
    def login(self) -> Tuple[bool, str]:
        """Login to Fandom and get session token"""
        try:
            # Step 1: Get login token
            params = {
                'action': 'query',
                'meta': 'tokens',
                'type': 'login',
                'format': 'json'
            }
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            login_token = data['query']['tokens']['logintoken']
            
            # Step 2: Login with token using standard login action (better for bots)
            login_params = {
                'action': 'login',
                'lgname': self.username,
                'lgpassword': self.password,
                'lgtoken': login_token,
                'format': 'json'
            }
            
            response = self.session.post(self.BASE_URL, data=login_params)
            response.raise_for_status()
            result = response.json()
            
            if result.get('login', {}).get('result') == 'Success':
                self.logged_in = True
                return True, f"Successfully logged in as {self.username}"
            else:
                error = result.get('login', {}).get('reason', 'Unknown error')
                return False, f"Login failed: {error}"
        
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def publish_page(self, page_title: str, markup: str, summary: str = "Added object page") -> Tuple[bool, str]:
        """Publish a page to the wiki"""
        
        if not self.logged_in:
            return False, "Not logged in. Please login first."
        
        try:
            # Get edit token
            params = {
                'action': 'query',
                'meta': 'tokens',
                'type': 'csrf',
                'format': 'json'
            }
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            edit_token = data['query']['tokens']['csrftoken']
            
            # Edit/create page
            edit_params = {
                'action': 'edit',
                'title': page_title,
                'text': markup,
                'summary': summary,
                'token': edit_token,
                'format': 'json'
            }
            
            response = self.session.post(self.BASE_URL, data=edit_params)
            response.raise_for_status()
            result = response.json()
            
            if 'edit' in result and result['edit'].get('result') == 'Success':
                page_id = result['edit'].get('pageid')
                return True, f"✓ Page published: https://ftbc.fandom.com/wiki/{page_title.replace(' ', '_')} (ID: {page_id})"
            else:
                error = result.get('edit', {}).get('result', 'Unknown error')
                return False, f"Publish failed: {error}"
        
        except Exception as e:
            return False, f"Publish error: {str(e)}"
    
    def check_page_exists(self, page_title: str) -> Tuple[bool, bool]:
        """Check if page exists on wiki. Returns (success, exists)"""
        try:
            params = {
                'action': 'query',
                'titles': page_title,
                'format': 'json'
            }
            response = self.session.get(self.BASE_URL, params=params)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            # If -1 in pages, it doesn't exist
            exists = -1 not in pages
            
            return True, exists
        
        except Exception as e:
            return False, False


def save_credentials(username: str, password: str, cred_file: Path = None) -> bool:
    """Save credentials to config file (git-ignored)"""
    if cred_file is None:
        cred_file = Path(__file__).parent.parent / "config" / ".fandom_creds.json"
    
    try:
        # Create config directory if it doesn't exist
        cred_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Simple encoding (in production, use proper encryption)
        creds = {
            'username': username,
            'password': password
        }
        
        # Create with restricted permissions
        with open(cred_file, 'w') as f:
            json.dump(creds, f)
        
        # Restrict permissions (Unix-like systems)
        try:
            import stat
            cred_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
        except:
            pass
        
        return True
    except Exception as e:
        print(f"Error saving credentials: {e}")
        return False


def load_credentials(cred_file: Path = None) -> dict:
    """Load saved credentials from config file"""
    if cred_file is None:
        cred_file = Path(__file__).parent.parent / "config" / ".fandom_creds.json"
    
    try:
        if cred_file.exists():
            with open(cred_file, 'r') as f:
                return json.load(f)
    except:
        pass
    
    return {}
