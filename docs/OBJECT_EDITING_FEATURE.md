# Object Page Editing Feature

## Overview

The object page editing feature allows users to create and edit wiki pages for FTBC objects through an interactive CLI workflow. When creating a new object page, the system automatically pre-fills structured data from the object's JSON definition while allowing players to input dynamic content sections.

## Workflow

### 1. Access Object Editing

```
> create                           # Select the "create" command
> Main Realm                       # Search for and select a realm
> 1                                # Select an object from the list
```

### 2. Object Page Display

Once an object is selected, the system shows:

```
============================================================
Object: Zombified Barf Bag [CREATE]
============================================================
Difficulty: unforgiving
Area: Unknown
Hint: find a wrench to unlock access to the sewers

Enter INFO section (description):
> [Player input...]

Enter OBTAINING section (how to get it):
> [Player input...]
```

### 3. Auto-Populated Fields

The system automatically fills the following from object JSON data and realm configuration:

| Field | Source | Example |
|-------|--------|---------|
| **ObjectName** | object.json | "Zombified Barf Bag" |
| **Difficulty** | object.json | "unforgiving" |
| **Area** | object.json (or Realm) | "Unknown" / "Main Realm" |
| **Hint** | object.json Description field | "find a wrench..." |
| **Theme Colors** | Realm config | accent_color, accent_label_color |
| **Background** | Realm theme | "Default.webp" |

### 4. Player Input Sections

Users provide the following when creating/editing:

| Section | Description | Example |
|---------|-------------|---------|
| **INFO** | Detailed object description | "This is a test object that can be found..." |
| **OBTAINING** | How to get/unlock the object | "You need a wrench to get through the door" |

### 5. Preview and Save

After entering content, the system shows a JSON preview:

```json
{
  "object": {
    "header": {
      "background_file": "Default.webp",
      "theme_accent_color": "#23bd1c",
      "theme_accent_label_color": "#ffffff"
    },
    "character_info": {
      "name": "Zombified Barf Bag",
      "difficulty": "unforgiving",
      "area": "Unknown",
      "hint": "find a wrench to unlock access to the sewers"
    },
    "sections": {
      "info": "[User input]",
      "obtaining": "[User input]"
    },
    "categories": ["unforgiving Objects", "Objects", "Unknown Objects"]
  }
}
```

User confirms with "yes" or "no" to save.

## Technical Details

### Function: `edit_object_page()`

**Location:** `wiki/main.py` (line 149)

**Parameters:**
- `realm_name` (str): The realm containing the object
- `obj_data` (dict): Object data from realm JSON
- `object_pages` (dict): Status of existing wiki pages

**Workflow:**
1. Display object metadata and auto-filled fields
2. Collect user input for info and obtaining sections
3. Generate complete page JSON using template renderer
4. Display preview and confirm save
5. Save to `realms/[RealmName]/objects/[ObjectName].json`

### Template System

The object page is generated using the **object.json template** (`wiki/templates/object.json`) with the following placeholders:

```json
{
  "object": {
    "header": {
      "background_file": "{{BACKGROUND_IMAGE}}",
      "theme_accent_color": "{{THEME_ACCENT_COLOR}}",
      "theme_accent_label_color": "{{THEME_ACCENT_LABEL_COLOR}}"
    },
    "character_info": {
      "name": "{{OBJECT_NAME}}",
      "gallery": ["{{OBJECT_IMAGE}}"],
      "difficulty": "{{DIFFICULTY}}",
      "area": "{{AREA_REALM}}",
      "hint": "{{HINT}}"
    },
    "sections": {
      "info": "{{INFO_DESCRIPTION}}",
      "obtaining": "{{OBTAINING_INSTRUCTIONS}}"
    },
    "categories": [
      "{{DIFFICULTY}} Objects",
      "Objects",
      "{{REALM}} Objects"
    ]
  }
}
```

### Object Page Generator

**Class:** `ObjectPageGenerator` (`wiki/generators/__init__.py`)

**Method:** `generate_object_page()`

```python
ObjectPageGenerator.generate_object_page(
    name="Zombified Barf Bag",
    difficulty="unforgiving",
    area="Main Realm",
    hint="find a wrench to unlock access to the sewers",
    info="This is a test object...",
    obtaining="You need a wrench...",
    image="Zombified_Barf_Bag.png",
    background="Default.webp"
)
```

The method:
1. Loads the object.json template
2. Retrieves realm theme colors from Config
3. Renders all placeholders with provided data
4. Returns a complete JSON structure ready to save

### Realm Configuration

Each realm has theme colors defined in `wiki/core/config.py`:

```python
REALMS_INFO = {
    "Main Realm": {
        "theme": "green",
        "accent_color": "#23bd1c",
        "accent_label_color": "#ffffff",
    },
    # ... more realms
}
```

These colors are automatically applied to all object pages created in that realm.

## File Storage

Created object pages are saved to:

```
realms/[RealmName]/objects/[ObjectName].json
```

Example:
- `realms/Main Realm/objects/Zombified Barf Bag.json`
- `realms/Yoyleland/objects/YoyleMan.json`

## Integration with Wiki Checker

The object page status is tracked through the wiki page checker:

- **[+]** = Page exists on Fandom Wiki
- **[x]** = No page exists

The status is checked in parallel using ThreadPoolExecutor (10 workers) for performance.

## Features

✅ **Auto-population** of structured object data from JSON
✅ **Theme-aware** styling from realm configuration
✅ **Template-based** generation for consistency
✅ **User input** for dynamic content sections
✅ **Preview** before saving
✅ **Automatic file storage** to proper directory
✅ **Existing page detection** with [+]/[x] status

## Testing

Run the interactive test:

```bash
python test_interactive_edit.py
```

This will:
1. Load the object template
2. Generate a sample object page
3. Create test object page files
4. Display preview of generated structure

## Usage Example

```bash
# Start the CLI
python wiki/main.py

# At prompt:
> create
> main realm
> 1

# Select first object and enter description/obtaining info
# Confirm save with "yes"
# Object page created in realms/Main Realm/objects/

# Check the created file:
# realms/Main Realm/objects/Zombified Barf Bag.json
```

## Future Enhancements

- [ ] Edit existing object pages
- [ ] Bulk upload to wiki
- [ ] Custom theme per object
- [ ] Image gallery management
- [ ] Page version history
- [ ] Markdown export option
