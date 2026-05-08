@echo off
REM Sprint 0A dashboard hourly refresh
REM Schedule via Windows Task Scheduler (Trigger: Daily, Repeat every 1 hour)
REM Or run manually: dashboard_sprint0a\refresh.bat

cd /d "%~dp0\.."
python scripts\build_dashboard_sprint0a.py
echo Done at %date% %time%
