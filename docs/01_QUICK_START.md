# Quick Start: Create Your First Object Page

Get up and running in 5 minutes!

## Prerequisites

- Python 3.11+ installed
- Virtual environment activated (`.venv/Scripts/Activate.ps1`)
- FTBC Wiki System cloned and set up

## Step 1: Start the System

```powershell
python wiki/main.py
```

You'll see:
```
FTBC Wiki System
================
1. create - Create/edit object pages
2. exit   - Exit program

Choose an option:
```

## Step 2: Select "create"

```
> create
```

## Step 3: Choose a Realm

```
Enter realm name (fuzzy matching enabled):
> Main Realm
```

You'll see all objects in that realm with status indicators:
- `[+]` = Page exists
- `[x]` = No page yet

## Step 4: Select an Object

Enter the object **number** or **name**:

```
> 1           # First object in the list
> Firey       # Object name (fuzzy matching works!)
> Firey Jr    # Will show similar matches if ambiguous
```

If multiple matches found:
```
Found 3 similar objects:
(1) Firey
(2) Firey Jr.
(3) Firey Speaker Box

Select which one:
> 1
```

## Step 5: Fill in Object Info

### INFO Section (What is this object?)

```
Enter INFO section (Describe the object).
(Type lines of text, then press Enter twice to finish):

> A character with a white round body and orange mouth.
> Often acts as a leader in the game.
> 
```

### OBTAINING Section (How to get it?)

```
Enter OBTAINING section (how to get it).
(Type lines of text, then press Enter twice to finish):

> Start at the main plaza.
> Head east towards the forest.
> Look for Firey near the large tree.
> 
```

### Additional Info

```
Enter image file name (press Enter to use default: Firey.png):
> 

Does this object have an old image? (yes/no):
> no

Enter previous difficulties (if any, e.g., 'Insane, Hard'):
> 

```

## Step 6: Review & Save

You'll see the generated wiki markup:

```
<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:Goiky.png|2000px]]
</div>

{{CharacterInfo
|name=Firey
|character=[[File:Firey.png]]
|difficulty=[[File:Effortless.png]] <span style="color:#17a897">'''Effortless'''</span>
|area=[[Goiky]]
|hint=[hint from JSON]
...
```

Then choose:

```
Save this page? (yes/no):
> yes

Page saved to: realms/Main Realm/objects/Firey.json
```

## 🎉 Done!

Your object page is now created and saved locally. 

**To publish to the wiki**, you can use the `publish` command from the main menu.

## 💡 Tips

- **Fuzzy matching**: Type partial names - "fir" will find "Firey"
- **Multi-line input**: Press Enter twice to finish entering text
- **Images**: Use `.png` or `.webp` formats
- **Old images**: For objects with redesigns, you can include old image references

## ❓ Common Questions

**Q: Can I edit a page after saving?**  
A: Yes! Select the same object again - you can modify and resave.

**Q: Where are files saved?**  
A: `realms/[RealmName]/objects/[ObjectName].json`

**Q: Does it auto-publish to the wiki?**  
A: Not automatically - you need to confirm publishing separately.

**Q: What if I make a mistake?**  
A: Edit the object again and resave. Changes are saved locally first.
