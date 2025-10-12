@echo off
echo 🚀 History Timeline Generator - antonnie.dev
echo.

if "%1"=="stats" (
    echo Showing cache statistics...
    C:/Users/SHADOW/AppData/Local/Programs/Python/Python313/python.exe ai-scrape.py --stats
    pause
    exit
)

if "%1"=="fetch-all" (
    echo Fetching data for all 366 dates...
    echo This will take several minutes but creates a complete database.
    C:/Users/SHADOW/AppData/Local/Programs/Python/Python313/python.exe ai-scrape.py --fetch-all
    pause
    exit
)

if "%1"=="" (
    echo Generating timeline for today...
    C:/Users/SHADOW/AppData/Local/Programs/Python/Python313/python.exe ai-scrape.py
    echo.
    echo Opening timeline in browser...
    start index.html
) else (
    echo Usage: generate_timeline.bat
    echo       generate_timeline.bat stats
    echo       generate_timeline.bat fetch-all
    echo.
    echo Generating timeline for today instead...
    C:/Users/SHADOW/AppData/Local/Programs/Python/Python313/python.exe ai-scrape.py
    echo.
    echo Opening timeline in browser...
    start index.html
)

pause