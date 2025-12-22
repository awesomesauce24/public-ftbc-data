"""
FTBC Wiki System - Revamped v6
Complete reboot with modular architecture for managing game content
"""

__version__ = "6.0.0"
__author__ = "Spongybot / Chrust"

from wiki.core.loader import RealmLoader
from wiki.core.config import Config

__all__ = ['RealmLoader', 'Config']
