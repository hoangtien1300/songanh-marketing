@echo off
title DANG NHAP FACEBOOK AUTOMATION CHROME - MO HINH SONG ANH

echo ======================================================================
echo   MO CHROME LUU SESSION FACEBOOK AUTOMATION (PORT 9222)
echo ======================================================================
echo.

set "PROFILE_DIR=D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile"
if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

if exist "%PROFILE_DIR%\SingletonLock" del /f /q "%PROFILE_DIR%\SingletonLock" >nul 2>&1
if exist "%PROFILE_DIR%\SingletonCookie" del /f /q "%PROFILE_DIR%\SingletonCookie" >nul 2>&1
if exist "%PROFILE_DIR%\SingletonSocket" del /f /q "%PROFILE_DIR%\SingletonSocket" >nul 2>&1
if exist "%PROFILE_DIR%\DevToolsActivePort" del /f /q "%PROFILE_DIR%\DevToolsActivePort" >nul 2>&1

start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --remote-allow-origins=* --user-data-dir="D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile" "https://www.facebook.com"

echo.
echo ======================================================================
echo Sep hay dang nhap Facebook tren cua so Chrome vua mo.
echo Khi dang nhap xong, Sep co the dong Chrome hoac de nguyen.
echo Session se duoc luu vinh vien tai:
echo D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile
echo ======================================================================
pause
