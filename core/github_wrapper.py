"""
GitHub Repo Wrapper - "Read It Don't Clone It" Pattern
Implements Rule 2 & Section 2 of RULES.md.

This adapter fetches specific files from external GitHub repos on demand
without cloning the entire codebase.
"""

import os
import requests
import base64
import logging
from functools import lru_cache
from typing import List, Dict, Optional, Union

logger = logging.getLogger("core.github_wrapper")


class GitHubWrapper:
    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = None):
        """
        Initialize wrapper.
        ARGS:
            token: GitHub Personal Access Token (optional, prevents rate limits)
        """
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

        # Registry of "Wrapped" repositories from REFERENCES.md
        self.registry = {
            "adafruit": ("adafruit", "Adafruit_CAD_Parts"),
            "openscad": ("tanius", "openscad-models"),
            "bolt": ("bolt-design", "standard-parts"),
        }

    @lru_cache(maxsize=100)
    def list_files(self, repo_alias: str, path: str = "") -> List[Dict]:
        """
        List files in a remote directory without downloading them.
        """
        if repo_alias not in self.registry:
            raise ValueError(f"Repo alias '{repo_alias}' not found in registry.")

        owner, repo = self.registry[repo_alias]
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            items = resp.json()

            # Simplified output
            return [
                {
                    "name": item["name"],
                    "path": item["path"],
                    "type": item["type"],
                    "download_url": item["download_url"],
                }
                for item in items
            ]
        except Exception as e:
            logger.error(f"Failed to list files for {repo_alias}/{path}: {e}")
            return []

    def fetch_file(self, repo_alias: str, file_path: str) -> Optional[bytes]:
        """
        Download a single specific file into memory.
        """
        if repo_alias not in self.registry:
            raise ValueError(f"Repo alias '{repo_alias}' not found.")

        owner, repo = self.registry[repo_alias]
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"

        try:
            resp = requests.get(url, headers=self.headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            if data.get("encoding") == "base64":
                return base64.b64decode(data["content"])
            else:
                # If raw URL is needed (for large files)
                raw_resp = requests.get(data["download_url"], stream=True)
                return raw_resp.content

        except Exception as e:
            logger.error(f"Failed to fetch {file_path}: {e}")
            return None

    def search_repo(self, repo_alias: str, query: str) -> List[Dict]:
        """
        Search for a file inside a specific Wrapped Repo.
        """
        if repo_alias not in self.registry:
            raise ValueError(f"Repo alias '{repo_alias}' not found.")

        owner, repo = self.registry[repo_alias]
        # GitHub Code Search API
        search_url = f"{self.BASE_URL}/search/code?q={query}+repo:{owner}/{repo}"

        try:
            resp = requests.get(search_url, headers=self.headers, timeout=10)
            items = resp.json().get("items", [])
            return [
                {"name": i["name"], "path": i["path"], "html_url": i["html_url"]}
                for i in items
            ]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


# Singleton
_github_wrapper = None


def get_wrapper():
    global _github_wrapper
    if not _github_wrapper:
        # Check environment for token
        token = os.environ.get("GITHUB_TOKEN")
        _github_wrapper = GitHubWrapper(token)
    return _github_wrapper
