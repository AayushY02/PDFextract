@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PIPELINE_SCRIPT=%SCRIPT_DIR%run_pipeline.ps1"

if not exist "%PIPELINE_SCRIPT%" (
    echo run_pipeline.ps1 was not found next to this launcher.
    endlocal & exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PIPELINE_SCRIPT%" %*
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Pipeline failed with exit code %EXIT_CODE%.
)

endlocal & exit /b %EXIT_CODE%
