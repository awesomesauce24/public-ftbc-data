"""
Template files for FTBC Wiki Bot
"""

import json
import os

def load_object_template():
    """Load the object template JSON"""
    template_path = os.path.join(os.path.dirname(__file__), 'object_template.json')
    with open(template_path, 'r', encoding='utf-8') as f:
        return json.load(f)

__all__ = ['load_object_template']
