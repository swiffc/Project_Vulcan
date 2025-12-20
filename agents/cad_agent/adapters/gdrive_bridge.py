"""
Google Drive Bridge
Thin wrapper for Google Drive MCP server integration.

Packages Used (via pip - NOT in project):
- google-api-python-client: Drive API
- google-auth: Authentication

OR connects to MCP GDrive server if available.
See REFERENCES.md for mcp-gdrive setup.
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger("cad_agent.gdrive")


class GDriveBridge:
    """
    Bridge to Google Drive for file sync.
    Can use either direct API or MCP server.
    """
    
    def __init__(self, mcp_client=None, credentials_path: str = None):
        self.mcp = mcp_client
        self.credentials_path = credentials_path
        self._service = None
        self.default_folder = "Vulcan_Exports"
        
    def _get_service(self):
        """Lazy-load Google Drive service."""
        if self._service:
            return self._service
            
        if not self.credentials_path:
            raise ValueError("No credentials path provided")
            
        # Lazy import
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        self._service = build('drive', 'v3', credentials=creds)
        return self._service
    
    async def upload(self, local_path: str, drive_folder: str = None) -> Dict:
        """Upload file to Google Drive."""
        folder = drive_folder or self.default_folder
        
        # Use MCP if available
        if self.mcp:
            return await self.mcp.call_tool("drive_upload", {
                "local_path": local_path,
                "folder": folder
            })
        
        # Direct API fallback
        from googleapiclient.http import MediaFileUpload
        
        service = self._get_service()
        file_metadata = {"name": Path(local_path).name}
        media = MediaFileUpload(local_path)
        
        result = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        logger.info(f"📤 Uploaded: {result['name']}")
        return {"id": result['id'], "link": result.get('webViewLink')}
    
    async def sync_folder(self, local_dir: str, drive_folder: str = None) -> Dict:
        """Sync local directory to Drive."""
        folder = drive_folder or self.default_folder
        uploaded = 0
        
        for filepath in Path(local_dir).rglob('*'):
            if filepath.is_file():
                await self.upload(str(filepath), folder)
                uploaded += 1
                
        logger.info(f"📦 Synced {uploaded} files to {folder}")
        return {"files_synced": uploaded, "folder": folder}
    
    async def list_files(self, folder: str = None) -> List[Dict]:
        """List files in Drive folder."""
        if self.mcp:
            return await self.mcp.call_tool("drive_list", {"folder": folder})
            
        service = self._get_service()
        results = service.files().list(
            pageSize=100,
            fields="files(id, name, mimeType, modifiedTime)"
        ).execute()
        
        return results.get('files', [])
