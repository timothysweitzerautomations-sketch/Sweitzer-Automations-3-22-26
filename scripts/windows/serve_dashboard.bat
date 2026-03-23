@echo off
setlocal
cd /d "%~dp0..\.."
echo.
echo  Sweitzer Automations 3-22-26 - local web dashboard
echo  Open in your browser:
echo    http://localhost:8080/index.html          (Revenue Pulse)
echo    http://localhost:8080/flip_tracker.html   (Flip profit tracker)
echo.
echo  Press Ctrl+C in this window to stop the server.
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m http.server 8080 --directory revenue_pulse
) else (
  python -m http.server 8080 --directory revenue_pulse
)
if %errorlevel% neq 0 (
  echo.
  echo  Python was not found. Install Python 3 from https://www.python.org/downloads/
  echo  and check "Add python.exe to PATH" during setup.
  echo.
)
pause
