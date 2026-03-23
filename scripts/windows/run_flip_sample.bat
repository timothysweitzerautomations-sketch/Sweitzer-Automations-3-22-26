@echo off
setlocal
cd /d "%~dp0..\.."
echo Running flip_engine on sample_flips.csv ...
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m revenue_pulse.flip_engine revenue_pulse\sample_flips.csv
) else (
  python -m revenue_pulse.flip_engine revenue_pulse\sample_flips.csv
)
echo.
pause
