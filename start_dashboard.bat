@echo off
echo ZED Camera Comprehensive Dashboard
echo ===================================
echo.
echo Starting dashboard launcher...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python launcher
python launch_dashboard.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
)