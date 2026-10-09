@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 立即抓取一次（不打开界面）

set PY=C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe
if exist "%PY%" (
    "%PY%" "%~dp0src\pipeline.py"
) else (
    echo 未找到本地 Python 环境，请改用界面里的「立即抓取」按钮。
)
echo.
pause
