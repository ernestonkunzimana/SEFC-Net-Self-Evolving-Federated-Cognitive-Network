@echo off
REM Quick test script for edge resilience module
REM Run from anywhere - automatically sets correct directory

echo ========================================
echo SEFC-Net Edge Resilience Test Runner
echo ========================================
echo.

REM Save current directory
pushd %CD%

REM Change to SEFCNet directory
cd /d C:\Users\ADMIN\OneDrive\Desktop\SEFCNet\SEFCNet

echo Running tests from: %CD%
echo.

REM Activate virtual environment if it exists
if exist "..\..\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call ..\..\.venv\Scripts\activate.bat
)

REM Run tests
python edge_resilience\test_edge_resilience.py

REM Restore original directory
popd

echo.
echo ========================================
echo Tests complete!
echo ========================================
pause
