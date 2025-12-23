#!/usr/bin/env python3
"""
FTBC Wiki Web Application
Full-featured web app for browsing and managing the wiki
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from pathlib import Path
import json
import sys

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


# Routes
@app.route('/')
def index():
    """Homepage - Browse realms"""
    realms = load_all_realms()
    return render_template('index.html', realms=realms)


@app.route('/realm/<realm_name>')
def view_realm(realm_name):
    """View a specific realm"""
    realms = load_all_realms()
    if realm_name not in realms:
        return "Realm not found", 404
    
    objects = realms[realm_name]
    return render_template('realm.html', realm_name=realm_name, objects=objects, realms=realms)


@app.route('/admin')
def admin():
    """Admin dashboard"""
    realms = load_all_realms()
    return render_template('admin.html', realms=realms)


@app.route('/admin/realm/<realm_name>')
def admin_realm(realm_name):
    """Admin edit realm"""
    realms = load_all_realms()
    if realm_name not in realms:
        return "Realm not found", 404
    
    objects = realms[realm_name]
    return render_template('admin_realm.html', realm_name=realm_name, objects=objects, realms=realms)


@app.route('/admin/realm/<realm_name>/edit/<int:obj_id>', methods=['GET', 'POST'])
def admin_edit_object(realm_name, obj_id):
    """Edit an object"""
    objects = load_realm(realm_name)
    
    if obj_id >= len(objects):
        return "Object not found", 404
    
    if request.method == 'POST':
        # Update object
        obj = request.get_json()
        objects[obj_id] = obj
        save_realm(realm_name, objects)
        return jsonify({'status': 'ok', 'message': 'Object updated'})
    
    obj = objects[obj_id]
    realms = load_all_realms()
    return render_template('admin_edit.html', realm_name=realm_name, obj_id=obj_id, obj=obj, realms=realms)


@app.route('/admin/realm/<realm_name>/new', methods=['GET', 'POST'])
def admin_new_object(realm_name):
    """Create new object"""
    objects = load_realm(realm_name)
    
    if request.method == 'POST':
        # Create new object
        obj = request.get_json()
        objects.append(obj)
        save_realm(realm_name, objects)
        return jsonify({'status': 'ok', 'message': 'Object created', 'id': len(objects) - 1})
    
    realms = load_all_realms()
    return render_template('admin_edit.html', realm_name=realm_name, obj_id=None, obj={}, realms=realms)


@app.route('/api/realms')
def api_realms():
    """API: Get all realms"""
    realms = load_all_realms()
    return jsonify(realms)


@app.route('/api/realm/<realm_name>')
def api_realm(realm_name):
    """API: Get realm objects"""
    objects = load_realm(realm_name)
    return jsonify(objects)


if __name__ == '__main__':
    if not REALMS_PATH.exists():
        print(f"Error: Realms directory not found at {REALMS_PATH}")
        sys.exit(1)
    
    app.run(debug=True, port=5000)
