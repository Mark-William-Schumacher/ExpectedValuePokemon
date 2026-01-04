# Server Startup Guide

## ⚠️ IMPORTANT: Fix Node.js in PyCharm First!

Since you installed Node.js v18.20.8 but PyCharm terminal can't find it, you MUST do ONE of these:

### Option 1: Restart PyCharm (EASIEST - DO THIS!)
1. Close PyCharm completely
2. Reopen PyCharm
3. Open a new terminal - Node.js will now work

### Option 2: Use the Startup Script
Double-click `start_servers.ps1` in the project root - it handles everything automatically!

### Option 3: Manually Fix in Current Terminal
Run this ONCE in your PyCharm terminal:
```powershell
$env:Path = $env:Path + ";C:\Program Files\nodejs"
```

---

## First Time Setup

### Install Frontend Dependencies (One Time Only)
Before starting the frontend for the first time, install dependencies:
```powershell
cd web/frontend
npm install
```

---

## Quick Start

### 1. Start Backend (Flask)
Open a terminal in the project root and run:
```powershell
python web/backend/app.py
```
The backend will start on: **http://127.0.0.1:5000**

### 2. Start Frontend (React)
Open a **second terminal** and run:
```powershell
cd web/frontend
npm start
```
The frontend will start on: **http://localhost:3000**

---

## Troubleshooting

### Node.js not found in PyCharm Terminal
If you see `'npm' is not recognized` error in PyCharm terminal:

**Solution 1: Restart PyCharm** (Recommended)
- Close PyCharm completely
- Reopen it - the PATH will be refreshed

**Solution 2: Add Node.js to PATH manually**
Run this in your PyCharm terminal once:
```powershell
$env:Path = $env:Path + ";C:\Program Files\nodejs"
```

Then verify:
```powershell
node --version
npm --version
```

---

## Running Both Servers (Single Command)
You can run both in separate terminal windows, or use this command to start both:

```powershell
# Start backend in background, then frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python web/backend/app.py"
cd web/frontend; npm start
```

---

## Your Node.js Version
- Node: v18.20.8
- npm: 10.8.2

## Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: React 18.2.0
- **Frontend Dev Server**: react-scripts
- **Proxy**: Frontend proxies API requests to backend at http://127.0.0.1:5000

