"""
System Manager - Backup Service
Handles automated backups to Google Drive.
"""

import logging
import tarfile
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger("system-manager.backup")


class BackupService:
    """Automated backup service with Google Drive integration."""

    def __init__(self, drive_client=None, backup_dir="backups"):
        self.drive_client = drive_client
        self.backup_paths: List[Path] = []
        self.last_backup: Optional[datetime] = None
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def add_backup_path(self, path: str) -> None:
        """Add a path to the backup list."""
        self.backup_paths.append(Path(path))
        logger.info(f"Added backup path: {path}")

    def create_backup_archive(self) -> str:
        """
        Create a compressed backup archive with timestamp.

        Returns:
            str: Path to the created backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"vulcan_backup_{timestamp}.tar.gz"

        logger.info(f"Creating backup archive: {backup_file}")

        # Create tar.gz archive
        with tarfile.open(backup_file, "w:gz") as tar:
            for path in self.backup_paths:
                if path.exists():
                    tar.add(str(path), arcname=str(path))
                    logger.info(f"  Added to archive: {path}")
                else:
                    logger.warning(f"  Path not found: {path}")

        # Calculate checksum
        checksum = self._calculate_checksum(backup_file)

        # Create manifest
        manifest = {
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "paths": [str(p) for p in self.backup_paths if p.exists()],
            "checksum": checksum,
            "size_bytes": backup_file.stat().st_size,
        }

        # Save manifest
        manifest_file = backup_file.with_suffix(".json")
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        logger.info(f"Backup archive created: {backup_file}")
        return str(backup_file)

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def verify_backup(self, backup_file: str) -> Dict[str, any]:
        """
        Verify backup integrity.

        Args:
            backup_file: Path to backup file

        Returns:
            dict: Verification results
        """
        logger.info(f"Verifying backup: {backup_file}")

        results = {"valid": True, "checks": [], "errors": []}

        backup_path = Path(backup_file)

        # Check file exists
        if not backup_path.exists():
            results["valid"] = False
            results["errors"].append("Backup file not found")
            return results
        results["checks"].append("File exists")

        # Check file size
        size_mb = backup_path.stat().st_size / 1024 / 1024
        if size_mb == 0:
            results["valid"] = False
            results["errors"].append("Backup file is empty")
            return results
        results["checks"].append(f"File size: {size_mb:.2f} MB")

        # Verify tar.gz format
        if not tarfile.is_tarfile(backup_file):
            results["valid"] = False
            results["errors"].append("Invalid tar.gz format")
            return results
        results["checks"].append("Valid tar.gz format")

        # Verify checksum if manifest exists
        manifest_file = backup_path.with_suffix(".json")
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                manifest = json.load(f)

            actual_checksum = self._calculate_checksum(backup_path)
            expected_checksum = manifest.get("checksum")

            if actual_checksum == expected_checksum:
                results["checks"].append("Checksum verified")
            else:
                results["valid"] = False
                results["errors"].append("Checksum mismatch")

        logger.info(f"Verification {'passed' if results['valid'] else 'failed'}")
        return results

    def get_backup_info(self, backup_file: str) -> Optional[Dict]:
        """Get metadata about a backup file."""
        manifest_file = Path(backup_file).with_suffix(".json")
        if manifest_file.exists():
            with open(manifest_file, "r") as f:
                return json.load(f)
        return None

    def cleanup_old_backups(self, retention_days: int = 7) -> List[str]:
        """
        Remove backups older than retention period.

        Args:
            retention_days: Number of days to keep backups

        Returns:
            list: Paths of deleted backups
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted = []

        for backup_file in self.backup_dir.glob("vulcan_backup_*.tar.gz"):
            # Get creation time from manifest
            manifest_file = backup_file.with_suffix(".json")
            if manifest_file.exists():
                with open(manifest_file, "r") as f:
                    manifest = json.load(f)
                created_at = datetime.fromisoformat(manifest["created_at"])

                if created_at < cutoff_date:
                    backup_file.unlink()
                    manifest_file.unlink()
                    deleted.append(str(backup_file))
                    logger.info(f"Deleted old backup: {backup_file}")

        return deleted

    def run_daily_backup(self) -> dict:
        """Execute daily backup routine."""
        logger.info("Starting daily backup...")

        try:
            # Create backup archive
            backup_file = self.create_backup_archive()

            # Verify backup
            verification = self.verify_backup(backup_file)

            # Cleanup old backups
            deleted = self.cleanup_old_backups(retention_days=7)

            self.last_backup = datetime.utcnow()

            results = {
                "started_at": datetime.utcnow().isoformat(),
                "backup_file": backup_file,
                "verification": verification,
                "deleted_old_backups": deleted,
                "completed_at": datetime.utcnow().isoformat(),
            }

            logger.info(f"Backup complete: {backup_file}")
            return results

        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return {"error": str(e), "started_at": datetime.utcnow().isoformat()}

    async def sync_to_drive(self, local_path: str, remote_folder: str) -> dict:
        """Sync a local directory to Google Drive."""
        if not self.drive_client:
            return {"error": "Google Drive client not configured"}

        # Placeholder for actual Drive sync implementation
        return {
            "local_path": local_path,
            "remote_folder": remote_folder,
            "status": "pending_implementation",
        }
