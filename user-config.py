# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

This file configures pywikibot to work with the FTBC wiki.
Loads credentials from .env file automatically.
"""

import os
from collections import defaultdict
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

# Bot account credentials - load from .env or environment
bot_username = os.environ.get('BOT_USERNAME')
bot_password = os.environ.get('BOT_PASSWORD')

# Configure usernames as defaultdict for pywikibot
usernames = defaultdict(lambda: defaultdict(str))
if bot_username:
    usernames['fandom']['fandom'] = bot_username

# Configure password
if bot_password:
    password = bot_password

# Other settings
console_encoding = 'utf-8'
