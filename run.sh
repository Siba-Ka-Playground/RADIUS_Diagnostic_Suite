#!/bin/bash
echo "[*] Initializing ZTAA RADIUS Diagnostic Suite..."

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies silently
echo "[*] Installing dependencies..."
pip install -r requirements.txt -q

# Launch the application
echo "[*] Launching Diagnostic Console..."
python3 app.py