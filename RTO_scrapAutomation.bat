@echo off
REM ================================================
REM RTO Data Collection Script Runner
REM ================================================

echo.
echo ========================================
echo   RTO Data Collection Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [INFO] Python found
echo.

REM Check if the Python script exists
if not exist "rto_scraper.py" (
    echo [ERROR] rto_scraper.py not found in current directory
    echo Please make sure the Python script is in the same folder as this BAT file
    pause
    exit /b 1
)

echo [INFO] Starting RTO data collection...
echo [INFO] This may take a while. Please do not close this window.
echo.

REM Run the Python script
python rto_scraper.py

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo [ERROR] Script encountered an error
    pause
    exit /b 1
) else (
    echo.
    echo [SUCCESS] Script completed successfully
    pause
    exit /b 0
)