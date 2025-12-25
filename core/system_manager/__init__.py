"""
System Manager Module - Backup and Maintenance
"""

from .backup_strategies import BackupManager, get_backup_manager

__all__ = ["BackupManager", "get_backup_manager"]
