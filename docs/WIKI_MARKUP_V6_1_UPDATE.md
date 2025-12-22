# Wiki Markup Generation System - v6.1 Update

## Overview
Enhanced the FTBC Wiki system to generate proper wiki-formatted markup that matches the exact style of completed functional object pages on ftbc.fandom.com.

## Key Improvements

### 1. New Wiki Markup Generator
**File:** `wiki/generators/__init__.py`

Added `ObjectPageGenerator.generate_wiki_markup()` method that generates complete, copy-paste-ready wiki markup with:

- **Background Image Styling**: Fixed positioning with z-index layering
- **CharacterInfo Template**: Proper Fandom template formatting
- **Colored Difficulty Icons**: Dynamic icon and color based on difficulty tier
- **Themed Accent Colors**: Per-realm color schemes applied to page styling
- **Arduous+ Spoiler Boxes**: Automatic collapsible spoiler boxes for challenging difficulties
- **Previous Difficulties Support**: Tracks previous difficulty tiers
- **Category Classification**: Automatic categorization by difficulty, realm, and object type

### 2. Enhanced Object Editing Workflow
**File:** `wiki/main.py`

Updated `edit_object_page()` to:

- Collect image file name (with automatic `.png` extension handling)
- Collect previous difficulties metadata
- Display **actual wiki markup** instead of simplified preview
- Output is immediately copy-paste-ready for Fandom wiki editor

### 3. Improved Source Editor Preview
**File:** `wiki/main.py`

Updated `format_source_editor_preview()` to:

- Use the new `generate_wiki_markup()` method
- Display actual wiki-formatted output that users see
- No longer just text summary - shows real markup

### 4. Difficulty Tier Detection
**Features:**
- Arduous and above (Arduous, Strenuous, Remorseless, Horrifying, IMPOSSIBLE) automatically get spoiler boxes
- Below Arduous show obtaining instructions directly (no spoiler)
- Matches wiki standard for "challenging objects"

### 5. Difficulty Icon & Color Mapping
**16 Difficulty Tiers Supported:**
- Effortless through IMPOSSIBLE
- Each has unique icon file and color code
- Colors match ftbc.fandom.com difficulty indicators

## Example Output

### For EXTREME Object (Specimum Sandwich):
```wiki
<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:Default.webp|2000px]]
</div>
<div style="--theme-accent-color:-webkit-linear-gradient(#C45508,#EEDC5B); --theme-accent-label-color:#ffffff;">
<div style="position:relative; z-index:1;">

{{CharacterInfo
|name=Specimum Sandwich
|character=[[File:Specimum Sandwich.png]]
|difficulty=[[File:Extreme.png|link=]] <span style="color:#ed2727">'''<b>Extreme</b>'''</span>
|area=[[Inverted Realm]]
|hint=all alone up there
|additionalinfo
|previousdifficulties = Insane
}}

== Info ==
A moldy green sandwich... yummy!

== Obtaining ==
Under one of the stairs in the upside down Roblox HQ

[[Category:Extreme Objects]]
[[Category:Objects]]
[[Category:Inverted Realm Objects]]
</div>
</div>
```

### For ARDUOUS Object (with spoiler):
```wiki
== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">Hidden location instructions here...</div>
</div>
```

## Files Modified

1. **wiki/generators/__init__.py**
   - Added `ARDUOUS_AND_ABOVE` set for difficulty detection
   - Added `DIFFICULTY_ICONS` mapping for all 16 difficulty tiers
   - Added `generate_wiki_markup()` static method

2. **wiki/main.py**
   - Updated `edit_object_page()` to collect additional metadata
   - Updated `format_source_editor_preview()` to use new generator
   - Now displays actual copyable wiki markup

3. **wiki/templates/object_new.json**
   - Created new template with wiki-formatted markup structure
   - Includes conditional spoiler box generation
   - Supports all metadata fields

## Files Added

- `wiki/templates/object_new.json` - New wiki-formatted template
- `tests/test_wiki_markup_generation.py` - Comprehensive test suite
- `tests/test_wiki_markup_simple.py` - Simplified test for quick verification

## Testing

**All 10/10 verification tests passing:**
✓ Config loads with 15 realms
✓ Object template loads correctly  
✓ RealmCommands works (15 realms)
✓ Objects load (593 objects in Main Realm)
✓ Fuzzy matching works
✓ Wiki checking works (380/593 pages found)
✓ Template rendering works
✓ Object page generation works
✓ Realm theme colors configured
✓ File structure correct

**Additional validation:**
✓ Wiki markup generation produces valid wiki syntax
✓ Arduous+ difficulty detection correctly identifies spoiler-eligible objects
✓ Image file name normalization prevents `.png.png` duplication
✓ All 16 difficulty tiers properly mapped to icons and colors

## Usage

### Creating an Object Page:
```bash
python wiki/main.py
> create
> Main Realm
> [Select object by number]
> [Enter INFO description]
> [Enter OBTAINING instructions]
> [Enter image file name or press Enter for default]
> [Enter previous difficulties if any]
```

The system will then display:
- The exact wiki markup ready to copy
- Preview of how it appears in Fandom editor
- Option to save locally

### Copying to Fandom:
1. System displays full wiki markup
2. Copy the markup from terminal
3. Go to ftbc.fandom.com wiki page
4. Click "Edit"
5. Paste markup into source editor
6. Save!

## Configuration

### Realm Theme Settings (wiki/core/config.py)
Each realm has:
- `accent`: Gradient color for background
- `accent_color`: Primary color
- `accent_label_color`: Text color (white or black for contrast)

### Difficulty Colors (wiki/core/config.py)
16 difficulty tiers with HEX color codes:
- Easy tiers: Green/yellow shades
- Hard tiers: Orange/red shades
- Extreme tiers: Deep red/purple shades
- Secret: Gold/tan shade

## Future Enhancements

Potential additions:
- Auto-upload to Fandom wiki integration
- Batch page generation from CSV
- Page preview rendering
- Wiki link validation
- Image file upload assistance
