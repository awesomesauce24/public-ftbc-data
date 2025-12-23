"""Configuration for wiki system"""

import json
from pathlib import Path
from typing import Dict, Any

class Config:
    """Configuration management for wiki system"""
    
    # Paths
    REALMS_PATH = Path(__file__).parent.parent.parent / "realms"
    
    # Difficulty colors (used for styling)
    DIFFICULTY_COLORS = {
        "Effortless": "#17a897",
        "Easy": "#10da8d",
        "Moderate": "#07fc55",
        "Normal": "#a1ff27",
        "Intermediate": "#ffb700",
        "Hard": "#FF7700",
        "Difficult": "#f54f25",
        "Extreme": "#ed2727",
        "Unforgiving": "#ff143f",
        "Insane": "#ff1c95",
        "Dreadful": "#db25ff",
        "Terrifying": "#8b17ff",
        "Arduous": "#5d0cff",
        "Strenuous": "#4048e5",
        "Remorseless": "#2084ff",
        "Horrifying": "#2bd0fd",
        "IMPOSSIBLE": "#000000",
        "Secret": "#FFD3AC",
    }
    
    # Realm information (styling, themes, etc)
    REALMS_INFO = {
        "Main Realm": {
            "theme": "green",
            "accent": "-webkit-linear-gradient(#23bd1c,#188a13)",
            "accent_color": "#23bd1c",
            "accent_label_color": "#ffffff",
            "background": "Goiky.png",
        },
        "Inverted": {
            "theme": "orange-gold",
            "accent": "-webkit-linear-gradient(#C45508,#EEDC5B)",
            "accent_color": "#C45508",
            "accent_label_color": "#ffffff",
            "background": "InvertedRealm.png",
        },
        "Yoyleland": {
            "theme": "purple",
            "accent": "-webkit-linear-gradient(#cd58e3,#70287a)",
            "accent_color": "#cd58e3",
            "accent_label_color": "#ffffff",
            "background": "YoylelandRealm.png",
        },
        "Backrooms": {
            "theme": "yellow",
            "accent": "-webkit-linear-gradient(#f2e06d,#c4b71a)",
            "accent_color": "#f2e06d",
            "accent_label_color": "#000000",
            "background": "BackroomsRealm.png",
        },
        "Yoyle Factory": {
            "theme": "metal-gray",
            "accent": "-webkit-linear-gradient(#46515D,#2A3944)",
            "accent_color": "#46515D",
            "accent_label_color": "#ffffff",
            "background": "YoylefactoryRealm.png",
        },
        "Classic Paradise": {
            "theme": "pink",
            "accent": "-webkit-linear-gradient(#ff5ed1,#b3008e)",
            "accent_color": "#ff5ed1",
            "accent_label_color": "#ffffff",
            "background": "ClassicParadiseRealm.png",
        },
        "Evil Forest": {
            "theme": "dark-purple",
            "accent": "-webkit-linear-gradient(#8e24aa,#4a0072)",
            "accent_color": "#8e24aa",
            "accent_label_color": "#ffffff",
            "background": "EvilForestRealm.png",
        },
        "Cherry Grove": {
            "theme": "brown",
            "accent": "-webkit-linear-gradient(#896a2e,#cf973a)",
            "accent_color": "#cf973a",
            "accent_label_color": "#000000",
            "background": "-CherryRealm.png",
        },
        "Barren Desert": {
            "theme": "sand",
            "accent": "-webkit-linear-gradient(#ffb14a,#5b2d00)",
            "accent_color": "#ffb14a",
            "accent_label_color": "#000000",
            "background": "BarrenDesertRealm.png",
        },
        "Frozen World": {
            "theme": "cyan",
            "accent": "-webkit-linear-gradient(#4dd0e1,#006064)",
            "accent_color": "#4dd0e1",
            "accent_label_color": "#000000",
            "background": "FrozenWorldRealm.png",
        },
        "Timber Peaks": {
            "theme": "green-olive",
            "accent": "-webkit-linear-gradient(#8bc34a,#33691e)",
            "accent_color": "#8bc34a",
            "accent_label_color": "#000000",
            "background": "TimberRealm.png",
        },
        "Midnight Rooftops": {
            "theme": "dark-blue",
            "accent": "-webkit-linear-gradient(#050522,#140f4a)",
            "accent_color": "#050522",
            "accent_label_color": "#ffffff",
            "background": "MidnightRooftopsRealm.png",
        },
        "Magma Canyon": {
            "theme": "red-orange",
            "accent": "-webkit-linear-gradient(#954116,#e93b14)",
            "accent_color": "#e93b14",
            "accent_label_color": "#ffffff",
            "background": "MagmaRealm.png",
        },
        "Sakura Serenity": {
            "theme": "mauve",
            "accent": "-webkit-linear-gradient(#b56f8f,#8e4f5f)",
            "accent_color": "#b56f8f",
            "accent_label_color": "#ffffff",
            "background": "SakuraRealm.png",
        },
        "Polluted Marshlands": {
            "theme": "green-brown",
            "accent": "-webkit-linear-gradient(#6e7f00,#c3d100)",
            "accent_color": "#6e7f00",
            "accent_label_color": "#000000",
            "background": "PollutedMarshlandsRealm.png",
        },
    }
    
    # Subrealms structure (maps parent realm to list of subrealms)
    SUBREALMS = {
        "Main Realm": [
            "Goiky",
            "Motionless",
            "Mythical Forest",
            "Nearing The End",
            "Nihilism",
            "peep.",
            "Sanctuary",
            "Hypostasis (Realm)",
            "Storm Of Doom",
            "mooD fo mrotS",
            "Zombie Apocalypse",
            "Benevolence",
        ],
        "Yoyleland": ["Abandonment"],
        "Backrooms": [
            "Level 0",
            "Level 1",
            "Level 2",
            "Level 3",
            "Level 4",
            "Level 153",
            "RUN FOR YOUR LIFE",
            "stairwell",
        ],
        "Yoyle Factory": [
            "Basement",
            "Abandonment",
            "Meltdown",
            "Out Of Bounds",
        ],
        "Classic Paradise": [
            "Starter Place",
            "Classic Insanity",
            "Classic Paradox",
        ],
        "Evil Forest": [
            "Evle Froets",
            "evefdpfroestost",
            "Limbo",
            "RUN",
        ],
        "Midnight Rooftops": ["Gooey Escape"],
    }
    
    # Section to subrealm mapping (for auto-detection from JSON)
    SECTION_TO_SUBREALM = {
        # Main Realm
        "Goiky": "Goiky",
        # Yoyle Factory (only map to subrealms for special areas, not "Normal Factory")
        "Lights Out": "Abandonment",
        "Abandonment": "Abandonment",
        "Meltdown": "Meltdown",
        "Out of Bounds": "Out Of Bounds",  # JSON has lowercase 'of', subrealm name is capitalized
        "Out Of Bounds": "Out Of Bounds",  # Also support capitalized version
    }
    
    # Subrealm-specific backgrounds (overrides parent realm background)
    SUBREALM_BACKGROUNDS = {
        "Yoyle Factory/Basement": "Basement.png",
        "Yoyle Factory/Abandonment": "Lights Out.png",
        "Yoyle Factory/Meltdown": "Meltdown.png",
        "Yoyle Factory/Out Of Bounds": "Out of Bounds.png",
    }
    
    # Subrealm-specific theme colors (overrides parent realm colors)
    SUBREALM_THEMES = {
        "Yoyle Factory/Meltdown": {
            "accent_color": "-webkit-linear-gradient(#78ff78,#00ff00)",
            "accent_label_color": "#ffffff",
        }
    }
    
    @classmethod
    def get_realm_info(cls, realm_name: str) -> Dict[str, Any]:
        """Get information for a specific realm"""
        return cls.REALMS_INFO.get(realm_name, {})
    
    @classmethod
    def get_color(cls, difficulty: str) -> str:
        """Get color code for difficulty"""
        return cls.DIFFICULTY_COLORS.get(difficulty, "#000000")
    
    @classmethod
    def get_subrealms(cls, realm_name: str) -> list:
        """Get list of subrealms for a realm"""
        return cls.SUBREALMS.get(realm_name, [])
    
    @classmethod
    def get_subrealm_from_section(cls, section: str) -> str:
        """Get subrealm name from section (for auto-detection)"""
        return cls.SECTION_TO_SUBREALM.get(section, "")
