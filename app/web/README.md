# FTBC Wiki Web Application

A modern web-based interface for creating and managing FTBC wiki pages.

## Quick Start

### 1. Install Dependencies

Make sure Flask is installed:

```bash
pip install flask
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

### 2. Start the Server

Navigate to the wiki directory and run:

```bash
cd wiki/web
python app.py
```

Or from the project root:

```bash
python wiki/web/app.py
```

### 3. Open in Browser

Once you see "Starting server at http://localhost:5000", open your browser and go to:

```
http://localhost:5000
```

## Features

### Home Page (`/`)
- Welcome overview
- Feature highlights
- Quick links to editor
- Documentation access

### Editor (`/editor`)
- **Realm Selection**: Choose from 15 realms
- **Object Search**: Fuzzy matching to find objects by name
- **Form Fields**:
  - Object name, difficulty level
  - Area/subrealm (auto-detects from JSON)
  - Description and obtaining instructions
  - Image filenames (current and old)
  - Previous difficulty levels
- **Live Preview**: Shows exact wiki markup in real-time
- **Actions**:
  - Generate preview (Ctrl+P)
  - Copy markup to clipboard
  - Save page locally as JSON
  - Download as text file
  - Publish to wiki (coming soon)

## API Endpoints

### Realms
- `GET /api/realms` - List all available realms

### Objects
- `GET /api/realm/<realm>/objects` - List objects in realm
- `GET /api/object/<realm>/<id>` - Get full object details
- `GET /api/object/search/<realm>/<query>` - Fuzzy search objects

### Markup Generation
- `POST /api/generate-markup` - Generate wiki markup from form data
- `POST /api/save-page` - Save page locally as JSON

## File Structure

```
wiki/web/
├── app.py                  # Main Flask application
├── templates/
│   ├── index.html         # Home page
│   └── editor.html        # Editor interface
└── static/
    ├── css/
    │   └── style.css      # Styling (modern gradients, responsive)
    └── js/
        └── editor.js      # Client-side logic (form handling, API calls)
```

## Keyboard Shortcuts

- **Ctrl+S** (or Cmd+S): Save page
- **Ctrl+P** (or Cmd+P): Generate preview
- **Ctrl+C**: Copy markup after generating preview

## Frontend Features

### Auto-save Draft
- Saves form state to browser localStorage every 30 seconds
- Recovers draft on page reload
- Useful if browser crashes

### Fuzzy Search
- Type partial object names
- Intelligent matching finds similar names
- Minimum 60% similarity threshold

### Responsive Design
- Works on desktop, tablet, and mobile
- Single-column layout on small screens
- Grid layout on large screens (form + preview side-by-side)

## Backend Integration

The web app integrates with the existing wiki system:

- Uses `Config` from `wiki/core/config.py` for realm info
- Uses `load_realm_objects()` from `wiki/core/loader.py` to load objects
- Uses `ObjectPageGenerator` from `wiki/generators/` for wiki markup
- Saves pages to the same format as CLI version

## Development

### Enable Debug Mode
Flask runs in debug mode by default. Changes to templates/CSS/JS are reflected immediately.

### Customize Styling
Edit `wiki/web/static/css/style.css` to modify:
- Color scheme
- Layout dimensions
- Font sizes
- Component styles

### Modify JavaScript
Edit `wiki/web/static/js/editor.js` to:
- Add form validation
- Change preview behavior
- Add new API calls
- Implement new features

## Production Deployment

For production, use a WSGI server:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wiki.web.app:app
```

Or with Waitress:

```bash
pip install waitress
waitress-serve --port=5000 wiki.web.app:app
```

## Troubleshooting

### Port Already in Use
Change the port in app.py:
```python
app.run(debug=True, port=8000)  # Use port 8000 instead
```

### Template Not Found
Make sure you're running the app from the correct directory:
```bash
cd wiki/web
python app.py
```

### API Returns 404
Check that realm names match exactly (case-sensitive).
List all realms: `curl http://localhost:5000/api/realms`

### Styles Not Loading
Clear browser cache (Ctrl+Shift+Delete) and refresh the page.

## Future Enhancements

- [ ] Direct wiki publishing with bot account
- [ ] Image upload and preview
- [ ] Batch object editing
- [ ] Revision history
- [ ] Collaborative editing
- [ ] Dark mode toggle
- [ ] Advanced search filters
- [ ] Page templates
- [ ] Wiki diff viewer

## Support

For issues or questions, refer to the main [documentation](../docs/README.md).
