@echo off
echo Starting DeskReject Guard UI...

REM Set PYTHONPATH so the deskreject module can be found
set PYTHONPATH=%~dp0src

REM Activate the virtual environment and run the app
call .venv\Scripts\activate.bat
streamlit run ui\app.py
