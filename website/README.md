# FTBC Wiki Website

A full-featured Flask web application for browsing and managing the FTBC Wiki.

## Features

- 🌐 **Browse Wiki** - View all realms and objects in a beautiful interface
- ✏️ **Admin Dashboard** - Edit and create objects directly in the browser
- 🔍 **Search** - Quickly find realms and objects
- 📱 **Responsive** - Works on desktop, tablet, and mobile

## Running the Website

1. Install Flask (if not already installed):
```bash
pip install Flask
```

2. Run the app:
```bash
python website/app.py
```

3. Open in your browser:
```
http://localhost:5000
```

## Pages

- **`/`** - Homepage/Browse all realms
- **`/realm/<name>`** - View specific realm
- **`/admin`** - Admin dashboard
- **`/admin/realm/<name>`** - Edit realm objects
- **`/admin/realm/<name>/edit/<id>`** - Edit specific object
- **`/admin/realm/<name>/new`** - Create new object

## API Endpoints

- **`/api/realms`** - Get all realms (JSON)
- **`/api/realm/<name>`** - Get realm objects (JSON)

## Publishing

After editing objects in the web interface:
1. Changes are saved to your realm JSON files
2. Run the `publish` command in the CLI app to update GitHub Pages
3. Or use the admin dashboard "Publish" button for instructions

## File Structure

```
website/
├── app.py              # Flask application
├── templates/          # HTML templates
│   ├── base.html       # Base template
│   ├── index.html      # Homepage
│   ├── realm.html      # View realm
│   ├── admin.html      # Admin dashboard
│   ├── admin_realm.html    # Edit realm
│   └── admin_edit.html     # Edit object
└── static/
    └── style.css       # Stylesheet
```
