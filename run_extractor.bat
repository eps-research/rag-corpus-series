@echo off
setlocal
cd /d "%~dp0"
echo.
echo ================================================
echo   EPS Research Astro Extractor v1.0.0
echo   Flynn, D.C. (2026) -- EPS Research
echo ================================================
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found.
    pause
    exit /b 1
)
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
    echo   done.
)
call venv\Scripts\activate.bat
echo Installing dependencies...
pip install -q streamlit pandas requests beautifulsoup4 nest-asyncio
echo.
echo ================================================
echo   1. Open LM Studio
echo   2. Load a model
echo   3. Start server on port 1234
echo ================================================
echo.
echo Starting at http://localhost:8501
echo Press Ctrl+C to stop.
echo.
streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
