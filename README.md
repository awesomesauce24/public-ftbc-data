# FTBC Wiki Management System

A Python-based CLI tool for managing Fandom wiki pages for the **Funny Tree Build Craft (FTBC)** game. This system automates creation, formatting, and management of wiki object pages.

## 🎯 Features

- **Create Wiki Pages** - Generate new object pages with proper formatting
- **Format & Reformat** - Convert wiki pages to standardized template
- **Batch Operations** - Process entire realms in parallel (8 workers)
- **Auto Stub Creation** - Generate placeholder files for missing pages (marked with `[x]`)
- **Case Normalization** - Automatically fix naming inconsistencies from the wiki
- **Parallel Fetching** - 8x faster batch processing using ThreadPoolExecutor
- **Robust Parsing** - Handle multiple wiki formats:
  - Traditional `== Info ==` sections
  - CharacterInfo template with `|hint=` parameter
  - Incomplete wiki pages
  - Pages with collapsible sections

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- `pip` (Python package manager)
- Fandom wiki bot credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/awesomesauce24/public-ftbc-data.git
   cd public-ftbc-data
   ```

2. **Create virtual environment** (optional but recommended)
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or: source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up credentials**
   - Create a `.env` file in the root directory
   - Add your wiki bot credentials:
     ```
     BOT_USERNAME=your_bot_username
     BOT_PASSWORD=your_bot_password
     ```

5. **Run the system**
   ```bash
   python main.py
   ```

## 📖 Usage Guide

### Command Reference

```
> create       - Create a new wiki object page
> update       - Update realm pages from wiki
> format       - Format pages + create stubs for missing
> help         - Show help message
> exit         - Exit the CLI
```

### Common Workflows

#### Format a Single Realm
```
$ python main.py
> format
Select realm/subrealm:
(1) Main Realm
(2) Midnight Rooftops
...
> 2

[+] Selected: Midnight Rooftops
[+] Found 41 objects
    Fetching from wiki and creating stubs...

[+] Saved: 24 pages from wiki
[+] Created: 17 stubs for missing pages (marked with [x])
[!] Failed: 0 pages
```

#### Format All Realms (Fast - Parallel)
```
> format
(@) Format ALL realms

[*] Main Realm (25 objects)
    [+] 25 saved, [+] 0 stubbed, [!] 0 failed
[*] Midnight Rooftops (41 objects)
    [+] 24 saved, [+] 17 stubbed, [!] 0 failed
[*] Timber Peaks (32 objects)
    [+] 32 saved, [+] 0 stubbed, [!] 0 failed
...
```

#### Create a New Page
```
> create
Select realm/subrealm:
(1) Main Realm
(2) Midnight Rooftops
...
> 2

[+] Selected: Midnight Rooftops
Available objects in Midnight Rooftops:
(1) Cursor
(2) Not Canon
...
> new

Enter object name: My New Object
[+] Creating stub for: My New Object

Enter info description:
> This is my awesome object

Enter obtaining instructions:
> Go to location X and jump

[+] Uploading to wiki...
[+] Successfully uploaded!
```

#### Work with Stub Files

1. **Find stubs** - Files starting with `[x]` are incomplete
   ```
   [x] Hot Sauce.txt
   [x] Glitter Bottle.txt
   ```

2. **Edit stub** - Open in your editor and fill in `[TODO]` sections:
   ```
   == Info ==
   [TODO: Add info description here]
   
   == Obtaining ==
   [TODO: Add obtaining instructions here]
   ```

3. **Rename when ready**
   ```
   [x] Hot Sauce.txt → Hot Sauce.txt
   ```

4. **Upload to wiki**
   ```
   > create
   (Select realm)
   (Upload newly edited page)
   ```

## 📁 Project Structure

```
public-ftbc-data/
├── README.md                 (This file)
├── ARCHITECTURE.md          (Detailed system architecture)
├── main.py                  (CLI entry point)
├── requirements.txt         (Python dependencies)
├── .env                     (Configuration - BOT_USERNAME, BOT_PASSWORD)
├── .gitignore              (Git ignore rules)
│
├── scripts/
│   ├── auth.py             (Wiki authentication)
│   ├── create_pages.py     (Page management - 2000+ lines)
│   └── __pycache__/
│
├── metadata/               (Configuration files)
│   ├── difficulties.json   (Difficulty settings)
│   ├── realm_gradients.json (Realm styling)
│   ├── special_cases.json  (Special realm configs)
│   ├── realms/            (Per-realm metadata)
│   └── subrealms/         (Per-subrealm metadata)
│
├── data/
│   ├── realms/            (Generated .txt files for realms)
│   └── subrealms/         (Generated .txt files for subrealms)
│
└── tests/                  (Test files)
    └── debug_*.py
```

## 🏗️ System Architecture

The system is organized into three main modules:

### `auth.py` - Authentication
- Handles Fandom wiki login
- Manages authenticated session
- Loads credentials from `.env`

### `create_pages.py` - Page Management
Organized in 6 logical sections:
1. **Utility Functions** - Data loading, metadata lookup
2. **Wiki Interaction** - Fetch/upload content
3. **Parsing** - Extract info from wiki markup
4. **Main Workflows** - Single realm operations
5. **Batch Operations** - All realms at once
6. **Public API** - Entry points for CLI

### `main.py` - CLI Interface
- User-friendly command loop
- Command dispatch
- Error handling and graceful exit

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed data flow diagrams and design decisions.

## ⚙️ Configuration

### Metadata Files

**difficulties.json**
```json
{
  "difficulties": [
    {
      "name": "Extreme",
      "icon": "Extreme.png",
      "color": "#ed2727",
      "priority": 10
    },
    ...
  ]
}
```

**realm_gradients.json**
```json
{
  "realms": [
    {
      "name": "Midnight Rooftops",
      "gradient": "-webkit-linear-gradient(#050522, #140f4a)",
      "accent": "#ffffff",
      "bg_image": "Midnight-rooftops.png"
    },
    ...
  ]
}
```

**special_cases.json**
```json
{
  "special_cases": {
    "The Backrooms": {
      "static_overlay": true,
      "static_image": "Staticbg.gif",
      "static_opacity": 0.05
    }
  }
}
```

## 🔄 Data Flow

```
Wiki (Fandom) ← → System → Local Files
  ↓
fetch_wiki_source() [with retry]
  ↓
parse_old_format() [extract sections]
  ↓
load_json() [get metadata]
  ↓
format_page() [build markup]
  ↓
Save to data/realms/[realm]/[object].txt
  ↓
Upload to wiki (optional)
```

## 📊 Performance

- **Single realm**: ~1 second per object (sequential)
- **Batch mode**: ~100ms per object (8 parallel workers)
- **Processing 41 objects**:
  - Sequential: ~41 seconds
  - Parallel: ~5 seconds
- **Bottleneck**: Wiki API response time (~500ms-1000ms)

## 🐛 Troubleshooting

### Authentication Failed
- Check `.env` file exists and contains valid credentials
- Verify BOT_USERNAME and BOT_PASSWORD are set correctly
- Ensure bot account has necessary wiki permissions

### Page Not Found on Wiki
- Check object name spelling
- Use the `update` command to download latest pages
- Some pages may not exist yet - they'll generate `[x]` stubs

### Parsing Errors
- Check wiki page formatting
- Some pages may use non-standard templates
- Create an issue with the page name for support

### Slow Performance
- Use batch mode (`@`) for multiple realms
- Batch uses 8 parallel workers (8x faster)
- Check internet connection - wiki API is the bottleneck

## 🤝 Contributing

### For Contributors

1. **Code Style**
   - Follow PEP 8 conventions
   - Use descriptive variable names
   - Add docstrings to functions

2. **Adding Features**
   - Add to appropriate section in `create_pages.py`
   - Update `ARCHITECTURE.md`
   - Test with multiple realms

3. **Bug Reports**
   - Include page name/realm
   - Describe what failed
   - Include error message

### Testing

Run tests with:
```bash
python tests/debug_structure.py
python tests/debug_username.py
python tests/test_polluted.py
```

## 📝 License

[Your License Here]

## 👨‍💻 Authors

- **awesomesauce24** - Repository owner
- Contributors welcome!

## 📚 Resources

- [FTBC Wiki](https://ftbc.fandom.com/)
- [Fandom API Docs](https://fandom.fandom.com/wiki/API)
- [MediaWiki Markup](https://www.mediawiki.org/wiki/Wikitext)

## 📧 Support

For issues, questions, or suggestions:
1. Check [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
2. Review existing code comments
3. Open an issue on GitHub

---

**Last Updated**: December 28, 2025  
**Version**: 1.0.0  
**Status**: Active Development
