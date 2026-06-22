@echo off
chcp 65001 >nul 2>&1
title SpiderMind 智能安装向导
setlocal enabledelayedexpansion

echo.
echo    ╔══════════════════════════════════════════════╗
echo    ║     SpiderMind 慢病智能管理平台 - 安装向导     ║
echo    ╚══════════════════════════════════════════════╝
echo.

:: ========================================
:: 步骤1：智能检测 Python 环境
:: ========================================
echo [1/5] 正在检测 Python 环境...
set "PYTHON_CMD="

:: 按优先级尝试各种 Python 命令
for %%c in (python python3 py "py -3") do (
    call :try_python "%%c" && goto :found_python
)

echo    [错误] 未检测到 Python！
echo.
echo    ╔══════════════════════════════════════════════╗
echo    ║  请先安装 Python 3.9 或更高版本               ║
echo    ║  下载地址：https://www.python.org/downloads/   ║
echo    ║  ⚠ 安装时务必勾选 "Add Python to PATH"       ║
echo    ╚══════════════════════════════════════════════╝
echo.
pause
exit /b 1

:try_python
set "test_cmd=%~1"
%test_cmd% --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=*" %%v in ('%test_cmd% --version 2^>^&1') do (
        echo    [√] 检测到 Python: %%v
    )
    :: 检查版本 >= 3.9
    for /f "tokens=2 delims= " %%v in ('%test_cmd% --version 2^>^&1') do (
        set "pyver=%%v"
        for /f "tokens=1,2 delims=." %%a in ("!pyver!") do (
            set "major=%%a"
            set "minor=%%b"
            if !major! gtr 3 goto :set_python_ok
            if !major! equ 3 if !minor! geq 9 goto :set_python_ok
        )
    )
    echo    [警告] Python 版本过低（需要 >= 3.9），尝试下一个...
    exit /b 1
)
exit /b 1

:set_python_ok
set "PYTHON_CMD=%test_cmd%"
exit /b 0

:found_python
echo    Python 命令: %PYTHON_CMD%
echo.

:: ========================================
:: 步骤2：检查 pip 并升级
:: ========================================
echo [2/5] 检查 pip 包管理器...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    [警告] pip 未安装或不可用
    echo    尝试安装 pip...
    %PYTHON_CMD% -m ensurepip --upgrade 2>nul
    if %errorlevel% neq 0 (
        echo    [错误] 无法安装 pip，请手动安装 Python
        pause
        exit /b 1
    )
)
echo    [√] pip 就绪
echo.

:: ========================================
:: 步骤3：创建虚拟环境（可选，智能检测）
:: ========================================
echo [3/5] 准备 Python 环境...
set "USE_VENV=0"
if exist "venv\Scripts\activate.bat" (
    echo    检测到已有虚拟环境，直接使用
    set "USE_VENV=1"
) else if exist "venv" (
    echo    虚拟环境目录存在但损坏，重新创建...
    rmdir /s /q venv 2>nul
)

if not exist "venv" (
    echo    正在创建虚拟环境（用于隔离依赖）...
    %PYTHON_CMD% -m venv venv 2>nul
    if %errorlevel% equ 0 (
        set "USE_VENV=1"
        echo    [√] 虚拟环境创建成功
    ) else (
        echo    [提示] 虚拟环境创建失败，将使用系统 Python 直接安装
        echo    这不会影响系统使用，仅依赖会安装到全局
        set "USE_VENV=0"
    )
)

if "%USE_VENV%"=="1" (
    call venv\Scripts\activate.bat 2>nul
    set "PIP_CMD=venv\Scripts\pip.exe"
    set "PY_RUN=venv\Scripts\python.exe"
) else (
    set "PIP_CMD=%PYTHON_CMD% -m pip"
    set "PY_RUN=%PYTHON_CMD%"
)
echo.

:: ========================================
:: 步骤4：安装依赖
:: ========================================
echo [4/5] 安装项目依赖...
echo    正在从 requirements.txt 读取依赖列表...

:: 检查是否已安装（快速跳过）
%PY_RUN% -c "import streamlit, pandas, requests, openpyxl, plotly" 2>nul
if %errorlevel% equ 0 (
    echo    [√] 核心依赖已安装，跳过安装步骤
    goto :skip_install
)

echo    正在下载安装（首次使用约需 1-3 分钟）...
%PIP_CMD% install -r requirements.txt --quiet --disable-pip-version-check
if %errorlevel% neq 0 (
    echo.
    echo    [警告] 依赖安装出现警告，尝试不使用缓存重新安装...
    %PIP_CMD% install -r requirements.txt --no-cache-dir --quiet
    if %errorlevel% neq 0 (
        echo.
        echo    [错误] 依赖安装失败！
        echo    可能的原因：
        echo    1. 网络连接问题 → 请检查网络后重试
        echo    2. pip 源连接超时 → 可尝试使用国内镜像
        echo    手动安装命令：pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
        echo.
        pause
        exit /b 1
    )
)
echo    [√] 依赖安装完成

:skip_install
echo.

:: ========================================
:: 步骤5：配置文件检查
:: ========================================
echo [5/5] 检查配置文件...
if not exist ".env" (
    if exist ".env.example" (
        echo    未检测到 .env 配置文件
        echo    正在从 .env.example 创建默认配置...
        copy .env.example .env >nul 2>&1
        echo    [√] .env 文件已创建
        echo.
        echo    ╔══════════════════════════════════════════════╗
        echo    ║  ⚠ 请配置你的 Coze API Token！              ║
        echo    ║                                             ║
        echo    ║  1. 访问 https://www.coze.cn                ║
        echo    ║  2. 点击右上角头像 -> 个人中心              ║
        echo    ║  3. 左侧菜单 -> 访问令牌 -> 新建令牌         ║
        echo    ║  4. 过期时间选"无过期时间"，勾选 chat 权限    ║
        echo    ║  5. 复制 Token 后粘贴到 .env 文件中          ║
        echo    ║  6. 用记事本打开 .env 文件编辑即可           ║
        echo    ╚══════════════════════════════════════════════╝
        echo.
        pause
    )
) else (
    :: 检查 .env 中的 Token 是否为占位符
    findstr /C:"在这里填入你的Token" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo    [提示] Token 仍为默认占位符，请配置真实 Token
        echo    用记事本打开 .env 文件，替换 COZE_API_TOKEN 的值
        echo.
    ) else (
        echo    [√] .env 配置就绪
    )
)

echo.
echo    ╔══════════════════════════════════════════════════╗
echo    ║          🎉 安装完成！                           ║
echo    ║         双击 "启动SpiderMind.bat" 即可运行        ║
echo    ╚══════════════════════════════════════════════════╝
echo.
echo    运行后浏览器访问: http://localhost:8502
echo.
pause
exit /b 0
