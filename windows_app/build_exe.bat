@echo off
REM Run from the PROJECT ROOT (parent of windows_app). Requires Python + pip install pyinstaller.
setlocal
cd /d "%~dp0.."
echo Building SweitzerAutomations-3-22-26.exe ...
echo.

python -m pip install -q -r windows_app\requirements-build.txt

set ICON_ARG=
if exist "windows\icon.ico" (
  set "ICON_ARG=--icon windows\icon.ico"
  echo Using windows\icon.ico
) else if exist "windows_app\icon.ico" (
  set "ICON_ARG=--icon windows_app\icon.ico"
  echo Using windows_app\icon.ico
) else (
  echo No windows\icon.ico or windows_app\icon.ico — optional. See README_ICON.txt
)

pyinstaller --noconfirm --onefile --windowed --name SweitzerAutomations ^
  --paths . ^
  --add-data "revenue_pulse;revenue_pulse" ^
  --hidden-import=revenue_pulse ^
  --hidden-import=revenue_pulse.revenue_engine ^
  --hidden-import=revenue_pulse.flip_engine ^
  %ICON_ARG% ^
  windows_app\launcher.py

if %errorlevel% neq 0 (
  echo Build failed.
  pause
  exit /b 1
)
echo.
echo Done: dist\SweitzerAutomations-3-22-26.exe
echo.
pause
