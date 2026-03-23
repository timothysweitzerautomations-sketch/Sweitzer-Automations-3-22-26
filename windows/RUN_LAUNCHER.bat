@echo off
REM Run the Tk launcher without building an exe (needs Python on PATH).
setlocal
cd /d "%~dp0.."
python windows_app\launcher.py
if %errorlevel% neq 0 pause
