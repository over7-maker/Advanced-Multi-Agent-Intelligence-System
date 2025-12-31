# 💾 AMAS Project Backup Instructions

**Date**: 2025-01-20  
**Version**: v1.1.0

---

## 📦 Backup Files Created

### 1. **Git Bundle Backup**
**File**: `backups/amas-v1.1.0-backup.bundle`

**Description**: Complete git repository backup including all branches, tags, and history.

**Usage**:
```bash
# Restore from bundle
git clone amas-v1.1.0-backup.bundle amas-restored
cd amas-restored
git checkout main
```

**Size**: ~50-100 MB (includes full git history)

### 2. **Source Code Archive**
**File**: `backups/amas-v1.1.0-source.zip`

**Description**: Complete source code snapshot at release v1.1.0.

**Usage**:
```bash
# Extract archive
unzip amas-v1.1.0-source.zip
cd amas-v1.1.0
```

**Size**: ~10-20 MB (source code only, no git history)

---

## 🔄 Backup Strategy

### Automatic Backups

1. **Git Bundle** (Recommended)
   - Contains full git history
   - Can restore entire repository
   - Includes all branches and tags

2. **Source Archive**
   - Lightweight backup
   - Source code only
   - Easy to share

### Manual Backup Options

#### Option 1: Git Bundle (Complete)
```bash
git bundle create backups/amas-v1.1.0-backup.bundle --all
```

#### Option 2: Source Archive (Lightweight)
```bash
git archive --format=zip --output=backups/amas-v1.1.0-source.zip --prefix=amas-v1.1.0/ HEAD
```

#### Option 3: Full Directory Copy
```bash
# Copy entire project directory
xcopy /E /I /H /Y "C:\Users\Admin\AMAS\Advanced-Multi-Agent-Intelligence-System" "D:\Backups\AMAS-v1.1.0"
```

#### Option 4: Docker Image Backup
```bash
# Save Docker images
docker save amas-backend:latest -o backups/amas-backend-v1.1.0.tar
docker save amas-frontend:latest -o backups/amas-frontend-v1.1.0.tar
```

---

## 📍 Backup Locations

### Local Backups
- **Directory**: `backups/`
- **Files**:
  - `amas-v1.1.0-backup.bundle` (Git bundle)
  - `amas-v1.1.0-source.zip` (Source archive)

### Remote Backups (Recommended)

1. **GitHub Repository**
   - All code is in git repository
   - Tagged releases: `v1.1.0`
   - Full history preserved

2. **Cloud Storage** (Manual)
   - Upload `backups/` directory to:
     - Google Drive
     - Dropbox
     - OneDrive
     - AWS S3
     - Azure Blob Storage

3. **External Drive**
   - Copy `backups/` directory to external drive
   - Store in safe location

---

## 🔐 Backup Security

### Sensitive Data

⚠️ **Important**: Backup files may contain:
- Environment variables (if `.env` is included)
- API keys (if committed)
- Database credentials

### Security Recommendations

1. **Exclude Sensitive Files**
   - `.env` files are in `.gitignore`
   - API keys should not be in repository
   - Use environment variables for secrets

2. **Encrypt Backups** (Optional)
   ```bash
   # Encrypt bundle
   7z a -pPASSWORD backups/amas-v1.1.0-backup.bundle.7z backups/amas-v1.1.0-backup.bundle
   ```

3. **Secure Storage**
   - Store backups in encrypted location
   - Use secure cloud storage
   - Limit access to backup files

---

## 📋 Backup Checklist

### Before Backup
- [x] All changes committed
- [x] Version numbers updated
- [x] Release tag created
- [x] Tests passing
- [x] Documentation updated

### Backup Creation
- [x] Git bundle created
- [x] Source archive created
- [x] Backup files verified
- [x] Backup location documented

### After Backup
- [ ] Verify backup files exist
- [ ] Test restore from bundle
- [ ] Upload to remote storage
- [ ] Document backup location
- [ ] Update backup schedule

---

## 🔄 Restore Instructions

### From Git Bundle

```bash
# Clone from bundle
git clone backups/amas-v1.1.0-backup.bundle amas-restored
cd amas-restored

# Checkout specific version
git checkout v1.1.0

# Or checkout main branch
git checkout main
```

### From Source Archive

```bash
# Extract archive
unzip backups/amas-v1.1.0-source.zip
cd amas-v1.1.0

# Install dependencies
pip install -r requirements.txt
cd frontend && npm install
```

### From GitHub

```bash
# Clone repository
git clone https://github.com/over7-maker/Advanced-Multi-Agent-Intelligence-System.git
cd Advanced-Multi-Agent-Intelligence-System

# Checkout release
git checkout v1.1.0
```

---

## 📅 Backup Schedule

### Recommended Schedule

- **Daily**: Git commits (automatic)
- **Weekly**: Git bundle backup
- **Monthly**: Full backup to remote storage
- **Before Major Releases**: Complete backup + tag

### Automated Backup Script

Create `scripts/backup.sh` or `scripts/backup.bat`:

```bash
#!/bin/bash
# Backup script for AMAS project

DATE=$(date +%Y%m%d)
VERSION=$(git describe --tags --abbrev=0)

# Create backups directory
mkdir -p backups

# Create git bundle
git bundle create backups/amas-${VERSION}-${DATE}.bundle --all

# Create source archive
git archive --format=zip --output=backups/amas-${VERSION}-${DATE}-source.zip --prefix=amas-${VERSION}/ HEAD

echo "Backup completed: backups/amas-${VERSION}-${DATE}.bundle"
echo "Source archive: backups/amas-${VERSION}-${DATE}-source.zip"
```

---

## ✅ Verification

### Verify Backup Integrity

```bash
# Verify git bundle
git bundle verify backups/amas-v1.1.0-backup.bundle

# Test restore
git clone backups/amas-v1.1.0-backup.bundle test-restore
cd test-restore
git log --oneline -5
```

### Verify Source Archive

```bash
# Extract and verify
unzip -t backups/amas-v1.1.0-source.zip
unzip backups/amas-v1.1.0-source.zip -d test-extract
ls test-extract/amas-v1.1.0/
```

---

## 📊 Backup Size Estimates

| Backup Type | Size | Description |
|-------------|------|-------------|
| Git Bundle | ~50-100 MB | Full git history, all branches |
| Source Archive | ~10-20 MB | Source code only |
| Docker Images | ~500 MB - 2 GB | Container images |
| Full Directory | ~200-500 MB | Complete project directory |

---

## 🎯 Best Practices

1. **Regular Backups**
   - Commit frequently
   - Create backups before major changes
   - Tag releases

2. **Multiple Locations**
   - Local backup (backups/)
   - Remote backup (GitHub)
   - Cloud storage (optional)

3. **Version Control**
   - Use git tags for releases
   - Document backup dates
   - Keep backup history

4. **Testing**
   - Test restore procedures
   - Verify backup integrity
   - Document restore steps

---

## 📞 Support

If you need help with backups or restoration:
- Check `RELEASE_v1.1.0.md` for release information
- Review git documentation for bundle usage
- Contact project maintainers

---

**Backup Created**: 2025-01-20  
**Version**: v1.1.0  
**Status**: ✅ Complete

