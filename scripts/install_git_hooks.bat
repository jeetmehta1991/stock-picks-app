@echo off
REM Pass 53 Day-9 v8h+1 owner-mandated git hook installer.
REM Run ONCE to enable pre-commit enforcement of CHECKLIST rules.
REM
REM What it does:
REM   1. Copies scripts/git_hooks/pre-commit to .git/hooks/pre-commit
REM   2. Makes it executable (Windows git uses bash for hooks)
REM
REM From repo root: scripts\install_git_hooks.bat

setlocal
cd /d "%~dp0\.."

if not exist .git\hooks (
    echo ERROR: .git/hooks not found. Are you in a git repo?
    exit /b 1
)

copy /Y scripts\git_hooks\pre-commit .git\hooks\pre-commit
if errorlevel 1 (
    echo ERROR: copy failed.
    exit /b 1
)

REM Windows git uses bash; no chmod needed but make sure CRLF doesn't break shebang
echo.
echo Installed: .git\hooks\pre-commit
echo Test it: python scripts\preflight.py --staged
echo.
echo To bypass once (NOT recommended): git commit --no-verify
endlocal
