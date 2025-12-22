# Quick Start: Object Page Editing

## ⚡ Quick Start

### Start the CLI
```bash
python wiki/main.py
```

### Create Object Page
```
> create
> Main Realm                    # Or any realm name
> 1                             # Object number (e.g., 1-593 for Main Realm)
> [Enter description]           # INFO section
> [Enter obtaining info]        # OBTAINING section
> yes                           # Confirm save
```

## 📋 What Gets Auto-Filled

| Field | Auto-Filled From | Example |
|-------|------------------|---------|
| **Name** | Object JSON | "Zombified Barf Bag" |
| **Difficulty** | Object JSON | "unforgiving" |
| **Area** | Object JSON | "Unknown" or Realm name |
| **Hint** | Object description | "find a wrench..." |
| **Theme** | Realm config | Green/Purple/etc |
| **Categories** | Auto-generated | "unforgiving Objects" |

## ✍️ What You Input

1. **INFO section** - Describe the object (what it is, how it looks, etc.)
2. **OBTAINING section** - How to get it (steps, requirements, etc.)

## 📁 Where Files Are Saved

Object pages are saved to:
```
realms/[RealmName]/objects/[ObjectName].json
```

Examples:
- `realms/Main Realm/objects/Zombified Barf Bag.json`
- `realms/Yoyleland/objects/YoyleMan.json`

## 🔍 Status Indicators

In object lists:
- **[+]** = Page already exists on wiki
- **[x]** = Page doesn't exist yet (you can create it)

## 📊 Example Output

```
============================================================
Object: Zombified Barf Bag [CREATE]
============================================================
Difficulty: unforgiving
Area: Unknown
Hint: find a wrench to unlock access to the sewers

Enter INFO section (description):
> A sickly object that resembles a barf bag from the original BFDI

Enter OBTAINING section (how to get it):
> Find in the sewers area, requires wrench to access

============================================================
Preview:
============================================================
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
      "info": "A sickly object...",
      "obtaining": "Find in the sewers..."
    },
    ...
  }
}

============================================================
Save this page? (yes/no):
> yes
[OK] Page saved to realms/Main Realm/objects/Zombified Barf Bag.json
```

## 🎮 Available Realms

1. Main Realm (593 objects)
2. Yoyleland
3. Backrooms
4. Evil Forest
5. Frozen World
6. Cherry Grove
7. Classic Paradise
8. Inverted Realm
9. Timber Peaks
10. Midnight Rooftops
11. Magma Canyon
12. Sakura Serenity
13. Barren Desert
14. Yoyle Factory (56 objects)
15. Polluted Marshlands

## 💡 Tips

- Use fuzzy search: type "main" for "Main Realm"
- Use object number for quick selection
- Press 'back' to return to previous menu
- Type 'help' for CLI help
- Type 'exit' to leave program

## 🚀 Commands

| Command | Description |
|---------|-------------|
| `create` | Create/edit object page |
| `realms` | Show all realms |
| `help` | Show help menu |
| `exit` | Exit program |

## ✅ Status Indicators

During object listing:

```
Objects (593):

(1) Zombified Barf Bag [+]
    Difficulty: unforgiving
(2) Vomit Drop [+]
    Difficulty: hard
(3) Ulm [x]
    Difficulty: arduous

...

============================================================
Total: 593 objects
  [+] WITH PAGE  : 379
  [x] NO PAGE    : 214
============================================================
```

## 📱 Mobile-Friendly Input

The system is designed for terminal input:
- Enter object number: `1` to `593`
- Enter back: `back`
- Confirm: `yes` or `no`

## 🎓 Common Workflow

### Creating Multiple Pages

```
> create
> Main Realm
> 1
> [description 1]
> [obtaining 1]
> yes
> [back to object list]
> 2
> [description 2]
> [obtaining 2]
> yes
> [back to main menu]
```

### Finding Objects

```
> create
> main          # Fuzzy search
> 1             # Select from matches
```

## 📝 JSON Structure

All object pages follow this structure:

```json
{
  "object": {
    "header": {
      "background_file": "...",
      "theme_accent_color": "...",
      "theme_accent_label_color": "..."
    },
    "character_info": {
      "name": "...",
      "gallery": ["..."],
      "difficulty": "...",
      "area": "...",
      "hint": "..."
    },
    "sections": {
      "info": "...",
      "obtaining": "..."
    },
    "categories": [...]
  }
}
```

## ❓ Frequently Asked

**Q: Can I edit pages after creating them?**
A: Yes, just create the page again with different content.

**Q: What if I make a mistake?**
A: The preview shows the JSON before saving. Choose "no" if it's wrong.

**Q: Where are object pages stored?**
A: In `realms/[RealmName]/objects/[ObjectName].json`

**Q: Can I delete pages?**
A: Manually remove the JSON file from the objects folder.

**Q: What if the object doesn't have theme colors?**
A: The realm's default theme colors are applied automatically.

---

**Last Updated:** 2024
**Status:** Production Ready ✅
