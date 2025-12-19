"""
Configuration for PyWikiBot scripts
"""

# Wiki site configuration
WIKI_CONFIG = {
    'family': 'ftbc',  # Adjust to your wiki family
    'code': 'en',      # Language code
}

# Bot settings
BOT_SETTINGS = {
    'max_retries': 3,
    'timeout': 30,
}

# Common categories or namespaces
CATEGORIES = {
    'realms': 'Category:Realms',
    'subrealms': 'Category:Subrealms',
    'characters': 'Category:Characters',
}
