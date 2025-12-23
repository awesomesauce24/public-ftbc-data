#!/usr/bin/env python3
"""
FTBC Wiki Page Creator & Publisher
Web app for creating and publishing wiki pages to GitHub Pages
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pathlib import Path
import json
import sys
import subprocess

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'ftbc-wiki-secret-2025'

# Get paths
PROJECT_ROOT = Path(__file__).parent.parent
REALMS_PATH = PROJECT_ROOT / 'data' / 'realms'


def load_all_realms():
    """Load all realm data"""
    realms = {}
    for realm_dir in sorted(REALMS_PATH.iterdir()):
        if realm_dir.is_dir() and realm_dir.name != '.cache':
            json_file = realm_dir / f"{realm_dir.name}.json"
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        realms[realm_dir.name] = json.load(f)
                except:
                    pass
    return realms


def load_realm(realm_name):
    """Load a specific realm"""
    json_file = REALMS_PATH / realm_name / f"{realm_name}.json"
    if json_file.exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []


def save_realm(realm_name, objects):
    """Save realm data"""
    json_file = REALMS_PATH / realm_name / f"{realm_name}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(objects, f, indent=2, ensure_ascii=False)


def publish_wiki():
    """Run the wiki generator"""
    try:
        result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / 'generate_wiki.py')],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


# Routes
@app.route('/')
def index():
    """Homepage - Create wiki pages"""
    realms = load_all_realms()
    return render_template('index.html', realms=realms)


@app.route('/create/<realm_name>')
def create_object(realm_name):
    """Create new object page"""
    realms = load_all_realms()
    if realm_name not in realms:
        return "Realm not found", 404
    return render_template('create.html', realm_name=realm_name, realms=realms)


@app.route('/edit/<realm_name>/<int:obj_id>')
def edit_object(realm_name, obj_id):
    """Edit object page"""
    objects = load_realm(realm_name)
    
    if obj_id >= len(objects):
        return "Object not found", 404
    
    realms = load_all_realms()
    obj = objects[obj_id]
    return render_template('edit.html', realm_name=realm_name, obj_id=obj_id, obj=obj, realms=realms)


@app.route('/api/realm/<realm_name>/object', methods=['POST'])
def api_save_object(realm_name):
    """API: Save or create object"""
    objects = load_realm(realm_name)
    data = request.get_json()
    
    obj_id = data.get('id')
    if obj_id is not None and obj_id < len(objects):
        # Update existing
        objects[obj_id] = data
    else:
        # Create new
        objects.append(data)
    
    save_realm(realm_name, objects)
    return jsonify({'status': 'ok', 'message': 'Page saved'})


@app.route('/api/publish', methods=['POST'])
def api_publish():
    """API: Publish wiki to GitHub Pages"""
    success, output = publish_wiki()
    return jsonify({
        'status': 'ok' if success else 'error',
        'message': output,
        'url': 'https://awesomesauce24.github.io/public-ftbc-data/'
    })


if __name__ == '__main__':
    if not REALMS_PATH.exists():
        print(f"Error: Realms directory not found at {REALMS_PATH}")
        sys.exit(1)
    
    app.run(debug=True, port=5000)
