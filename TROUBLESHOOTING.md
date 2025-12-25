# 🔧 Troubleshooting Guide

## Issue #1: Cannot Push to GitHub ❌

### Error Message
```
fatal: unable to access 'https://github.com/...': Could not resolve host: github.com
```

### Root Cause
Intermittent DNS resolution failure. Your DNS server (10.179.243.243) is unstable.

### ✅ Solutions (Try in Order)

#### Solution 1: Flush DNS Cache (Quickest)
```powershell
# Flush DNS
ipconfig /flushdns

# Retry push
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet
git push -u origin main
```

#### Solution 2: Add GitHub to Hosts File (Bypass DNS)
```powershell
# Open PowerShell as Administrator
# Add GitHub IP to hosts file
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "`n20.87.245.0 github.com"

# Retry push
git push -u origin main
```

**To Remove Later** (optional):
- Open `C:\Windows\System32\drivers\etc\hosts` in Notepad (as Admin)
- Delete the line `20.87.245.0 github.com`

#### Solution 3: Use SSH Instead of HTTPS (Best Long-Term)
```powershell
# 1. Generate SSH key (press Enter 3 times for no passphrase)
ssh-keygen -t ed25519 -C "nkernest666@gmail.com" -f C:\Users\ADMIN\.ssh\id_ed25519 -N ""

# 2. Copy public key
Get-Content C:\Users\ADMIN\.ssh\id_ed25519.pub | clip

# 3. Add to GitHub:
#    - Go to https://github.com/settings/keys
#    - Click "New SSH key"
#    - Paste the key from clipboard
#    - Click "Add SSH key"

# 4. Change remote to SSH
git remote set-url origin git@github.com:ernestonkunzimana/SEFC-Net-Self-Evolving-Federated-Cognitive-Network.git

# 5. Test connection
ssh -T git@github.com

# 6. Push
git push -u origin main
```

#### Solution 4: Use GitHub CLI (Alternative)
```powershell
# Install GitHub CLI
winget install GitHub.cli

# Authenticate
gh auth login

# Push
gh repo sync
```

#### Solution 5: Push via GitHub Desktop
- Download GitHub Desktop: https://desktop.github.com/
- Open repository in GitHub Desktop
- Click "Push origin"

---

## Issue #2: Cannot Run Edge Resilience Tests ❌

### Error Message
```
ModuleNotFoundError: No module named 'edge_resilience'
```

### Root Cause
Python can't find the `edge_resilience` module because it's looking in the wrong directory.

### ✅ Solutions (Choose One)

#### Solution 1: Run from Correct Directory (Quickest)
```powershell
# Change to SEFCNet directory (where edge_resilience folder is)
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet

# Run test
python edge_resilience/test_edge_resilience.py
```

#### Solution 2: Set PYTHONPATH (One-Time)
```powershell
# Set PYTHONPATH to include SEFCNet directory
$env:PYTHONPATH = "C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet"

# Run test from anywhere
python C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet\edge_resilience\test_edge_resilience.py
```

#### Solution 3: Install as Package (Best Long-Term)
```powershell
# Install SEFCNet as editable package
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet
pip install -e .

# Now run from anywhere
python -m edge_resilience.test_edge_resilience
```

#### Solution 4: Create Test Runner Script
Create `test_edge.bat` in project root:
```batch
@echo off
cd /d C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet
python edge_resilience/test_edge_resilience.py
pause
```

Then just double-click `test_edge.bat` to run tests.

---

## Quick Test Command (Copy-Paste Ready)

```powershell
# Test edge resilience (from project root)
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet ; python edge_resilience/test_edge_resilience.py

# Or with PYTHONPATH
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet ; $env:PYTHONPATH="$PWD\SEFCNet" ; python -c "from edge_resilience import get_connectivity_manager; print('✅ Import successful!')"
```

---

## Verification Commands

### Check Git Status
```powershell
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet
git status
git log --oneline -3
```

### Check Remote
```powershell
git remote -v
git ls-remote origin
```

### Check Network
```powershell
# Ping GitHub
ping github.com -n 2

# Check DNS
nslookup github.com

# Test HTTPS connection
curl -I https://github.com 2>&1 | Select-String "HTTP"
```

### Check Python Environment
```powershell
# Check Python version
python --version

# Check installed packages
pip list | Select-String "tensorflow|torch|numpy"

# Check PYTHONPATH
$env:PYTHONPATH
```

---

## Current System Status

### ✅ What's Working
- Git repository initialized
- 2 commits created locally
- 260 files tracked
- Dependencies installed
- Virtual environment active
- Edge resilience module created

### ⏳ Pending
- Push to GitHub (network issue)
- Test edge resilience module (path issue)

### 📊 Commits Ready to Push
```
Commit 1 (f1de689): Initial commit - 251 files
Commit 2 (35e6528): Edge Resilience Module - 9 files

Total: 260 files, 1651+ lines added
```

---

## Emergency Backup (If All Else Fails)

### Export Commits as Patches
```powershell
cd C:\Users\ADMIN\OneDrive\Desktop\SEFCNet

# Export all commits as patches
git format-patch --root -o patches/

# Later, apply patches to a new repo:
# git am patches/*.patch
```

### Create ZIP Backup
```powershell
# Create backup
Compress-Archive -Path C:\Users\ADMIN\OneDrive\Desktop\SEFCNet -DestinationPath C:\Users\ADMIN\Desktop\SEFCNet-backup-$(Get-Date -Format 'yyyyMMdd').zip
```

---

## Need More Help?

### Check Logs
```powershell
# Git verbose output
$env:GIT_CURL_VERBOSE=1
$env:GIT_TRACE=1
git push -u origin main --verbose 2>&1 | Out-File git-debug.log
```

### System Information
```powershell
# Network adapters
Get-NetAdapter | Select-Object Name, Status, LinkSpeed

# DNS servers
Get-DnsClientServerAddress | Where-Object {$_.InterfaceAlias -notlike "*Loopback*"}

# Python path
python -c "import sys; print('\n'.join(sys.path))"
```

---

**Last Updated**: December 25, 2025  
**Status**: Edge Resilience Module Complete, Ready to Push
