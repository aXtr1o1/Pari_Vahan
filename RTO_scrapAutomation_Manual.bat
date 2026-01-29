@echo off
REM ================================================
REM RTO Data Collection Script Runner
REM ================================================

echo.
echo ========================================
echo   RTO Data Collection Script
echo ========================================
echo.

REM Get current hour (24-hour format)
for /f "tokens=1-2 delims=:" %%a in ('time /t') do set hour=%%a
REM Remove leading space if present
set hour=%hour: =%
REM Handle AM/PM format if present
echo %hour% | findstr /r "^[0-9][0-9]*$" >nul
if errorlevel 1 (
    REM Time is in 12-hour format, get 24-hour format
    for /f "tokens=1-3 delims=:. " %%a in ("%TIME%") do set hour=%%a
)

REM Remove leading zero for comparison
set /a hour_num=%hour%

echo [INFO] Current time hour: %hour_num%
echo.

REM Check if current time is before 6 AM
if %hour_num% LSS 6 (
    echo ========================================
    echo   RISKY TIME DETECTED
    echo ========================================
    echo [WARNING] Current time is before 6:00 AM
    echo [WARNING] This is a risky time to scrape data
    echo [WARNING] Parivahan website might be under maintenance
    echo.
    echo [INFO] SAFE FALLBACK: Script execution aborted
    echo [INFO] Please run this script after 6:00 AM
    echo.
    pause
    exit /b 1
)

echo [INFO] Time check passed (after 6:00 AM)
echo.

@REM REM Check if today's folder already exists
@REM REM Use Python to get the correct date format (YYYY-MM-DD)
@REM for /f "delims=" %%i in ('python -c "import time; print(time.strftime('%%Y-%%m-%%d'))"') do set today_date=%%i
@REM set "today_folder=%today_date%_RTO_Files"
@REM set "downloads_path=%USERPROFILE%\Downloads\%today_folder%"

@REM echo [INFO] Checking for existing folder: %today_folder%
@REM echo [INFO] Full path: %downloads_path%
@REM echo.

@REM if exist "%downloads_path%" (
@REM     echo ========================================
@REM     echo   FOLDER ALREADY EXISTS
@REM     echo ========================================
@REM     echo [WARNING] Today's RTO folder already exists:
@REM     echo [PATH] %downloads_path%
@REM     echo.
@REM     echo [INFO] This indicates data collection has already been completed for today.
@REM     echo.
@REM     echo If you want to rerun this script:
@REM     echo   1. Delete the folder: %today_folder%
@REM     echo   2. Run this BAT file again manually
@REM     echo.
@REM     pause
@REM     exit /b 0
@REM )

@REM echo [INFO] Folder check passed (no existing folder for today)
@REM echo.

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

REM Check for internet connectivity with non-stop retry
set /a retry_count=0

:CHECK_INTERNET
set /a retry_count+=1
echo [INFO] Checking internet connectivity... (Attempt %retry_count%)

REM Try ping with shorter timeout
ping -n 1 -w 1000 8.8.8.8 >nul 2>&1
if errorlevel 1 (
    REM If Google DNS fails, try Cloudflare DNS
    ping -n 1 -w 1000 1.1.1.1 >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] No internet connection detected
        echo [INFO] Waiting 3 seconds before retry...
        timeout /t 3 /nobreak >nul
        goto CHECK_INTERNET
    )
)

REM Verify DNS resolution
ping -n 1 -w 2000 www.google.com >nul 2>&1
if errorlevel 1 (
    echo [WARNING] DNS resolution failed, retrying...
    timeout /t 3 /nobreak >nul
    goto CHECK_INTERNET
)

echo [INFO] Internet connection confirmed
echo.

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