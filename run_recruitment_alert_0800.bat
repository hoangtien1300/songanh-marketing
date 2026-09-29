@echo off
chcp 65001 >nul
cd /d "d:\Song_Anh\marketing_workflow_app"
python daily_recruitment_telegram_alert_0800.py %*
