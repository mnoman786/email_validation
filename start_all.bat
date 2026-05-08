@echo off
chcp 65001 >nul
echo ========================================
echo   EmailGuard - Starting All Services
echo ========================================
echo.
echo Opening two terminal windows:
echo   Window 1: Django Backend  (port 8000)
echo   Window 2: Next.js Frontend (port 3000)
echo.

:: Start backend in new terminal window
start "EmailGuard - Backend" cmd /k "%~dp0start_backend.bat"

:: Wait 3 seconds for backend to initialize before starting frontend
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

:: Start frontend in new terminal window
start "EmailGuard - Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo ========================================
echo   Services are starting in other windows
echo ----------------------------------------
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/api/docs/
echo   Admin:    http://localhost:8000/admin
echo   Login:    admin@emailguard.io / admin123
echo ========================================
echo.
pause
