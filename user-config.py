# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

Credentials are handled by pywikibot's login system.
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

# Other settings
console_encoding = 'utf-8'
