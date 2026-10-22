@echo off
title AI Road Predictive Maintenance System Launcher (Component 4)
color 0b

echo ======================================================================
echo   AI Road Maintenance Research System (Component 4 - J26-IT-336)
echo   Sri Lanka Road Development Authority (RDA) Pavement Analytics
echo ======================================================================
echo.

echo [1/3] Starting FastAPI Backend Server on port 8000...
start "RoadPredict Backend (FastAPI)" cmd /k "cd /d %~dp0 && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"

echo [2/3] Starting Frontend Dev Server on port 5173...
start "RoadPredict Frontend (Vite React)" cmd /k "cd /d %~dp0frontend && npm run dev -- --host 127.0.0.1 --port 5173"

echo [3/3] Waiting for servers to initialize...
timeout /t 3 /nobreak > nul

echo Opening Research Dashboard in your browser...
start http://127.0.0.1:5173

echo.
echo ======================================================================
echo System is running!
echo Frontend Dashboard: http://127.0.0.1:5173
echo Backend API Docs:   http://127.0.0.1:8000/docs
echo.
echo (Keep the opened command prompt windows running while using the app)
echo ======================================================================
pause
