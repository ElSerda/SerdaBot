@echo off
REM Quick test for max_tokens_chill=60 on Windows

echo.
echo ========================================
echo   Quick Test - SerdaBot max_tokens=60
echo ========================================
echo.

REM Activate venv
call .\venv\Scripts\activate.bat

REM Show config values
echo 1. Checking config.yaml...
echo.
findstr /C:"max_tokens_chill" src\config\config.yaml
findstr /C:"max_tokens_ask" src\config\config.yaml
findstr /C:"temperature_ask" src\config\config.yaml
findstr /C:"temperature_chill" src\config\config.yaml
echo.

REM Ask user if they want to run full test
echo 2. Run full test? (y/n)
set /p run_test="Run python test? [y/n]: "

if /i "%run_test%"=="y" (
    echo.
    echo Running test...
    python scripts\test_max_tokens_60.py
) else (
    echo.
    echo Skipped. You can run it manually with:
    echo   python scripts\test_max_tokens_60.py
)

echo.
echo ========================================
echo   Test complete!
echo ========================================
echo.
pause
