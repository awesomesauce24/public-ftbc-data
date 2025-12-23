# Architecture Document

## System Design

### Layer 1: Core Data Layer
- **Config**: Centralized configuration (colors, realm info, paths)
- **Loader**: Load JSON and text data from disk
- **Parser**: Extract structured data from wiki markup

### Layer 2: CLI Layer
- **Commands**: High-level commands for users (RealmCommands, SearchCommands, ExportCommands)
- **Main**: Interactive CLI interface

### Layer 3: Generator Layer
- **WikiPageGenerator**: Generate MediaWiki-formatted pages
- **MarkdownPageGenerator**: Generate markdown pages

### Layer 4: Utility Layer
- **FileUtils**: Safe file I/O operations
- **StringUtils**: String normalization and formatting

## Data Flow

```
Realms Folder (JSON + TXT)
    ↓
Loaders (RealmLoader, SubrealmLoader)
    ↓
Parsers (extract structured data)
    ↓
Commands (user-facing operations)
    ↓
Generators (format output)
    ↓
User/Export
```

## Key Relationships

```
Config
  ├─ REALMS_PATH → used by Loaders
  ├─ DIFFICULTY_COLORS → used by Generators
  └─ REALMS_INFO → realm metadata

RealmLoader
  ├─ loads from REALMS_PATH
  ├─ creates SubrealmLoader instances
  └─ used by RealmCommands

SubrealmLoader
  ├─ loads from realm subdirectories
  └─ used by RealmCommands

Parsers
  ├─ process output from Loaders
  └─ used by Generators

Commands
  ├─ orchestrate Loaders and Parsers
  ├─ invoked from Main CLI
  └─ call Generators for output

Generators
  ├─ format data from Parsers
  ├─ take Config for styling
  └─ produce wiki/markdown output
```

## Module Dependencies

```
main.py
├─ cli.commands (RealmCommands, SearchCommands, ExportCommands)
│  ├─ core.loader (RealmLoader, SubrealmLoader)
│  │  └─ core.config (Config)
│  └─ core.config
│
core.parser
├─ (no dependencies - pure functions)
│
generators
├─ core.config
│
utils
├─ (no dependencies - pure functions)
```

## Extension Points

### Add New Command Type
1. Create class in `cli/commands.py`
2. Implement methods using loaders
3. Integrate into `main.py` menu

### Add New Parser
1. Add static method to `ObjectParser` or `RealmParser`
2. Test with sample wiki markup
3. Use in generators or commands

### Add New Generator
1. Create class in `generators/__init__.py`
2. Implement generation methods
3. Register in commands

### Add New Config
1. Add constant to `Config` class
2. Add accessor method if complex
3. Document in README

## Design Principles

### Single Responsibility
- Each class/module handles one concern
- Loaders handle file I/O
- Parsers handle data extraction
- Generators handle formatting

### Separation of Concerns
- Data loading separate from formatting
- CLI separate from business logic
- Configuration separate from logic

### No External Dependencies
- Uses only Python stdlib
- Easier to maintain and deploy
- Lighter footprint

### Reusability
- All modules can be imported independently
- Functions are pure where possible
- Classes are composable

### Testability
- Clear inputs and outputs
- Minimal side effects
- Easy to mock

## Performance Considerations

- Lazy loading: data loaded only when needed
- In-memory caching possible for frequently accessed data
- Bulk operations supported for export

## Security Notes

- All file operations use Path for safety
- Input validation in parsers
- Safe encoding handling (UTF-8)

## Future Architecture Changes

Could be extended with:
- Database layer (SQLite/PostgreSQL)
- REST API layer
- Caching layer
- Worker/queue system for batch jobs
- WebUI on top of CLI
