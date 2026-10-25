@echo off
REM Synthetic test run: fresh database, made-up participants, load test, then charts.
REM Runs from the folder this file is in, so it works on any computer.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Could not find .venv\Scripts\python.exe in this folder.
    echo Set up the project first: py -m venv .venv  then  .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b
)

echo Step 1 of 4: deleting the old database
if exist "instance\capstone.db" del "instance\capstone.db" 2>nul
if exist "instance\capstone.db" (
    echo.
    echo The database is still in use. Close every app window first, then run this file again.
    pause
    exit /b
)

echo.
echo Step 2 of 4: loading the synthetic participants
".venv\Scripts\python.exe" scripts\seed_demo.py
if errorlevel 1 (
    echo.
    echo Loading the synthetic data failed. Copy the error above and send it.
    pause
    exit /b
)

echo.
echo Step 3 of 4: starting the app in a new window and running the load test
start "Training app - close this window to stop the app" ".venv\Scripts\python.exe" app.py
timeout /t 5 /nobreak >nul
echo.
echo ^> python scripts\load_test.py
".venv\Scripts\python.exe" scripts\load_test.py
echo.
echo Open http://127.0.0.1:5000/admin to see the dashboard.
echo When you are done, press any key here to make the charts.
pause >nul

echo.
echo Step 4 of 4: making the charts
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check matplotlib
".venv\Scripts\python.exe" scripts\make_charts.py
start "" "%CD%\charts"
echo.
echo Done. The charts folder is open.
echo The app is still running in the other window. Close it when you are finished.
pause
