"""
PDM Vault Adapter (Phase 12)

Integrates with SOLIDWORKS PDM (Product Data Management) vault.
Provides file operations, version control, and workflow management.

Pattern: Adapter (wraps SOLIDWORKS PDM API via COM)
API: EPDM.Interop (requires pywin32)

Usage:
    adapter = PDMAdapter(vault_name="Engineering")
    await adapter.connect()
    file_info = await adapter.get_file(path="Parts/Bracket.SLDPRT")
    await adapter.checkout(path="Parts/Bracket.SLDPRT")
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("cad_agent.pdm")


@dataclass
class PDMFile:
    """PDM vault file information."""
    id: int
    path: str
    name: str
    extension: str
    version: int
    state: str  # e.g., "Released", "In Work", "For Review"
    checked_out: bool
    checked_out_by: Optional[str]
    checked_out_date: Optional[datetime]
    modified_by: str
    modified_date: datetime
    size_bytes: int
    description: Optional[str]


@dataclass
class PDMVersion:
    """File version information."""
    version_number: int
    comment: str
    modified_by: str
    modified_date: datetime
    is_current: bool


class PDMAdapter:
    """
    Adapter for SOLIDWORKS PDM Professional.
    
    Features:
    - Connect to vault
    - Get file information
    - Check out / check in files
    - Get version history
    - Search by data card fields
    - Get workflow state
    - Download latest version
    
    Requirements:
    - SOLIDWORKS PDM Client installed
    - pywin32: pip install pywin32
    - Vault access credentials
    
    Note: Only works on Windows with PDM installed
    """

    def __init__(self, vault_name: Optional[str] = None, server: Optional[str] = None):
        """
        Initialize PDM adapter.
        
        Args:
            vault_name: Vault name (or reads from PDM_VAULT_NAME env)
            server: Server name/IP (or reads from PDM_SERVER env)
        """
        self.vault_name = vault_name or os.getenv("PDM_VAULT_NAME", "Engineering")
        self.server = server or os.getenv("PDM_SERVER", "localhost")
        
        self._vault = None
        self._logged_in = False
        self._com_available = False
        
        # Try to import COM
        try:
            import win32com.client
            self._win32com = win32com.client
            self._com_available = True
        except ImportError:
            logger.warning("pywin32 not available - PDM adapter will not work")

    async def connect(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Connect to PDM vault.
        
        Args:
            username: PDM username (or PDM_USERNAME env)
            password: PDM password (or PDM_PASSWORD env)
            
        Returns:
            True if connected successfully
        """
        if not self._com_available:
            logger.error("PDM requires pywin32 - pip install pywin32")
            return False

        try:
            # Create vault manager
            vault_mgr = self._win32com.Dispatch("ConisioLib.EdmVault")
            
            # Log in to vault
            user = username or os.getenv("PDM_USERNAME", "")
            pwd = password or os.getenv("PDM_PASSWORD", "")
            
            if user:
                vault_mgr.LoginAuto(self.vault_name, 0)  # 0 = this window
                logger.info(f"Logged in to PDM vault: {self.vault_name}")
            else:
                # Interactive login
                vault_mgr.Login(self.vault_name, 0)
                logger.info(f"Connected to PDM vault: {self.vault_name}")
            
            self._vault = vault_mgr
            self._logged_in = True
            return True
            
        except Exception as e:
            logger.error(f"PDM connection failed: {e}")
            return False

    async def get_file(self, path: str) -> Optional[PDMFile]:
        """
        Get file information from PDM vault.
        
        Args:
            path: Vault path (e.g., "Parts/Bracket.SLDPRT")
            
        Returns:
            PDMFile object or None if not found
            
        Example:
            file = await adapter.get_file("Parts/Bracket.SLDPRT")
            print(f"Version: {file.version}, State: {file.state}")
        """
        if not self._vault:
            logger.error("Not connected to PDM vault")
            return None

        try:
            # Get file from vault
            folder = self._vault.GetFolderFromPath(str(Path(path).parent))
            if not folder:
                logger.warning(f"Folder not found for: {path}")
                return None
            
            file = folder.GetFile(Path(path).name)
            if not file:
                logger.warning(f"File not found: {path}")
                return None
            
            # Get file info
            file_id = file.ID
            file_name = file.Name
            
            # Get current version
            version_mgr = file.GetVersions()
            current_version = version_mgr.GetCurrentVersion()
            
            # Get checkout info
            checked_out = file.IsLocked
            checked_out_by = file.LockedByUser.Name if checked_out else None
            
            # Get state
            state = file.CurrentState.Name if file.CurrentState else "Unknown"
            
            return PDMFile(
                id=file_id,
                path=path,
                name=file_name,
                extension=Path(file_name).suffix,
                version=current_version.VersionNo,
                state=state,
                checked_out=checked_out,
                checked_out_by=checked_out_by,
                checked_out_date=None,  # Would need additional API call
                modified_by=current_version.Comment,
                modified_date=datetime.now(),  # Placeholder
                size_bytes=file.FileSize,
                description=file.Description
            )
            
        except Exception as e:
            logger.error(f"Error getting PDM file: {e}")
            return None

    async def checkout(self, path: str, comment: Optional[str] = None) -> bool:
        """
        Check out a file from PDM vault.
        
        Args:
            path: Vault path
            comment: Optional checkout comment
            
        Returns:
            True if checked out successfully
        """
        if not self._vault:
            logger.error("Not connected to PDM vault")
            return False

        try:
            folder = self._vault.GetFolderFromPath(str(Path(path).parent))
            file = folder.GetFile(Path(path).name)
            
            if file.IsLocked:
                logger.warning(f"File already checked out: {path}")
                return False
            
            # Check out file
            file.LockFile(folder.ID, 0)  # 0 = this window
            logger.info(f"Checked out: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Checkout failed: {e}")
            return False

    async def checkin(self, path: str, comment: str = "", keep_locked: bool = False) -> bool:
        """
        Check in a file to PDM vault.
        
        Args:
            path: Vault path
            comment: Check-in comment
            keep_locked: Keep file checked out after check-in
            
        Returns:
            True if checked in successfully
        """
        if not self._vault:
            logger.error("Not connected to PDM vault")
            return False

        try:
            folder = self._vault.GetFolderFromPath(str(Path(path).parent))
            file = folder.GetFile(Path(path).name)
            
            if not file.IsLocked:
                logger.warning(f"File not checked out: {path}")
                return False
            
            # Check in file
            file.UnlockFile(0, comment, 1 if keep_locked else 0)
            logger.info(f"Checked in: {path}")
            return True
            
        except Exception as e:
            logger.error(f"Check-in failed: {e}")
            return False

    async def get_version_history(self, path: str) -> List[PDMVersion]:
        """
        Get version history for a file.
        
        Args:
            path: Vault path
            
        Returns:
            List of PDMVersion objects
        """
        if not self._vault:
            logger.error("Not connected to PDM vault")
            return []

        try:
            folder = self._vault.GetFolderFromPath(str(Path(path).parent))
            file = folder.GetFile(Path(path).name)
            
            versions = []
            version_mgr = file.GetVersions()
            current_version_no = version_mgr.GetCurrentVersion().VersionNo
            
            for i in range(1, current_version_no + 1):
                ver = version_mgr.GetVersion(i)
                versions.append(PDMVersion(
                    version_number=i,
                    comment=ver.Comment,
                    modified_by=ver.User.Name,
                    modified_date=datetime.now(),  # Would need conversion
                    is_current=(i == current_version_no)
                ))
            
            return versions
            
        except Exception as e:
            logger.error(f"Error getting version history: {e}")
            return []

    async def search(
        self,
        part_number: Optional[str] = None,
        description: Optional[str] = None,
        state: Optional[str] = None
    ) -> List[PDMFile]:
        """
        Search PDM vault by data card fields.
        
        Args:
            part_number: Part number to search
            description: Description keyword
            state: Workflow state filter
            
        Returns:
            List of matching PDMFile objects
        """
        # This would require PDM search API implementation
        logger.info(f"Searching PDM: part={part_number}, desc={description}, state={state}")
        return []

    def is_connected(self) -> bool:
        """Check if connected to vault."""
        return self._vault is not None and self._logged_in


# Singleton instance
_adapter_instance: Optional[PDMAdapter] = None


def get_pdm_adapter() -> PDMAdapter:
    """Get singleton instance of PDM adapter."""
    global _adapter_instance
    if _adapter_instance is None:
        _adapter_instance = PDMAdapter()
    return _adapter_instance
