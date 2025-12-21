"""
Core modules for FTBC Wiki Bot
Contains authentication, scraping, and formatting utilities
"""

from .authenticate import authenticate
from .bot import init_site, edit_page, create_page, get_page_content
from .scrapers import scrape_realms, get_page_html, extract_gallery_items
from .object_formatter import (
    create_object_template,
    format_from_dict,
    create_object_with_autofill,
    check_page_exists,
    format_wiki_page_name
)

__all__ = [
    'authenticate',
    'init_site',
    'edit_page',
    'create_page',
    'get_page_content',
    'scrape_realms',
    'get_page_html',
    'extract_gallery_items',
    'create_object_template',
    'format_from_dict',
    'create_object_with_autofill',
    'check_page_exists',
    'format_wiki_page_name'
]
