@echo off
:: setup.bat — Windows Command Prompt setup for Poketwo Autocatcher
setlocal EnableDelayedExpansion

:: ── 1. Locate Python 3.12 ────────────────────────────────────────────────────
set PYTHON=

:: Try py launcher first (most reliable on Windows)
py -3.12 --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set PYTHON=py -3.12
    goto :found
)

:: Fall back to bare python / python3
for %%C in (python python3) do (
    %%C -c "import sys; exit(0 if sys.version_info[:2]==(3,12) else 1)" >nul 2>&1
    if !ERRORLEVEL!==0 (
        set PYTHON=%%C
        goto :found
    )
)

echo ERROR: Python 3.12 not found.
echo Install it from https://www.python.org/downloads/ and make sure it is on PATH.
exit /b 1

:found
echo Using interpreter: %PYTHON%

:: ── 2. Create virtual environment ────────────────────────────────────────────
if not exist ".venv\" (
    echo Creating virtual environment in .venv ...
    %PYTHON% -m venv .venv
) else (
    echo Virtual environment already exists, skipping creation.
)

:: ── 3. Activate ───────────────────────────────────────────────────────────────
call .venv\Scripts\activate.bat

:: ── 4. Install dependencies ───────────────────────────────────────────────────
echo Upgrading pip ...
python -m pip install --upgrade pip --quiet

echo Installing dependencies from bot/main/requirements.txt ...
pip install -r bot/main/requirements.txt

echo.
echo Setup complete.
echo   Activate the environment any time with:
echo     .venv\Scripts\activate.bat
echo   Then launch with:
echo     python bot/main/main.py

endlocal
