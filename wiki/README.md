# Wiki Bot Structure

The wiki folder is now organized into logical modules:

## Directory Structure

```
wiki/
├── main.py                 # Main entry point for the bot
├── .env                    # Environment variables (credentials)
├── .gitignore             # Git ignore file
│
├── core/                   # Core modules
│   ├── __init__.py        # Package initialization
│   ├── authenticate.py    # Wiki authentication & login
│   ├── bot.py             # PyWikiBot utilities
│   ├── scrapers.py        # Wiki page scraping utilities
│   └── object_formatter.py# Object formatting for wiki pages
│
├── config/                # Configuration files
│   ├── __init__.py        # Package initialization
│   ├── config.py          # Bot configuration settings
│   └── user-config.py     # User-specific configuration
│
└── templates/             # Templates and data files
    ├── __init__.py        # Package initialization
    └── object_template.json # Template with realm/object formatting
```

## Module Descriptions

### core/
- **authenticate.py**: Handles login credentials and wiki authentication
- **bot.py**: Core PyWikiBot operations (edit, create, read pages)
- **scrapers.py**: Fetches and parses wiki page content
- **object_formatter.py**: Formats game objects for wiki display

### config/
- **config.py**: Bot settings, categories, and configuration constants
- **user-config.py**: User-specific overrides and preferences

### templates/
- **object_template.json**: Contains styling and configuration for realms and objects

## Usage

Import modules from the new structure:

```python
from core import authenticate, scrape_realms, format_from_dict
from config import WIKI_CONFIG, BOT_SETTINGS
from templates import load_object_template
```

The main.py has already been updated with the new import paths.
