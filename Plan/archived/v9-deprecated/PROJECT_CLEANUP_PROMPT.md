# 🧹 Project Cleanup: Remove Unused Files

> **IMPORTANT:** This should only be done AFTER UI improvements are complete and tested!

---

## 📋 Overview

The project has accumulated unused files during development. We'll identify them, review together, and safely archive them in a "check zone" before final deletion.

**Safety First:**
- ✅ All files moved to `/check-zone` first
- ✅ You review the list before moving
- ✅ We keep check zone for 1 week
- ✅ Easy to restore if needed

---

## 🎯 Step 1: Create Check Zone Directory

```bash
cd /path/to/MarketPulse

# Create check zone structure
mkdir -p check-zone/backend
mkdir -p check-zone/frontend
mkdir -p check-zone/data
mkdir -p check-zone/docs
mkdir -p check-zone/scripts

# Create tracking file
touch check-zone/MOVED_FILES.txt
echo "# Files moved to check zone on $(date)" > check-zone/MOVED_FILES.txt
echo "# Review this list before permanent deletion" >> check-zone/MOVED_FILES.txt
echo "" >> check-zone/MOVED_FILES.txt
```

---

## 🔍 Step 2: Identify Potentially Unused Files

### **2.1: Create Detection Script**

Save this as `scripts/find_unused_files.sh`:

```bash
#!/bin/bash
# Script to identify potentially unused files in MarketPulse project

echo "════════════════════════════════════════════════"
echo "🔍 Scanning for Unused Python Files"
echo "════════════════════════════════════════════════"
echo ""

# Find Python files not imported anywhere
find backend -name "*.py" -type f | while read file; do
  basename=$(basename "$file" .py)
  
  # Skip special files
  if [ "$basename" = "__init__" ] || [ "$basename" = "main" ] || [ "$basename" = "config" ]; then
    continue
  fi
  
  # Check if imported anywhere in backend
  grep_count=$(grep -r "import.*$basename\|from.*$basename" backend --include="*.py" 2>/dev/null | grep -v "^Binary" | wc -l)
  
  if [ $grep_count -eq 0 ]; then
    echo "❌ UNUSED: $file"
    echo "   Reason: Not imported in any Python file"
  fi
done

echo ""
echo "════════════════════════════════════════════════"
echo "🔍 Scanning for Unused Data Files"
echo "════════════════════════════════════════════════"
echo ""

# Find CSV/JSON files not referenced in code
if [ -d "data" ]; then
  find data -name "*.csv" -o -name "*.json" | while read file; do
    basename=$(basename "$file")
    
    # Check if referenced in Python code
    grep_count=$(grep -r "$basename" backend --include="*.py" 2>/dev/null | grep -v "^Binary" | wc -l)
    
    if [ $grep_count -eq 0 ]; then
      echo "❌ UNUSED: $file"
      echo "   Reason: Not referenced in backend code"
    fi
  done
fi

echo ""
echo "════════════════════════════════════════════════"
echo "🔍 Scanning for Old/Backup Files"
echo "════════════════════════════════════════════════"
echo ""

# Find obvious backup/old files
find . -type f \( \
  -name "*_old*" -o \
  -name "*_backup*" -o \
  -name "*.bak" -o \
  -name "*_v[0-9]*" -o \
  -name "*copy*" -o \
  -name "*.tmp" -o \
  -name "*~" \
\) | grep -v "node_modules" | grep -v ".git" | grep -v "check-zone" | while read file; do
  echo "❌ BACKUP/OLD: $file"
  echo "   Reason: Backup or versioned filename"
done

echo ""
echo "════════════════════════════════════════════════"
echo "🔍 Scanning for Duplicate Documentation"
echo "════════════════════════════════════════════════"
echo ""

# Find duplicate or old documentation
if [ -d "docs" ]; then
  find docs -type f \( \
    -name "*draft*" -o \
    -name "*WIP*" -o \
    -name "*notes*" -o \
    -name "TODO*" \
  \) | while read file; do
    echo "❌ OLD DOC: $file"
    echo "   Reason: Draft or temporary documentation"
  done
fi

echo ""
echo "════════════════════════════════════════════════"
echo "🔍 Scanning for Unused Frontend Files"
echo "════════════════════════════════════════════════"
echo ""

# Find unused React components (not imported anywhere)
if [ -d "frontend/src" ]; then
  find frontend/src -name "*.tsx" -o -name "*.jsx" | while read file; do
    basename=$(basename "$file" .tsx)
    basename=$(basename "$basename" .jsx)
    
    # Skip index and App files
    if [ "$basename" = "index" ] || [ "$basename" = "App" ] || [ "$basename" = "main" ]; then
      continue
    fi
    
    # Check if imported anywhere
    grep_count=$(grep -r "import.*$basename\|from.*$basename" frontend/src --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" 2>/dev/null | grep -v "^Binary" | wc -l)
    
    if [ $grep_count -eq 0 ]; then
      echo "❌ UNUSED: $file"
      echo "   Reason: Component not imported anywhere"
    fi
  done
fi

echo ""
echo "════════════════════════════════════════════════"
echo "✅ Scan Complete"
echo "════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Review the output above"
echo "2. Create files_to_archive.txt with files to move"
echo "3. Send me the list for review"
echo ""
```

### **2.2: Run the Detection Script**

```bash
# Make it executable
chmod +x scripts/find_unused_files.sh

# Run it and save output
./scripts/find_unused_files.sh > unused_files_report.txt

# View the report
cat unused_files_report.txt
```

---

## 📝 Step 3: Create Archive List

### **3.1: Review the Report**

Open `unused_files_report.txt` and review each file marked as unused.

### **3.2: Create Archive List**

Create a file called `files_to_archive.txt` with this format:

```
# Format: filepath - [reason why unused]

# Backend Files
backend/old_processor.py - Old version before refactor
backend/utils/deprecated_helpers.py - Replaced by new utils module
backend/tests/old_test.py - Test file no longer used

# Data Files
data/raw/transactions_v1.csv - Old dataset, v2 is current
data/processed/backup_20240901.json - Backup from September, no longer needed

# Documentation
docs/old_design.md - Outdated design doc
docs/notes_draft.md - Personal notes, not needed in repo

# Frontend Files
frontend/src/components/OldDashboard.tsx - Replaced by new Dashboard
frontend/public/old_logo.png - Old branding

# Scripts
scripts/temp_fix.py - Temporary script, issue resolved
```

**Important Guidelines:**

✅ **DO include:**
- Files with "old", "backup", "v1", "temp" in name
- Duplicate functionality (old versions)
- Personal notes/drafts
- Test files not in use
- Commented-out entire files

❌ **DO NOT include:**
- `__init__.py` files (needed for Python modules)
- `config.py` or configuration files
- `requirements.txt` or `package.json`
- Any file imported in working code
- Documentation that's still relevant

---

## 📤 Step 4: Send Me the List for Review

**DO NOT MOVE ANYTHING YET!**

Send me your `files_to_archive.txt` so I can review it.

**Format your message like this:**

```
Hey, I ran the unused files scan. Here's what I found:

[Paste contents of files_to_archive.txt]

Total files to archive: [count]

Can you review this list before I move them to check-zone?
```

---

## 🚚 Step 5: Move Files to Check Zone (After My Approval)

**Only do this AFTER I approve the list!**

### **5.1: Create Move Script**

Save this as `scripts/move_to_check_zone.sh`:

```bash
#!/bin/bash
# Script to safely move unused files to check zone

CHECK_ZONE="check-zone"
LOG_FILE="$CHECK_ZONE/MOVED_FILES.txt"

# Check if files_to_archive.txt exists
if [ ! -f "files_to_archive.txt" ]; then
  echo "❌ Error: files_to_archive.txt not found"
  exit 1
fi

echo "════════════════════════════════════════════════"
echo "🚚 Moving Files to Check Zone"
echo "════════════════════════════════════════════════"
echo ""

# Read each line from files_to_archive.txt
while IFS= read -r line; do
  # Skip comments and empty lines
  if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
    continue
  fi
  
  # Extract filepath (before the dash)
  filepath=$(echo "$line" | cut -d'-' -f1 | xargs)
  
  # Check if file exists
  if [ ! -f "$filepath" ] && [ ! -d "$filepath" ]; then
    echo "⚠️  SKIP: $filepath (not found)"
    continue
  fi
  
  # Determine destination
  dest="$CHECK_ZONE/$filepath"
  dest_dir=$(dirname "$dest")
  
  # Create destination directory
  mkdir -p "$dest_dir"
  
  # Move the file
  mv "$filepath" "$dest"
  
  if [ $? -eq 0 ]; then
    echo "✅ MOVED: $filepath → $dest"
    echo "$filepath - Moved on $(date)" >> "$LOG_FILE"
  else
    echo "❌ FAILED: $filepath"
  fi
  
done < files_to_archive.txt

echo ""
echo "════════════════════════════════════════════════"
echo "✅ Move Complete"
echo "════════════════════════════════════════════════"
echo ""
echo "Files moved to: $CHECK_ZONE/"
echo "Log file: $LOG_FILE"
echo ""
echo "Next steps:"
echo "1. Test the application thoroughly"
echo "2. If everything works, keep check-zone for 1 week"
echo "3. If something breaks, restore from check-zone"
echo ""
```

### **5.2: Execute the Move**

```bash
# Make script executable
chmod +x scripts/move_to_check_zone.sh

# Run it
./scripts/move_to_check_zone.sh

# Review what was moved
cat check-zone/MOVED_FILES.txt
```

---

## 🧪 Step 6: Test Everything

**Critical: Test thoroughly after moving files!**

### **6.1: Backend Tests**

```bash
cd backend

# Run all tests
pytest

# Start the backend
uvicorn app.main:app --reload

# Check logs for import errors
# Visit http://localhost:8000/docs
```

### **6.2: Frontend Tests**

```bash
cd frontend

# Install dependencies (check nothing broke)
npm install

# Start frontend
npm run dev

# Test all pages:
# - Dashboard
# - Customers  
# - Products
# - Revenue
```

### **6.3: Check for Errors**

Look for:
- ❌ Import errors
- ❌ Missing file errors
- ❌ 404s on frontend
- ❌ API endpoints failing

**If you see ANY errors:**
```bash
# Restore the problematic file
cp check-zone/path/to/file.py path/to/file.py

# Update files_to_archive.txt to remove it
# Re-run the move script
```

---

## ✅ Step 7: Commit the Cleanup

**Only commit if everything works!**

```bash
# Stage the deletions
git add -A

# Commit
git commit -m "chore: Archive unused files to check-zone

- Moved [X] unused Python files
- Moved [Y] old data files  
- Moved [Z] deprecated components
- All tests passing
- Application working correctly

Files moved to check-zone/ for 1-week review period."

# Push to dev branch
git push origin dev-ui-improvements
```

---

## 📦 Step 8: Final Archive (After 1 Week)

**Wait 1 week to ensure nothing breaks in production.**

After 1 week, if everything still works:

```bash
# Delete check-zone permanently
rm -rf check-zone/

# Commit
git add -A
git commit -m "chore: Remove check-zone after successful 1-week review"
git push
```

**Or, compress it for long-term storage:**

```bash
# Create archive
tar -czf archived_files_$(date +%Y%m%d).tar.gz check-zone/

# Move to safe location
mv archived_files_*.tar.gz ~/backups/

# Delete check-zone
rm -rf check-zone/

# Commit
git add -A
git commit -m "chore: Compress and archive check-zone files"
git push
```

---

## 🚨 Emergency Restore Procedures

### **If Something Breaks:**

```bash
# Option 1: Restore a single file
cp check-zone/path/to/file.py path/to/file.py
git add path/to/file.py
git commit -m "fix: Restore needed file from check-zone"

# Option 2: Restore everything
rsync -av check-zone/ ./
rm -rf check-zone/
git add -A
git commit -m "revert: Restore all files from check-zone"

# Option 3: Revert the entire commit
git revert HEAD
git push
```

---

## 📊 Expected Results

### **Typical Cleanup for MarketPulse:**

**Backend:**
- 5-10 old Python scripts
- 2-3 unused utility files
- 3-5 test files not in use

**Frontend:**
- 3-5 old components
- 2-3 unused assets (images, icons)
- 1-2 old CSS files

**Data:**
- 2-4 old CSV versions
- 1-2 backup JSON files

**Docs:**
- 3-5 draft documents
- 2-3 personal notes

**Total:** Expect to archive 20-30 files

**Size reduction:** Usually 5-10% of repo size

---

## ✅ Success Checklist

Before merging to main:

```
□ Ran find_unused_files.sh script
□ Created files_to_archive.txt with reasons
□ Sent list to Guy for review
□ Got approval from Guy
□ Ran move_to_check_zone.sh script
□ Tested backend (pytest passes)
□ Tested frontend (all pages load)
□ No import errors in logs
□ All API endpoints working
□ Committed changes to dev branch
□ Will wait 1 week before final deletion
□ Have emergency restore procedure ready
```

---

## 🎯 Summary

**What we're doing:**
1. ✅ Identify unused files automatically
2. ✅ Review list together (you + me)
3. ✅ Move to check-zone (not delete yet)
4. ✅ Test thoroughly
5. ✅ Keep check-zone for 1 week
6. ✅ Delete permanently after 1 week

**Why this is safe:**
- Files moved to check-zone, not deleted
- Easy to restore if needed
- 1-week safety buffer
- Everything tested before commit
- Can revert entire change if needed

**Why this is professional:**
- Shows good repo maintenance
- Clean codebase for recruiters
- Faster builds and deployments
- Better project structure
- Demonstrates attention to detail

---

**Ready to start? Run Step 1 to create the check-zone directory!** 🚀
