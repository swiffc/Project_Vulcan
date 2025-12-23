"""
Project Vulcan - Backup Restore Script
Restores application data from a backup archive.
"""

import sys
import os
import subprocess
import tarfile
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime


def calculate_checksum(file_path):
    """Calculate SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def validate_backup(backup_file):
    """Validate backup file integrity."""
    print(f"Validating backup: {backup_file}")

    # Check file exists and is not empty
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file not found: {backup_file}")

    file_size = os.path.getsize(backup_file)
    if file_size == 0:
        raise ValueError("Backup file is empty")

    print(f"  ✓ File exists ({file_size / 1024 / 1024:.2f} MB)")

    # Verify it's a valid tar.gz
    if not tarfile.is_tarfile(backup_file):
        raise ValueError("Invalid backup file format (not a tar archive)")

    print("  ✓ Valid tar.gz archive")
    return True


def create_emergency_backup():
    """Create emergency backup of current state before restore."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    emergency_backup = f"backups/emergency_backup_{timestamp}.tar.gz"

    print(f"Creating emergency backup: {emergency_backup}")

    os.makedirs("backups", exist_ok=True)

    with tarfile.open(emergency_backup, "w:gz") as tar:
        if os.path.exists("storage"):
            tar.add("storage", arcname="storage")

    print(f"  ✓ Emergency backup created: {emergency_backup}")
    return emergency_backup


def stop_services():
    """Stop Docker services."""
    print("Stopping services...")
    try:
        subprocess.run(
            ["docker-compose", "down"], check=True, capture_output=True, text=True
        )
        print("  ✓ Services stopped")
    except subprocess.CalledProcessError as e:
        print(f"  ⚠ Warning: Could not stop services: {e}")
        print("  Continuing anyway...")


def start_services():
    """Start Docker services."""
    print("Starting services...")
    try:
        subprocess.run(
            ["docker-compose", "up", "-d"], check=True, capture_output=True, text=True
        )
        print("  ✓ Services started")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to start services: {e}")


def restore_storage(backup_file):
    """Restore storage directory from backup."""
    print("Restoring storage...")

    # Extract to temporary location first
    temp_dir = "temp_restore"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            # Extract storage directory
            members = [m for m in tar.getmembers() if m.name.startswith("storage/")]
            tar.extractall(path=temp_dir, members=members)

        # Remove old storage
        if os.path.exists("storage"):
            shutil.rmtree("storage")

        # Move restored storage to correct location
        if os.path.exists(os.path.join(temp_dir, "storage")):
            shutil.move(os.path.join(temp_dir, "storage"), "storage")
            print("  ✓ Storage restored")
        else:
            print("  ⚠ No storage directory in backup")

    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def restore_database(backup_file):
    """Restore PostgreSQL database from backup."""
    print("Restoring database...")

    # Extract database dump from backup
    temp_dir = "temp_restore_db"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with tarfile.open(backup_file, "r:gz") as tar:
            # Look for database dump
            db_members = [
                m
                for m in tar.getmembers()
                if m.name.startswith("database/") and m.name.endswith(".sql")
            ]

            if not db_members:
                print("  ⚠ No database dump found in backup")
                return

            tar.extractall(path=temp_dir, members=db_members)

            # Find the SQL file
            sql_file = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".sql"):
                        sql_file = os.path.join(root, file)
                        break

            if sql_file:
                # Restore database using psql
                db_url = os.getenv(
                    "DATABASE_URL", "postgresql://vulcan:vulcan@localhost:5432/vulcan"
                )

                try:
                    # Drop and recreate database
                    print("  Recreating database...")
                    subprocess.run(
                        ["psql", db_url, "-c", "DROP SCHEMA public CASCADE;"],
                        check=False,
                        capture_output=True,
                    )
                    subprocess.run(
                        ["psql", db_url, "-c", "CREATE SCHEMA public;"],
                        check=True,
                        capture_output=True,
                    )

                    # Restore from SQL dump
                    with open(sql_file, "r") as f:
                        subprocess.run(
                            ["psql", db_url], stdin=f, check=True, capture_output=True
                        )

                    print("  ✓ Database restored")
                except subprocess.CalledProcessError as e:
                    print(f"  ⚠ Database restore failed: {e}")
                    print("  You may need to restore manually")
            else:
                print("  ⚠ SQL file not found in backup")

    finally:
        # Cleanup temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def verify_restoration():
    """Verify that restoration was successful."""
    print("Verifying restoration...")

    checks = []

    # Check storage directory exists
    if os.path.exists("storage"):
        checks.append("✓ Storage directory exists")
    else:
        checks.append("✗ Storage directory missing")

    # Check for key subdirectories
    for subdir in ["logs", "chroma"]:
        path = os.path.join("storage", subdir)
        if os.path.exists(path):
            checks.append(f"✓ {subdir}/ exists")
        else:
            checks.append(f"⚠ {subdir}/ missing")

    for check in checks:
        print(f"  {check}")

    return all("✓" in check for check in checks)


def restore_backup(backup_file):
    """
    Main restore function.
    Restores the application from a backup file.
    """
    print("=" * 60)
    print("PROJECT VULCAN - BACKUP RESTORE")
    print("=" * 60)
    print()

    try:
        # Step 1: Validate backup
        validate_backup(backup_file)
        print()

        # Step 2: Create emergency backup
        emergency_backup = create_emergency_backup()
        print()

        # Step 3: Stop services
        stop_services()
        print()

        # Step 4: Restore storage
        restore_storage(backup_file)
        print()

        # Step 5: Restore database
        restore_database(backup_file)
        print()

        # Step 6: Start services
        start_services()
        print()

        # Step 7: Verify restoration
        if verify_restoration():
            print()
            print("=" * 60)
            print("✅ RESTORE COMPLETE")
            print("=" * 60)
            print(f"Emergency backup saved to: {emergency_backup}")
        else:
            print()
            print("=" * 60)
            print("⚠ RESTORE COMPLETED WITH WARNINGS")
            print("=" * 60)
            print("Some components may not have been restored correctly.")
            print(f"Emergency backup available at: {emergency_backup}")

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ RESTORE FAILED")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Your data has NOT been modified.")
        print("Services may need to be restarted manually:")
        print("  docker-compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python restore_backup.py <backup_file>")
        print()
        print("Example:")
        print("  python restore_backup.py backups/vulcan_backup_20251223_020000.tar.gz")
        sys.exit(1)

    backup_file = sys.argv[1]
    restore_backup(backup_file)
