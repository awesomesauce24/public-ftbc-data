#!/usr/bin/env python3
from scripts.create_pages import *
from pathlib import Path

# Simulate Dango creation
obj_file, realm, location = find_object('Dango')
obj_data = json.load(open(obj_file))

difficulty = obj_data['difficulty']
diff_icon, diff_hex, difficulty_proper, difficulty_priority = get_difficulty_info(difficulty)
gradient, accent, bg_image = get_realm_gradient(realm)
special_case = {}

# Generate wiki markup
image_filename = "Dango.png"
gallery_markup = f"[[File:{image_filename}]]"
has_old_image = False

info = "a beloved Japanese sweet dumpling."
obtaining = "Check ontop of the crane, where you can find [[Bandy]]."

prev_diff_markup = ""
categories = [
    f"[[Category:{difficulty_proper} Objects]]",
    "[[Category:Objects]]",
    f"[[Category:{realm} Objects]]",
]

# Build obtaining section (no collapsible for Extreme)
if difficulty_priority >= 11:
    obtaining_markup = f"""== Obtaining ==
'''''The following text will show instructions on how to get this object. If you wish to find it by yourself, avoid opening the text.'''''
<div class="mw-collapsible mw-collapsed" style="width:100%">
<div class="mw-collapsible-content">
{obtaining}
</div>
</div>"""
else:
    obtaining_markup = f"""== Obtaining ==
{obtaining}"""

static_overlay = ""

wiki_markup = f"""{static_overlay}<div align="center" style="position:fixed; z-index:-1; top:0; left:0; right:0; bottom:0;">
[[File:{bg_image}|2000px]]
</div>
<div style="--theme-accent-color:{gradient}; --theme-accent-label-color:{accent};">
<div style="position:relative; z-index:1;">

{{{{CharacterInfo
|name=Dango
|character={gallery_markup}
|difficulty=[[File:{diff_icon}|link=]] <span style="color:{diff_hex}">'''<b>{difficulty_proper}</b>'''</span>
|area=[[{realm}]]
|hint={obj_data['description']}{prev_diff_markup}
}}}}

== Info ==
{info}

{obtaining_markup}

{chr(10).join(categories)}
</div>
</div>"""

print(wiki_markup)
