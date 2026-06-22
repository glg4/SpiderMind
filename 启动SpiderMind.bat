@echo off
chcp 65001 >nul 2>&1
title SpiderMind 慢病智能管理系统
setlocal enabledelayedexpansion

echo.
echo    ╔══════════════════════════════════════════════╗
echo    ║   SpiderMind 慢病轻量化智能管理平台 v2.4      ║
echo    ╚══════════════════════════════════════════════╝
echo.

:: ========================================
:: 步骤1：智能检测 Python
:: ========================================
set "PYTHON_CMD="
set "USE_VENV=0"

:: 优先使用虚拟环境中的 Python
if exist "venv\Scripts\python.exe" (
    set "PYTHON_CMD=venv\Scripts\python.exe"
    set "USE_VENV=1"
    echo [√] 使用虚拟环境 Python
    goto :check_config
)

:: 其次搜索系统 Python
for %%c in (python python3 py "py -3") do (
    %%c --version >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=%%c"
        echo [√] 检测到 Python (系统安装)
        goto :check_config
    )
)

echo    [X] 未检测到 Python！
echo    请先运行 setup.bat 安装环境，或手动安装 Python 3.9+
echo    下载地址：https://www.python.org/downloads/
pause
exit /b 1

:check_config

:: ========================================
:: 步骤2：检查配置文件
:: ========================================
if not exist ".env" (
    if exist ".env.example" (
        echo [!] 未找到 .env 配置文件，正在创建...
        copy .env.example .env >nul 2>&1
    )
)

:: 快速检查 Token 是否配置
set "TOKEN_CHECK="
for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
    if "%%a"=="COZE_API_TOKEN" set "TOKEN_CHECK=%%b"
)

if "%TOKEN_CHECK%"=="" (
    echo [!] Token 未配置
    echo    请用记事本打开 .env 文件填入 Token
    echo    获取: https://www.coze.cn -> 个人中心 -> 访问令牌
    start notepad.exe .env 2>nul
    echo    配置完成后请重新运行此脚本
    pause
    exit /b 1
)

:: 检查是否为占位符
echo %TOKEN_CHECK% | findstr /C:"在这里填入" >nul 2>&1
if %errorlevel% equ 0 (
    echo [!] Token 仍为占位符，请填入真实 Token
    start notepad.exe .env 2>nul
    pause
    exit /b 1
)

echo [√] Token 已配置
echo.

:: ========================================
:: 步骤3：检查依赖是否已安装
:: ========================================
echo [检查] 验证依赖...
%PYTHON_CMD% -c "import streamlit, pandas, requests, openpyxl, plotly" 2>nul
if %errorlevel% neq 0 (
    echo [!] 依赖未安装或缺失，尝试自动安装...
    if "%USE_VENV%"=="1" (
        venv\Scripts\pip.exe install -r requirements.txt --quiet 2>nul
    ) else (
        %PYTHON_CMD% -m pip install -r requirements.txt --quiet 2>nul
    )
    if %errorlevel% neq 0 (
        echo [X] 自动安装失败，请先运行 setup.bat
        pause
        exit /b 1
    )
    echo [√] 依赖已修复
)
echo [√] 依赖检查通过
echo.

:: ========================================
:: 步骤4：智能选择端口（避免冲突）
:: ========================================
set "PORT=8502"
set "FALLBACK_PORTS=8503 8504 8505 8506 8507"

:: 检查默认端口是否被占用
%PYTHON_CMD% -c "import socket; s=socket.socket(); s.settimeout(1); r=s.connect_ex(('127.0.0.1',%PORT%)); s.close(); exit(r)" 2>nul
if %errorlevel% neq 0 (
    echo [√] 端口 %PORT% 可用
    goto :start_server
)

echo [!] 端口 %PORT% 已被占用，搜索可用端口...
for %%p in (%FALLBACK_PORTS%) do (
    %PYTHON_CMD% -c "import socket; s=socket.socket(); s.settimeout(1); r=s.connect_ex(('127.0.0.1',%%p)); s.close(); exit(r)" 2>nul
    if %errorlevel% neq 0 (
        set "PORT=%%p"
        echo [√] 找到可用端口: !PORT!
        goto :start_server
    )
)

echo [X] 所有端口均被占用！请关闭其他 Streamlit 应用后重试
pause
exit /b 1

:start_server

:: ========================================
:: 步骤5：启动服务
:: ========================================
echo.
echo    ╔══════════════════════════════════════════════╗
echo    ║  系统启动中...                               ║
echo    ║  浏览器将自动打开                            ║
echo    ║  地址: http://localhost:%PORT%              ║
echo    ║  按 Ctrl+C 可停止服务                        ║
echo    ╚══════════════════════════════════════════════╝
echo.

:: 尝试自动打开浏览器
start http://localhost:%PORT% 2>nul

:: 启动 Streamlit
%PYTHON_CMD% -m streamlit run main.py --server.port %PORT% --browser.gatherUsageStats false --server.headless true

echo.
echo 系统已停止。按任意键关闭窗口...
pause >nul
exit /b 0
