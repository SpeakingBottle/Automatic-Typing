@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PYTHONW=C:\Users\Deki\AppData\Local\Programs\Python\Python313\pythonw.exe"
if not exist "%PYTHONW%" set "PYTHONW=pythonw"
start "" "%PYTHONW%" "%~dp0main.py"
