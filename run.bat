@echo off
title Autonomous DA - Enterprise Analytics, Tally, Power BI & Research Suite
echo ========================================================
echo   Starting Autonomous DA (All-in-One Analytics Platform)
echo ========================================================
echo.
call .venv\Scripts\activate
streamlit run app.py --server.port=8501 --server.headless=true --browser.gatherUsageStats=false
pause
