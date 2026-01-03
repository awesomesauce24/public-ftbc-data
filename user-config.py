# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are loaded from .env file by the main script.
"""

import os

# Family and language settings
family = 'fandom'

# Setup credentials from environment (set by .env file)
bot_user = os.environ.get('BOT_USERNAME')
bot_pass = os.environ.get('BOT_PASSWORD')

if bot_user and bot_pass:
    # Dynamically set usernames and password to avoid warnings
    from collections import defaultdict as _dd
    _usernames = _dd(lambda: _dd(str))
    _usernames['fandom']['fandom'] = bot_user
    usernames = _usernames
    password = bot_pass

# Other settings
console_encoding = 'utf-8'
