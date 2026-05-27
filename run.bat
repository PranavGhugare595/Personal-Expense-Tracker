@echo off
title AI Expense Tracker Suite Launcher
color 0B
echo ===============================================================
echo   🚀 STARTING AI EXPENSE TRACKER PORTAL 🚀
echo ===============================================================
echo.

:: 1. Launch the frontend interface in the default web browser
echo [Launcher] Opening Frontend Website (index.html)...
start "" "%~dp0index.html"
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
