@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title PyFyve

:: Full PowerShell path — avoids "not recognized" on minimal Windows VMs
:: where System32 may not be in the inherited PATH at launch time.
set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"

:: ── WINDOWS TERMINAL RELAUNCH ──────────────────────────────────────────────
:: If already inside a WT session, skip the relaunch and go straight to setup.
:: The terminal background and colour are set by console.py when Python starts,
:: so no PowerShell call is needed here.
if defined WT_SESSION goto :inside_wt

where wt >nul 2>&1
if %errorlevel% equ 0 (
    wt --size 150,45 --title "PyFyve" cmd /c "cd /d \"%~dp0\" && \"%~f0\""
    exit /b
)

:inside_wt
:: Set background to dark grey instantly via ANSI escape (no PowerShell delay)
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
echo %ESC%]11;#2D2D2D%ESC%\
mode con: cols=150 lines=45
cls

echo ===================================================
echo        PyFyve Initializing...
echo ===================================================

:: ── PYTHON CHECK & INSTALL ─────────────────────────────────────────────────
echo [ .. ] Verifying Python Environment...
set "PY_CMD="

python --version 2>nul | find "3.13" >nul
if %errorlevel% equ 0 set "PY_CMD=python"

if not defined PY_CMD (
    py -3.13 --version >nul 2>&1
    if !errorlevel! equ 0 set "PY_CMD=py -3.13"
)

if not defined PY_CMD (
    echo [ !! ] Python 3.13 not found. Installing via Winget...
    winget install --id 9NQ7512CXL7T --source msstore --accept-package-agreements --accept-source-agreements
    if !errorlevel! neq 0 (
        echo [ EX ] Automatic installation failed.
        echo        Please install Python 3.13 manually from https://python.org
        pause & exit /b 1
    )
    echo [ OK ] Python Install Manager installed.

    :: Refresh PATH from the Windows Registry so the new install is visible
    :: without requiring a terminal restart.
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

:: ── VIRTUAL ENVIRONMENT ────────────────────────────────────────────────────
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

:: ── INSTALL / UPDATE DEPENDENCIES ──────────────────────────────────────────
:: Hash check uses Python (already active) instead of PowerShell.
:: This avoids a 300-600ms PowerShell cold-start on every launch.
if exist "requirements.txt" (
    set "REQ_HASH_FILE=.venv\.req_hash"

    :: Write hash to temp file; Python avoids quote-escaping issues in FOR loops
    python -c "import hashlib; print(hashlib.md5(open('requirements.txt','rb').read()).hexdigest())" > "%TEMP%\pyfyve_hash.tmp" 2>nul
    set "CURRENT_HASH="
    if exist "%TEMP%\pyfyve_hash.tmp" set /p CURRENT_HASH=<"%TEMP%\pyfyve_hash.tmp"
    del "%TEMP%\pyfyve_hash.tmp" 2>nul

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

:: ── LAUNCH ─────────────────────────────────────────────────────────────────
echo [ .. ] Starting PyFyve Setup...
python setup.py