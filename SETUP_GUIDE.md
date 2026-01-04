# 🚀 New Machine Setup Guide
**Last Updated**: January 2026

---

- [START_SERVERS.md](./START_SERVERS.md) - Server startup guide
- [LOCAL_IMAGES_SOLUTION.md](./LOCAL_IMAGES_SOLUTION.md) - Image serving details
- [BACKEND_FIX_SUMMARY.md](./BACKEND_FIX_SUMMARY.md) - Backend 500 error resolution

## Support & Documentation

---

| **Check Python** | `python --version` |
| **Check Node** | `node --version` |
| **Frontend Only** | `cd web/frontend; npm start` |
| **Backend Only** | `python web/backend/app.py` |
| **Web App** | `.\start_servers.ps1` |
| **Desktop App** | `python core_module/ui/showCards.py` |
| **Download Images** | `python download_and_cache_images.py` |
| **Update Database** | `python core_module/update_gradable_cards.py` |
|------|---------|
| Task | Command |

## Quick Reference Commands

---

```
└── requirements.txt              # Python dependencies
├── start_servers.ps1             # Automated startup
├── download_and_cache_images.py  # Image downloader
│       └── package.json
│       ├── src/App.jsx           # React app
│   └── frontend/
│   │   └── static/assets/images/ # Card images
│   │   ├── app.py                # Flask server
│   ├── backend/
├── web/
│   └── update_gradable_cards.py  # Database updater
│   │   └── showCards.py          # Desktop app
│   ├── ui/
├── core_module/
ExpectedValuePokemon/
```

## File Structure Reference

---

```
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force
# Kill Node processes

Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
# Kill Python processes
```powershell
**Solution**:
**Problem**: Flask (5000) or React (3000) port busy  
### Port Already in Use

```
python download_and_cache_images.py
```powershell
**Solution**:
**Problem**: Images not downloaded  
### Images Not Loading in Web App

```
python core_module/update_gradable_cards.py
```powershell
**Solution**:
**Problem**: Database not populated  
### Backend 500 Errors

```
pip install flask-cors
```powershell
**Solution**:
### "No module named 'flask_cors'"

3. Verify with `node --version`
2. Or restart PyCharm after Node.js installation
   ```
   $env:Path = "C:\Program Files\nodejs;$env:Path"
   ```powershell
1. If in PyCharm terminal:
**Solution**:
**Problem**: Node.js not in PATH  
### "npm is not recognized"

## Troubleshooting

---

```
.\start_servers.ps1
# Start web app

python download_and_cache_images.py
# Download any new card images

python core_module/update_gradable_cards.py
# Update card data from API
```powershell
### Regular Updates (Weekly/Monthly)

```
.\start_servers.ps1
# 7. Start the web app

python download_and_cache_images.py
# 6. Download images for web app

python core_module/update_gradable_cards.py
# 5. Update card database (REQUIRED FIRST TIME)

cd ../..
npm install
cd web/frontend
# 4. Install frontend dependencies

pip install flask-cors
pip install -r requirements.txt
# 3. Install Python dependencies

# 2. Restart terminal/PyCharm
# 1. Install Node.js 18 LTS from nodejs.org
```powershell
### Brand New Machine

## Complete Workflow Example

---

Frontend: http://localhost:3000
```
npm start
cd web/frontend
```powershell
**Terminal 2 - Frontend:**

Backend: http://127.0.0.1:5000
```
python web/backend/app.py
$env:PYTHONPATH = (Get-Location).Path
```powershell
**Terminal 1 - Backend:**
#### Manual Start

4. Open browser automatically
3. Start React frontend (port 3000)
2. Start Flask backend (port 5000)
1. Check if Node.js is installed
This will:
```
.\start_servers.ps1
```powershell
#### Quick Start (Automated)

### Option B: Use Web App (React + Flask)

- ✅ Fast and lightweight
- ✅ No web server needed
- ✅ Standalone desktop application
```
python core_module/ui/showCards.py
```powershell
### Option A: Use Python Desktop App (Tkinter)

## Daily Usage

---

**⏱️ Expected time**: 5-15 minutes (first time only)

- ✅ Skip already downloaded images
- ✅ Download all card images to `web/backend/static/assets/images/`
- ✅ Generate cache with local_image fields
This will:

```
python download_and_cache_images.py
```powershell
### Step 4: Download Card Images for Web App

**⏱️ Expected time**: 10-30 minutes depending on data freshness

- ✅ Populate the database with gradable cards
- ✅ Calculate profitability metrics
- ✅ Update PSA population data
- ✅ Fetch latest card prices from API
This will:

```
python core_module/update_gradable_cards.py
```powershell

**IMPORTANT**: Run this first to populate your database with card data!
### Step 3: Update Card Database

```
cd ../..
npm install
cd web/frontend
```powershell
### Step 2: Install Frontend Dependencies

```
pip install flask-cors
# Also install flask-cors (if not in requirements)

pip install -r requirements.txt
# Install Python packages

cd C:\Users\905mw\PycharmProjects\ExpectedValuePokemon
# Navigate to project root
```powershell
### Step 1: Install Python Dependencies

## Initial Setup (First Time Only)

---

4. Restart your terminal/IDE after installation
3. **Important**: Check "Add to PATH" during installation
2. Run the MSI installer
1. Download Node.js 18 LTS from [nodejs.org](https://nodejs.org/)
If not installed:

**Required**: Node.js 18 LTS or higher
```
npm --version
node --version
```powershell
### 2. Check Node.js Installation

Should show Python 3.8 or higher. If not installed, download from [python.org](https://www.python.org/downloads/)
```
python --version
```powershell
### 1. Check Python Installation

## Prerequisites Check


