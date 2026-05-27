@echo off
title AI Expense Tracker Suite Launcher
color 0B
echo ===============================================================
echo   🚀 STARTING AI EXPENSE TRACKER PORTAL 🚀
echo ===============================================================
echo.

:: 1. Launch the default web browser to open the local server
echo [Launcher] Opening Frontend Website (http://localhost:8000)...
start "" "http://localhost:8000"
echo [Launcher] Frontend launched successfully!
echo.

:: 2. Move to backend directory and start the FastAPI server
echo [Launcher] Initializing Backend Server Connection...
cd "%~dp0backend"
.venv\Scripts\python run.py

echo.
echo ===============================================================
echo   Press any key to close launcher...
echo ===============================================================
pause > nul
