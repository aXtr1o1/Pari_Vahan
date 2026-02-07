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

REM NOTE:
REM - 'ping' (ICMP) is frequently blocked/throttled on some networks, causing false "no internet".
REM - Use a quick HTTPS check (plus TCP+DNS fallback) for more reliable detection.
 powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; $ok=$false; try { $p=@{ TimeoutSec=5; Uri='https://www.msftconnecttest.com/connecttest.txt'; ErrorAction='Stop' }; if((Get-Command Invoke-WebRequest).Parameters.ContainsKey('UseBasicParsing')){ $p.UseBasicParsing=$true }; $r=Invoke-WebRequest @p; if($r.StatusCode -ge 200 -and $r.StatusCode -lt 400){$ok=$true} } catch {}; if(-not $ok){ try { if(Test-NetConnection -ComputerName '1.1.1.1' -Port 443 -InformationLevel Quiet){$ok=$true} } catch {} }; if(-not $ok){ try { [void][System.Net.Dns]::GetHostEntry('www.google.com'); $ok=$true } catch {} }; if($ok){ exit 0 } else { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] No internet connection detected
    echo [INFO] Waiting 3 seconds before retry...
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