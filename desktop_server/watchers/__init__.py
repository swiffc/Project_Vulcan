"""
Desktop Server Watchers
=======================
Process and application watchers for auto-launch functionality.
"""

from .solidworks_watcher import SolidWorksWatcher, get_watcher

__all__ = ["SolidWorksWatcher", "get_watcher"]
