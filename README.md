# 🃏 Pokemon Card Grading - Expected Value Calculator

A comprehensive tool for analyzing Pokemon card grading profitability, featuring both desktop and web interfaces.

## 🚀 Quick Start

**New to this project?** Everything you need is here:

```powershell
.\start_servers.ps1
```

This intelligent script will:
- ✅ Check all prerequisites (Python, Node.js)
- ✅ Prompt for any missing setup
- ✅ Offer to update database and download images
- ✅ Let you choose Desktop or Web app
- ✅ Start everything automatically

## 📚 Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [SETUP_GUIDE.md](./SETUP_GUIDE.md) | Complete setup for new machines | First time setup |
| [QUICK_START.md](./QUICK_START.md) | Daily quick reference | Regular usage |
| [USAGE_GUIDE.md](./USAGE_GUIDE.md) | Detailed script explanations | Learning the tools |
| [DOCUMENTATION_SUMMARY.md](./DOCUMENTATION_SUMMARY.md) | Overview of all docs | Understanding the system |

## 🎯 Features

### Desktop App (Python/Tkinter)
- Fast, lightweight standalone GUI
- Advanced filtering and sorting
- PDF export functionality
- Favorites system
- Offline capable

### Web App (React + Flask)
- Modern responsive UI
- Real-time filtering
- Card image gallery
- USD/CAD currency toggle
- REST API backend

## 📦 What's Included

- **Card Database**: SQLite database with card prices, PSA populations, and analytics
- **API Integration**: Fetches data from PokeData.io
- **Profitability Calculator**: Computes expected value, net gain, and lucrative factor
- **Image Cache**: Local storage for card images
- **Dual Interface**: Both desktop and web options

## 🛠️ Tech Stack

- **Backend**: Python 3.8+, Flask, SQLite
- **Frontend**: React, Node.js 18 LTS
- **Desktop**: Python Tkinter
- **APIs**: PokeData.io, eBay data

## 📋 Prerequisites

- **Python** 3.8 or higher
- **Node.js** 18 LTS or higher (for web app)
- **npm** (comes with Node.js)

## 💻 Installation

### Option 1: Automated (Recommended)
```powershell
.\start_servers.ps1 -SetupOnly
```

### Option 2: Manual
```powershell
# Install Python dependencies
pip install -r requirements.txt
pip install flask-cors

# Install frontend dependencies
cd web/frontend
npm install
cd ../..

# Update database (REQUIRED first time)
python core_module/update_gradable_cards.py

# Download images for web app
python download_and_cache_images.py
```

## 🎮 Usage

### Desktop App
```powershell
python core_module/ui/showCards.py
```

### Web App
```powershell
.\start_servers.ps1
```
Then open: http://localhost:3000

## 📊 Data Updates

Update your card data weekly or monthly:

```powershell
# Update database with latest prices and PSA data
python core_module/update_gradable_cards.py

# Download new card images
python download_and_cache_images.py
```

## 🔧 Troubleshooting

### "npm is not recognized"
Install Node.js 18 LTS from [nodejs.org](https://nodejs.org/), then restart your terminal.

### Backend 500 Errors
Run database update: `python core_module/update_gradable_cards.py`

### Images Not Loading
Download images: `python download_and_cache_images.py`

See [SETUP_GUIDE.md](./SETUP_GUIDE.md) for more troubleshooting.

## 📖 Project Structure

```
ExpectedValuePokemon/
├── core_module/           # Core logic and desktop app
│   ├── ui/
│   │   └── showCards.py  # Desktop application
│   └── update_gradable_cards.py  # Database updater
├── web/
│   ├── backend/          # Flask API server
│   └── frontend/         # React web app
├── start_servers.ps1     # Main startup script
└── download_and_cache_images.py  # Image downloader
```

## 🤝 Contributing

This is a personal project for analyzing Pokemon card grading profitability. Feel free to fork and adapt for your own use.

## 📄 License

Personal use project. Card data provided by PokeData.io API.

## 🆘 Support

- Check [SETUP_GUIDE.md](./SETUP_GUIDE.md) for complete setup instructions
- See [QUICK_START.md](./QUICK_START.md) for daily usage
- Read [BACKEND_FIX_SUMMARY.md](./BACKEND_FIX_SUMMARY.md) for backend issues
- Review [LOCAL_IMAGES_SOLUTION.md](./LOCAL_IMAGES_SOLUTION.md) for image problems

---

**Made with ❤️ for Pokemon card grading analysis**

