@echo off
title FinTrack Launcher
cd /d "%~dp0"
echo Starting FinTrack in the background...
start "" pythonw app.py
timeout /t 1 >nul
start http://127.0.0.1:5000
exit
