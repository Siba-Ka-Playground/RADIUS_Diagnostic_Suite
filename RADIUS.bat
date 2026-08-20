@echo off
if "%1"=="setup" goto setup
if "%1"=="RADIUS" goto RADIUS
echo Usage: RADIUS.bat [setup^|RADIUS]
goto :eof

:setup
echo [*] Initializing ZTAA RADIUS Diagnostic Suite Setup...

:: Detect and Install Python if missing
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed. Attempting installation via Winget...
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    echo [*] Python installed. Please close this window, reopen the terminal, and run 'RADIUS.bat setup' again.
    pause
    goto :eof
)

echo [*] Setting up local environment...
python -m venv venv
call venv\Scripts\activate
echo [*] Installing Python dependencies...
pip install -r requirements.txt -q
echo [*] Setup complete. Type 'RADIUS.bat RADIUS' to start.
goto :eof

:RADIUS
echo [*] Launching Diagnostic Console...
call venv\Scripts\activate
python app.py
goto :eof