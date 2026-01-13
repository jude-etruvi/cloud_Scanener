@echo off
REM Daily Security Scan Script for Windows
REM Schedule this with Task Scheduler for automated daily scans

REM Configuration
set SCANNER_DIR=C:\cloud_security_scanner
set OUTPUT_DIR=%SCANNER_DIR%\reports\daily
set LOG_FILE=%SCANNER_DIR%\logs\daily_scan.log

REM Get current date
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TODAY=%datetime:~0,8%

REM Create output directory
if not exist "%OUTPUT_DIR%\%TODAY%" mkdir "%OUTPUT_DIR%\%TODAY%"

REM Change to scanner directory
cd /d "%SCANNER_DIR%"

REM Activate virtual environment if exists
if exist "%SCANNER_DIR%\venv\Scripts\activate.bat" (
    call "%SCANNER_DIR%\venv\Scripts\activate.bat"
)

REM Run scan
echo Starting daily security scan at %date% %time% >> "%LOG_FILE%"

python scanner.py --provider all --output-dir "%OUTPUT_DIR%\%TODAY%" --verbose >> "%LOG_FILE%" 2>&1

set SCAN_EXIT_CODE=%ERRORLEVEL%

REM Check results
if %SCAN_EXIT_CODE% EQU 0 (
    echo Scan completed successfully - no critical/high issues found >> "%LOG_FILE%"
) else (
    echo Scan found critical/high issues - review required >> "%LOG_FILE%"
)

REM Clean up old reports (optional - requires PowerShell)
powershell -Command "Get-ChildItem '%OUTPUT_DIR%' -Directory | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-30)} | Remove-Item -Recurse -Force"

echo Daily scan completed at %date% %time% >> "%LOG_FILE%"

exit /b %SCAN_EXIT_CODE%
