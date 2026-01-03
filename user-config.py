# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are loaded from .env file by the main script.
"""

import os

# Family and language settings
family = 'fandom'

# Setup credentials from environment (set by .env file)
_bot_user = os.environ.get('BOT_USERNAME')
_bot_pass = os.environ.get('BOT_PASSWORD')

if _bot_user and _bot_pass:
    # Dynamically set usernames and password to avoid warnings
    from collections import defaultdict as _dd
    _usernames = _dd(lambda: _dd(str))
    _usernames['fandom']['fandom'] = _bot_user
    usernames = _usernames
    password = _bot_pass

# Other settings
console_encoding = 'utf-8'
