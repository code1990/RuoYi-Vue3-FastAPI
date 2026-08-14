@echo off
setlocal

set "ROOT_DIR=%~dp0"
set "FRONTEND_DIR=%ROOT_DIR%ruoyi-fastapi-frontend"
set "DOWNLOADS_DIR=%USERPROFILE%\Downloads"
set "ZIP_FILE=%DOWNLOADS_DIR%\ruoyi-fastapi-frontend-dist.zip"

if not exist "%FRONTEND_DIR%\package.json" (
  echo Frontend package.json was not found: "%FRONTEND_DIR%"
  exit /b 1
)

pushd "%ROOT_DIR%"
git pull --ff-only
if errorlevel 1 (
  popd
  echo Git pull failed.
  exit /b 1
)
popd

pushd "%FRONTEND_DIR%"
call npm.cmd run build:prod
if errorlevel 1 (
  popd
  echo Frontend production build failed.
  exit /b 1
)

if not exist "dist" (
  popd
  echo Frontend dist directory was not generated.
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Compress-Archive -Path '.\dist\*' -DestinationPath '%ZIP_FILE%' -Force"
if errorlevel 1 (
  popd
  echo ZIP archive creation failed.
  exit /b 1
)

popd
echo Deployment package created: "%ZIP_FILE%"
endlocal
