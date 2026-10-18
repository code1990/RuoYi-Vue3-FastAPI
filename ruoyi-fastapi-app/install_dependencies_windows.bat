@echo off
setlocal

set "APP_DIR=%~dp0"
set "PNPM_VERSION=10.28.1"

if not exist "%APP_DIR%package.json" (
  echo package.json was not found: "%APP_DIR%"
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js is not installed. Install Node.js 20.19.0+ LTS, reopen this window, then run this script again.
  pause
  exit /b 1
)

for /f "tokens=*" %%i in ('node -p "process.versions.node"') do set "NODE_VERSION=%%i"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$v=[version]'%NODE_VERSION%'; if ((($v.Major -eq 20) -and ($v -ge [version]'20.19.0')) -or ($v -ge [version]'22.12.0')) { exit 0 }; exit 1"
if errorlevel 1 (
  echo Node.js %NODE_VERSION% is unsupported. Install Node.js 20.19.0+ LTS or 22.12.0+.
  pause
  exit /b 1
)

where corepack >nul 2>nul
if errorlevel 1 (
  echo Corepack was not found. Reinstall a supported Node.js version with Corepack enabled.
  pause
  exit /b 1
)

pushd "%APP_DIR%"
call corepack enable
if errorlevel 1 goto :failed

if exist "pnpm-lock.yaml" (
  call corepack pnpm@%PNPM_VERSION% install --frozen-lockfile
) else (
  echo pnpm-lock.yaml was not found. Installing from package.json and creating a new lockfile.
  call corepack pnpm@%PNPM_VERSION% install --no-frozen-lockfile
)
if errorlevel 1 goto :failed

popd
echo Dependencies installed with pnpm %PNPM_VERSION%.
echo Next: run "pnpm build:app" before opening HBuilderX for cloud packaging.
pause
exit /b 0

:failed
set "EXIT_CODE=%ERRORLEVEL%"
popd
echo Dependency installation failed. Copy the first ERROR line and its details for troubleshooting.
pause
exit /b %EXIT_CODE%
