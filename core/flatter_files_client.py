import os
import httpx
from typing import Optional

class FlatterFilesClient:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("FLATTER_FILES_API_KEY")
        self.base_url = base_url or os.getenv("FLATTER_FILES_BASE_URL")
        if not self.api_key or not self.base_url:
            raise ValueError("FLATTER_FILES_API_KEY and FLATTER_FILES_BASE_URL must be set.")

    async def download_file(self, file_id: str, download_path: str) -> Optional[str]:
        """
        Downloads a file from Flatter Files.
        
        Args:
            file_id: The ID of the file to download.
            download_path: The path to save the downloaded file.
            
        Returns:
            The path to the downloaded file, or None if the download failed.
        """
        url = f"{self.base_url}/api/v1/file/{file_id}/download"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        async with httpx.AsyncClient() as client:
            try:
                with open(download_path, "wb") as f:
                    async with client.stream("GET", url, headers=headers) as response:
                        if response.status_code != 200:
                            return None
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
                return download_path
            except Exception:
                return None
