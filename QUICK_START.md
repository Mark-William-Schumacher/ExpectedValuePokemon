# 🚀 Quick Start Guide

> **Setting up on a new machine?** See [NEW_MACHINE_SETUP.md](./NEW_MACHINE_SETUP.md) for complete step-by-step instructions!

---

## Prerequisites Check

Before running, ensure you have:
- ✅ **Python 3.8+** installed and in PATH
- ✅ **Node.js 18 LTS** installed (for web app)
- ✅ **Database populated** (`python core_module/update_gradable_cards.py`)
- ✅ **Images downloaded** (for web app: `python download_and_cache_images.py`)

**Quick check:**
```powershell
.\start_servers.ps1 -SetupOnly
```

---

## Starting the Application

### Easiest Way (Recommended)
```powershell
.\start_servers.ps1
```
Then choose:
1. Desktop App (Python Tkinter)
2. Web App (React + Flask)

---

### Direct Start Commands

#### Desktop App
```powershell
.\start_servers.ps1 -Desktop
```
Or manually:
```powershell
$env:PYTHONPATH = (Get-Location).Path
python core_module/ui/showCards.py
```

#### Web App
```powershell
.\start_servers.ps1 -Web
```
Or manually (requires 2 terminals):

**Terminal 1 - Backend:**
```powershell
$env:PYTHONPATH = (Get-Location).Path
python web/backend/app.py
```

**Terminal 2 - Frontend:**
```powershell
cd web/frontend
npm start
```

**URLs:**
- Backend API: http://127.0.0.1:5000
- Frontend App: http://localhost:3000

---

## Data Management

### Update Database
```powershell
python core_module/update_gradable_cards.py
```
**When to run:** Weekly, or when you need fresh card prices/data
**Time:** 10-30 minutes (depends on API rate limits)
**What it does:** Fetches prices, PSA populations, calculates grading profitability

### Download Images
```powershell
python download_and_cache_images.py
```
**When to run:** After database updates, or if images are missing
**Time:** 10-20 minutes (only downloads missing images)
**Where:** Saves to `web/backend/static/assets/images/`

---

## Script Options

### Interactive Mode
```powershell
.\start_servers.ps1
```
Prompts you to choose Desktop or Web app

### Direct Start
```powershell
.\start_servers.ps1 -Desktop      # Start desktop app
.\start_servers.ps1 -Web          # Start web app
```

### With Data Updates
```powershell
.\start_servers.ps1 -UpdateData -Web          # Update DB, then start web
.\start_servers.ps1 -DownloadImages -Web      # Download images, then start web
```

### Setup & Checks
```powershell
.\start_servers.ps1 -SetupOnly    # Check prerequisites only
.\start_servers.ps1 -SkipChecks -Web  # Fast start, skip all checks
```

---

## Common Issues & Quick Fixes

### "npm is not recognized"
**Problem:** Node.js not in PATH (especially in PyCharm terminal)

**Solutions:**
1. Restart PyCharm after installing Node.js
2. Add to PATH for current session:
   ```powershell
   $env:Path = "C:\Program Files\nodejs;$env:Path"
   ```
3. Install Node.js 18 LTS from [nodejs.org](https://nodejs.org/)

---

### Images Not Loading (Broken Links)
**Problem:** Card images not downloaded

**Solution:**
```powershell
python download_and_cache_images.py
```

Images are served by Flask backend at:
`http://127.0.0.1:5000/static/assets/images/<filename>`

---

### Backend 500 Errors
**Problem:** Database missing or not populated

**Solution:**
```powershell
python core_module/update_gradable_cards.py
```

---

### Port Already in Use
**Problem:** Flask (5000) or React (3000) port busy

**Solution:**
```powershell
# Kill Python processes
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Kill Node processes
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
```

---

### WebSocket Connection Failed
**Problem:** Browser console shows: `WebSocket connection to 'ws://localhost:3000/ws' failed`

**This is normal** - React's hot reload feature. App still works fine.

---

## What Each Script Does

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `start_servers.ps1` | Automated setup & launch | Every time you want to start the app |
| `update_gradable_cards.py` | Updates database with fresh card data | Weekly, or when you need new data |
| `download_and_cache_images.py` | Downloads card images for web app | After DB updates, or if images missing |
| `showCards.py` | Desktop app (Tkinter) | Simpler alternative to web app |

---

## File Reference

| File | Purpose |
|------|---------|
| `NEW_MACHINE_SETUP.md` | **Complete setup guide for new machines** |
| `QUICK_START.md` | Quick commands reference (this file) |
| `SETUP_GUIDE.md` | General setup instructions |
| `START_SERVERS.md` | Server startup details |
| `LOCAL_IMAGES_SOLUTION.md` | Image serving solution |
| `BACKEND_FIX_SUMMARY.md` | Backend troubleshooting |

---

## URLs

- **Backend API:** http://127.0.0.1:5000
- **Frontend App:** http://localhost:3000
- **Node.js Download:** https://nodejs.org/ (Get version 18 LTS)
- **Python Download:** https://www.python.org/


