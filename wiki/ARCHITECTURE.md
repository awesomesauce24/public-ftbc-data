# Wiki Bot - Architecture

The wiki bot is organized into logical, maintainable modules.

## New Architecture

```
wiki/
├── main.py                    # Entry point - command routing
│
├── cli/                       # Command-Line Interface (NEW!)
│   ├── __init__.py           # Package exports
│   ├── commands.py           # All command implementations
│   ├── ui.py                 # UI/display components
│   └── utils.py              # CLI utility functions
│
├── core/                      # Core functionality
│   ├── __init__.py           # Package exports
│   ├── authenticate.py       # Wiki authentication
│   ├── bot.py                # PyWikiBot operations
│   ├── scrapers.py           # Wiki content fetching
│   └── object_formatter.py   # Object formatting
│
├── config/                    # Configuration
│   ├── __init__.py
│   ├── config.py
│   └── user-config.py
│
├── templates/                 # Templates
│   ├── __init__.py
│   └── object_template.json
│
└── ARCHITECTURE.md           # This file
```

## Module Descriptions

### **main.py** (Entry Point)
- Command router with `COMMAND_MAP`
- Main menu loop (~84 lines)
- Keyboard interrupt handling

### **cli/** (Command-Line Interface)
All user-facing components consolidated in one folder:

- **commands.py**
  - `cmd_help()` - Display help
  - `cmd_exit()` - Exit bot
  - `cmd_realms()` - Show realms
  - `cmd_subrealms()` - Show subrealms
  - `cmd_objtemplate()` - Show template
  - `cmd_createobj()` - Create object workflow
  - Helper functions for input

- **ui.py**
  - `display_header()` - Formatted headers
  - `display_footer()` - Separator
  - `display_welcome()` - Welcome message
  - `display_help()` - Help display
  - `display_realms()` - Realm list
  - `display_subrealm_section()` - Subrealm display
  - `prompt_post_generation()` - Post-generation menu

- **utils.py**
  - `copy_to_clipboard()` - Clipboard operations
  - `open_browser()` - URL operations
  - `edit_wiki_page()` - Wiki editing

### **core/** (Core Functionality)
Wiki operations and data processing:

- **authenticate.py** - Login and authentication
- **bot.py** - PyWikiBot operations
- **scrapers.py** - Fetching wiki content
- **object_formatter.py** - Formatting objects for wiki

### **config/** (Configuration)
Settings and configuration files for the bot

### **templates/** (Templates)
Template files and JSON configurations

## Organization Benefits

✅ **Separation of Concerns**
- CLI logic isolated in `cli/` folder
- Core wiki operations in `core/` folder
- Configuration separated in `config/` folder

✅ **Easier Navigation**
- All CLI components in one place
- Quick to find UI functions, commands, utils
- Related code grouped together

✅ **Better Extensibility**
- Add new command: Add to `cli/commands.py`
- Add new UI element: Add to `cli/ui.py`
- Add new wiki operation: Add to `core/`

✅ **Cleaner Imports**
- `from cli import ...` - All CLI stuff
- `from core import ...` - All core stuff
- `from config import ...` - All config stuff

## Usage

Run the bot:
```bash
python wiki/main.py
```

Import in other projects:
```python
from cli import cmd_help, display_welcome
from core import authenticate, scrape_realms
```

## File Statistics

| Component | Lines | Purpose |
|-----------|-------|---------|
| main.py | 84 | Command routing & main loop |
| cli/commands.py | 245 | Command implementations |
| cli/ui.py | 113 | Display functions |
| cli/utils.py | 75 | Utility functions |
| core/authenticate.py | 92 | Authentication |
| core/scrapers.py | 177 | Web scraping |
| core/object_formatter.py | 395 | Data formatting |
| core/bot.py | 66 | Wiki operations |



