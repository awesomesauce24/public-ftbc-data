# -*- coding: utf-8 -*-
"""
PyWikiBot configuration for FTBC Fandom wiki.

This file configures pywikibot to work with the FTBC wiki.
Update the bot credentials below with your actual bot username/password.
"""

# Family and language settings
family = 'fandom'
mylang = 'en'

# Site URL
site = {
    'fandom:en': ('ftbc.fandom.com', '/api.php')
}

# Bot account credentials
# Set these to your bot username and password
# Options:
# 1. Set directly here (NOT RECOMMENDED for security):
#    usernames['fandom']['en'] = 'YourBotUsername'
#    password = 'YourBotPassword'
#
# 2. Use environment variables (RECOMMENDED):
#    Set PYWIKIBOT_FTBC_USER and PYWIKIBOT_FTBC_PASS
#
# 3. Use credentials file (RECOMMENDED):
#    Create a file with your credentials and reference it

import os

# Try to load from environment variables
ftbc_user = os.environ.get('PYWIKIBOT_FTBC_USER')
ftbc_pass = os.environ.get('PYWIKIBOT_FTBC_PASS')

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
