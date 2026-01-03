# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are loaded from .env file by the main script.
"""

import os

# Family and language settings
family = 'fandom'

# Setup credentials from environment (set by .env file)
if os.environ.get('BOT_USERNAME'):
    from collections import defaultdict
    usernames = defaultdict(lambda: defaultdict(str))
    usernames['fandom']['fandom'] = os.environ.get('BOT_USERNAME')
    
    # Password from environment
    _password = os.environ.get('BOT_PASSWORD')
    if _password:
        password = _password

# Other settings
console_encoding = 'utf-8'
