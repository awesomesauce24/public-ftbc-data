# Repository Organization Guide

## Directory Structure

```
public-ftbc-data/
├── Realms/                          # JSON data for all game realms
│   ├── Main Realm.json
│   ├── Yoyle Factory.json
│   ├── Backrooms.json
│   ├── Sub-realms/                  # Subrealm JSON files
│   └── ...
│
├── wiki/                            # Wiki bot and automation system
│   ├── main.py                      # Main entry point
│   ├── cli/                         # Command-line interface
│   ├── core/                        # Core modules (formatter, scrapers, etc.)
│   ├── config/                      # Configuration files
│   └── templates/                   # Wiki templates and styling
│
├── scripts/                         # Utility scripts
│   ├── add_areas.py                 # Add Area field to Main Realm.json
│   └── generate_objects_sections.py # Generate Objects wiki sections
│
├── docs/                            # Documentation and summaries
│   ├── CLEANUP_COMPLETE.md
│   ├── CREATE_PAGE_SUMMARY.txt
│   ├── ENHANCED_CREATE_PAGE_SUMMARY.txt
│   └── SPONGYBOT_V5_SUMMARY.txt
│
├── outputs/                         # Generated files (not committed)
│   └── OBJECTS_SECTION_*.txt        # Wiki Objects sections for each realm
│
├── utilities/                       # Utility modules
│   ├── data.py
│   └── organize_images.py
│
├── tests/                           # Test scripts and validation
├── FTBC Characters/                 # Character documentation
└── rbx_private/                     # Private Roblox files (not committed)
```

## Key Files

### Root Level
- **README.md** - Main project documentation
- **requirements.txt** - Python dependencies
- **.gitignore** - Git ignore rules

## Important Directories

### `/Realms/`
Contains JSON data files for all game realms. Each realm has:
- **ObjectName** - Name of the object/character
- **Difficulty** - Difficulty level
- **Description** - Hint/description
- **Area/Section/Level** - Location within realm (varies by realm)

### `/wiki/`
Complete wiki automation system with:
- Authentication and bot management
- Page creation and editing
- Object formatting and templates
- Wiki page scraping utilities

### `/scripts/`
Utility scripts for data processing:
- `add_areas.py` - Extracts and adds Area field to Main Realm objects
- `generate_objects_sections.py` - Generates ObjectDifficultyList wiki sections

### `/docs/`
Documentation and project summaries

### `/outputs/`
Generated files (ignored by git):
- Wiki Objects sections for each realm
- Preview files for review before publishing

## Running Scripts

### Add Areas to Main Realm
```bash
python scripts/add_areas.py
```
Parses object descriptions and adds Area field based on location mentions.

### Generate Objects Sections
```bash
python scripts/generate_objects_sections.py
```
Generates formatted Objects wiki sections for all realms with:
- Grouped by difficulty
- ObjectDifficultyList templates
- Image galleries
- Icon and color coding

Output saved to `outputs/OBJECTS_SECTION_*.txt`

## Data Schema

### Main Realm
```json
{
  "ObjectName": "Sharp",
  "Difficulty": "terrifying",
  "Description": "hint text...",
  "Area": "Candyland"
}
```

### Yoyle Factory
```json
{
  "ObjectName": "Coffee Mug",
  "Difficulty": "unforgiving",
  "Description": "tea is better",
  "Section": "Normal Factory"
}
```

### Backrooms
```json
{
  "ObjectName": "Clay",
  "Difficulty": "intermediate",
  "Description": "hint text...",
  "Level": "Level 0"
}
```

## Wiki Integration

The wiki formatter intelligently uses location fields:
- **Main Realm** → Uses Area field (e.g., "Candyland", "City")
- **Yoyle Factory** → Uses Section field (e.g., "Normal Factory", "Meltdown")
- **Backrooms** → Uses Level field (e.g., "Level 0", "Level 4")

All are extracted in `wiki/core/object_formatter.py`:
- `extract_object_area()`
- `extract_object_section()`
- `extract_object_level()`
