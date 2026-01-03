# FTBC Data Scripts

Utility scripts for managing FTBC (Fibonacci Battle Creators) game data and wiki content.

## Metadata Enrichment

### `enrich_objectjsons.py`
Enriches the base rbxlx-extracted object metadata with wiki-ready structure.

**What it does:**
- Takes raw object data from `metadata/objectjsons/`
- Adds realm data (icon, image, gradient, accent colors)
- Includes difficulty icons and color codes
- Auto-generates wiki categories
- Creates placeholders for images and wiki content

**Output:** Enhanced metadata with structure ready for wiki page generation

### `populate_images.py`
Searches local realm folders for object image files and populates the metadata.

**What it does:**
- Scans realm directories for image files matching object names
- Tries multiple extensions: .jpg, .png, .webp
- Handles "New" suffix variants (e.g., "American Flag New.png")
- Populates the `images` array in metadata

**Status:** Ready to use if images are stored locally in realm folders

### `populate_images_wiki.py`
Fetches image information from the Fandom wiki for each object.

**What it does:**
- Checks the FTBC Fandom wiki for image files
- Tries multiple extensions: webp, png, jpg
- Handles "New" suffix variants
- Populates the `images` array with wiki file references

**Usage:** `python populate_images_wiki.py`

**Note:** Requires internet connection; may be slow for large datasets (~1500 objects)

## Wiki Integration

### `wiki_scraper_enricher.py` (In Progress)
Extracts additional data from the FTBC Fandom wiki to populate images and previous difficulties.

**What it does:**
- Fetches wiki pages for each object using MediaWiki API
- Parses CharacterInfo templates
- Extracts image files (current and "New" variants)
- Extracts previous difficulty history

**Status:** In development - Wiki API access is currently being blocked/redirected to HTML. May need alternative approach (Selenium, different API endpoint, or HTML scraping). The core metadata enrichment is complete and functional without this.

### `wiki_scraper.py` (existing)
Original wiki scraper for object pages from the FTBC Fandom wiki.

### `create_pages.py`
Interactive tool to scan realms and check which objects have wiki pages.

**Usage:** `python create_pages.py`
- Select a realm by number, name, or 'all'
- Shows [+] for existing pages, [x] for pages to create
- Displays coverage statistics

### `interactive_create_pages.py`
Full interactive wiki page creator with editing capabilities.

**Usage:** `python interactive_create_pages.py`

**Features:**
- Select realm and object
- Auto-populates CharacterInfo template with:
  - Object name, difficulty, realm
  - Images from metadata
  - Previous difficulties
- Prompts for additional content:
  - Info section
  - Obtaining section
  - Extra previous difficulties
  - Old image filename
- Generates complete wiki markup
- Preview before upload
- Upload to wiki
- Menu to continue editing or switch realms

**Workflow:**
1. Choose realm
2. Select object
3. Edit Info/Obtaining sections
4. Preview generated wiki markup
5. Upload to wiki
6. Choose next action:
   - Edit another object in same realm
   - Switch to different realm
   - Quit

## Authentication & Editing

### `auth.py` (existing)
Handles authentication for wiki API access.

### `edit_object.py` (existing)
Makes updates to object metadata and wiki pages.

## Workflow

Typical workflow for updating object data:

1. **Extract from game:** Use rbxlx inspection tools to generate base metadata
2. **Enrich metadata:** `python enrich_objectjsons.py`
3. **Add images:** `python populate_images.py` or `python populate_images_wiki.py`
4. **Scrape wiki:** `python wiki_scraper.py` (to get additional content)
5. **Generate pages:** `python create_pages.py` (if needed)

## Configuration

- **Metadata directory:** `metadata/objectjsons/` - Contains realm-organized object metadata
- **Realms config:** `metadata/realms.json` - Realm styling and layout information
- **Game files:** `.rbxlx` files in `../Downloads/rbx/`

## Data Structure

See `metadata/objectjsons/` for enriched metadata format examples.

Key fields:
- `name` - Object name
- `difficulty` - Current difficulty level (Title Case)
- `realm` - Which realm the object is in
- `realmData` - Realm styling information
- `images` - Array of image files available for this object
- `categories` - Wiki categories this object belongs to
- `difficultyInfo` - Icon and color for the difficulty level
- `wiki` - Placeholder sections for wiki content (info, obtaining)
