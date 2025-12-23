# FTBC Wiki System

## Overview
This is the FTBC Wiki System v6.0 - a Python CLI application for managing wiki content for the FTBC game. It provides tools for managing realm and subrealm data, page generation and formatting, content search and export, and publishing to Fandom wiki.

## Project Structure
```
wiki/                    # Main Python package
├── main.py              # Interactive CLI entry point
├── cli/                 # Command-line interface commands
├── core/                # Core modules (config, loader, parser)
├── generators/          # Wiki and markdown page generators
├── publishers/          # Fandom wiki publishing utilities
├── templates/           # JSON templates for objects/realms
└── utils/               # Utility functions

realms/                  # Game data organized by realm
├── Main Realm/          # Each realm has its own directory
│   ├── Main Realm.json  # Realm data
│   ├── page.txt         # Wiki description
│   ├── objects/         # Object JSON files
│   └── subrealms/       # Subrealm subdirectories
└── ...                  # Other realms

docs/                    # Documentation files
```

## Running the Application
The application runs as an interactive CLI. Use the "FTBC Wiki CLI" workflow which runs:
```
python wiki/main.py
```

### Available Commands
- `realms` - Display all realms and subrealms
- `create` - Create a new realm/object page
- `setup` - Setup Fandom credentials for publishing
- `help` - Show help menu
- `exit` - Exit the program

## Dependencies
- Python 3.11+
- requests (for Fandom API)

## Configuration
- Credentials for Fandom publishing are stored in `wiki/config/.fandom_creds.json` (git-ignored)
- Realm configurations are in `wiki/core/config.py`

## Recent Changes
- 2024-12-23: Initial Replit environment setup
