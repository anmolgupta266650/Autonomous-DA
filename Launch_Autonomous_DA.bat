@echo off
title Autonomous DA Enterprise Launcher
cd /d "%~dp0"

echo ===================================================
echo     Starting Autonomous DA Enterprise Platform...
echo ===================================================

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Launching Streamlit web application on port 8501...
start "" "%PYTHON_EXE%" -m streamlit run app.py --server.port=8501 --server.headless=true --browser.gatherUsageStats=false

timeout /t 3 /nobreak >nul
start http://localhost:8501

echo.
echo Application running at: http://localhost:8501
echo You may close this window or leave it minimized.

