@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title PyFyve

:: ── WINDOWS TERMINAL DETECTION & RELAUNCH ─────────────────────────────────────
:: WT_SESSION is set by Windows Terminal for every process running inside it.
:: If it's not set, we're in cmd — try to move to Windows Terminal for better visuals.

if defined WT_SESSION goto :inside_wt

:: Check if Windows Terminal is already installed
where wt >nul 2>&1
if %errorlevel% equ 0 goto :relaunch_in_wt

:: Not installed — try to install silently (non-blocking: if it fails, continue in cmd)
echo [ .. ] Installing Windows Terminal for better visuals...
winget install --id 9N0DX20HK701 --source msstore --accept-package-agreements --accept-source-agreements --silent >nul 2>&1
if %errorlevel% equ 0 (
    where wt >nul 2>&1
    if %errorlevel% equ 0 goto :relaunch_in_wt
)
:: WT install failed or unavailable — fall through to run in cmd normally
echo [ .. ] Running in standard terminal.
goto :inside_wt

:relaunch_in_wt
:: Relaunch this exact script inside Windows Terminal.
:: --title sets the tab name; the new session will have WT_SESSION set so this block is skipped.
wt --title "PyFyve" cmd /c "cd /d \"%~dp0\" && \"%~f0\""
exit /b

:inside_wt
:: ── FROM HERE DOWN: normal startup regardless of terminal ─────────────────────
color 0F

mode con: cols=150 lines=45

echo ===================================================
echo        PyFyve Initializing...
echo ===================================================

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

if %ERRORLEVEL% NEQ 0 (
    pause
)