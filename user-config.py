# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

This file configures pywikibot to work with the FTBC wiki.
Loads credentials from .env file automatically.
"""

import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    # Look for .env in current directory or parent directories
    env_path = Path.cwd() / '.env'
    if not env_path.exists():
        env_path = Path.cwd().parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Family and language settings
family = 'fandom'
mylang = 'en'

# Site URL
site = {
    'fandom:en': ('ftbc.fandom.com', '/api.php')
}

# Bot account credentials - load from .env or environment
ftbc_user = os.environ.get('BOT_USERNAME')
ftbc_pass = os.environ.get('BOT_PASSWORD')

if ftbc_user and ftbc_pass:
    usernames = {'fandom': {'en': ftbc_user}}
    password = ftbc_pass
else:
    # Fallback: prompt for credentials
    import getpass
    ftbc_user = input('Enter bot username: ')
    ftbc_pass = getpass.getpass('Enter bot password: ')
    usernames = {'fandom': {'en': ftbc_user}}
    password = ftbc_pass

# Other settings
console_encoding = 'utf-8'
