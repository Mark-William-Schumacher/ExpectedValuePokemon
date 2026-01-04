# Expected Value Pokemon - Startup Script
# Checks prerequisites, updates data, and starts servers
param(
    [switch]$SetupOnly,
    [switch]$UpdateData,
    [switch]$DownloadImages,
    [switch]$SkipChecks,
    [switch]$Desktop,
    [switch]$Web
)
# Color functions
function Write-Success { param($msg) Write-Host "✓ $msg" -ForegroundColor Green }
function Write-Error-Msg { param($msg) Write-Host "✗ $msg" -ForegroundColor Red }
function Write-Warning-Msg { param($msg) Write-Host "⚠ $msg" -ForegroundColor Yellow }
function Write-Info { param($msg) Write-Host "ℹ $msg" -ForegroundColor Cyan }
function Write-Section { param($msg) Write-Host "`n=== $msg ===" -ForegroundColor Magenta }
$ErrorActionPreference = "Continue"
$projectRoot = $PSScriptRoot
# Banner
Clear-Host
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Expected Value Pokemon - Startup Script      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
if (-not $SkipChecks) {
    Write-Section "Checking Prerequisites"
    # Check Python
    Write-Info "Checking Python installation..."
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python") {
            Write-Success "Python found: $pythonVersion"
        }
    } catch {
        Write-Error-Msg "Python not found"
        Write-Warning-Msg "Install Python 3.8+ from https://www.python.org/"
        Read-Host "Press Enter to exit"
        exit 1
    }
    # Check Node.js
    Write-Info "Checking Node.js installation..."
    try {
        $nodeVersion = node --version 2>&1
        Write-Success "Node.js found: $nodeVersion"
    } catch {
        Write-Error-Msg "Node.js not found"
        Write-Warning-Msg "Install Node.js 18 LTS from https://nodejs.org/"
        Write-Info "After install, restart PyCharm or run:"
        Write-Host "`$env:Path = `"C:\Program Files\nodejs;`$env:Path`"" -ForegroundColor Yellow
        $continue = Read-Host "`nContinue without Node.js? (y/n)"
        if ($continue -ne "y") { exit 1 }
    }
    # Check npm
    Write-Info "Checking npm..."
    try {
        $npmVersion = npm --version 2>&1
        Write-Success "npm found: v$npmVersion"
    } catch {
        Write-Warning-Msg "npm not found"
    }
    # Check Python modules
    Write-Info "Checking Python dependencies..."
    $missing = @()
    "flask","flask_cors","requests","beautifulsoup4" | ForEach-Object {
        $m = $_ -replace "-","_"
        python -c "import $m" 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) { $missing += $_ }
    }
    if ($missing.Count -gt 0) {
        Write-Warning-Msg "Missing: $($missing -join ', ')"
        $install = Read-Host "Install? (y/n)"
        if ($install -eq "y") {
            pip install -r requirements.txt
        }
    } else {
        Write-Success "All Python modules found"
    }
    # Check frontend deps
    if (Test-Path "$projectRoot\web\frontend\node_modules") {
        Write-Success "Frontend dependencies found"
    } else {
        Write-Warning-Msg "Frontend dependencies not installed"
        $install = Read-Host "Install? (y/n)"
        if ($install -eq "y") {
            Push-Location "$projectRoot\web\frontend"
            npm install
            Pop-Location
        }
    }
    # Check database
    if (Test-Path "$projectRoot\web\backend\pokemon.db") {
        Write-Success "Database found"
    } else {
        Write-Warning-Msg "Database missing - run: python core_module/update_gradable_cards.py"
    }
    # Check images
    $imgs = @(Get-ChildItem "$projectRoot\web\backend\static\assets\images\*.webp" -ErrorAction SilentlyContinue)
    if ($imgs.Count -gt 0) {
        Write-Success "Found $($imgs.Count) images"
    } else {
        Write-Warning-Msg "No images - run: python download_and_cache_images.py"
    }
}
if ($UpdateData) {
    Write-Section "Updating Database"
    $env:PYTHONPATH = $projectRoot
    python "$projectRoot\core_module\update_gradable_cards.py"
    if ($LASTEXITCODE -eq 0) { Write-Success "Updated" }
}
if ($DownloadImages) {
    Write-Section "Downloading Images"
    python "$projectRoot\download_and_cache_images.py"
    if ($LASTEXITCODE -eq 0) { Write-Success "Downloaded" }
}
if ($SetupOnly) {
    Write-Success "Setup complete"
    Write-Info "To start: .\start_servers.ps1"
    Read-Host "Press Enter"
    exit 0
}
# Choose mode if not specified
if (-not $Desktop -and -not $Web) {
    Write-Section "Choose Mode"
    Write-Host "[1] Desktop App (Tkinter)"
    Write-Host "[2] Web App (React + Flask)"
    Write-Host "[3] Exit"
    $choice = Read-Host "Choice (1-3)"
    switch ($choice) {
        "1" { $Desktop = $true }
        "2" { $Web = $true }
        "3" { exit 0 }
        default { exit 1 }
    }
}
# Start Desktop
if ($Desktop) {
    Write-Section "Starting Desktop App"
    $env:PYTHONPATH = $projectRoot
    python "$projectRoot\core_module\ui\showCards.py"
    exit $LASTEXITCODE
}
# Start Web
if ($Web) {
    Write-Section "Starting Web App"
    if (-not (Test-Path "$projectRoot\web\backend\pokemon.db")) {
        Write-Warning-Msg "No database! Backend may fail."
        $c = Read-Host "Continue? (y/n)"
        if ($c -ne "y") { exit 1 }
    }
    Write-Info "Starting Flask: http://127.0.0.1:5000"
    Write-Info "Starting React: http://localhost:3000"
    Write-Warning-Msg "Press Ctrl+C in each window to stop"
    # Backend
    $backendCmd = "cd '$projectRoot'; `$env:PYTHONPATH='$projectRoot'; python web\backend\app.py"
    Start-Process powershell -ArgumentList "-NoExit","-Command",$backendCmd
    Write-Success "Backend starting..."
    Start-Sleep 3
    # Frontend  
    $frontendCmd = "cd '$projectRoot\web\frontend'; npm start"
    Start-Process powershell -ArgumentList "-NoExit","-Command",$frontendCmd
    Write-Success "Frontend starting..."
    Start-Sleep 5
    Start-Process "http://localhost:3000"
    Write-Success "Servers running!"
    Read-Host "Press Enter to close (servers continue)"
    exit 0
}
Write-Error-Msg "No mode selected"
exit 1
