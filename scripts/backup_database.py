"""
Project Vulcan - Database Backup Script
Creates a PostgreSQL database backup.
"""

import os
import subprocess
from datetime import datetime
from pathlib import Path


def backup_database(output_dir="backups/database"):
    """
    Create a PostgreSQL database backup using pg_dump.

    Returns:
        str: Path to the created backup file
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"{output_dir}/vulcan_db_{timestamp}.sql"

    # Get database URL from environment
    db_url = os.getenv(
        "DATABASE_URL", "postgresql://vulcan:vulcan@localhost:5432/vulcan"
    )

    print(f"Backing up database to: {backup_file}")

    try:
        # Run pg_dump
        with open(backup_file, "w") as f:
            subprocess.run(["pg_dump", db_url], stdout=f, check=True, text=True)

        print(f"✓ Database backup created: {backup_file}")
        return backup_file

    except subprocess.CalledProcessError as e:
        print(f"✗ Database backup failed: {e}")
        if os.path.exists(backup_file):
            os.remove(backup_file)
        raise
    except FileNotFoundError:
        print("✗ pg_dump not found. Please install PostgreSQL client tools.")
        raise


if __name__ == "__main__":
    try:
        backup_file = backup_database()
        print(f"\nBackup complete: {backup_file}")
    except Exception as e:
        print(f"\nBackup failed: {e}")
        exit(1)
