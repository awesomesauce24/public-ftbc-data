"""Generators for creating wiki-formatted output"""

from typing import Dict, Any, List
from wiki.core.config import Config
from wiki.templates import TemplateLoader


class WikiPageGenerator:
    """Generate wiki-formatted pages from data"""
    
    @staticmethod
    def generate_realm_page(realm_name: str, realm_data: Dict[str, Any], description: str = "") -> Dict[str, Any]:
        """Generate a realm page from template with data"""
        template = TemplateLoader.load_realm_template()
        
        return TemplateLoader.render(
            template,
            BACKGROUND_IMAGE=realm_data.get('background_image', 'Default.webp'),
            THEME_ACCENT_COLOR=realm_data.get('accent_color', '#ff6f00'),
            THEME_ACCENT_LABEL_COLOR=realm_data.get('accent_label_color', '#ffffff'),
            DESCRIPTION=description,
            DIFFICULTY=realm_data.get('difficulty', ''),
            OBTAINING_INSTRUCTIONS=realm_data.get('obtaining', ''),
            SUBREALM_LIST='\n'.join(realm_data.get('subrealms', [])),
            REALM=realm_name
        )
    
    @staticmethod
    def generate_object_list(objects: List[Dict[str, Any]], difficulty: str) -> str:
        """Generate wiki-formatted object list using template"""
        template = TemplateLoader.load_object_template()
        color = Config.get_color(difficulty)
        
        gallery = ""
        for obj in objects:
            if 'icon' in obj and 'name' in obj:
                gallery += f"File:{obj['icon']}|[[File:{difficulty}.png|18px]] '''{obj['name']}'''\n"
        
        return TemplateLoader.render(
            template,
            DIFFICULTY=difficulty,
            ICON=f"{difficulty}.png",
            COLOR=color,
            TOTAL=len(objects),
            OBJECT_GALLERY=gallery.strip()
        )
    
    @staticmethod
    def generate_realm_index() -> str:
        """Generate index page for all realms"""
        page = "= Realms Index =\n\n"
        page += "Complete list of realms in FTBC:\n\n"
        page += "{{Columns|2|\n"
        
        for realm in sorted(Config.REALMS_INFO.keys()):
            page += f"* [[{realm}]]\n"
        
        page += "}}\n"
        
        return page


class ObjectPageGenerator:
    """Generate object pages from template"""
    
    # Difficulty tier mappings for "Dreadful and above" spoiler detection
    ARDUOUS_AND_ABOVE = {
        "Dreadful", "Terrifying", "Arduous", "Strenuous", "Remorseless", "Horrifying", "IMPOSSIBLE"
    }
    
    # Difficulty icons (file names on wiki)
    DIFFICULTY_ICONS = {
        "Effortless": "Effortless.png",
        "Easy": "Easy.png",
        "Moderate": "Moderate.png",
        "Normal": "Normal.png",
        "Intermediate": "Intermediate.png",
        "Hard": "Hard.png",
        "Difficult": "Difficult.png",
        "Extreme": "Extreme.png",
        "Unforgiving": "Unforgiving.png",
        "Insane": "Insane.png",
        "Dreadful": "Dreadful.png",
        "Terrifying": "Terrifying.png",
        "Arduous": "Arduous.png",
        "Strenuous": "Strenuous.png",
        "Remorseless": "Remorseless.png",
        "Horrifying": "Horrifying.png",
        "IMPOSSIBLE": "IMPOSSIBLE.png",
        "Secret": "Secret.png",
    }
    
    @staticmethod
    def generate_object_page(name: str, difficulty: str, area: str, hint: str, 
                            info: str, obtaining: str, image: str = "", 
                            background: str = "") -> Dict[str, Any]:
        """Generate object page from JSON template"""
        template = TemplateLoader.load_object_template()
        theme = Config.get_realm_info(area)
        
        return TemplateLoader.render(
            template,
            OBJECT_NAME=name,
            OBJECT_IMAGE=image or f"{name}.png",
            BACKGROUND_IMAGE=background or theme.get('background', 'Default.webp'),
            DIFFICULTY=difficulty,
            THEME_ACCENT_COLOR=theme.get('accent_color', '#ff6f00'),
            THEME_ACCENT_LABEL_COLOR=theme.get('accent_label_color', '#ffffff'),
            AREA_REALM=area,
            HINT=hint,
            INFO_DESCRIPTION=info,
            OBTAINING_INSTRUCTIONS=obtaining,
            REALM=area
        )
    
    @staticmethod
    def generate_wiki_markup(name: str, difficulty: str, area: str, hint: str,
                            info: str, obtaining: str, image: str = "",
                            background: str = "", previous_difficulties: str = "") -> str:
        """Generate actual wiki markup that can be pasted directly into Fandom editor"""
        # Normalize difficulty to title case for lookups
        difficulty_normalized = difficulty.title() if difficulty.lower() != "impossible" else "IMPOSSIBLE"
        
        theme = Config.get_realm_info(area)
        difficulty_color = Config.get_color(difficulty_normalized)
        difficulty_icon = ObjectPageGenerator.DIFFICULTY_ICONS.get(difficulty_normalized, "Unknown.png")
        is_arduous_plus = difficulty_normalized in ObjectPageGenerator.ARDUOUS_AND_ABOVE
        
        # Use realm background if not specified
        if not background:
            background = theme.get('background', 'Default.webp')
        
        # Normalize image name (ensure .png extension only once)
        if not image:
            image = f"{name}.png"
        elif not image.endswith('.png'):
            image = f"{image}.png"
        
        # Build obtaining section with spoiler box for Dreadful+
        obtaining_section = ""
        if is_arduous_plus:
            obtaining_section = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">{obtaining}</div>
</div>"""
        else:
            obtaining_section = f"""== Obtaining ==
{obtaining}"""
        
        # Build previous difficulties line if provided
        previous_line = ""
        if previous_difficulties.strip():
            previous_line = f"|previousdifficulties = {previous_difficulties}\n"
        
        # Build the full wiki markup
        markup = f"""<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{background}|2000px]]
</div>
<div style="--theme-accent-color:{theme.get('accent', '#ff6f00')}; --theme-accent-label-color:{theme.get('accent_label_color', '#ffffff')};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name={name}
|character=[[File:{image}]]
|difficulty=[[File:{difficulty_icon}|link=]] <span style="color:{difficulty_color}">'''<b>{difficulty_normalized}</b>'''</span>
|area=[[{area}]]
|hint={hint}
|additionalinfo
{previous_line}}}}}

== Info ==
{info}

{obtaining_section}

[[Category:{difficulty_normalized} Objects]]
[[Category:Objects]]
[[Category:{area} Objects]]
</div>
</div>"""
        
        return markup


class MarkdownPageGenerator:
    """Generate markdown-formatted pages"""
    
    @staticmethod
    def generate_realm_md(realm_name: str, realm_data: Dict[str, Any], description: str = "") -> str:
        """Generate markdown page for a realm"""
        md = f"# {realm_name}\n\n"
        
        if description:
            md += "## Description\n"
            md += description + "\n\n"
        
        if realm_data:
            md += "## Data\n"
            md += "```json\n"
            import json
            md += json.dumps(realm_data, indent=2) + "\n"
            md += "```\n\n"
        
        return md
