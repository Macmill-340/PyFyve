@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
title PyFyve

:: ── WINDOWS TERMINAL RELAUNCH ──────────────────────────────────────────────
:: If already inside a WT session, skip the relaunch and proceed to setup.
:: Terminal background is set by console.py the moment Python starts.
if defined WT_SESSION goto :inside_wt

where wt >nul 2>&1
if %errorlevel% equ 0 (
    wt --size 150,45 --title "PyFyve" cmd /c "cd /d \"%~dp0\" && \"%~f0\""
    exit /b
)

:inside_wt
:: Apply dark background via a pure-batch ANSI OSC sequence.
:: Works in Windows Terminal; harmless no-op in plain cmd.exe.
for /f %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"
echo %ESC%]11;#2D2D2D%ESC%\
mode con: cols=150 lines=45
cls

echo ===================================================
echo        PyFyve Initializing...
echo ===================================================

:: ── PYTHON CHECK & INSTALL ─────────────────────────────────────────────────
:: Decision rationale (do not simplify without reading this):
::
::   Winget + Microsoft Store:  Fails with 0x8007052e (Store auth error) on
::     fresh VMs. Root cause is the Store identity token not being provisioned
::     yet. Not fixable from a script. Unreliable.
::
::   MSIX direct download + Add-AppxPackage:  Requires PowerShell AND
::     "Sideload apps" policy to be enabled (off by default on fresh Windows 11
::     Home/Pro VMs). Two independent failure modes.
::
::   Python .exe installer (current approach):  No admin rights required,
::     no Store auth, no sideloading, no PowerShell. curl.exe ships with every
::     Windows 10 1803+ and all Windows 11 builds. The .exe installer is NOT
::     being discontinued — the py launcher is just no longer bundled WITH it
::     from 3.14+, which does not affect us since we detect and set PY_CMD
::     explicitly. When Python 3.13 reaches end-of-life, update PYTHON_VER and
::     PYTHON_URL below.
::
:: PYTHON_VER is used only for display. PYTHON_URL is the actual download target.
set "PYTHON_VER=3.13.3"
set "PYTHON_URL=https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe"

echo [ .. ] Verifying Python Environment...
set "PY_CMD="

:: Check 1: system Python on PATH
python --version 2>nul | find "3.13" >nul
if %errorlevel% equ 0 set "PY_CMD=python"

:: Check 2: py launcher
if not defined PY_CMD (
    py -3.13 --version >nul 2>&1
    if !errorlevel! equ 0 set "PY_CMD=py -3.13"
)

:: Check 3: download and install silently
if not defined PY_CMD (
    set "PYTHON_INSTALLER=%TEMP%\pyfyve-python-installer.exe"

    echo [ !! ] Python %PYTHON_VER% not found. Downloading installer from python.org...
    "%SystemRoot%\System32\curl.exe" -L --silent --show-error -o "!PYTHON_INSTALLER!" "%PYTHON_URL%"
    if !errorlevel! neq 0 (
        echo [ EX ] Download failed. Please install Python 3.13 from https://python.org
        del "!PYTHON_INSTALLER!" 2>nul
        pause & exit /b 1
    )

    echo [ .. ] Installing Python %PYTHON_VER% ^(this may take a moment^)...
    "!PYTHON_INSTALLER!" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    if !errorlevel! neq 0 (
        echo [ EX ] Installation failed. Please install Python 3.13 from https://python.org
        del "!PYTHON_INSTALLER!" 2>nul
        pause & exit /b 1
    )
    del "!PYTHON_INSTALLER!" 2>nul
    echo [ OK ] Python %PYTHON_VER% installed.

    :: Propagate the installer's PATH changes into this session so we don't
    :: require the user to restart the terminal.
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%B"
    set "PATH=!SYS_PATH!;!USER_PATH!"
    set "PATH=%LOCALAPPDATA%\Microsoft\WindowsApps;!PATH!"

    set "PY_CMD=py -3.13"
)

:: Verify the resolved Python command actually executes.
:: If it does not (e.g. a stale PATH entry pointing at a deleted installation),
:: clear PY_CMD and fall through to re-download rather than aborting with a
:: cryptic error. This handles the case where the user has manually removed
:: Python without updating PATH.
%PY_CMD% --version >nul 2>&1
if !errorlevel! neq 0 (
    echo [ !! ] Python resolved to '%PY_CMD%' but failed to execute.
    echo [ .. ] PATH entry may be stale. Re-downloading Python installer...
    set "PY_CMD="
    set "PYTHON_INSTALLER=%TEMP%\pyfyve-python-installer.exe"

    "%SystemRoot%\System32\curl.exe" -L --silent --show-error -o "!PYTHON_INSTALLER!" "%PYTHON_URL%"
    if !errorlevel! neq 0 (
        echo [ EX ] Download failed. Please install Python 3.13 from https://python.org
        del "!PYTHON_INSTALLER!" 2>nul
        pause & exit /b 1
    )

    echo [ .. ] Installing Python %PYTHON_VER%...
    "!PYTHON_INSTALLER!" /quiet InstallAllUsers=0 PrependPath=1 Include_pip=1
    del "!PYTHON_INSTALLER!" 2>nul

    :: Refresh PATH again after the repair install
    for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USER_PATH=%%B"
    for /f "tokens=2*" %%A in ('reg query "HKLM\System\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%B"
    set "PATH=!SYS_PATH!;!USER_PATH!"
    set "PATH=%LOCALAPPDATA%\Microsoft\WindowsApps;!PATH!"
    set "PY_CMD=py -3.13"

    :: Final check — if still broken, the system needs a restart
    py -3.13 --version >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ EX ] Python could not be installed. Please restart this terminal and try again.
        pause & exit /b 1
    )
)
echo [ OK ] Python is active.

:: ── VIRTUAL ENVIRONMENT ────────────────────────────────────────────────────
echo [ .. ] Verifying virtual environment...
if not exist ".venv\Scripts\activate" (
    echo [ .. ] Creating .venv...
    %PY_CMD% -m venv .venv
    if errorlevel 1 (
        echo [ EX ] Failed to create virtual environment.
        pause & exit /b 1
    )
    echo [ OK ] Virtual environment created.
)

call "%~dp0.venv\Scripts\activate"

:: ── INSTALL / UPDATE DEPENDENCIES ──────────────────────────────────────────
:: Hash check via Python (already active in the venv) — avoids any
:: PowerShell cold-start overhead on every subsequent launch.
if exist "requirements.txt" (
    set "REQ_HASH_FILE=.venv\.req_hash"

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
