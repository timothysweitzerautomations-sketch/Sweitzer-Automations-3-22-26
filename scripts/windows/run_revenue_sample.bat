@echo off
setlocal
cd /d "%~dp0..\.."
echo Running revenue_engine on sample_sales.csv ...
echo.
where py >nul 2>&1
if %errorlevel%==0 (
  py -3 -m revenue_pulse.revenue_engine revenue_pulse\sample_sales.csv
) else (
  python -m revenue_pulse.revenue_engine revenue_pulse\sample_sales.csv
)
echo.
pause
