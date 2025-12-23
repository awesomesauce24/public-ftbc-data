#!/usr/bin/env python3
"""
FTBC Wiki Web Application
Flask-based web UI for creating and publishing wiki pages
"""

from flask import Flask, render_template, request, jsonify
from pathlib import Path
import sys
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.config import Config
from core.loader import RealmLoader
from generators import ObjectPageGenerator
from difflib import SequenceMatcher

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# Initialize realm loader
realm_loader = RealmLoader(Path(Config.REALMS_PATH))


def fuzzy_match_objects(query: str, objects: list) -> list:
    """Find objects matching query with fuzzy matching"""
    matches = []
    for obj in objects:
        name = obj.get('ObjectName', '')
        if name.lower() == query.lower():
            return [obj]  # Exact match
        
        similarity = SequenceMatcher(None, name.lower(), query.lower()).ratio()
        if similarity > 0.6:
            matches.append((similarity, obj))
    
    matches.sort(reverse=True, key=lambda x: x[0])
    return [obj for _, obj in matches]


def normalize_difficulty(difficulty_str: str) -> str:
    """Normalize difficulty strings from JSON to wiki standard"""
    mapping = {
        'effortless': 'Common',
        'easy': 'Uncommon',
        'moderate': 'Uncommon+',
        'normal': 'Medium',
        'intermediate': 'Medium+',
        'hard': 'Hard',
        'difficult': 'Hard+',
        'extreme': 'Harder',
        'unforgiving': 'Harder+',
        'insane': 'Very Hard',
        'dreadful': 'Very Hard+',
        'terrifying': 'Deadly',
        'arduous': 'Dreadful',
        'strenuous': 'Dreadful+',
        'remorseless': 'Insane',
        'horrifying': 'Impossible',
    }
    
    normalized = difficulty_str.lower().strip()
    return mapping.get(normalized, difficulty_str)


@app.route('/')
def index():
    """Home page"""
    realms = sorted(Config.REALMS_INFO.keys())
    return render_template('index.html', realms=realms)


@app.route('/api/realms')
def api_realms():
    """Get all realms"""
    try:
        realms = sorted(Config.REALMS_INFO.keys())
        return jsonify(realms)
    except Exception as e:
        return jsonify({'error': f'Failed to load realms: {str(e)}'}), 500


@app.route('/api/realm/<realm_name>/objects')
def api_realm_objects(realm_name):
    """Get objects for a realm"""
    try:
        print(f'[DEBUG] Loading objects for realm: {realm_name}')
        realm_data = realm_loader.get_realm_data(realm_name)
        
        if not realm_data:
            print(f'[DEBUG] Realm data is empty for: {realm_name}')
            print(f'[DEBUG] Realms path: {realm_loader.realms_path}')
            print(f'[DEBUG] Available realms: {realm_loader.get_all_realms()}')
            return jsonify({'error': f'Realm "{realm_name}" not found. Make sure the realm JSON file exists.'}), 404
        
        # Realm data is a list of objects, not a dict with 'Objects' key
        objects = realm_data if isinstance(realm_data, list) else realm_data.get('Objects', [])
        
        if not objects:
            print(f'[DEBUG] No objects in realm data for: {realm_name}')
            return jsonify({'error': f'No objects found in realm "{realm_name}"'}), 404
        
        # Return basic info for each object
        result = []
        for idx, obj in enumerate(objects, 1):
            result.append({
                'id': idx,
                'name': obj.get('ObjectName', 'Unknown'),
                'difficulty': obj.get('Difficulty', 'Unknown'),
                'description': obj.get('Description', '')
            })
        
        print(f'[DEBUG] Successfully loaded {len(result)} objects for realm: {realm_name}')
        return jsonify(result)
    except Exception as e:
        print(f'[ERROR] Exception loading objects for {realm_name}: {str(e)}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error loading objects: {str(e)}'}), 500


@app.route('/api/object/<realm_name>/<int:obj_id>')
def api_object(realm_name, obj_id):
    """Get object details"""
    try:
        realm_data = realm_loader.get_realm_data(realm_name)
        
        if not realm_data:
            return jsonify({'error': f'Realm "{realm_name}" not found'}), 404
        
        # Realm data is a list of objects
        objects = realm_data if isinstance(realm_data, list) else realm_data.get('Objects', [])
        
        if not objects:
            return jsonify({'error': f'No objects in realm "{realm_name}"'}), 404
        
        if 0 < obj_id <= len(objects):
            obj = objects[obj_id - 1]
            return jsonify({
                'id': obj_id,
                'name': obj.get('ObjectName', ''),
                'difficulty': normalize_difficulty(obj.get('Difficulty', '')),
                'description': obj.get('Description', ''),
                'hint': obj.get('Description', ''),
                'section': obj.get('Section', ''),
                'area': realm_name,  # Auto-detect from realm name
                'obtaining': obj.get('Obtaining', ''),
                'image': obj.get('Image', ''),
                'old_image': obj.get('OldImage', ''),
                'previous_difficulties': obj.get('PreviousDifficulties', '')
            })
        
        return jsonify({'error': f'Object ID {obj_id} not found in realm "{realm_name}"'}), 404
    except Exception as e:
        return jsonify({'error': f'Error loading object: {str(e)}'}), 500


@app.route('/api/object/search/<realm_name>/<query>')
def api_object_search(realm_name, query):
    """Search for objects by name"""
    try:
        realm_data = realm_loader.get_realm_data(realm_name)
        
        if not realm_data:
            return jsonify({'error': f'Realm "{realm_name}" not found'}), 404
        
        # Realm data is a list of objects
        objects = realm_data if isinstance(realm_data, list) else realm_data.get('Objects', [])
        
        if not objects:
            return jsonify([])  # Empty array, not error
        
        matches = fuzzy_match_objects(query, objects)
        
        result = []
        for idx, obj in enumerate(objects, 1):
            if obj in matches:
                result.append({
                    'id': idx,
                    'name': obj.get('ObjectName', ''),
                    'difficulty': obj.get('Difficulty', '')
                })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Error searching objects: {str(e)}'}), 500


@app.route('/editor')
def editor():
    """Editor page"""
    realms = sorted(Config.REALMS_INFO.keys())
    return render_template('editor.html', realms=realms)


@app.route('/api/generate-markup', methods=['POST'])
def api_generate_markup():
    """Generate wiki markup from form data"""
    try:
        data = request.json
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract form data
        realm = data.get('realm', '')
        obj_name = data.get('name', '')
        difficulty = data.get('difficulty', '')
        area = data.get('area', realm)
        hint = data.get('hint', '')
        info = data.get('info', '')
        obtaining = data.get('obtaining', '')
        image = data.get('image', f'{obj_name}.png')
        old_image = data.get('old_image', '')
        previous_difficulties = data.get('previous_difficulties', '')
        
        if not obj_name:
            return jsonify({'error': 'Object name is required'}), 400
        
        # Generate markup
        markup = ObjectPageGenerator.generate_wiki_markup(
            obj_name,
            difficulty,
            area,
            hint,
            info,
            obtaining,
            image=image,
            old_image=old_image,
            previous_difficulties=previous_difficulties
        )
        
        return jsonify({'markup': markup})
    except Exception as e:
        return jsonify({'error': f'Error generating markup: {str(e)}'}), 500


@app.route('/api/save-page', methods=['POST'])
def api_save_page():
    """Save page locally"""
    try:
        data = request.json
        realm = data.get('realm', '')
        obj_name = data.get('name', '')
        
        # Create page data
        page_data = {
            'object': {
                'name': obj_name,
                'difficulty': data.get('difficulty', ''),
                'info': data.get('info', ''),
                'obtaining': data.get('obtaining', ''),
                'image': data.get('image', ''),
                'oldImage': data.get('old_image', ''),
                'previousDifficulties': data.get('previous_difficulties', '')
            },
            'wiki_markup': data.get('markup', '')
        }
        
        # Save to file
        cache_dir = Path(Config.REALMS_PATH) / realm / "objects"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        page_file = cache_dir / f"{obj_name}.json"
        
        with open(page_file, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({'success': True, 'path': str(page_file)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    import os
    debug = os.getenv('FLASK_ENV') == 'development'
    port = int(os.getenv('PORT', 5000))
    
    print("FTBC Wiki Web Application")
    print("=" * 40)
    if debug:
        print(f"Starting server at http://localhost:{port}")
    else:
        print("Running in production mode")
    print("Press Ctrl+C to stop")
    print("=" * 40)
    
    app.run(debug=debug, host='0.0.0.0', port=port)
