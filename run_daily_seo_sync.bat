@echo off
chcp 65001 > nul
TITLE Song Anh Group - Daily SEO Zero-Touch Sync Engine

SET APP_DIR=d:\Song_Anh\marketing_workflow_app
SET LOG_FILE=%APP_DIR%\daily_sync_log.txt

echo [%DATE% %TIME%] Starting Automatic Daily SEO Sync Engine... >> "%LOG_FILE%"

cd /d "%APP_DIR%"
python "%APP_DIR%\gsc_ga4_seo_extractor.py" >> "%LOG_FILE%" 2>&1

IF %ERRORLEVEL% EQU 0 (
    echo [%DATE% %TIME%] SUCCESS: Daily SEO Sync Completed Cleanly. >> "%LOG_FILE%"
) ELSE (
    echo [%DATE% %TIME%] ERROR: Daily SEO Sync Failed with exit code %ERRORLEVEL%. >> "%LOG_FILE%"
)

powershell -Command "if (-not (Get-ScheduledTask -TaskName 'SongAnh_Daily_SEO_Sync' -ErrorAction SilentlyContinue)) { $action = New-ScheduledTaskAction -Execute '%APP_DIR%\run_daily_seo_sync.bat'; $trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM; Register-ScheduledTask -TaskName 'SongAnh_Daily_SEO_Sync' -Action $action -Trigger $trigger -Description 'Song Anh Daily SEO Sync Zero-Touch Automation'; Write-Host 'Task Scheduler Registered Successfully.' }" > nul 2>&1

exit /b 0
