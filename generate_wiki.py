#!/usr/bin/env python3
"""
Generate GitHub Pages site from realm data
Run this script to update the wiki HTML with the latest realm data
"""

import json
import os
from pathlib import Path


def escape_html(text):
    """Escape HTML special characters"""
    replacements = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def load_realms(realms_path):
    """Load all realm data from JSON files"""
    realms = {}
    for realm_dir in sorted(realms_path.iterdir()):
        if realm_dir.is_dir() and realm_dir.name != '.cache':
            json_file = realm_dir / f"{realm_dir.name}.json"
            if json_file.exists():
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        realms[realm_dir.name] = json.load(f)
                except Exception as e:
                    print(f"Error loading {realm_dir.name}: {e}")
    return realms


def generate_html(realms_data):
    """Generate HTML content with realm data"""
    # Convert realms dict to JavaScript object
    realms_js = json.dumps(realms_data, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FTBC Wiki - Realms & Objects</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
            animation: fadeIn 0.6s ease;
        }}

        header h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}

        header p {{
            font-size: 1.2em;
            opacity: 0.95;
        }}

        .realms-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}

        .realm-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
            cursor: pointer;
            animation: slideUp 0.5s ease;
        }}

        .realm-card:hover {{
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .realm-card h2 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 3px solid #764ba2;
            padding-bottom: 10px;
        }}

        .objects-list {{
            margin-top: 15px;
            max-height: 400px;
            overflow-y: auto;
        }}

        .object-item {{
            padding: 10px;
            margin: 8px 0;
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            transition: all 0.2s ease;
        }}

        .object-item:hover {{
            background: #e8e8ff;
            transform: translateX(5px);
        }}

        .object-name {{
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}

        .difficulty {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-right: 10px;
            margin-top: 5px;
        }}

        .difficulty.easy {{
            background: #d4edda;
            color: #155724;
        }}

        .difficulty.normal {{
            background: #fff3cd;
            color: #856404;
        }}

        .difficulty.hard {{
            background: #f8d7da;
            color: #721c24;
        }}

        .difficulty.terrifying {{
            background: #6c3483;
            color: #fff;
        }}

        .description {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
            font-style: italic;
        }}

        .object-count {{
            color: #999;
            font-size: 0.95em;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}

        footer {{
            text-align: center;
            color: white;
            margin-top: 40px;
            padding: 20px;
            opacity: 0.9;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 768px) {{
            header h1 {{
                font-size: 2em;
            }}
            .realms-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .search-box {{
            margin-bottom: 30px;
            display: flex;
            gap: 10px;
        }}

        .search-box input {{
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        .search-box input::placeholder {{
            color: #999;
        }}

        .no-results {{
            text-align: center;
            color: white;
            padding: 40px;
            font-size: 1.2em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎮 FTBC Wiki</h1>
            <p>Complete guide to realms and collectible objects</p>
        </header>

        <div class="search-box">
            <input 
                type="text" 
                id="searchInput" 
                placeholder="Search realms or objects..."
                onkeyup="filterRealms()"
            >
        </div>

        <div class="realms-grid" id="realmsContainer">
            <!-- Realms will be populated here -->
        </div>

        <div id="noResults" class="no-results" style="display:none;">
            No results found. Try a different search term.
        </div>

        <footer>
            <p>FTBC Wiki • Generated from public realm data</p>
            <p style="font-size: 0.9em; margin-top: 10px;">
                <a href="https://github.com/awesomesauce24/public-ftbc-data" style="color: white;">View on GitHub</a>
            </p>
        </footer>
    </div>

    <script>
        const realmsData = {realms_js};

        function getDifficultyColor(difficulty) {{
            return difficulty.toLowerCase();
        }}

        function renderRealms(data) {{
            const container = document.getElementById('realmsContainer');
            const noResults = document.getElementById('noResults');

            if (Object.keys(data).length === 0) {{
                container.style.display = 'none';
                noResults.style.display = 'block';
                return;
            }}

            container.style.display = 'grid';
            noResults.style.display = 'none';
            container.innerHTML = '';

            Object.entries(data).forEach(([realmName, objects]) => {{
                const card = document.createElement('div');
                card.className = 'realm-card';
                
                const objectsHtml = objects.slice(0, 5).map(obj => `
                    <div class="object-item">
                        <div class="object-name">${{escapeHtml(obj.ObjectName)}}</div>
                        <span class="difficulty ${{getDifficultyColor(obj.Difficulty)}}">
                            ${{obj.Difficulty}}
                        </span>
                        <div class="description">${{escapeHtml(obj.Description)}}</div>
                    </div>
                `).join('');

                const moreText = objects.length > 5 ? `<div class="object-count">+ ${{objects.length - 5}} more objects</div>` : '';

                card.innerHTML = `
                    <h2>${{escapeHtml(realmName)}}</h2>
                    <div class="objects-list">
                        ${{objectsHtml}}
                        ${{moreText}}
                    </div>
                    <div class="object-count">Total objects: ${{objects.length}}</div>
                `;

                container.appendChild(card);
            }});
        }}

        function filterRealms() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            if (!searchTerm) {{
                renderRealms(realmsData);
                return;
            }}

            const filtered = {{}};
            Object.entries(realmsData).forEach(([realmName, objects]) => {{
                const realmMatches = realmName.toLowerCase().includes(searchTerm);
                const objectsMatches = objects.filter(obj => 
                    obj.ObjectName.toLowerCase().includes(searchTerm) ||
                    obj.Description.toLowerCase().includes(searchTerm)
                );

                if (realmMatches || objectsMatches.length > 0) {{
                    filtered[realmName] = realmMatches ? objects : objectsMatches;
                }}
            }});

            renderRealms(filtered);
        }}

        function escapeHtml(text) {{
            const map = {{
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            }};
            return text.replace(/[&<>"']/g, m => map[m]);
        }}

        // Initial render
        renderRealms(realmsData);
    </script>
</body>
</html>"""
    
    return html


def main():
    script_dir = Path(__file__).parent
    realms_path = script_dir / 'data' / 'realms'
    docs_path = script_dir / 'docs'
    
    if not realms_path.exists():
        print(f"Error: Realms directory not found at {realms_path}")
        return
    
    docs_path.mkdir(exist_ok=True)
    
    print("Loading realms data...")
    realms_data = load_realms(realms_path)
    print(f"Found {len(realms_data)} realms")
    
    print("Generating HTML...")
    html_content = generate_html(realms_data)
    
    output_file = docs_path / 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ Generated {output_file}")
    print(f"✓ Wiki ready at https://awesomesauce24.github.io/public-ftbc-data")


if __name__ == '__main__':
    main()
