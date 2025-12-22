# Quick Reference: Wiki Markup Generation

## What's New

The wiki system now generates **actual wiki markup** that you can copy directly into the Fandom editor. No more manual formatting!

## One-Minute Overview

1. **Run the CLI**: `python wiki/main.py`
2. **Type**: `create`
3. **Select realm and object**
4. **Enter description and obtaining instructions**
5. **System shows copy-paste-ready wiki markup**
6. **Paste into Fandom editor → Done!**

## Key Features

### ✓ Automatic Difficulty Handling
- **Extreme and below** → Instructions shown directly
- **Arduous and above** → Instructions in collapsible spoiler box

### ✓ Colored Difficulty Icons
- Extreme: Red (#ed2727)
- Arduous: Purple (#5d0cff)
- IMPOSSIBLE: Black (#000000)
- ... and 13 more!

### ✓ Realm-Themed Styling
Each realm has unique:
- Background gradient
- Accent color
- Text color (auto-adjusted for readability)

### ✓ Previous Difficulties
Track what difficulty an object used to have:
- "Insane"
- "Insane, Hard, Easy"
- etc.

## Example Workflow

```
$ python wiki/main.py
> create
> Main Realm
> (1) Teardrop
  (2) TV
  ... [593 objects]
> 1
Object: Teardrop [CREATE]
Difficulty: Normal
Area: Main Realm
Hint: It's sad

Enter INFO section (description):
> A blue teardrop-shaped object that cries
Enter OBTAINING section (how to get it):
> Found near the Sad Face in the valley
Enter image file name (press Enter to use default: Teardrop.png):
> [press Enter]
Enter previous difficulties (if any, e.g., 'Insane, Hard'):
> [press Enter]

===== Source Editor Preview (Copy & Paste into Fandom) =====
<div align="center" style="position:fixed; z-index:-1; ...
[[File:Default.webp|2000px]]
...
{{CharacterInfo
|name=Teardrop
|character=[[File:Teardrop.png]]
|difficulty=[[File:Normal.png|link=]] <span style="color:#a1ff27">'''<b>Normal</b>'''</span>
|area=[[Main Realm]]
|hint=It's sad
|additionalinfo
}}
...
[markup truncated for brevity]
```

## Spoiler Box Example

When difficulty is **Arduous or higher**, you get this automatically:

```wiki
== Obtaining ==
'''''The following text will show instructions on how to get this object. 
If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
Your obtaining instructions here...
</div>
</div>
```

The spoiler starts **collapsed** so readers must click to reveal.

## Supported Difficulties

| Tier | Color | Spoiler Box |
|------|-------|------------|
| Effortless | #17a897 | No |
| Easy | #10da8d | No |
| Moderate | #07fc55 | No |
| Normal | #a1ff27 | No |
| Intermediate | #ffb700 | No |
| Hard | #FF7700 | No |
| Difficult | #f54f25 | No |
| Extreme | #ed2727 | No |
| Unforgiving | #ff143f | No |
| Insane | #ff1c95 | No |
| Dreadful | #db25ff | No |
| Terrifying | #8b17ff | No |
| **Arduous** | #5d0cff | **YES** |
| **Strenuous** | #4048e5 | **YES** |
| **Remorseless** | #2084ff | **YES** |
| **Horrifying** | #2bd0fd | **YES** |
| IMPOSSIBLE | #000000 | No* |

*IMPOSSIBLE is typically not assigned to regular objects

## Realm Color Schemes

- **Main Realm**: Green gradient
- **Inverted Realm**: Orange-gold gradient
- **Evil Forest**: Dark purple gradient
- **Frozen World**: Cyan gradient
- **Yoyleland**: Purple gradient
- ... and 10 more!

## Tips & Tricks

### Tip 1: Image Names
- If you have a custom image file, enter the filename (with or without `.png`)
- System automatically adds `.png` if missing
- Default is `[ObjectName].png`

### Tip 2: Previous Difficulties
- Leave blank if this is the first version
- Add comma-separated list for history
- Example: "Insane, Hard, Easy" means it was Insane → Hard → Easy → Current

### Tip 3: Copy-Paste Ready
- The markup shown is **ready to use**
- Copy the entire block
- Go to https://ftbc.fandom.com/wiki/[ObjectName]
- Click "Edit"
- Paste into source editor
- Save!

### Tip 4: Special Characters
- If object name has special characters: `Test's Object`
- Wiki will handle it correctly in the markup
- No escaping needed

## Verification

Test the system:
```bash
python tests/verify_all_tests.py
```

Should show:
```
===== RESULTS: 10/10 tests passed =====
🎉 ALL TESTS PASSED - SYSTEM READY FOR USE!
```

## Files to Know About

- `wiki/generators/__init__.py` - Contains markup generation logic
- `wiki/main.py` - CLI and editing workflow
- `wiki/core/config.py` - Difficulty colors and realm themes
- `wiki/templates/object.json` - Object template structure

## For More Info

See: `docs/WIKI_MARKUP_V6_1_UPDATE.md`
