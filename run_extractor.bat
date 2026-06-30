@echo off
setlocal

:: ================================================
::   EPS Research Astro Extractor v1.1.0 — Windows Launcher
::   Flynn, D.C. (2026) -- EPS Research
::   ORCID: 0000-0002-2768-6650
:: ================================================

:: Move to the folder containing this .bat file
cd /d "%~dp0"

echo.
echo ================================================
echo   EPS Research Astro Extractor v1.1.0
echo   Flynn, D.C. (2026) -- EPS Research
echo ================================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ from python.org
    echo        and make sure "Add to PATH" is checked during install.
    pause
    exit /b 1
)

:: Check app.py is present
if not exist "app.py" (
    echo ERROR: app.py not found in this folder.
    echo        Place run_extractor.bat in the same folder as app.py.
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment -- this happens once and takes a minute...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo   done.
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install dependencies (fast on repeat launches -- pip skips installed packages)
echo Checking dependencies...
pip install -q streamlit pandas requests beautifulsoup4 nest-asyncio

echo.
echo ================================================
echo   BEFORE EXTRACTING:
echo   1. Open LM Studio
echo   2. Load a model (Qwen, Llama, Mistral, etc.)
echo   3. Go to Local Server tab
echo   4. Start server (default port: 1234)
echo ================================================
echo.
echo Starting Astro Extractor at http://localhost:8501
echo Your browser will open automatically.
echo Press Ctrl+C in this window to stop.
echo.

:: Launch -- no headless flag so browser opens automatically
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause
