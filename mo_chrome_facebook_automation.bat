@echo off
chcp 65001 > nul
echo ======================================================================
echo   🚀 KHỞI ĐỘNG CHROME CHUYÊN DỤNG CHO TOOL AUTOMATION FACEBOOK 🚀
echo   Port: 9222 | Profile: D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile
echo ======================================================================
echo.

set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME_PATH% set CHROME_PATH="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
if not exist %CHROME_PATH% set CHROME_PATH="%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

set PROFILE_DIR=D:\Song_Anh\_Shared_Core\Credentials\facebook_chrome_profile

if not exist "%PROFILE_DIR%" mkdir "%PROFILE_DIR%"

start "" %CHROME_PATH% --remote-debugging-port=9222 --user-data-dir="%PROFILE_DIR%" --disable-notifications https://www.facebook.com

echo ✅ Đã khởi động Chrome thành công!
echo 💡 Sếp chỉ cần đăng nhập Facebook trên cửa sổ này một lần đầu tiên.
echo 🤖 Các Tool Python (Re-comment, Đăng bài) sẽ tự động kết nối qua Port 9222.
echo.
pause
