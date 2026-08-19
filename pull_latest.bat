@echo off
cd /d "%~dp0"
git pull --ff-only
if errorlevel 1 (
  echo.
  echo Pull failed. Resolve local changes, then try again.
)
timeout /t 5 /nobreak >nul
