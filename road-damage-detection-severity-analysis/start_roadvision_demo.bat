
@echo off
setlocal
title RoadVision AI - Panel Demo Launcher

REM Main project folder
set "ROOT=%~dp0"

echo ==========================================
echo       ROADVISION AI - PANEL DEMO
echo ==========================================
echo.

REM Verify Python environment
if not exist "%ROOT%.venv312\Scripts\python.exe" (
    echo ERROR: Python environment not found!
    pause
    exit /b 1
)

REM Verify Python API
if not exist "%ROOT%api_server.py" (
    echo ERROR: Python API server not found!
    pause
    exit /b 1
)

REM Verify React application
if not exist "%ROOT%road-damage-frontend\package.json" (
    echo ERROR: React frontend not found!
    pause
    exit /b 1
)

echo All required project files found!
echo.

REM Start FastAPI from the correct project folder
echo [1/2] Starting Python AI Backend...

start "RoadVision AI Backend" /D "%ROOT%" cmd.exe /k ""%ROOT%.venv312\Scripts\python.exe" -m uvicorn api_server:app --host 127.0.0.1 --port 8000"

REM Start React from its own project folder
echo [2/2] Starting React Dashboard...

start "RoadVision AI Frontend" /D "%ROOT%road-damage-frontend" cmd.exe /k "npm.cmd run dev"

echo.
echo ==========================================
echo ROADVISION AI - STARTUP REQUESTED
echo ==========================================
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo.
echo Check BOTH terminal windows for errors.
echo Wait until BOTH servers show READY.
echo.

pause

REM Open React Dashboard
start "" "http://localhost:5173"

endlocal
