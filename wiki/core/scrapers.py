#!/usr/bin/env python3
"""
Wiki scraper utilities for FTBC Wiki
Handles fetching and parsing wiki page content
"""

import requests
import re
from bs4 import BeautifulSoup

def get_page_html(session, wiki_url, page_title):
    """Fetch raw HTML of a wiki page"""
    params = {
        'action': 'parse',
        'page': page_title,
        'format': 'json'
    }
    
    try:
        response = session.get(f'{wiki_url}/api.php', params=params)
        if response.status_code != 200:
            return None
        
        data = response.json()
        if 'parse' in data:
            return data['parse']['text']['*']
        return None
    except Exception as e:
        print(f"Error fetching page: {str(e)}")
        return None

def extract_gallery_items(gallery_text):
    """Extract items from a gallery section"""
    items = []
    # Parse gallery items: File:name.png|[[Link Name]]  or  File:name.png|text|[[Link]]
    lines = gallery_text.split('\n')
    for line in lines:
        # Look for [[Name]] patterns
        matches = re.findall(r'\[\[([^\]]+)\]\]', line)
        if matches:
            # Get the last match (the actual page link, not the image link)
            name = matches[-1].split('|')[-1].strip()
            if name and name not in items:
                items.append(name)
    return items

def scrape_realms(session, wiki_url):
    """Scrape all realms from the Realms page"""
    params = {
        'action': 'query',
        'titles': 'Realms',
        'prop': 'revisions',
        'rvprop': 'content',
        'format': 'json'
    }
    
    try:
        response = session.get(f'{wiki_url}/api.php', params=params)
        data = response.json()
        pages = data['query']['pages']
        page_id = list(pages.keys())[0]
        wikitext = pages[page_id]['revisions'][0]['*']
        
        realms_data = {
            'normal_realms': [],
            'main_realm_subrealms': [],
            'yoyleland_subrealms': [],
            'backrooms_subrealms': [],
            'yoyle_factory_subrealms': [],
            'classic_paradise_subrealms': [],
            'evil_forest_subrealms': [],
            'midnight_rooftops_subrealms': [],
            'off_game': [],
            'cancelled': [],
            'future_realms': []
        }
        
        # Extract Normal Realms
        if '= Normal Realms =' in wikitext:
            start = wikitext.find('= Normal Realms =')
            end = wikitext.find('\n= ', start + 1)
            if end == -1:
                end = len(wikitext)
            normal_section = wikitext[start:end]
            realms_data['normal_realms'] = extract_gallery_items(normal_section)
        
        # Extract Sub-Realms
        if '= Sub-Realms =' in wikitext:
            start = wikitext.find('= Sub-Realms =')
            end = wikitext.find('\n= ', start + 1)
            if end == -1:
                end = len(wikitext)
            sub_section = wikitext[start:end]
            
            # Extract each subsection
            if '== Main Realm ==' in sub_section:
                s = sub_section.find('== Main Realm ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['main_realm_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== Yoyleland ==' in sub_section:
                s = sub_section.find('== Yoyleland ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['yoyleland_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== The Backrooms ==' in sub_section:
                s = sub_section.find('== The Backrooms ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['backrooms_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== Yoyle Factory ==' in sub_section:
                s = sub_section.find('== Yoyle Factory ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['yoyle_factory_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== Classic Paradise ==' in sub_section:
                s = sub_section.find('== Classic Paradise ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['classic_paradise_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== Evil Forest ==' in sub_section:
                s = sub_section.find('== Evil Forest ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['evil_forest_subrealms'] = extract_gallery_items(sub_section[s:e])
            
            if '== Midnight Rooftops ==' in sub_section:
                s = sub_section.find('== Midnight Rooftops ==')
                e = sub_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(sub_section)
                realms_data['midnight_rooftops_subrealms'] = extract_gallery_items(sub_section[s:e])
        
        # Extract Other sections
        if '= Other=' in wikitext:
            start = wikitext.find('= Other=')
            end = len(wikitext)
            other_section = wikitext[start:end]
            
            if '== Off Game ==' in other_section:
                s = other_section.find('== Off Game ==')
                e = other_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(other_section)
                realms_data['off_game'] = extract_gallery_items(other_section[s:e])
            
            if '== Cancelled ==' in other_section:
                s = other_section.find('== Cancelled ==')
                e = other_section.find('\n== ', s + 1)
                if e == -1:
                    e = len(other_section)
                realms_data['cancelled'] = extract_gallery_items(other_section[s:e])
            
            if '== Future Realms ==' in other_section:
                s = other_section.find('== Future Realms ==')
                e = len(other_section)
                realms_data['future_realms'] = extract_gallery_items(other_section[s:e])
        
        return realms_data
    
    except Exception as e:
        print(f"Error parsing Realms page: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
