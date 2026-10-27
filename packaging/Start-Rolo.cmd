@echo off
setlocal
powershell.exe -NoProfile -STA -File "%~dp0RoloLauncher.ps1"
exit /b %errorlevel%
