# FTBC Wiki System Documentation

Welcome to the FTBC Wiki System documentation. This guide covers everything you need to know about creating and managing wiki pages for Find The BFB Characters game objects.

## 📚 Documentation Sections

### Getting Started
- **[Quick Start](./01_QUICK_START.md)** - Get up and running in 5 minutes
- **[Setup Guide](./02_SETUP.md)** - Installation and configuration

### Using the System
- **[Creating Object Pages](./03_CREATING_PAGES.md)** - Step-by-step guide for creating wiki pages
- **[Editing Objects](./04_EDITING_OBJECTS.md)** - Modify existing pages
- **[Publishing to Wiki](./05_PUBLISHING.md)** - How to publish pages to the Fandom wiki

### Reference
- **[Wiki Markup Reference](./06_WIKI_MARKUP.md)** - Format guide and syntax
- **[Field Reference](./07_FIELDS.md)** - All available fields and their purposes
- **[Realms & Areas](./08_REALMS_AREAS.md)** - Complete list of realms and subareas

### Architecture
- **[System Design](./09_ARCHITECTURE.md)** - How the system works internally
- **[Configuration](./10_CONFIG.md)** - Configuring realms, colors, backgrounds

## 🚀 Quick Navigation

**I want to...**
- Create a new object page → See [Quick Start](./01_QUICK_START.md)
- Edit an existing page → See [Editing Objects](./04_EDITING_OBJECTS.md)
- Publish changes to wiki → See [Publishing to Wiki](./05_PUBLISHING.md)
- Understand the system → See [System Design](./09_ARCHITECTURE.md)
- Find technical details → See [Configuration](./10_CONFIG.md)

## 🔑 Key Concepts

### Objects
Game objects that appear in the FTBC game. Each object has:
- Name, difficulty, description
- Location info (realm/area)
- How to obtain it
- Associated image(s)

### Realms
Game worlds/maps like Main Realm, Yoyleland, Yoyle Factory, etc.

### Subareas
Specific locations within realms (e.g., Goiky in Main Realm, Abandonment in Yoyle Factory)

### Wiki Pages
Markdown-formatted pages with object info, displayed on ftbc.fandom.com

## ⚡ Common Tasks

```bash
# Start the system
python wiki/main.py

# Select a realm
> create
> Main Realm

# Choose an object
> 1    # by number
> Firey  # by name (fuzzy matching supported)

# Fill in required info
> [Description]
> [How to obtain]

# Review and save
> yes
```

## 📖 File Structure

```
wiki/
├── main.py                 # Main CLI entry point
├── core/
│   ├── config.py          # Configuration & realm info
│   ├── loader.py          # Load realm data
│   └── parser.py          # Parse wiki content
├── generators/
│   └── __init__.py        # Generate wiki markup
├── publishers/
│   └── __init__.py        # Publish to Fandom wiki
└── cli/
    └── commands.py        # CLI commands

realms/
├── Main Realm/
│   ├── Main Realm.json    # Object data
│   └── objects/           # Generated wiki pages
└── [Other realms...]
```

## 🎨 Features

- ✅ Auto-detect object location from JSON
- ✅ Fuzzy object name matching
- ✅ Automatic theme/color application
- ✅ Support for object image galleries (current + old)
- ✅ Difficulty tier icons (16 tiers)
- ✅ Spoiler boxes for Dreadful+ difficulties
- ✅ Auto-publish to Fandom wiki
- ✅ Multi-line text input for descriptions

## 🆘 Need Help?

Check the relevant guide above, or review the source code in `wiki/` directory.

## 📝 Last Updated

December 23, 2025
