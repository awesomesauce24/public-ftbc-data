# GitHub Pages Setup Complete! 🚀

Your FTBC Wiki is now ready to be published on GitHub Pages!

## What was created:

- **`docs/index.html`** - The interactive wiki site (auto-generated)
- **`docs/.nojekyll`** - Configuration for GitHub Pages
- **`generate_wiki.py`** - Script to regenerate the site when data changes

## To enable GitHub Pages:

1. Push your changes to GitHub
2. Go to your repository **Settings** → **Pages**
3. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main**
   - Folder: **/docs**
4. Click **Save**

Your site will be live at: **https://awesomesauce24.github.io/public-ftbc-data**

## When you add/update realm data:

Just run:
```bash
python generate_wiki.py
```

This updates `docs/index.html` with the latest realm information. Push to GitHub and it automatically deploys!

## Features:
- ✅ Live search across all realms and objects
- ✅ Responsive mobile design
- ✅ Beautiful gradient theme
- ✅ No backend server needed
- ✅ Instant loading (static HTML)
