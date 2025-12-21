"""
CLI (Command-Line Interface) module for FTBC Wiki Bot
Contains all commands, UI components, and CLI utilities
"""

from .commands import (
    cmd_help,
    cmd_exit,
    cmd_search
)

from .ui import display_welcome

__all__ = [
    'cmd_help',
    'cmd_exit',
    'cmd_search',
    'display_welcome'
]
