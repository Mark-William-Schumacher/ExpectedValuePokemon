# Pokemon Card Grading Project - Usage Scripts

This directory contains utility scripts for running the Pokemon card grading application.

## Quick Reference

### For New Machines
1. Read [SETUP_GUIDE.md](../SETUP_GUIDE.md) first
2. Run `.\start_servers.ps1 -SetupOnly` to check and install everything
3. Run `.\start_servers.ps1` to launch

### Daily Usage
- **Desktop App**: `python core_module/ui/showCards.py`
- **Web App**: `.\start_servers.ps1`

### Data Updates
- **Update Database**: `python core_module/update_gradable_cards.py`
- **Download Images**: `python download_and_cache_images.py`

## Available Commands

### start_servers.ps1
Main startup script with interactive setup

**Options:**
- Default: Interactive menu
- `-SetupOnly`: Check/install prerequisites only
- `-UpdateData`: Update card database
- `-DownloadImages`: Download card images
- `-SkipChecks`: Skip prerequisite checks (fast start)

**Examples:**
```powershell
# Interactive mode (recommended)
.\start_servers.ps1

# First time setup
.\start_servers.ps1 -SetupOnly -UpdateData -DownloadImages

# Quick start (skip checks)
.\start_servers.ps1 -SkipChecks

# Update data and start
.\start_servers.ps1 -UpdateData
```

### update_gradable_cards.py
Updates the card database with latest data from APIs

**When to run:**
- First time setup
- Weekly/monthly to refresh card prices
- When you want latest PSA population data
- Before using the app after long periods

**What it does:**
- Fetches card prices from PokeData API
- Updates PSA population data
- Calculates profitability metrics
- Populates card_analytics table
- Updates grading_financials

**Duration**: 10-30 minutes

### download_and_cache_images.py
Downloads card images for the web application

**When to run:**
- After updating the database
- When images are missing in web app
- After adding new sets

**What it does:**
- Refreshes cache with local_image fields
- Downloads images to `web/backend/static/assets/images/`
- Skips already downloaded images

**Duration**: 5-15 minutes (first time)

### showCards.py
Launches the desktop application

**Features:**
- Standalone Python/Tkinter GUI
- No web server needed
- Fast filtering and pagination
- PDF export functionality
- Favorite cards feature

**Usage:**
```powershell
python core_module/ui/showCards.py
```

## Workflow Examples

### Brand New Machine
```powershell
# 1. Install Node.js 18 LTS (if not installed)

# 2. Run full setup
.\start_servers.ps1 -SetupOnly

# 3. Update database
.\start_servers.ps1 -UpdateData

# 4. Download images
.\start_servers.ps1 -DownloadImages

# 5. Launch (choose desktop or web)
.\start_servers.ps1
```

### Weekly Maintenance
```powershell
# Update card data
python core_module/update_gradable_cards.py

# Download any new images
python download_and_cache_images.py

# Launch app
.\start_servers.ps1
```

### Quick Daily Use
```powershell
# If everything is setup, just run:
.\start_servers.ps1 -SkipChecks
```

## Project Structure

```
ExpectedValuePokemon/
├── start_servers.ps1           # Main startup script
├── SETUP_GUIDE.md             # New machine setup
├── QUICK_START.md             # Quick reference
├── core_module/
│   ├── update_gradable_cards.py   # Database updater
│   └── ui/
│       └── showCards.py       # Desktop app
├── download_and_cache_images.py   # Image downloader
└── web/
    ├── backend/
    │   └── app.py             # Flask API server
    └── frontend/
        └── src/App.jsx        # React web app
```

## Support

- [SETUP_GUIDE.md](../SETUP_GUIDE.md) - Complete setup instructions
- [BACKEND_FIX_SUMMARY.md](../BACKEND_FIX_SUMMARY.md) - Backend troubleshooting
- [LOCAL_IMAGES_SOLUTION.md](../LOCAL_IMAGES_SOLUTION.md) - Image serving details

