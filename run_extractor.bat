@echo off
setlocal

:: ================================================
::   EPS Research Astro Extractor — Windows Launcher
::   Flynn, D.C. (2026) -- EPS Research
::   ORCID: 0000-0002-2768-6650
:: ================================================

:: Move to the folder containing this .bat file
cd /d "%~dp0"

echo.
echo ================================================
echo   EPS Research Astro Extractor v1.0.0
echo   Flynn, D.C. (2026) -- EPS Research
echo ================================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install Python 3.10+ and ensure it is on your PATH.
    pause
    exit /b 1
)

:: Create venv if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
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

:: Install / upgrade dependencies
echo Installing dependencies...
pip install -q --upgrade pip
pip install -q streamlit pandas requests beautifulsoup4 nest-asyncio

:: Try crawl4ai + Playwright (optional -- falls back to bs4)
echo Installing crawl4ai (optional JS crawler)...
pip install -q crawl4ai >nul 2>&1 && (
    playwright install chromium >nul 2>&1 && (
        echo   crawl4ai + Chromium ready.
    ) || (
        echo   Chromium unavailable -- bs4 fallback active (works fine).
    )
) || (
    echo   crawl4ai unavailable -- bs4 fallback active (works fine).
)

echo.
echo ================================================
echo   BEFORE RUNNING:
echo   1. Open LM Studio
echo   2. Load a model (Qwen, Llama, Mistral, etc.)
echo   3. Go to Local Server tab
echo   4. Start server (default port: 1234)
echo ================================================
echo.
echo Starting Astro Extractor at http://localhost:8501
echo Your browser will open automatically.
echo Press Ctrl+C to stop.
echo.

:: Launch -- no headless flag so browser opens automatically
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false

pause
