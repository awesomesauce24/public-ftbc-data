# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

This file configures pywikibot to work with the FTBC wiki.
Loads credentials from .env file automatically.
"""

import os
from pathlib import Path

# Load .env file if it exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

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
    usernames['fandom']['en'] = ftbc_user
    password = ftbc_pass
else:
    # Fallback: prompt for credentials
    import getpass
    usernames['fandom']['en'] = input('Enter bot username: ')
    password = getpass.getpass('Enter bot password: ')

# Other settings
console_encoding = 'utf-8'
