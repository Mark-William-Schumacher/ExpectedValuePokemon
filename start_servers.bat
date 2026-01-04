@echo off
REM Pokemon Card Expected Value - Server Startup Script (Batch Version)

echo.
echo Starting Pokemon Card Expected Value Application...
echo.

REM Check if Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Node.js not found in PATH. Adding it...
    set "PATH=%PATH%;C:\Program Files\nodejs"
)

REM Verify Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js still not found. Please restart PyCharm.
    pause
    exit /b 1
)

echo Node.js found:
node --version
npm --version
echo.

REM Start Backend in a new window
echo Starting Flask Backend Server...
start "Flask Backend" cmd /k "cd /d %~dp0 && python web\backend\app.py"
timeout /t 2 /nobreak >nul

REM Start Frontend in a new window
echo Starting React Frontend Server...
start "React Frontend" cmd /k "cd /d %~dp0web\frontend && npm start"

echo.
echo Both servers are starting up!
echo - Backend: http://127.0.0.1:5000
echo - Frontend: http://localhost:3000
echo.
echo Check the new terminal windows for server output.
pause

