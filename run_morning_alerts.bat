@echo off
chcp 65001 >nul
cd /d "d:\Song_Anh\marketing_workflow_app"
if "%1"=="" (
    python song_anh_telegram_alert_bot.py --marketing
) else (
    python song_anh_telegram_alert_bot.py %1
)
