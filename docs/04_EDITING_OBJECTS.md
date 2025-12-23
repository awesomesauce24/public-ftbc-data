# Editing & Updating Pages

Guide for modifying existing object wiki pages.

## Editing a Page

### Select the Object Again

Simply select the same object in the create workflow:

```
> create
> Main Realm
> Firey
```

### Make Changes

Update any of the fields:
- INFO section (description)
- OBTAINING section (how to get)
- Image filename
- Previous difficulties

### Save Changes

```
Save this page? (yes/no):
> yes
```

The system overwrites the previous version.

## What You Can Change

✅ **Editable:**
- INFO section content
- OBTAINING section content
- Image filename
- Previous difficulties list
- Old image reference

⚠️ **Cannot Change** (from JSON):
- Object name
- Difficulty tier
- Area/location
- Hint text

(To change these, you'd need to modify the source JSON file)

## Preview Changes

Before saving, review the generated markup to ensure:
- Formatting looks correct
- All text is included
- Categories are right
- Images are referenced properly

## Publishing Changes

After local save:

```
> publish
> Main Realm
> Firey
```

Updates the wiki with your changes.

## Reverting Changes

If you mess up and want to go back:

1. Locate the saved file:
   ```
   realms/Main Realm/objects/Firey.json
   ```

2. Either:
   - Delete it and recreate (if backed up in git)
   - Edit the JSON manually to revert
   - Use git to restore previous version

## Batch Updates

To update multiple objects at once:

```
# In shell/terminal
for i in 1 2 3 4 5; do
  echo "$i" | python wiki/main.py
done
```

Or manually repeat the workflow for each object.

## Tips

- Save changes frequently
- Test on one object before bulk updating
- Review markup before publishing
- Keep backups (git commit regularly)
