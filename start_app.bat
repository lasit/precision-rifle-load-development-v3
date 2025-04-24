@echo off
setlocal enabledelayedexpansion
echo Precision Rifle Load Development App
echo ===================================
echo.

:: Change to the directory where the script is located
cd /d "%~dp0"

:: Kill any running instances of the application
echo Checking for running instances...
call kill_app.bat

:: Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

:: Check if pip is installed
python -m pip --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo pip is not installed.
    echo Installing pip...
    python -m ensurepip --upgrade
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install pip.
        echo Please install pip manually.
        echo.
        pause
        exit /b 1
    )
)

:: Check if the requirements are installed
echo Checking dependencies...
set MISSING_DEPS=0

:: Create a temporary file to store the list of installed packages
python -m pip freeze > installed_packages.tmp

:: Read requirements.txt and check if each package is installed
for /f "tokens=*" %%a in (requirements.txt) do (
    :: Skip empty lines and comments
    echo %%a | findstr /r "^#" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo %%a | findstr /r "^$" >nul
        if %ERRORLEVEL% NEQ 0 (
            :: Extract package name (remove version specifier)
            for /f "tokens=1 delims=><=~" %%p in ("%%a") do (
                set PKG_NAME=%%p
                :: Remove spaces
                set PKG_NAME=!PKG_NAME: =!
                
                :: Check if package is installed
                findstr /i /c:"!PKG_NAME!" installed_packages.tmp >nul
                if %ERRORLEVEL% NEQ 0 (
                    echo Missing dependency: !PKG_NAME!
                    set MISSING_DEPS=1
                )
            )
        )
    )
)

:: Delete the temporary file
del installed_packages.tmp

:: Install dependencies if any are missing
if %MISSING_DEPS% EQU 1 (
    echo Installing missing dependencies...
    python -m pip install -r requirements.txt
    
    :: Check if installation was successful
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install dependencies.
        echo Please try running 'pip install -r requirements.txt' manually.
        echo.
        pause
        exit /b 1
    )
    echo Dependencies installed successfully.
) else (
    echo All dependencies are already installed.
)

:: Run the application
echo Starting the application...
python run.py

:: Keep the terminal window open after the application exits
echo Application closed. Press any key to close this window...
pause
