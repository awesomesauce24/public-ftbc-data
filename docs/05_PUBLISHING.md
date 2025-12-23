# Publishing Pages to Fandom Wiki

Guide for publishing object pages to ftbc.fandom.com.

## Overview

The system can auto-publish pages to the Fandom wiki using the Spongybot bot account.

## Prerequisites

1. **Local page created** - Must have saved locally first
2. **Bot credentials** - `.fandom_creds.json` with username/password
3. **Internet connection** - For API communication

## Setting Up Bot Credentials

Create `.fandom_creds.json` in repo root:

```json
{
  "username": "ChruustGaming@Spongybot",
  "password": "your_api_password_here"
}
```

⚠️ **Security**: This file is git-ignored - never commit it!

## Publishing a Page

### Method 1: From Main Menu

```powershell
python wiki/main.py
> publish
```

Then select realm and object.

### Method 2: During Creation

After saving locally, you'll see:

```
Page saved locally. Publish to wiki? (yes/no):
> yes
```

## Publishing Process

1. **Authenticate** - Logs into Fandom using bot credentials
2. **Create/Update** - Creates new page or updates existing
3. **Add Edit Summary** - "Updated / Created By Spongybot"
4. **Verify** - Confirms success

Output:
```
Publishing to Fandom...
✓ Successfully published: Firey
  URL: https://ftbc.fandom.com/wiki/Firey
```

## Page Locations on Wiki

Pages are created at:
```
https://ftbc.fandom.com/wiki/[ObjectName]
```

For subrealm objects:
```
https://ftbc.fandom.com/wiki/[Subrealm]/[ObjectName]
```

Examples:
- `https://ftbc.fandom.com/wiki/Firey`
- `https://ftbc.fandom.com/wiki/Yoyle_Factory/Abandonment/Aura_Sphere`

## Troubleshooting

### "Cannot authenticate"

- Check `.fandom_creds.json` has correct username/password
- Ensure bot account exists on Fandom
- Test credentials manually on Fandom wiki

### "API error"

- Check internet connection
- Verify bot account has permission to edit
- Try publishing again after waiting a moment

### "Page already exists"

This is normal - the system updates existing pages. Check the wiki to verify changes were applied.

## Batch Publishing

To publish multiple pages at once:

```powershell
# After creating/editing pages:
> publish
> Main Realm
> 1    # Publish object 1
> publish
> Main Realm
> 2    # Publish object 2
# ... etc
```

Or modify the code to automate.

## Verifying Published Content

After publishing, visit:
```
https://ftbc.fandom.com/wiki/[ObjectName]
```

Check:
- ✓ Title and difficulty are correct
- ✓ Description and obtaining sections displayed
- ✓ Image is showing
- ✓ Categories at bottom are correct
- ✓ Theme colors match realm

## Editing Published Pages

Simply edit the local page again and republish - it overwrites the wiki version.

## Rolling Back

If you publish something wrong:

1. Edit locally to fix
2. Republish with correct content
3. Or manually edit on Fandom wiki directly

## Edit Summaries

All published pages include edit summary:
```
Updated / Created By Spongybot
```

This shows in wiki page history for tracking.
