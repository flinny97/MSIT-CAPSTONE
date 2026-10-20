@echo off
REM Start the training web app on this computer only (http://127.0.0.1:5000)
cd /d "%~dp0"
echo Starting the app. Open http://127.0.0.1:5000 in your browser.
echo Close this window to stop the app.
".venv\Scripts\python.exe" app.py
pause
