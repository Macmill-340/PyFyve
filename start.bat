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
    if %errorlevel% neq 0 (
        echo [ EX ] Automatic installation failed.
        echo        Please install Python 3.13 manually from https://python.org
        echo        Make sure to check "Add Python to PATH" during installation.
        pause & exit /b 1
    )
    echo.
    echo [ !! ] Python was just installed.
    echo        Windows requires a restart of this terminal to recognise it.
    echo.
    echo        Please CLOSE this window and run start.bat again.
    echo.
    pause & exit /b 0
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

:: 4. ACTIVATE
call "%~dp0.venv\Scripts\activate"

:: 5. INSTALL / UPDATE DEPENDENCIES (checksum-aware — reinstalls if requirements.txt changes)
if exist "requirements.txt" (
    set "REQ_HASH_FILE=.venv\.req_hash"
    set "CURRENT_HASH="
    for /f "delims=" %%H in ('powershell -NoProfile -Command "Get-FileHash requirements.txt -Algorithm MD5 | Select-Object -ExpandProperty Hash"') do set "CURRENT_HASH=%%H"

    set "STORED_HASH="
    if exist "!REQ_HASH_FILE!" (
        set /p STORED_HASH=<"!REQ_HASH_FILE!"
    )

    if /i "!CURRENT_HASH!" neq "!STORED_HASH!" (
        echo [ .. ] Installing/updating required libraries...
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

:: 6. LAUNCH
echo [ .. ] Starting AI Setup Engine...
python setup.py

pause