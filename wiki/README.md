# Wiki System - Revamped v6

Complete reboot of the wiki management system with clean, modular architecture.

## Overview

The wiki system provides tools for managing FTBC game content including:
- Realm and subrealm data management
- Page generation and formatting
- Content search and export
- Structured data handling

## Directory Structure

```
wiki/
├── main.py                  # Interactive CLI entry point
├── __init__.py             # Package initialization
│
├── core/                   # Core modules
│   ├── config.py          # Configuration (colors, realm info, paths)
│   ├── loader.py          # Data loaders (RealmLoader, SubrealmLoader)
│   ├── parser.py          # Data parsers (RealmParser, ObjectParser)
│   └── __init__.py
│
├── cli/                    # Command-line interface
│   ├── commands.py        # CLI commands (RealmCommands, SearchCommands, ExportCommands)
│   └── __init__.py
│
├── generators/            # Page generators
│   └── __init__.py       # WikiPageGenerator, MarkdownPageGenerator
│
└── utils/                 # Utilities
    └── __init__.py       # FileUtils, StringUtils
```

## Core Concepts

### 1. **RealmLoader**
Loads and manages realm data from the `realms/` folder.

```python
from wiki.core.loader import RealmLoader
from wiki.core.config import Config

loader = RealmLoader(Config.REALMS_PATH)
realms = loader.get_all_realms()
realm_data = loader.get_realm_data("Main Realm")
description = loader.get_realm_description("Main Realm")
```

### 2. **SubrealmLoader**
Loads and manages subrealm data organized under parent realms.

```python
from wiki.core.loader import SubrealmLoader

sub_loader = SubrealmLoader(Config.REALMS_PATH)
subrealms = sub_loader.get_all_subrealms_for_realm("Main Realm")
sub_data = sub_loader.get_subrealm_data("Main Realm", "Basement")
```

### 3. **Config**
Central configuration with:
- Realm paths
- Difficulty color codes
- Realm styling and themes

```python
from wiki.core.config import Config

color = Config.get_color("Hard")  # "#FF7700"
realm_info = Config.get_realm_info("Main Realm")
```

### 4. **Parsers**
Extract structured data from wiki markup:

```python
from wiki.core.parser import RealmParser, ObjectParser

objects = RealmParser.extract_objects_from_description(description)
obj = ObjectParser.extract_from_line("[[File:Icon.png|18px]] '''[[Name]]'''")
```

### 5. **Generators**
Create wiki and markdown pages from structured data:

```python
from wiki.generators import WikiPageGenerator, MarkdownPageGenerator

wiki_page = WikiPageGenerator.generate_realm_page("Main Realm", data)
md_page = MarkdownPageGenerator.generate_realm_md("Main Realm", data)
```

## CLI Commands

### Interactive Mode
Run `python wiki/main.py` to start the interactive CLI:

```
> realms                    # List all realms
> realm Main Realm          # Show realm details
> subrealms Main Realm      # List subrealms
> subrealm Main Realm Basement  # Show subrealm details
> search Level              # Search for "Level" in realms/subrealms
> export realms             # Export list of realms
> export Main Realm         # Export realm structure as JSON
> help                      # Show menu
> exit                      # Exit program
```

## Usage Examples

### Load and Display Realm
```python
from wiki.cli.commands import RealmCommands

cmd = RealmCommands()
realm_info = cmd.show_realm("Main Realm")
print(f"Realm: {realm_info['name']}")
print(f"Subrealms: {realm_info['subrealms']}")
```

### Search Content
```python
from wiki.cli.commands import SearchCommands

cmd = SearchCommands()
results = cmd.search_realms("forest")
subrealm_results = cmd.search_subrealms("level")
```

### Export Data
```python
from wiki.cli.commands import ExportCommands

cmd = ExportCommands()
realm_list = cmd.export_realm_list('json')
realm_struct = cmd.export_realm_structure("Backrooms", 'json')
```

## Data Structure

### Realm Folder
```
realms/Main Realm/
├── Main Realm.json      # JSON data
├── page.txt             # Wiki description
└── subrealms/           # Subrealms folder
    ├── Basement/
    │   ├── Basement.json
    │   └── page.txt
    ├── Motionless/
    └── ... (more subrealms)
```

## Architecture Principles

1. **Modularity** - Each module has a single responsibility
2. **Simplicity** - Clean, straightforward code with minimal dependencies
3. **Reusability** - Core components can be used independently
4. **Extensibility** - Easy to add new generators, loaders, and commands
5. **Configuration** - Centralized settings in Config class

## Extending the System

### Add a New Command
```python
# In wiki/cli/commands.py
class MyCommand:
    def __init__(self):
        self.loader = RealmLoader(Config.REALMS_PATH)
    
    def my_action(self):
        pass
```

### Add a New Generator
```python
# In wiki/generators/__init__.py
class MyGenerator:
    @staticmethod
    def generate_something(data):
        return "formatted output"
```

### Add New Config
```python
# In wiki/core/config.py
class Config:
    NEW_SETTING = "value"
    
    @classmethod
    def get_new_setting(cls):
        return cls.NEW_SETTING
```

## Requirements

- Python 3.7+
- No external dependencies (uses only stdlib)

## Future Enhancements

- [ ] Wiki API client for uploading pages
- [ ] Database backend for caching
- [ ] Advanced search with filters
- [ ] Batch operations
- [ ] Web UI dashboard
- [ ] Automated sync from game sources

## Version History

- **v6.0.0** - Complete reboot with modular architecture
