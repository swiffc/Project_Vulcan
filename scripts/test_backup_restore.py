"""
Project Vulcan - Backup & Restore Test Script
Automated end-to-end test for backup and restore functionality.
"""

import os
import sys
import json
import subprocess
import tarfile
from pathlib import Path
from datetime import datetime


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def create_test_data():
    """Create test data for backup testing."""
    print_section("Creating Test Data")

    # Create test storage structure
    test_dirs = [
        "storage/test_backup/logs",
        "storage/test_backup/data",
    ]

    for dir_path in test_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created: {dir_path}")

    # Create test files
    test_files = {
        "storage/test_backup/logs/test.log": "Test log entry\n",
        "storage/test_backup/data/test.json": json.dumps(
            {"test": "data", "timestamp": datetime.now().isoformat()}
        ),
    }

    for file_path, content in test_files.items():
        with open(file_path, "w") as f:
            f.write(content)
        print(f"  ✓ Created: {file_path}")

    return test_files


def create_test_backup():
    """Create a test backup archive."""
    print_section("Creating Test Backup")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backups/test_backup_{timestamp}.tar.gz"

    # Create backups directory
    Path("backups").mkdir(exist_ok=True)

    # Create backup archive
    with tarfile.open(backup_file, "w:gz") as tar:
        if os.path.exists("storage/test_backup"):
            tar.add("storage/test_backup", arcname="storage/test_backup")
            print(f"  ✓ Added storage/test_backup to archive")

    # Verify backup was created
    if os.path.exists(backup_file):
        size_mb = os.path.getsize(backup_file) / 1024 / 1024
        print(f"  ✓ Backup created: {backup_file} ({size_mb:.2f} MB)")
        return backup_file
    else:
        raise FileNotFoundError("Backup file was not created")


def modify_test_data():
    """Modify test data to simulate data loss."""
    print_section("Simulating Data Loss")

    # Delete test data
    import shutil

    if os.path.exists("storage/test_backup"):
        shutil.rmtree("storage/test_backup")
        print("  ✓ Deleted storage/test_backup")
    else:
        print("  ⚠ storage/test_backup already deleted")


def restore_test_backup(backup_file):
    """Restore from test backup."""
    print_section("Restoring from Backup")

    # Extract backup
    with tarfile.open(backup_file, "r:gz") as tar:
        tar.extractall()
        print(f"  ✓ Extracted {backup_file}")


def verify_restoration(original_files):
    """Verify that data was restored correctly."""
    print_section("Verifying Restoration")

    all_verified = True

    for file_path, expected_content in original_files.items():
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                actual_content = f.read()

            if actual_content == expected_content:
                print(f"  ✓ Verified: {file_path}")
            else:
                print(f"  ✗ Content mismatch: {file_path}")
                all_verified = False
        else:
            print(f"  ✗ Missing: {file_path}")
            all_verified = False

    return all_verified


def cleanup_test_data():
    """Clean up test data and backups."""
    print_section("Cleaning Up")

    import shutil

    # Remove test storage
    if os.path.exists("storage/test_backup"):
        shutil.rmtree("storage/test_backup")
        print("  ✓ Removed storage/test_backup")

    # Remove test backups
    import glob

    test_backups = glob.glob("backups/test_backup_*.tar.gz")
    for backup in test_backups:
        os.remove(backup)
        print(f"  ✓ Removed {backup}")


def run_test():
    """Run the complete backup and restore test."""
    print("\n" + "=" * 60)
    print("  PROJECT VULCAN - BACKUP & RESTORE TEST")
    print("=" * 60)

    try:
        # Step 1: Create test data
        original_files = create_test_data()

        # Step 2: Create backup
        backup_file = create_test_backup()

        # Step 3: Simulate data loss
        modify_test_data()

        # Step 4: Restore backup
        restore_test_backup(backup_file)

        # Step 5: Verify restoration
        if verify_restoration(original_files):
            print_section("TEST PASSED ✅")
            print("  All data was successfully backed up and restored!")
            cleanup_test_data()
            return 0
        else:
            print_section("TEST FAILED ❌")
            print("  Some data was not restored correctly.")
            return 1

    except Exception as e:
        print_section("TEST ERROR ❌")
        print(f"  Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_test()
    sys.exit(exit_code)
