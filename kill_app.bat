@echo off
echo Killing any running instances of the application...

:: Kill any Python processes running run.py
taskkill /F /FI "WINDOWTITLE eq Precision Rifle Load Development*" /T >nul 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *run.py*" /T >nul 2>nul

echo All instances killed.
