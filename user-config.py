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

if _bot_user:
    # Set username for pywikibot
    from collections import defaultdict as _dd
    _usernames = _dd(lambda: _dd(str))
    _usernames['fandom']['fandom'] = _bot_user
    usernames = _usernames

# pywikibot will automatically read BOT_PASSWORD from environment
# No need to set password variable here - it's not a standard pywikibot config

# Other settings
console_encoding = 'utf-8'
