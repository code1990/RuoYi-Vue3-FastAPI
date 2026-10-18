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
call npm.cmd install
set "EXIT_CODE=%ERRORLEVEL%"
popd

if not "%EXIT_CODE%"=="0" (
  echo Frontend dependency installation failed.
  pause
  exit /b %EXIT_CODE%
)

echo Frontend dependencies installed successfully.
pause
endlocal
