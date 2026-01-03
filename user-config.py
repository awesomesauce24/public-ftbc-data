# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are loaded from .env file by the main script.
"""

from collections import defaultdict
import os

# Family and language settings
family = 'fandom'

# Load credentials from environment (set by .env file)
usernames = defaultdict(lambda: defaultdict(str))
if os.environ.get('BOT_USERNAME'):
    usernames['fandom']['fandom'] = os.environ.get('BOT_USERNAME')

# Password from environment
password = os.environ.get('BOT_PASSWORD')

# Other settings
console_encoding = 'utf-8'
