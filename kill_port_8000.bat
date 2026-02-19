@echo off
set PORT=8000
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%PORT% ^| findstr LISTENING') do (
    echo Killing process on port %PORT% with PID %%a
    taskkill /PID %%a /F
)
echo Port %PORT% serbest bırakıldı.
pause
