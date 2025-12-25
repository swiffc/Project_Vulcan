# Project Vulcan - Backup and Restore

This document outlines the backup and restore procedures for Project Vulcan.

---

## 📦 What is Backed Up?

The System Manager automatically backs up:

### Application Data
- **`storage/` directory**: All application data including:
  - `logs/`: Application and system logs
  - `recordings/`: Screen recordings
  - `verification/`: Visual verification diff images
  - `chroma/`: ChromaDB vector store

### Database
- **PostgreSQL database**: Trading Journal and Validation History
- Backed up separately using `pg_dump`

### Backup Schedule
- **Daily backups** at 2 AM UTC
- **Retention**: 7 days (older backups automatically deleted)
- **Location**: `backups/` directory

---

## 📁 Backup File Structure

```
backups/
├── vulcan_backup_20251223_020000.tar.gz    # Compressed archive
├── vulcan_backup_20251223_020000.json      # Manifest (metadata + checksum)
└── database/
    └── vulcan_db_20251223_020000.sql       # Database dump
```

### Manifest File
Each backup includes a JSON manifest with:
- Timestamp
- List of backed-up paths
- SHA-256 checksum
- File size

---

## 🔄 Restore Procedure

### Automated Restore

Use the restore script for automated restoration:

```bash
python scripts/restore_backup.py backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz
```

**The script will**:
1. ✅ Validate backup file integrity
2. ✅ Create emergency backup of current state
3. ✅ Stop Docker services
4. ✅ Restore storage directory
5. ✅ Restore PostgreSQL database
6. ✅ Start Docker services
7. ✅ Verify restoration

### Manual Restore

If the automated script fails, follow these steps:

#### 1. Stop Services
```bash
docker-compose down
```

#### 2. Restore Storage
```bash
# Extract backup
tar -xzf backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz

# Verify extraction
ls -la storage/
```

#### 3. Restore Database
```bash
# Find database dump in backup
tar -tzf backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz | grep .sql

# Extract database dump
tar -xzf backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz database/

# Restore database
psql $DATABASE_URL < database/vulcan_db_YYYYMMDD_HHMMSS.sql
```

#### 4. Start Services
```bash
docker-compose up -d
```

---

## ✅ Verification

### Verify Backup Integrity

```python
from agents.system_manager.src.backup import BackupService

bs = BackupService()
result = bs.verify_backup('backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz')

if result['valid']:
    print("✓ Backup is valid")
else:
    print("✗ Backup verification failed:", result['errors'])
```

### Verify Restoration

After restore, check:

```bash
# Check storage directory
ls -la storage/

# Check database
psql $DATABASE_URL -c "\dt"

# Check services
docker-compose ps
```

---

## 🧪 Testing

### Automated Test

Run the automated backup/restore test:

```bash
python scripts/test_backup_restore.py
```

This will:
1. Create test data
2. Run backup
3. Delete test data
4. Restore backup
5. Verify data integrity

### Manual Test Procedure

1. **Create Test Data**:
   - Add sample trades via Web UI
   - Upload test CAD files
   - Create test validations

2. **Run Backup**:
   ```bash
   # Trigger manual backup via System Manager
   curl -X POST http://localhost:8000/api/system/backup
   ```

3. **Verify Backup Created**:
   ```bash
   ls -lh backups/
   # Should see timestamped .tar.gz and .json files
   ```

4. **Test Restore**:
   ```bash
   # Delete test data
   # Run restore
   python scripts/restore_backup.py backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz
   ```

5. **Verify Data Restored**:
   - Check trades exist in Web UI
   - Verify CAD files present
   - Confirm validations restored

---

## 🛠️ Troubleshooting

### Issue: Backup file not found

**Cause**: Backup may not have been created or wrong path  
**Solution**:
```bash
# List all backups
ls -lh backups/

# Check System Manager logs
docker-compose logs system-manager
```

### Issue: Database restore fails

**Cause**: PostgreSQL not running or connection issues  
**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Start PostgreSQL if needed
docker-compose up -d postgres

# Verify connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: Checksum mismatch

**Cause**: Backup file corrupted  
**Solution**:
- Use a different backup file
- Check disk space and file system integrity
- Re-run backup

### Issue: Services won't start after restore

**Cause**: Configuration or dependency issues  
**Solution**:
```bash
# Check logs
docker-compose logs

# Restart services
docker-compose restart

# If still failing, rebuild
docker-compose down
docker-compose up --build -d
```

---

## 📊 Backup Management

### Create Manual Backup

```python
from agents.system_manager.src.backup import BackupService

bs = BackupService()
bs.add_backup_path("storage")
backup_file = bs.create_backup_archive()
print(f"Backup created: {backup_file}")
```

### List Backups

```bash
ls -lh backups/vulcan_backup_*.tar.gz
```

### Get Backup Info

```python
from agents.system_manager.src.backup import BackupService

bs = BackupService()
info = bs.get_backup_info('backups/vulcan_backup_YYYYMMDD_HHMMSS.tar.gz')
print(f"Created: {info['created_at']}")
print(f"Size: {info['size_bytes'] / 1024 / 1024:.2f} MB")
```

### Clean Old Backups

```python
from agents.system_manager.src.backup import BackupService

bs = BackupService()
deleted = bs.cleanup_old_backups(retention_days=7)
print(f"Deleted {len(deleted)} old backups")
```

---

## 🎯 Recovery Time Objectives (RTO)

- **Storage Restore**: ~5 minutes (depends on data size)
- **Database Restore**: ~2 minutes
- **Total RTO**: ~10 minutes for complete restoration

---

## 📝 Best Practices

1. **Regular Testing**: Test restore procedure monthly
2. **Off-site Backups**: Consider Google Drive sync for disaster recovery
3. **Monitor Backups**: Check backup logs daily
4. **Verify Integrity**: Run verification after each backup
5. **Document Changes**: Update this guide when procedures change

---

## 🔗 Related Scripts

- [restore_backup.py](file:///c:/Users/DCornealius/Documents/GitHub/Project_Vulcan_Fresh/scripts/restore_backup.py) - Automated restore
- [backup_database.py](file:///c:/Users/DCornealius/Documents/GitHub/Project_Vulcan_Fresh/scripts/backup_database.py) - Database backup
- [test_backup_restore.py](file:///c:/Users/DCornealius/Documents/GitHub/Project_Vulcan_Fresh/scripts/test_backup_restore.py) - Automated testing
- [backup.py](file:///c:/Users/DCornealius/Documents/GitHub/Project_Vulcan_Fresh/agents/system_manager/src/backup.py) - Backup service

