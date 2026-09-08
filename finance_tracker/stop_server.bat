@echo off
echo Stopping FinTrack background server...
taskkill /F /IM pythonw.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq FinTrack*" 2>nul
echo Server stopped successfully.
pause
