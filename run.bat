@echo off
echo [*] Initializing ZTAA RADIUS Diagnostic Suite...

:: Create and activate virtual environment
python -m venv venv
call venv\Scripts\activate

:: Install dependencies
echo [*] Installing dependencies...
pip install -r requirements.txt -q

:: Launch the application
echo [*] Launching Diagnostic Console...
python app.py
pause