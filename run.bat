@echo off
title Autonomous DA - No-Code Analytics & BI Platform
echo ========================================================
echo        Starting Autonomous DA (Streamlit App)
echo ========================================================
echo.
call .venv\Scripts\activate
streamlit run app.py
pause
