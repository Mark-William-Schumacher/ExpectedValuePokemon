# Pokemon Card Expected Value - Server Startup Script
# Run this script to start both backend and frontend servers

Write-Host "🎮 Starting Pokemon Card Expected Value Application..." -ForegroundColor Cyan
Write-Host ""

# Check if Node.js is available
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "⚠️  Node.js not found in PATH. Adding it..." -ForegroundColor Yellow

    # Try common Node.js installation paths
    $nodePaths = @(
        "C:\Program Files\nodejs",
        "C:\Program Files (x86)\nodejs",
        "$env:APPDATA\npm",
        "$env:ProgramFiles\nodejs"
    )

    foreach ($path in $nodePaths) {
        if (Test-Path $path) {
            $env:Path = "$path;$env:Path"
            Write-Host "   Added $path to PATH" -ForegroundColor Gray
        }
    }

    if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
        Write-Host "❌ Node.js still not found. Please:" -ForegroundColor Red
        Write-Host "   1. Restart PyCharm completely (EASIEST FIX)" -ForegroundColor Yellow
        Write-Host "   2. Or verify Node.js is installed: node --version in external PowerShell" -ForegroundColor Yellow
        pause
        exit 1
    }
}

Write-Host "✅ Node.js version: $(node --version)" -ForegroundColor Green
Write-Host "✅ npm version: $(npm --version)" -ForegroundColor Green
Write-Host ""

# Start Backend in a new window
Write-Host "🚀 Starting Flask Backend Server..." -ForegroundColor Cyan
$backendPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$backendPath'; `$env:PYTHONPATH = '$backendPath'; Write-Host '🔥 Flask Backend Server' -ForegroundColor Yellow; python web/backend/app.py"
)

Write-Host "✅ Backend starting at http://127.0.0.1:5000" -ForegroundColor Green
Start-Sleep -Seconds 2

# Start Frontend in a new window
Write-Host "🚀 Starting React Frontend Server..." -ForegroundColor Cyan
$frontendPath = Join-Path $backendPath "web\frontend"
$nodePath = "C:\Program Files\nodejs"
Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "`$env:Path = '$nodePath;' + `$env:Path; cd '$frontendPath'; Write-Host '⚛️  React Frontend Server' -ForegroundColor Cyan; npm start"
)

Write-Host "✅ Frontend starting at http://localhost:3000" -ForegroundColor Green
Write-Host ""
Write-Host "✨ Both servers are starting up!" -ForegroundColor Green
Write-Host "📖 Check the new terminal windows for server output" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this launcher..." -ForegroundColor Gray
pause | Out-Null

