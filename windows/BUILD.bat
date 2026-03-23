@echo off
REM Build SweitzerAutomations-3-22-26.exe — run from this folder or double-click.
setlocal
cd /d "%~dp0.."
call windows_app\build_exe.bat
