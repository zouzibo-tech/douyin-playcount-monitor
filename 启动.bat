@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 抖音合集播放量监控

if exist "抖音监控.exe" (
    echo 正在启动 ... 界面会自动在浏览器中打开。
    "抖音监控.exe"
    goto :eof
)

if exist "dist\抖音监控\抖音监控.exe" (
    echo 正在启动 ... 界面会自动在浏览器中打开。
    "dist\抖音监控\抖音监控.exe"
    goto :eof
)

set PY=C:\Users\Administrator\.workbuddy\binaries\python\envs\default\Scripts\python.exe
if exist "%PY%" (
    echo 以源码模式启动 ...
    "%PY%" "%~dp0src\app.py"
    goto :eof
)

echo.
echo 未找到 抖音监控.exe，也未找到本地 Python 环境。
echo 请把打包好的 dist\抖音监控 整个文件夹复制到本机后再运行。
echo.
pause
