#!/usr/bin/env python3
"""
PyWikiBot script for FTBC Wiki
"""

import os
from dotenv import load_dotenv
import pywikibot
from pywikibot import pagegenerators, textlib

# Load environment variables from .env file
load_dotenv()

# Initialize site
def init_site():
    """Initialize connection to wiki site"""
    username = os.getenv('WIKI_USERNAME')
    password = os.getenv('WIKI_PASSWORD')
    
    site = pywikibot.Site('en', 'ftbc')  # Adjust namespace as needed
    
    if username and password:
        site.login(username, password)
        print(f"Logged in as: {username}")
    
    return site

def edit_page(site, title, text, summary):
    """Edit a wiki page"""
    page = pywikibot.Page(site, title)
    page.text = text
    page.save(summary=summary)
    print(f"Edited: {title}")

def create_page(site, title, text, summary):
    """Create a new wiki page"""
    page = pywikibot.Page(site, title)
    if page.exists():
        print(f"Page already exists: {title}")
        return False
    page.text = text
    page.save(summary=summary)
    print(f"Created: {title}")
    return True

def get_page_content(site, title):
    """Get content of a wiki page"""
    page = pywikibot.Page(site, title)
    if page.exists():
        return page.text
    else:
        print(f"Page not found: {title}")
        return None

def main():
    """Main function"""
    site = init_site()
    print(f"Connected to wiki: {site}")
    
    # Example: Get a page
    # content = get_page_content(site, "Main Page")
    # print(content)

if __name__ == "__main__":
    main()
