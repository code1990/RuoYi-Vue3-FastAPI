@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%ruoyi-fastapi-frontend"

if not exist "%FRONTEND_DIR%\package.json" (
  echo Frontend package.json was not found: "%FRONTEND_DIR%"
  pause
  exit /b 1
)

pushd "%FRONTEND_DIR%"
start "RuoYi Frontend Dev Server" cmd /k "set CHOKIDAR_USEPOLLING=true&& set CHOKIDAR_INTERVAL=100&& call npm.cmd run dev -- --strictPort"
popd

powershell -NoProfile -ExecutionPolicy Bypass -Command "$deadline = (Get-Date).AddSeconds(30); do { if (Test-NetConnection -ComputerName 127.0.0.1 -Port 5173 -InformationLevel Quiet) { Start-Process msedge.exe 'http://localhost:5173'; exit 0 }; Start-Sleep -Milliseconds 500 } while ((Get-Date) -lt $deadline); exit 1"
if errorlevel 1 (
  echo Frontend dev server did not start on http://localhost:5173 within 30 seconds.
  pause
  exit /b 1
)

echo Frontend dev server is running at http://localhost:5173
endlocal
