@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title PyFyve

:: ── SET THEME IMMEDIATELY ──
powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host -NoNewLine ([char]27 + ']11;#2D2D2D' + [char]7)"
cls

:: ── WINDOWS TERMINAL RELAUNCH ──
if defined WT_SESSION goto :inside_wt

where wt >nul 2>&1
if %errorlevel% equ 0 (
    wt --size 150,45 --title "PyFyve" cmd /c "cd /d \"%~dp0\" && \"%~f0\""
    exit /b
)

:inside_wt
:: Ensure the theme is set inside the WT session too
powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host -NoNewLine ([char]27 + ']11;#2D2D2D' + [char]7)"
cls
mode con: cols=150 lines=45

echo ===================================================
echo        PyFyve Initializing...
echo ===================================================

:: ... Rest of your script (Python checks, Venv, Pip, etc.) ...

:: 1. PYTHON CHECK & INSTALL
echo [ .. ] Verifying Python Environment...
set "PY_CMD="

python --version 2>nul | find "3.13" >nul
if %errorlevel% equ 0 set "PY_CMD=python"

if not defined PY_CMD (
    py -3.13 --version >nul 2>&1
    if !errorlevel! equ 0 set "PY_CMD=py -3.13"
)

if not defined PY_CMD (
    echo [ !! ] Python 3.13 not found. Installing Python Install Manager...
    winget install --id 9NQ7512CXL7T --source msstore --accept-package-agreements --accept-source-agreements
    if !errorlevel! neq 0 (
        echo [ EX ] Automatic installation failed.
        echo        Please install Python 3.13 manually from https://python.org
        pause & exit /b 1
    )
    echo [ OK ] Python Install Manager installed.

    :: Refresh PATH from the Windows Registry — avoids needing to restart the terminal
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%B"
    set "PATH=!SYS_PATH!;!USER_PATH!"
    set "PATH=%LOCALAPPDATA%\Microsoft\WindowsApps;!PATH!"

    set "PY_CMD=py -3.13"
)

%PY_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ EX ] Python was installed but could not be located. Please restart this terminal.
    pause & exit /b 1
)
echo [ OK ] Python is active.

:: 2. VIRTUAL ENVIRONMENT
echo [ .. ] Verifying virtual environment...
if not exist ".venv\Scripts\activate" (
    echo [ .. ] Creating .venv...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ EX ] Failed to create venv.
        pause & exit /b 1
    )
    echo [ OK ] Environment created.
)

call "%~dp0.venv\Scripts\activate"

:: 3. INSTALL / UPDATE DEPENDENCIES
if exist "requirements.txt" (
    set "REQ_HASH_FILE=.venv\.req_hash"
    set "CURRENT_HASH="
    for /f "delims=" %%H in ('powershell -NoProfile -Command "Get-FileHash requirements.txt -Algorithm MD5 | Select-Object -ExpandProperty Hash"') do set "CURRENT_HASH=%%H"

    set "STORED_HASH="
    if exist "!REQ_HASH_FILE!" set /p STORED_HASH=<"!REQ_HASH_FILE!"

    if /i "!CURRENT_HASH!" neq "!STORED_HASH!" (
        echo [ .. ] Installing/updating required libraries...
        python -m pip install --upgrade pip --quiet
        python -m pip install -r requirements.txt --quiet
        if errorlevel 1 (
            echo [ EX ] Failed to install libraries. Check your internet connection.
            pause & exit /b 1
        )
        echo !CURRENT_HASH!>"!REQ_HASH_FILE!"
        echo [ OK ] Libraries installed.
    ) else (
        echo [ OK ] Libraries are up to date.
    )
) else (
    echo [ !! ] requirements.txt not found. Skipping library install.
)

:: 4. LAUNCH
echo [ .. ] Starting PyFyve Setup...
python setup.py