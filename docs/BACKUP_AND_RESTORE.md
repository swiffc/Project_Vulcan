# Project Vulcan - Backup and Restore

This document outlines the backup and restore procedures for Project Vulcan.

## What is Backed Up?

The System Manager is responsible for backing up the following data:

-   **`storage/` directory:** This directory contains all the application data, including:
    -   `logs/`: Log files.
    -   `recordings/`: Screen recordings.
    -   `verification/`: Visual verification diff images.
    -   `chroma/`: ChromaDB vector store.
-   **Database:** The PostgreSQL database containing the Trading Journal and Validation History.

Backups are performed daily at 2 AM UTC.

## Restore Procedure

To restore from a backup, follow these steps:

1.  **Stop all services:**
    ```bash
    docker-compose down
    ```
2.  **Restore the `storage/` directory:**
    -   Replace the contents of the `storage/` directory with the contents of the backup.
3.  **Restore the database:**
    -   Use the `pg_restore` command to restore the database from the backup file.
4.  **Start all services:**
    ```bash
    docker-compose up -d
    ```

## Restore Script

A restore script `scripts/restore_backup.py` is provided to automate the restore process.

**Usage:**
```bash
python scripts/restore_backup.py <backup_file>
```
This script will stop the services, restore the data, and start the services again.
