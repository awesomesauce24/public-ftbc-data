# Creating Object Pages

Complete guide for creating wiki pages for FTBC objects.

## Overview

Creating an object page involves:
1. Selecting a realm
2. Choosing an object
3. Writing descriptions
4. Saving to local JSON
5. Publishing to wiki (optional)

## Step-by-Step Workflow

### 1. Start the System

```powershell
python wiki/main.py
```

### 2. Choose "create"

```
FTBC Wiki System
================
1. create - Create/edit object pages
2. exit   - Exit program

Choose an option:
> create
```

### 3. Select Realm

Enter realm name (fuzzy matching works):

```
Enter realm name (fuzzy matching enabled):
> Main Realm
```

Available realms:
- Main Realm
- Inverted
- Yoyleland
- Backrooms
- Yoyle Factory
- Classic Paradise
- Evil Forest
- Cherry Grove
- Barren Desert
- Frozen World
- Timber Peaks
- Midnight Rooftops
- Magma Canyon
- Sakura Serenity
- Polluted Marshlands

### 4. View Objects List

You'll see all objects in the realm:

```
Realm: Main Realm - Objects
==================================================
Total: 593 objects
  [+] WITH PAGE  : 45
  [x] NO PAGE    : 548
==================================================

Objects (593):

(1) One [x]
    Difficulty: Effortless
(2) Two [x]
    Difficulty: Insane
(3) Three [+]
    Difficulty: Hard
...
```

### 5. Select Object

Choose by **number** or **name**:

```
Enter object number or name to edit/create (or 'back'):
> Firey           # By name
> 5               # By number
```

**Fuzzy Matching**: If multiple objects match, you'll see:

```
Found 3 similar objects:
(1) Firey
(2) Firey Jr.
(3) Firey Speaker Box

Select which one:
> 1
```

### 6. Write INFO Section

Describe what the object is:

```
Enter INFO section (Describe the object).
(Type lines of text, then press Enter twice to finish):

> Firey is a circular orange character with a white body.
> He is known for his leadership qualities.
> Often wears a determined expression.
> 
```

**Tips:**
- Write 2-4 sentences describing the object
- Include physical appearance, role, or notable traits
- Multiple paragraphs are OK

### 7. Write OBTAINING Section

How to find or get the object:

```
Enter OBTAINING section (how to get it).
(Type lines of text, then press Enter twice to finish):

> Start at the main plaza in Goiky.
> Head east towards the forest area.
> Firey can be found near the large oak tree.
> Interact with him to obtain this object.
> 
```

**Tips:**
- Give clear directions
- Include any requirements or conditions
- List specific steps/landmarks

### 8. Image Configuration

#### Current Image

```
Enter image file name (press Enter to use default: Firey.png):
> 
```

- Press Enter for default `[ObjectName].png`
- Or enter custom name: `Firey.webp`, `Firey_v2.png`, etc.

#### Old Image (Optional)

```
Does this object have an old image? (yes/no):
> yes
Enter old image file name:
> Firey_old.png
```

If yes, the page will show both versions in a gallery.

### 9. Previous Difficulties

If the object's difficulty has changed:

```
Enter previous difficulties (if any, e.g., 'Insane, Hard'):
> Easy, Moderate
```

The system auto-formats with icons and colors:
```
[[File:Easy.png]] Easy  [[File:Moderate.png]] Moderate
```

### 10. Review Markup

You'll see the generated wiki markup:

```
<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:Goiky.png|2000px]]
</div>
<div style="--theme-accent-color:#23bd1c; --theme-accent-label-color:#ffffff;">
<div style="position:relative; z-index:1;">

{{CharacterInfo
|name=Firey
|character=[[File:Firey.png]]
|difficulty=[[File:Effortless.png]] <span style="color:#17a897">'''<b>Effortless</b>'''</span>
|area=[[Goiky]]
|hint=hint text from JSON
|additionalinfo
|previousdifficulties = [[File:Easy.png]] <span style="color:#10da8d">'''<b>Easy</b>'''</span> [[File:Moderate.png]] <span style="color:#07fc55">'''<b>Moderate</b>'''</span>
}}

== Info ==
Firey is a circular orange character with a white body...

== Obtaining ==
Start at the main plaza in Goiky...

[[Category:Effortless Objects]]
[[Category:Objects]]
[[Category:Goiky Objects]]
[[Category:Main Realm Objects]]
</div>
</div>
```

### 11. Save Page

```
Save this page? (yes/no):
> yes

Page saved to: realms/Main Realm/objects/Firey.json
```

The page is now saved locally as a JSON file.

## What Gets Auto-Filled

| Field | Source | Example |
|-------|--------|---------|
| Name | Object JSON | "Firey" |
| Difficulty | Object JSON | "Effortless" |
| Icon | Difficulty tier | `Effortless.png` |
| Color | Difficulty tier | `#17a897` |
| Area | JSON Section field + description hints | "Goiky" |
| Background | Realm config | `Goiky.png` |
| Theme colors | Realm config | Green gradient |
| Hint | Object JSON | Text from Description field |
| Categories | Auto-generated | "Effortless Objects", "Goiky Objects" |

## Special Cases

### Objects with Multiple Locations

If an object's description contains location hints like "(Start in Goiky)":

```json
{
  "ObjectName": "Two",
  "Description": "invisible platforms are cool. (Start in Goiky)",
  "Section": ""
}
```

The system extracts "Goiky" and assigns it correctly.

### Yoyle Factory Subareas

Some objects are in specific Yoyle Factory areas:

```json
{
  "ObjectName": "Aura Sphere",
  "Section": "Abandonment"
}
```

Auto-detects area as "Yoyle Factory/Abandonment" with special background and theme.

### Objects with Image Galleries

Old designs can be shown alongside current:

```
Does this object have an old image? (yes/no):
> yes
Enter old image file name:
> Boombox.png
```

Generates:
```
|character=<gallery>
Boombox.webp|Current
Boombox.png|Old
</gallery>
```

## Publishing

After saving locally, you can publish to the wiki:

```
> publish
```

See [Publishing Guide](./05_PUBLISHING.md) for details.

## Editing Existing Pages

Select the same object again to edit:

```
Enter object number or name:
> Firey
```

Make changes and save - the system updates the page.

## Common Patterns

### Simple Object Description

```
Firey is a circular orange character. He's known for his leadership skills.
```

### Detailed Description with Paragraphs

```
Three is a digit character who works as an accountant. 
He has a very organized and structured personality.

Three's appearance is blocky and geometric, with sharp edges.
He often carries a clipboard or calculator.
```

### Location-Based Obtaining

```
In Main Realm, start at the central plaza.
Walk north to the forest entrance.
Follow the path east for about 2 minutes.
Three can be found near the accounting office building.
Interact with the desk to obtain this object.
```

## Troubleshooting

### "Object not found"

- Check object name spelling
- Use fuzzy matching instead (partial names work)
- Try using the number instead

### "Invalid area detected"

- Ensure the object's Section field in JSON is correct
- Or add a location hint to Description: "(Start in [Area])"

### Image file errors

- Ensure image files exist in the wiki or are properly named
- Use standard formats: `.png` or `.webp`

### Page won't save

- Check file permissions on `realms/[Realm]/objects/` folder
- Ensure disk space is available
- Try saving with a simpler filename
