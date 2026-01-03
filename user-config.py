# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are loaded from environment by pywikibot automatically.
"""

import os

# Family and language settings
family = 'fandom'

# Setup username from environment
_bot_user = os.environ.get('BOT_USERNAME')
_bot_pass = os.environ.get('BOT_PASSWORD')

if _bot_user and _bot_pass:
    # Set username for pywikibot
    from collections import defaultdict as _dd
    _usernames = _dd(lambda: _dd(str))
    _usernames['fandom']['fandom'] = _bot_user
    usernames = _usernames
    
    # Set password directly from environment
    # This is the variable pywikibot uses for login
    exec(f"password = '{_bot_pass}'")

# Other settings
console_encoding = 'utf-8'
