@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
color 0A
title PyFyve

:: 1. ELEVATE TO ADMIN
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ -- ] Requesting Admin Privileges...
    powershell -Command "Start-Process -FilePath '%0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

echo ===================================================
echo        PyFyve Initializing...
echo ===================================================

:: 2. PYTHON 3.13 CHECK
echo [ .. ] Verifying Python 3.13 Environment...
set "PY_BIN=%LOCALAPPDATA%\Python\bin"
set "PATH=%PY_BIN%;%PATH%"

py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ !! ] Python 3.13 not found. Installing...
    winget install --id 9NQ7512CXL7T --source msstore --accept-package-agreements --accept-source-agreements
    py install 3.13
    timeout /t 3 /nobreak >nul
    for /f "tokens=2*" %%A in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "syspath=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "userpath=%%B"
    set "PATH=%PY_BIN%;!syspath!;!userpath!"
)

py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ EX ] Python 3.13 still not found. Add this to PATH manually:
    echo        %PY_BIN%
    pause & exit /b 1
)
echo [ OK ] Python 3.13 is active.

:: 3. VIRTUAL ENVIRONMENT
echo [ .. ] Verifying virtual environment...
if not exist ".venv\Scripts\activate" (
    echo [ .. ] Creating .venv...
    py -3.13 -m venv .venv
    if errorlevel 1 (
        echo [ EX ] Failed to create venv. Please restart the script.
        pause & exit /b 1
    )
    echo [ OK ] Environment created.
)

:: 4. ACTIVATE AND INSTALL DEPENDENCIES
call "%~dp0.venv\Scripts\activate"

if not exist ".venv\.installed" (
    echo [ .. ] Installing required libraries...
    python -m pip install --upgrade pip --quiet
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt --quiet
        echo done>".venv\.installed"
        echo [ OK ] Libraries installed.
    )
) else (
    echo [ OK ] Libraries are up to date.
)

:: 5. LAUNCH
echo [ .. ] Starting AI Setup Engine...
python setup.py

pause