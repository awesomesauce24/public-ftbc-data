# Wiki Management System Architecture

## Overview
The FTBC Wiki Management System is a Python CLI tool for managing wiki object pages. It consists of three main modules that work together:

## Module Structure

### 1. `auth.py` - Authentication
**Purpose:** Handle authentication with Fandom wiki

**Key Classes:**
- `WikiAuth` - Manages wiki login and session

**Key Functions:**
- `authenticate()` - Main entry point, returns authenticated session

**Flow:**
1. Load credentials from `.env` (BOT_USERNAME, BOT_PASSWORD)
2. Get login token from wiki API
3. Perform login
4. Return authenticated session

---

### 2. `create_pages.py` - Wiki Page Management
**Purpose:** Create, format, and manage wiki object pages

**Organized Sections:**

#### UTILITY FUNCTIONS (Data loading & configuration)
- `load_json()` - Load JSON files safely
- `get_special_case()` - Get special formatting for realms
- `get_difficulty_info()` - Get difficulty properties (icon, color, priority)
- `get_realm_gradient()` - Get gradient and accent color for realms
- `list_realms_and_subrealms_hierarchical()` - List all realms/subrealms
- `check_wiki_page_exists()` - Check if wiki page exists
- `find_fuzzy_matches()` - Find similar object names

#### WIKI INTERACTION (Fetching & uploading)
- `upload_wiki_page()` - Upload page content to wiki
- `fetch_wiki_source()` - Fetch raw wiki source (with retry strategies)

#### PARSING (Extract info from content)
- `parse_old_format()` - Parse wiki/txt content for Info & Obtaining sections
  - Handles multiple formats:
    - Traditional `== Info ==` sections
    - CharacterInfo template with `|hint=` parameter
    - Incomplete/missing info sections

#### MAIN WORKFLOWS (Single realm operations)
- `update_realm()` - Update/download pages from single realm
- `create_object_in_realm()` - Create new wiki page with CLI guidance
- `update_realm_format()` - Format + create stubs for single realm
  - Deletes old files
  - Fetches from wiki in parallel (8 workers)
  - Reformats existing pages
  - Creates `[x]` stubs for missing/incomplete pages

#### BATCH OPERATIONS (All realms)
- `reformat_and_stub_all_realms()` - Format + stub all realms at once
  - Uses parallel fetching (8 workers) for speed
  - Much faster than single-realm operations

#### PUBLIC API (Entry points from main.py)
- `create(session)` - Create new wiki object page
- `update_realm(session)` - Update realm pages
- `update_realm_format(session)` - Format pages + create stubs

---

### 3. `main.py` - CLI Entry Point
**Purpose:** Provide user-friendly command-line interface

**Key Functions:**
- `show_help()` - Display available commands
- `main()` - Main CLI loop

**Commands:**
```
> create       - Create a new wiki object page
> update       - Update realm pages from wiki
> format       - Format pages + create stubs for missing
> help         - Show help message
> exit         - Exit the CLI
```

**Flow:**
1. Authenticate with wiki
2. Display welcome message
3. Loop accepting commands
4. Parse command and call appropriate function from `create_pages.py`
5. Catch KeyboardInterrupt (Ctrl+C) to exit gracefully

---

## Data Flow

### Create New Page Flow
```
main.py (create command)
  → create_pages.create()
    → create_object_in_realm()
      → list_realms_and_subrealms_hierarchical()  (show options)
      → find_fuzzy_matches()  (if needed)
      → load_json()  (get metadata)
      → get_difficulty_info()  (format difficulty)
      → get_realm_gradient()  (format realm styling)
      → build wiki markup
      → upload_wiki_page()  (uses auth.session)
```

### Format Realm Pages Flow
```
main.py (format command)
  → create_pages.update_realm_format()
    → list_realms_and_subrealms_hierarchical()  (show options)
    → load_json()  (get all objects in realm)
    → ThreadPoolExecutor (8 workers) for each object:
      → fetch_wiki_source()  (parallel fetching)
      → parse_old_format()  (extract info/obtaining)
      → If found: reformat and save
      → If not found: create [x] stub file
    → Display summary
```

---

## Key Design Decisions

1. **Parallel Fetching**: Uses `ThreadPoolExecutor` with 8 workers for batch operations to speed up wiki API calls

2. **Case-Insensitive Search**: Wiki API accepts any case, but returns proper case from wiki - used to ensure consistent naming

3. **Stub Creation**: Missing pages get `[x]` prefix so users can:
   - Fill in missing Info/Obtaining sections
   - Rename to remove `[x]` when ready
   - Upload with `create` command

4. **Modular Organization**: Logical sections make the code easy to navigate and maintain

5. **Error Handling**: Graceful fallbacks for network errors, missing pages, incomplete formatting

---

## Usage Examples

### Format single realm
```
> format
(2) Midnight Rooftops
[+] Saved: 18 pages
[+] Created: 17 stubs (marked with [x])
```

### Format all realms (parallel)
```
> format
(@) Format ALL realms
[*] Main Realm (25 objects)
    [+] 25 saved, [+] 0 stubbed, [!] 0 failed
[*] Midnight Rooftops (41 objects)
    [+] 24 saved, [+] 17 stubbed, [!] 0 failed
...
```

### Create new page
```
> create
(Select realm)
(Enter object name)
(Enter info description)
(Enter obtaining instructions)
[+] Uploaded to wiki
```

---

## File Organization

```
├── main.py              (CLI entry point)
├── scripts/
│   ├── auth.py         (Wiki authentication)
│   ├── create_pages.py (Page management - 2000+ lines, organized in sections)
│   └── __pycache__/
├── metadata/           (Configuration files)
│   ├── difficulties.json
│   ├── realm_gradients.json
│   ├── special_cases.json
│   ├── realms/         (Realm metadata)
│   └── subrealms/      (Subrealm metadata)
├── data/
│   ├── realms/         (Generated .txt files)
│   └── subrealms/
└── .env               (Credentials - BOT_USERNAME, BOT_PASSWORD)
```

---

## Performance Characteristics

- **Single realm format**: ~1 second per object (sequential)
- **Batch format**: ~100ms per object (8 parallel workers)
- **41 objects**: ~41 seconds sequential vs ~5 seconds batch
- **Bottleneck**: Wiki API response time (~500ms-1000ms per request)

