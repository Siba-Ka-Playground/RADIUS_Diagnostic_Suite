@echo off
echo [*] Initializing ZTAA RADIUS Diagnostic Suite...

:: 1. Detect and Install Python if missing
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed. Attempting installation via Winget...
    winget install -e --id Python.Python.3.11 --accept-package-agreements --accept-source-agreements
    
    echo [*] Python installed. Please close this window and run the script again to refresh environment variables.
    pause
    exit /b
)

:: 2. Setup Virtual Environment
echo [*] Setting up local environment...
python -m venv venv
call venv\Scripts\activate

:: 3. Install Dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt -q

:: 4. Launch Application
echo [*] Launching Diagnostic Console...
python app.py
pause