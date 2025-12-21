#!/usr/bin/env python3
"""
Object formatter for wiki pages
Converts object data to wiki page format
"""

import json
import os
import requests

def load_realm_config():
    """Load realm configuration from JSON template"""
    template_path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'object_template.json')
    try:
        with open(template_path, 'r') as f:
            data = json.load(f)
        return data.get('realms', {})
    except FileNotFoundError:
        print(f"Template file not found at {template_path}")
        return {}

def format_wiki_page_name(name):
    """Format object name to wiki page format (spaces to underscores)"""
    return name.replace(" ", "_")

def check_page_exists(page_name, wiki_url="https://ftbc.fandom.com"):
    """Check if a wiki page already exists"""
    try:
        # Format page name for URL
        formatted_name = format_wiki_page_name(page_name)
        url = f"{wiki_url}/wiki/{formatted_name}"
        
        # Use a simple GET request and check for 404 in response
        response = requests.get(url, timeout=10, allow_redirects=True)
        
        # Status 200-299 means page exists, 404 means it doesn't
        if response.status_code == 404:
            return False
        elif 200 <= response.status_code < 300:
            return True
        else:
            # Other status codes - assume it exists
            return True
    except requests.exceptions.Timeout:
        print("⚠ Request timed out checking page")
        return None
    except requests.exceptions.RequestException as e:
        print(f"⚠ Error checking page: {e}")
        return None
    except Exception as e:
        print(f"⚠ Unexpected error checking page: {e}")
        return None

def get_realm_folder_name(realm_name):
    """Convert realm display name to folder name"""
    folder_mapping = {
        'Main Realm': 'Main Realm',
        'Inverted Realm': 'InvertedRealm',
        'Yoyleland': 'Yoyleland',
        'Backrooms': 'Backrooms',
        'Yoyle Factory': 'YoyleFactory',
        'Classic Paradise': 'ClassicParadise',
        'Evil Forest': 'EvilForest',
        'Cherry Grove': 'CherryGrove',
        'Barren Desert': 'BarrenDesert',
        'Frozen World': 'FrozenWorld',
        'Timber Peaks': 'TimberPeaks',
        'Midnight Rooftops': 'MidnightRooftops',
        'Magma Canyon': 'MagmaCanyon',
        'Sakura Serenity': 'SakuraSerenity',
        'Polluted Marshlands': 'PollutedMarshlands',
    }
    return folder_mapping.get(realm_name, realm_name)

def load_realm_data(realm_name):
    """Load realm data from .json file"""
    folder_name = get_realm_folder_name(realm_name)
    
    # Try the mapped name first
    realm_path = os.path.join(
        os.path.dirname(__file__),
        '..', '..',
        'Realms',
        f'{folder_name}.json'
    )
    
    try:
        with open(realm_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        pass
    
    # Try the realm name directly (in case it has spaces)
    realm_path_alt = os.path.join(
        os.path.dirname(__file__),
        '..', '..',
        'Realms',
        f'{realm_name}.json'
    )
    
    try:
        with open(realm_path_alt, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"DEBUG: File not found at {realm_path} or {realm_path_alt}")
        return None

def extract_object_area(realm_name, object_name):
    """Extract area for object from realm JSON file (Main Realm)"""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            area = obj.get('Area')
            if area and area.lower() != 'unknown':
                return area
    
    return None

def extract_object_section(realm_name, object_name):
    """Extract section for object from realm JSON file (Yoyle Factory)"""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            section = obj.get('Section')
            if section:
                return section
    
    return None

def extract_object_level(realm_name, object_name):
    """Extract level for object from realm JSON file (Backrooms)"""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            level = obj.get('Level')
            if level:
                return level
    
    return None

def extract_object_hint(realm_name, object_name):
    """Extract hint for object from realm JSON file"""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            return obj.get('Description', None)
    
    return None

def extract_object_difficulty(realm_name, object_name):
    """Extract difficulty for object from realm JSON file. Returns formatted string."""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            difficulty_raw = obj.get('Difficulty', '')
            # Map raw difficulty to wiki format with color
            difficulty_map = {
                'effortless': ('Effortless', '#17a897'),
                'easy': ('Easy', '#10da8d'),
                'moderate': ('Moderate', '#07fc55'),
                'normal': ('Normal', '#a1ff27'),
                'intermediate': ('Intermediate', '#ffb700'),
                'hard': ('Hard', '#FF7700'),
                'difficult': ('Difficult', '#f54f25'),
                'extreme': ('Extreme', '#ed2727'),
                'unforgiving': ('Unforgiving', '#ff143f'),
                'insane': ('Insane', '#ff1c95'),
                'dreadful': ('Dreadful', '#db25ff'),
                'terrifying': ('Terrifying', '#8b17ff'),
                'arduous': ('Arduous', '#5d0cff'),
                'strenuous': ('Strenuous', '#4048e5'),
                'remorseless': ('Remorseless', '#2084ff'),
                'horrifying': ('Horrifying', '#2bd0fd'),
                'impossible': ('IMPOSSIBLE', '#000000'),
                'medal': ('Medal', '#331900'),
                'medallion': ('Medallion', '#331900'),
                'event': ('Event', '#df81c2'),
            }
            
            difficulty_lower = difficulty_raw.lower()
            if difficulty_lower in difficulty_map:
                name, color = difficulty_map[difficulty_lower]
                return f'[[File:{name}.png|link=]] <span style="color:{color}">\'\'\'<b>{name}</b>\'\'\'</span>'
    
    return None

def extract_difficulty_name(realm_name, object_name):
    """Extract just the difficulty name (without formatting) for use in categories"""
    realm_data = load_realm_data(realm_name)
    if not realm_data or not isinstance(realm_data, list):
        return None
    
    # Search for object in realm data
    for obj in realm_data:
        if obj.get('ObjectName') == object_name:
            difficulty_raw = obj.get('Difficulty', '')
            difficulty_map = {
                'effortless': 'Effortless',
                'easy': 'Easy',
                'moderate': 'Moderate',
                'normal': 'Normal',
                'intermediate': 'Intermediate',
                'hard': 'Hard',
                'difficult': 'Difficult',
                'extreme': 'Extreme',
                'unforgiving': 'Unforgiving',
                'insane': 'Insane',
                'dreadful': 'Dreadful',
                'terrifying': 'Terrifying',
                'arduous': 'Arduous',
                'strenuous': 'Strenuous',
                'remorseless': 'Remorseless',
                'horrifying': 'Horrifying',
                'impossible': 'IMPOSSIBLE',
                'medal': 'Medal',
                'medallion': 'Medallion',
                'event': 'Event',
            }
            
            difficulty_lower = difficulty_raw.lower()
            if difficulty_lower in difficulty_map:
                return difficulty_map[difficulty_lower]
    
    return None


def get_realm_config(realm_name):
    """Get configuration for a realm"""
    configs = load_realm_config()
    return configs.get(realm_name, {})

def get_area_for_realm(realm_name):
    """Get the main area name for a realm"""
    area_mapping = {
        'Main Realm': 'Main Realm',
        'Yoyle Factory': 'Yoyle Factory',
        'Backrooms': 'Backrooms',
        'Inverted Realm': 'Inverted',
        'Yoyleland': 'Yoyleland',
        'Classic Paradise': 'Classic Paradise',
        'Evil Forest': 'Evil Forest',
        'Cherry Grove': 'Cherry Grove',
        'Barren Desert': 'Barren Desert',
        'Frozen World': 'Frozen World',
        'Timber Peaks': 'Timber Peaks',
        'Midnight Rooftops': 'Midnight Rooftops',
        'Magma Canyon': 'Magma Canyon',
        'Sakura Serenity': 'Sakura Serenity',
        'Polluted Marshlands': 'Polluted Marshlands',
    }
    return area_mapping.get(realm_name, realm_name)

def format_character_info(name, character_images=None, difficulty=None, area=None, 
                         hint=None, previous_difficulties=None, info=None, 
                         obtaining=None, trivia=None, realm=None, categories=None):
    """
    Format a character/object for wiki page
    
    Args:
        name: Object name
        character_images: List of image tuples (filename, caption)
        difficulty: Difficulty level with icon
        area: Area location link
        hint: Hint text
        previous_difficulties: List of previous difficulties
        info: General info section
        obtaining: How to obtain
        trivia: Trivia list
        realm: Realm name
        categories: List of categories
    
    Returns:
        Formatted wiki page string
    """
    
    # Get realm background and theme colors from config
    realm_config = get_realm_config(realm)
    bg_file = realm_config.get('background_file', f'{realm} Sky.webp')
    theme_color = realm_config.get('theme_accent_color', '-webkit-linear-gradient(#23bd1c,#188a13)')
    label_color = realm_config.get('theme_accent_label_color', '#ffffff')
    
    bg_line = '[[File:{{{File|' + bg_file + '}}}|{{{Size|2000px}}}]]'
    
    # Build character image gallery
    character_line = ''
    if character_images:
        if len(character_images) == 1:
            filename, caption = character_images[0]
            character_line = f'[[File:{filename}]]'
        else:
            character_line = '<gallery>\n'
            for filename, caption in character_images:
                if caption:
                    character_line += f'{filename}|{caption}\n'
                else:
                    character_line += f'{filename}\n'
            character_line += '</gallery>'
    
    # Build the CharacterInfo template with proper formatting
    page = f'''<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;"> {bg_line} </div>
<div style="--theme-accent-color:{theme_color}; --theme-accent-label-color:{label_color};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo|name={name}
|character=<gallery>
{chr(10).join([f"{filename}|{caption}" if caption else filename for filename, caption in (character_images or [])])}
</gallery>
|difficulty={difficulty if difficulty else ""}
|area=[[{area if area else ""}]]
|hint={hint if hint else ""}'''
    
    # Add previous difficulties if provided
    if previous_difficulties:
        page += '\n|previousdifficulties = \n'
        page += '\n'.join(previous_difficulties)
    
    page += '\n}}'
    
    # Add Info section if provided
    if info:
        page += f'''
==Info==
{info}
'''
    
    # Add Obtaining section if provided
    if obtaining:
        # Check if difficulty is Dreadful or above (requires collapsible format)
        high_difficulty_list = ['Dreadful', 'Terrifying', 'Arduous', 'Strenuous', 'Remorseless', 'Horrifying']
        difficulty_name = extract_difficulty_name(realm, name) if realm and name else None
        
        # If we couldn't get difficulty from realm data, try parsing from formatted difficulty string
        if not difficulty_name and difficulty:
            for high_diff in high_difficulty_list:
                if high_diff.lower() in difficulty.lower():
                    difficulty_name = high_diff
                    break
        
        if difficulty_name in high_difficulty_list:
            # Use collapsible format for high difficulty objects
            page += f'''
==Obtaining==
'''
            page += "''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.''\n"
            page += '<div class="mw-collapsible mw-collapsed" style="width:100%">\n'
            page += '<div class="mw-collapsible-content">\n'
            page += f'{obtaining}\n'
            page += '</div>\n'
            page += '</div>\n'
        else:
            # Standard format for lower difficulty objects
            page += f'''
==Obtaining==
{obtaining}
'''
    
    # Add Trivia section if provided
    if trivia:
        page += f'''
==Trivia==
{chr(10).join([f"*{t}" for t in trivia])}
'''
    
    # Add categories
    if categories:
        for cat in categories:
            page += f"\n[[Category:{cat}]]"
    
    page += "\n\n</div>\n</div>"
    
    return page


def create_object_template():
    """Load and return the object template from JSON"""
    template_path = os.path.join(os.path.dirname(__file__), 'object_template.json')
    try:
        with open(template_path, 'r') as f:
            template = json.load(f)
        return template
    except FileNotFoundError:
        print(f"Template file not found at {template_path}")
        return {}


def format_from_dict(obj_data):
    """Format object from dictionary"""
    # Convert character_images from dict format to tuple format if needed
    character_images = obj_data.get('character_images')
    if character_images and isinstance(character_images[0], dict):
        character_images = [(img['filename'], img['caption']) for img in character_images]
    
    return format_character_info(
        name=obj_data.get('name', 'Unknown'),
        character_images=character_images,
        difficulty=obj_data.get('difficulty'),
        area=obj_data.get('area'),
        hint=obj_data.get('hint'),
        previous_difficulties=obj_data.get('previous_difficulties'),
        info=obj_data.get('info'),
        obtaining=obj_data.get('obtaining'),
        trivia=obj_data.get('trivia'),
        realm=obj_data.get('realm'),
        categories=obj_data.get('categories')
    )

def create_object_with_autofill(name, realm_name, character_images=None, 
                               info=None, obtaining=None, trivia=None, 
                               previous_difficulties=None, categories=None):
    """Create an object with auto-populated fields from realm data"""
    
    # Auto-populate realm
    realm = realm_name
    
    # Try to get specific area/section/level from object data, fall back to realm name
    area = None
    
    # Check for Yoyle Factory section
    if 'Yoyle Factory' in realm_name:
        area = extract_object_section(realm_name, name)
    # Check for Backrooms level
    elif 'Backrooms' in realm_name:
        area = extract_object_level(realm_name, name)
    # Check for Main Realm area
    else:
        area = extract_object_area(realm_name, name)
    
    # Fall back to realm name if no specific location found
    if not area:
        area = get_area_for_realm(realm_name)
    
    # Extract hint from realm .txt file
    hint = extract_object_hint(realm_name, name)
    if not hint:
        hint = f"Object in {realm_name}"
    
    # Extract difficulty from realm .txt file
    difficulty = extract_object_difficulty(realm_name, name)
    if not difficulty:
        difficulty = '[[File:Effortless.png]] <span style="color:#17a897">\'\'\'<b>Effortless</b>\'\'\'</span>'
    
    # Extract difficulty name for auto-categories
    difficulty_name = extract_difficulty_name(realm_name, name)
    
    # Build categories - always include realm category
    final_categories = []
    
    # If no user-provided categories, auto-populate with difficulty and Objects
    if not categories:
        if difficulty_name:
            final_categories.append(f'{difficulty_name} Objects')
        final_categories.append('Objects')
    else:
        final_categories.extend(categories)
    
    # Always include realm category
    final_categories.append(f'{realm_name} Objects')
    
    # Create object data
    obj_data = {
        'name': name,
        'character_images': character_images or [],
        'difficulty': difficulty,
        'area': area,
        'hint': hint,
        'previous_difficulties': previous_difficulties or [],
        'info': info or f"Character from {realm_name}",
        'obtaining': obtaining or f"Found in {realm_name}",
        'trivia': trivia or [],
        'realm': realm,
        'categories': final_categories
    }
    
    return format_from_dict(obj_data)
