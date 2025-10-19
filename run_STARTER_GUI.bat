@echo off
REM Launch script for Universal Starter GUI (Windows)

echo Starting Universal Starter GUI...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if dependencies are installed
echo Checking dependencies...
python -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements_STARTER_GUI.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK
echo.

REM Run the application
echo Launching application...
python universal_STARTER_GUI.py

pause
exit /b 0
