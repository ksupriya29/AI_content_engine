@echo off
echo ============================================
echo   AI Content Engine - Streamlit Launcher
echo ============================================
echo.
echo Make sure your API keys are set in .env file
echo.
cd /d "%~dp0"
python -m streamlit run app.py
pause