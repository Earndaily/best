@echo off
REM The Infiltrator - Windows Quick Start
REM This batch file makes it easy to run the infiltrator on Windows

echo ============================================================
echo THE INFILTRATOR - Windows Quick Start
echo ============================================================
echo.

REM Check for Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10+ from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [OK] Python detected
echo.

REM Check for dependencies
echo Checking dependencies...
python -c "import playwright" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Playwright not installed
    echo.
    echo Installing dependencies...
    pip install playwright requests python-socks[asyncio]
    
    echo.
    echo Installing Playwright browsers...
    playwright install chromium
    playwright install-deps chromium
    
    echo.
    echo [OK] Dependencies installed
) else (
    echo [OK] Dependencies already installed
)

echo.
echo ============================================================
echo SELECT RUN MODE:
echo ============================================================
echo.
echo 1. Run Full Infiltrator (Interactive Bootstrap + Complete Mission)
echo 2. Run Bootstrap Only (Configuration Only)
echo 3. Run Complete Integration (Requires existing config)
echo 4. Test Individual Components
echo 5. Exit
echo.

set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto full_run
if "%choice%"=="2" goto bootstrap_only
if "%choice%"=="3" goto complete_only
if "%choice%"=="4" goto test_components
if "%choice%"=="5" goto end

echo Invalid choice
pause
exit /b 1

:full_run
echo.
echo ============================================================
echo FULL INFILTRATOR RUN
echo ============================================================
echo.
echo This will:
echo   1. Configure your identity (URL, Proxy, User-Agent)
echo   2. Perform identity synchronization
echo   3. Launch browser with full protections
echo   4. Execute browsing mission
echo.
pause

echo.
echo Running bootstrap...
python entrypoint_windows.py

if errorlevel 1 (
    echo.
    echo [ERROR] Bootstrap failed
    pause
    exit /b 1
)

echo.
echo Bootstrap complete. Starting mission...
timeout /t 3 /nobreak >nul

python infiltrator_complete.py
goto end

:bootstrap_only
echo.
echo ============================================================
echo BOOTSTRAP ONLY
echo ============================================================
echo.
python entrypoint_windows.py
goto end

:complete_only
echo.
echo ============================================================
echo COMPLETE INTEGRATION
echo ============================================================
echo.
echo NOTE: This requires an existing configuration from bootstrap
echo.

if not exist "infiltrator_config.env" (
    echo [ERROR] Configuration file not found
    echo Please run Bootstrap first (Option 1 or 2)
    pause
    exit /b 1
)

python infiltrator_complete.py
goto end

:test_components
echo.
echo ============================================================
echo TEST INDIVIDUAL COMPONENTS
echo ============================================================
echo.
echo 1. Kinematic Mouse (Bézier curves + Fitts's Law)
echo 2. Temporal Entropy (Gaussian timing)
echo 3. Reading Mimicry (Scrolling + honeypot detection)
echo 4. Identity Sync (GeoIP + timezone)
echo 5. Back to main menu
echo.

set /p test_choice="Enter choice (1-5): "

if "%test_choice%"=="1" (
    echo.
    echo Testing Kinematic Mouse...
    python kinematic_mouse.py
) else if "%test_choice%"=="2" (
    echo.
    echo Testing Temporal Entropy...
    python temporal_entropy.py
) else if "%test_choice%"=="3" (
    echo.
    echo Testing Reading Mimicry...
    echo NOTE: This requires a running Playwright browser
    python reading_mimicry.py
) else if "%test_choice%"=="4" (
    echo.
    set /p test_ip="Enter test IP address (e.g., 8.8.8.8): "
    python identity_sync.py --proxy-ip %test_ip% --os-type windows
) else if "%test_choice%"=="5" (
    cls
    goto start
) else (
    echo Invalid choice
)

echo.
pause
goto test_components

:end
echo.
echo ============================================================
echo Session Complete
echo ============================================================
echo.
echo Thank you for using The Infiltrator research framework
echo.
pause
