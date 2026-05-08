@echo off
chcp 65001 >NUL
echo ========================================
echo   EmailGuard Frontend - Local Dev
echo ========================================

cd /d "%~dp0frontend"

:: Check if Node is installed
where node >NUL 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js not found.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('node --version') do echo Node.js: %%v

:: Create .env.local if missing
if not exist ".env.local" (
    echo Creating .env.local...
    copy .env.local.example .env.local >NUL
)

:: Install if node_modules missing
if not exist "node_modules\" (
    echo Installing npm packages... (first time may take 2-3 minutes)
    npm install
    if errorlevel 1 (
        echo ERROR: npm install failed.
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Frontend is RUNNING
echo ----------------------------------------
echo   URL: http://localhost:3000
echo ========================================
echo   Press CTRL+C to stop
echo.

npm run dev

pause
